#!/bin/bash
# Ticket-system adapter. SOURCED by _lib.sh, never run.
#
# ── WHAT LIVES HERE, AND WHAT DELIBERATELY DOES NOT ─────────────────────────
# The local loop does ticket references and NOTHING ELSE to a tracker from a
# hook. It does not read a ticket's state, label it, comment on it, or close it —
# because:
#
#   * A hook is a bash subprocess and CANNOT reach the session's MCP connection.
#     There is no token or endpoint a spawned hook could use. So any Jira network
#     work must be done by the AGENT (which can call the Atlassian Rovo MCP), never
#     by a hook. See references/ticket-adapters.md.
#
#   * Ticket CLOSURE is out of this loop's scope entirely. A sandbox deploy does
#     not make a ticket "done"; tickets stay open until production, which is the
#     the production delivery system's domain, not the local loop's. So nothing here gates or
#     performs a closure. The agent closes a ticket only when the user asks.
#
# What remains is one tracker-agnostic capability check. Ticket-ref parsing,
# examples and config reads live in _config.sh (ticket_system, ticket_project,
# ticket_remote, ticket_example, ref_pattern, extract_refs, ticket_label).

# Is the tracker CLI we would need even installed? GitHub tickets are GitHub
# issues, reachable from a shell via `gh`; audit reports whether it is present.
# Jira is handled agent-side through the Rovo MCP — there is no CLI for a bash
# hook to check, so it is not a shell-callable tracker here.
ticket_cli_present() {
  case "$(ticket_system)" in
    github) command -v gh >/dev/null 2>&1 ;;
    *)      return 1 ;;
  esac
}
