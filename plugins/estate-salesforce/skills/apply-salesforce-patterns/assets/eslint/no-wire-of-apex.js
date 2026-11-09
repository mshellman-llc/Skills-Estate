/**
 * ESLint rule: no-wire-of-apex (LWC001)
 *
 * Flags @wire(...) of a method imported from '@salesforce/apex/...'. House pattern is
 * imperative Apex — explicit call sites, explicit error handling, portable to React.
 * LDS wires (lightning/uiRecordApi etc.) are untouched.
 *
 * PMD cannot parse modern LWC JavaScript, so this rule lives in ESLint, next to the
 * @salesforce/eslint-config-lwc stack every sfdx repo already runs.
 *
 * Wiring it up (eslint-plugin-local-rules approach):
 *   1. npm i -D eslint-plugin-local-rules
 *   2. Put this file at eslint-local-rules/no-wire-of-apex.js and create
 *      eslint-local-rules/index.js:  module.exports = { 'no-wire-of-apex': require('./no-wire-of-apex') };
 *   3. .eslintrc: { "plugins": ["local-rules"], "rules": { "local-rules/no-wire-of-apex": "warn" } }
 * Escalate "warn" to "error" on greenfield repos, mirroring the APX rule tiers.
 *
 * Suppress a deliberate exception with a reason, same policy as Apex:
 *   // eslint-disable-next-line local-rules/no-wire-of-apex -- legacy component, refactor tracked in W-0001234
 */
'use strict';

module.exports = {
    meta: {
        type: 'suggestion',
        docs: {
            description:
                'Apex methods are called imperatively (house architecture LWC001); ' +
                '@wire is reserved for LDS adapters',
        },
        schema: [],
        messages: {
            noWireApex:
                "@wire({{name}}) wires an Apex method — call it imperatively " +
                "(await {{name}}(...)); LDS wires (lightning/ui*Api) are fine.",
        },
    },
    create(context) {
        const apexImports = new Set();
        return {
            ImportDeclaration(node) {
                if (
                    typeof node.source.value === 'string' &&
                    node.source.value.startsWith('@salesforce/apex/')
                ) {
                    for (const spec of node.specifiers) {
                        if (spec.local) {
                            apexImports.add(spec.local.name);
                        }
                    }
                }
            },
            // 'wire' only ever appears as a decorator call, so matching the call
            // expression directly keeps the rule parser-agnostic.
            CallExpression(node) {
                if (
                    node.callee.type === 'Identifier' &&
                    node.callee.name === 'wire' &&
                    node.arguments.length > 0 &&
                    node.arguments[0].type === 'Identifier' &&
                    apexImports.has(node.arguments[0].name)
                ) {
                    context.report({
                        node,
                        messageId: 'noWireApex',
                        data: { name: node.arguments[0].name },
                    });
                }
            },
        };
    },
};
