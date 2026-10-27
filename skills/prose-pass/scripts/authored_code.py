"""Extract JavaScript strings, templates, comments and JSON without executing it.

This is a lexical reader, not an evaluator. Unterminated constructs are errors.
The caller checks every returned text value, including UI text inside templates.
"""
import json
import re


def javascript_parts(source):
    parts = []
    length = len(source)
    index = 0

    def literal(quote):
        nonlocal index
        index += 1
        text = []
        while index < length:
            char = source[index]
            if char == quote:
                index += 1
                parts.append(''.join(text))
                return
            if char == '\\':
                index += 1
                if index >= length:
                    break
                char = source[index]
                escapes = {'n': '\n', 'r': '\r', 't': '\t', 'b': '\b', 'f': '\f', 'v': '\v', '0': '\0'}
                if char in ('u', 'x'):
                    count = 4 if char == 'u' else 2
                    if char == 'u' and source[index + 1:index + 2] == '{':
                        end = source.find('}', index + 2)
                        if end < 0:
                            raise SyntaxError('Unterminated Unicode escape')
                        text.append(chr(int(source[index + 2:end], 16)))
                        index = end + 1
                    else:
                        value = source[index + 1:index + 1 + count]
                        if len(value) != count:
                            raise SyntaxError('Incomplete character escape')
                        text.append(chr(int(value, 16)))
                        index += count + 1
                    continue
                if char == '\r' and source[index + 1:index + 2] == '\n':
                    index += 1
                if char not in ('\n', '\r'):
                    text.append(escapes.get(char, char))
                index += 1
                continue
            if quote == '`' and source[index:index + 2] == '${':
                index += 2
                code(True)
                text.append(' ')
                continue
            if char in ('\n', '\r') and quote != '`':
                raise SyntaxError('Unterminated JavaScript string')
            text.append(char)
            index += 1
        raise SyntaxError('Unterminated JavaScript string or template')

    def code(expression=False):
        nonlocal index
        depth = 1
        previous = ''
        while index < length:
            char = source[index]
            if char.isspace():
                index += 1
                continue
            if source.startswith('//', index):
                end = source.find('\n', index + 2)
                end = length if end < 0 else end
                parts.append(source[index + 2:end])
                index = end
                continue
            if source.startswith('/*', index):
                end = source.find('*/', index + 2)
                if end < 0:
                    raise SyntaxError('Unterminated JavaScript comment')
                parts.append(source[index + 2:end])
                index = end + 2
                continue
            if char in "\"'`":
                literal(char)
                previous = 'value'
                continue
            if char in '{[' and previous == '=':
                try:
                    value, consumed = json.JSONDecoder().raw_decode(source[index:])
                except ValueError:
                    pass
                else:
                    parts.append(value)
                    index += consumed
                    previous = 'value'
                    continue
            if char == '/' and (not previous or previous in ('=', '(', '[', '{', ',', ':', ';', '!', '?', '&', '|', 'return', 'throw', 'case', '=>', 'typeof', 'in', 'of', 'else', '+', '-', '*', '%', '^', '~', '<', '>')):
                index += 1
                in_class = False
                while index < length:
                    token = source[index]
                    if token == '\\':
                        index += 2
                        continue
                    if token == '\n':
                        raise SyntaxError('Unterminated JavaScript regular expression')
                    if token == '[':
                        in_class = True
                    elif token == ']':
                        in_class = False
                    elif token == '/' and not in_class:
                        index += 1
                        while index < length and source[index].isalpha():
                            index += 1
                        break
                    index += 1
                else:
                    raise SyntaxError('Unterminated JavaScript regular expression')
                previous = 'value'
                continue
            word = re.match(r'[\w$]+', source[index:])
            if word:
                previous = word.group()
                index += len(previous)
                continue
            if expression:
                if char == '{':
                    depth += 1
                elif char == '}':
                    depth -= 1
                    if depth == 0:
                        index += 1
                        return
            if source[index:index + 2] in ('++', '--'):
                previous = 'value' if previous not in ('', '=', '(', '[', '{', ',', ':', ';', 'return', 'throw', '=>') else source[index:index + 2]
                index += 2
                continue
            if source.startswith('=>', index):
                previous = '=>'
                index += 2
            else:
                previous = char
                index += 1
        if expression:
            raise SyntaxError('Unterminated JavaScript template expression')

    code()
    return parts
