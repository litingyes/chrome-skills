import { useState } from 'react'
import { useI18n } from '../i18n/context'

type CodeBlockProps = {
  code: string
  label?: string
}

export function CodeBlock({ code, label }: CodeBlockProps) {
  const { messages } = useI18n()
  const [copied, setCopied] = useState(false)

  async function handleCopy() {
    try {
      await navigator.clipboard.writeText(code)
      setCopied(true)
      window.setTimeout(() => setCopied(false), 2000)
    } catch {
      setCopied(false)
    }
  }

  const copyLabel = copied ? messages.common.copied : messages.common.copy
  const copyAria = copied ? messages.common.copiedAria : messages.common.copyAria

  return (
    <div className={`code-block${copied ? ' code-block--copied' : ''}`}>
      {label ? (
        <div className="code-block__header">
          <span className="code-block__label">{label}</span>
          <button
            type="button"
            className={`code-block__copy${copied ? ' code-block__copy--copied' : ''}`}
            onClick={handleCopy}
            aria-label={copyAria}
          >
            {copied ? <CheckIcon /> : null}
            <span aria-live="polite">{copyLabel}</span>
          </button>
        </div>
      ) : (
        <button
          type="button"
          className={`code-block__copy code-block__copy--solo${copied ? ' code-block__copy--copied' : ''}`}
          onClick={handleCopy}
          aria-label={copyAria}
        >
          {copied ? <CheckIcon /> : null}
          <span aria-live="polite">{copyLabel}</span>
        </button>
      )}
      <pre>
        <code>{code}</code>
      </pre>
    </div>
  )
}

function CheckIcon() {
  return (
    <svg className="code-block__copy-icon" viewBox="0 0 12 12" aria-hidden="true">
      <path d="M2 6.25 4.75 9 10 3" />
    </svg>
  )
}
