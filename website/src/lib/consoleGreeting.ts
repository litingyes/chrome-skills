export function logConsoleGreeting() {
  const title = 'color: oklch(0.52 0.14 250); font-weight: 600; font-size: 13px'
  const body = 'color: inherit; font-size: 12px'

  console.log('%cchrome-skills%c — hub skill for agent browser automation.', title, body)
  console.log(
    '%cTip:%c type %c/chrome%c anywhere on this page.',
    'font-weight: 600',
    body,
    'font-family: monospace',
    body,
  )
  console.log('Source: https://github.com/litingyes/chrome-skills')
}
