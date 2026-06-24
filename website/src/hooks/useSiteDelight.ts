import { useEffect, useState } from 'react'

export function useScrollSpy(sectionIds: readonly string[]) {
  const [activeId, setActiveId] = useState<string | null>(null)

  useEffect(() => {
    const sections = sectionIds
      .map((id) => document.getElementById(id))
      .filter((el): el is HTMLElement => el !== null)

    if (sections.length === 0) return

    const observer = new IntersectionObserver(
      (entries) => {
        const visible = entries
          .filter((entry) => entry.isIntersecting)
          .sort((a, b) => b.intersectionRatio - a.intersectionRatio)

        if (visible[0]?.target.id) {
          setActiveId(visible[0].target.id)
        }
      },
      { rootMargin: '-18% 0px -62% 0px', threshold: [0, 0.2, 0.45, 0.7] },
    )

    for (const section of sections) {
      observer.observe(section)
    }

    return () => observer.disconnect()
  }, [sectionIds])

  return activeId
}

export function useChromeShortcut(onMatch: () => void) {
  useEffect(() => {
    const sequence = '/chrome'
    let buffer = ''
    let resetTimer: number | undefined

    function resetBuffer() {
      buffer = ''
    }

    function onKeyDown(event: KeyboardEvent) {
      const target = event.target
      if (
        target instanceof HTMLInputElement ||
        target instanceof HTMLTextAreaElement ||
        target instanceof HTMLSelectElement ||
        (target instanceof HTMLElement && target.isContentEditable)
      ) {
        return
      }

      if (event.metaKey || event.ctrlKey || event.altKey) return

      buffer += event.key
      if (!sequence.startsWith(buffer)) {
        buffer = event.key === '/' ? '/' : ''
      }

      if (buffer === sequence) {
        onMatch()
        buffer = ''
      }

      window.clearTimeout(resetTimer)
      resetTimer = window.setTimeout(resetBuffer, 1400)
    }

    window.addEventListener('keydown', onKeyDown)
    return () => {
      window.removeEventListener('keydown', onKeyDown)
      window.clearTimeout(resetTimer)
    }
  }, [onMatch])
}
