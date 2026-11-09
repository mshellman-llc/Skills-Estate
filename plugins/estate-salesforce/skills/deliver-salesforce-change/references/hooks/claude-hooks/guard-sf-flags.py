#!/usr/bin/env python3
"""Check literal Salesforce CLI calls in Claude hook events; never execute them.

This is a workflow guard, not a shell security boundary. Scripts and dynamically
constructed commands still require agent review and an org identity preflight.
"""
import json
import os
import shlex
import sys


def refuse(message):
    print('BLOCKED: ' + message, file=sys.stderr)
    return 2


def check(command):
    # Quoted messages that mention a command are not invocations. Each literal
    # sf executable token is checked, including multiple calls on one line.
    lexer = shlex.shlex(command, posix=True, punctuation_chars=';&|()<>')
    lexer.whitespace_split = True
    try:
        tokens = list(lexer)
    except ValueError:
        return refuse('Could not parse the shell command. Use a plain, separate command.')
    for i, token in enumerate(tokens):
        if os.path.basename(token) not in ('sf', 'sfdx'):
            continue
        args = []
        for value in tokens[i + 1:]:
            if value and all(c in ';&|()<>' for c in value):
                break
            args.append(value)
        if any(a == '--use-most-recent' or a.startswith('--use-most-recent=') for a in args):
            return refuse('Use the recorded deployment job ID; --use-most-recent can select another job.')
        if '--help' in args or '-h' in args or not args:
            continue
        # These operations use local files, local configuration, or cached auth
        # listings. Generating a manifest FROM AN ORG is deliberately excluded.
        local = (args[:1] in (['version'], ['--version']) or
                 args[:2] in (['config', 'get'], ['config', 'list'], ['alias', 'list'],
                              ['org', 'list'], ['plugins', 'inspect'], ['plugins', 'list']) or
                 args[:3] in (['project', 'convert', 'source'], ['project', 'convert', 'mdapi'],
                              ['project', 'generate', 'project']) or
                 (args[:3] == ['project', 'generate', 'manifest'] and
                  not any(a == '--from-org' or a.startswith('--from-org=') for a in args)))
        if local:
            continue
        targets = []
        for n, arg in enumerate(args):
            if arg in ('--target-org', '-o', '--targetusername'):
                if n + 1 >= len(args) or args[n + 1].startswith('-'):
                    return refuse('The explicit org target is missing its value.')
                targets.append(args[n + 1])
            elif arg.startswith(('--target-org=', '--targetusername=', '-o=')):
                targets.append(arg.split('=', 1)[1])
        if len(targets) != 1 or not targets[0].strip():
            return refuse('Use one explicit --target-org for this org operation. With no confirmed org, continue local preparation only.')
        retrieve = (args[:2] == ['project', 'retrieve'] or
                    args[:1] in (['force:source:retrieve'], ['force:mdapi:retrieve']))
        if retrieve:
            return refuse('Retrieve through the reviewed seeding workflow into a separate scratch tree; this routine hook does not authorize source replacement.')
    return 0


def main():
    try:
        event = json.load(sys.stdin)
        command = event['tool_input']['command']
        if not isinstance(command, str):
            raise ValueError('command is not a string')
    except (ValueError, KeyError, TypeError):
        return refuse('Hook input must contain tool_input.command as a string.')
    return check(command)


if __name__ == '__main__':
    raise SystemExit(main())
