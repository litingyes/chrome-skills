export function withViewTransition(update: () => void) {
  if (typeof document.startViewTransition === 'function') {
    document.startViewTransition(() => update())
    return
  }
  update()
}
