// Choose a test browser without falling back to the user's installed Chrome.
const fs = require('node:fs');
const path = require('node:path');

function launchOptions(env = process.env) {
  const channel = env.PLAYWRIGHT_CHANNEL;
  const guidance = ' Use the connected browser or Playwright bundled Chromium.';
  if (channel && channel !== 'chromium') {
    throw new Error('Installed browser channels are disabled.' + guidance);
  }
  const options = {headless: true};
  if (env.PW_CHROMIUM) {
    const supplied = path.resolve(env.PW_CHROMIUM);
    const resolved = fs.existsSync(supplied) ? fs.realpathSync(supplied) : supplied;
    if ([supplied, resolved].some(value => /(?:^|\/)Google Chrome(?: Canary| Beta| Dev)?\.app(?:\/|$)/i.test(value))) {
      throw new Error('Direct launch of installed Google Chrome is disabled; do not retry with elevated permissions.' + guidance);
    }
    options.executablePath = resolved;
  }
  return options;
}

module.exports = {launchOptions};
