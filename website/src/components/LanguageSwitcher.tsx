import { useI18n } from '../i18n/context'
import { isLocale, LOCALES } from '../i18n/locales'

export function LanguageSwitcher() {
  const { locale, setLocale, messages } = useI18n()

  return (
    <div className="lang-select">
      <label className="lang-select__label visually-hidden" htmlFor="site-locale">
        {messages.header.languageAria}
      </label>
      <select
        id="site-locale"
        className="lang-select__control"
        value={locale}
        onChange={(e) => {
          if (isLocale(e.target.value)) setLocale(e.target.value)
        }}
      >
        {LOCALES.map(({ id, label }) => (
          <option key={id} value={id}>
            {label}
          </option>
        ))}
      </select>
    </div>
  )
}
