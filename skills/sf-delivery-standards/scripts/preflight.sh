#!/bin/bash
# preflight.sh — what is installed, what is authenticated, what is missing.
#
#   preflight.sh                        # infer requirements from aleysian.* config
#   preflight.sh --ticket-system jira --host github    # before init, when there is no config
#
# WHY THIS EXISTS AS ITS OWN SCRIPT
# --------------------------------
# "Install the prerequisites" is not an actionable sentence. This gives the agent a
# machine-readable answer to "what is actually missing here" and prints one
# copy-pasteable command per gap, rather than pointing at a wall of documentation.
#
# It also separates two states that look identical from the outside and are not:
# a tool that is MISSING, and a tool that is installed but NOT AUTHENTICATED. The
# second is more dangerous, because everything reports fine and every call fails.
#
# AUTH IS ALWAYS INTERACTIVE HERE
# -------------------------------
# Every auth command this prints is a browser or device flow. None of them takes a
# token as an argument, and that is deliberate: the alternative teaches people to
# paste long-lived credentials into a terminal — or worse, into a chat window with
# an AI agent in it, where it lands in a transcript. There is no case where an agent
# should be handling one of these secrets. See references/prerequisites.md.
#
# Exit 0 when everything REQUIRED is present and authenticated, 1 otherwise.
# Optional gaps never fail the run; they are reported as what they cost.

set -u

TSYS=""; HOSTV=""
while [ $# -gt 0 ]; do
  case "$1" in
    --ticket-system) TSYS="$2"; shift ;;
    --host)          HOSTV="$2"; shift ;;
    -h|--help) sed -n '1,30p' "$0"; exit 0 ;;
    *) echo "unknown argument: $1" >&2; exit 1 ;;
  esac
  shift
done

# Fall back to the repo's config when the flags are absent (i.e. after init).
if git rev-parse --git-dir >/dev/null 2>&1; then
  [ -z "$TSYS" ]  && TSYS=$(git config aleysian.ticket.system 2>/dev/null || echo "")
  [ -z "$HOSTV" ] && HOSTV=$(git config aleysian.host 2>/dev/null || echo "")
fi
TSYS="${TSYS:-github}"; HOSTV="${HOSTV:-github}"

MISSING=0
ok()   { printf '  \033[32mok\033[0m       %-12s %s\n' "$1" "${2:-}"; }
gap()  { printf '  \033[31mMISSING\033[0m  %-12s %s\n' "$1" "$2"; MISSING=1; }
auth() { printf '  \033[33mNO AUTH\033[0m  %-12s %s\n' "$1" "$2"; MISSING=1; }
soft() { printf '  \033[33moptional\033[0m %-12s %s\n' "$1" "$2"; }
fix()  { printf '           \033[1m%s\033[0m\n' "$1"; }
sect() { printf '\n\033[1m%s\033[0m\n' "$1"; }

OS="$(uname -s)"
printf '\n\033[1mPrerequisites\033[0m  (ticket=%s host=%s os=%s)\n' "$TSYS" "$HOSTV" "$OS"

# ═══ Package manager — everything else installs through it ═════
sect "Package manager"
# macOS is the supported platform. Elsewhere the tool checks below still hold; only
# the install commands differ, so report and stay out of the way rather than
# printing brew commands that will not work.
if [ "$OS" = "Darwin" ]; then
  if command -v brew >/dev/null 2>&1; then ok brew "$(brew --version 2>/dev/null | head -1)"
  else
    gap brew "Homebrew installs everything below — the prerequisite to the prerequisites."
    fix '/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"'
    printf '           Asks for the Mac password once, then prints two more commands that put\n'
    printf '           brew on the PATH. Run those, then open a NEW terminal window.\n'
  fi
else
  soft "n/a" "$OS — the checks below still apply; install each with your own package manager"
fi

# ═══ Required, regardless of configuration ════════════════════
sect "Required"

if command -v git >/dev/null 2>&1; then ok git "$(git --version | awk '{print $3}')"
else gap git "the entire stack is git hooks"; fix "brew install git"; fi

