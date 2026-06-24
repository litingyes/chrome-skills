import { en } from './en'
import { zhCN } from './zh-CN'
import type { Messages } from './types'

export const LOCALES = [
  { id: 'en', label: 'English', htmlLang: 'en', messages: en },
  { id: 'zh-CN', label: '简体中文', htmlLang: 'zh-CN', messages: zhCN },
] as const

export type Locale = (typeof LOCALES)[number]['id']

export const DEFAULT_LOCALE: Locale = 'en'

const localeIds = new Set<string>(LOCALES.map((l) => l.id))

export function isLocale(value: string): value is Locale {
  return localeIds.has(value)
}

export function getLocaleConfig(locale: Locale) {
  const config = LOCALES.find((l) => l.id === locale)
  if (!config) throw new Error(`Unknown locale: ${locale}`)
  return config
}

export function getMessages(locale: Locale): Messages {
  return getLocaleConfig(locale).messages
}
