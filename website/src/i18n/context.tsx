import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
  type ReactNode,
} from 'react'
import {
  DEFAULT_LOCALE,
  getLocaleConfig,
  getMessages,
  isLocale,
  type Locale,
} from './locales'
import type { Messages } from './types'
import { withViewTransition } from '../lib/viewTransition'

const STORAGE_KEY = 'chrome-skills-locale'

function readStoredLocale(): Locale {
  try {
    const stored = localStorage.getItem(STORAGE_KEY)
    if (stored && isLocale(stored)) return stored
  } catch {
    /* ignore */
  }
  return DEFAULT_LOCALE
}

type I18nContextValue = {
  locale: Locale
  messages: Messages
  setLocale: (locale: Locale) => void
}

const I18nContext = createContext<I18nContextValue | null>(null)

export function I18nProvider({ children }: { children: ReactNode }) {
  const [locale, setLocaleState] = useState<Locale>(readStoredLocale)

  const setLocale = useCallback((next: Locale) => {
    withViewTransition(() => {
      setLocaleState(next)
      try {
        localStorage.setItem(STORAGE_KEY, next)
      } catch {
        /* ignore */
      }
    })
  }, [])

  const messages = getMessages(locale)

  useEffect(() => {
    const { htmlLang } = getLocaleConfig(locale)
    document.documentElement.lang = htmlLang
    document.title = messages.meta.title

    const meta = document.querySelector('meta[name="description"]')
    if (meta) meta.setAttribute('content', messages.meta.description)
  }, [locale, messages])

  const value = useMemo(
    () => ({ locale, messages, setLocale }),
    [locale, messages, setLocale],
  )

  return <I18nContext.Provider value={value}>{children}</I18nContext.Provider>
}

export function useI18n() {
  const ctx = useContext(I18nContext)
  if (!ctx) throw new Error('useI18n must be used within I18nProvider')
  return ctx
}

export type { Locale }