if command -v sf >/dev/null 2>&1; then ok sf "$(sf --version 2>/dev/null | head -1 | awk '{print $1}')"
else
  gap sf "no deploys, no validates — this is the Salesforce CLI"
  fix "brew install --cask sf-cli        # or: npm install -g @salesforce/cli"
fi

if command -v jq >/dev/null 2>&1; then ok jq "$(jq --version)"
else
  gap jq "hooks parse JSON with it, and install.sh REFUSES to merge your Claude settings without it"
  fix "brew install jq"
fi

# ═══ Tracker ══════════════════════════════════════════════════
sect "Tracker ($TSYS)"
case "$TSYS" in
  github)
    if ! command -v gh >/dev/null 2>&1; then
      gap gh "issue create/comment/view and deploy annotation need it"
      fix "brew install gh"
      fix "gh auth login          # interactive: pick GitHub.com, then a browser opens"
    elif gh auth status >/dev/null 2>&1; then
      ok gh "$(gh auth status 2>&1 | grep -m1 'Logged in' | sed 's/^ *//')"
    else
      auth gh "installed, but not logged in — every tracker call fails silently"
      fix "gh auth login"
    fi ;;
  jira)
    # Jira is agent-side via the Atlassian Rovo MCP now — no CLI to install or
    # authenticate, and a bash preflight cannot reach an MCP, so nothing to check here.
    soft "Rovo MCP" "Jira runs agent-side via the Atlassian Rovo MCP (company-wide, interactive"
    printf '           auth). There is no tracker CLI to install — confirm the Rovo MCP is\n'
    printf '           connected in your Claude client.\n' ;;
  pattern|none)
    soft "n/a" "ticket.system=$TSYS needs no CLI — refs and the audit trail only" ;;
esac

# ═══ Host ═════════════════════════════════════════════════════
sect "Host ($HOSTV)"
case "$HOSTV" in
  github)
    command -v gh >/dev/null 2>&1 && ok gh "also the merge surface" \
      || { gap gh "no PR create or merge"; fix "brew install gh && gh auth login"; } ;;
  gitlab)
    if command -v glab >/dev/null 2>&1; then ok glab ""
    else gap glab "no MR create or merge"; fix "brew install glab"; fix "glab auth login   # interactive"; fi ;;
  azure)
    if command -v az >/dev/null 2>&1; then ok az ""
    else gap az "no PR create or complete"; fix "brew install azure-cli"; fix "az login   # opens a browser"; fi ;;
  bitbucket)
    soft "n/a" "no CLI exists — merges happen in the browser, and guard-push.sh gates the push instead" ;;
  none)
    soft "n/a" "no remote — aleysian-merge is the review gate (add ~/.aleysian/bin to PATH)" ;;
esac

# ═══ Quality gates — degrade loudly, never block ══════════════
sect "Quality gates (optional, but each gap is a real hole)"

if [ -f package.json ]; then
  command -v node >/dev/null 2>&1 && ok node "$(node --version)" \
    || { soft node "prettier, ESLint and Jest gates all skip without it"; fix "brew install node"; }
  [ -d node_modules ] && ok node_modules "installed" \
    || { soft node_modules "gates 2, 3 and 5 warn and skip"; fix "npm install"; }
else
  soft "npm" "no package.json — prettier/ESLint/Jest gates are inert in this project"
fi

command -v pmd >/dev/null 2>&1 && ok pmd "installed" \
  || { soft pmd "staged Apex goes in unanalysed — the gate warns rather than blocking"; fix "brew install pmd"; }

# ═══ Verdict ══════════════════════════════════════════════════
printf '\n'
if [ "$MISSING" = "0" ]; then
  printf '\033[32mAll required prerequisites are present and authenticated.\033[0m\n\n'
  exit 0
fi
printf '\033[31mSomething required is missing or unauthenticated.\033[0m Run the bold commands above,\n'
printf 'in order, then re-run this script. Anything asking for a password wants YOUR Mac or\n'
printf 'browser password — type it in the terminal or the browser, never into a chat window.\n\n'
exit 1
