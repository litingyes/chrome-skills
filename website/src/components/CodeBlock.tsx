import { useState } from 'react'
import { useI18n } from '../i18n/context'

type CodeBlockProps = {
  code: string
  label?: string
}

type CopyState = 'idle' | 'copied' | 'failed'

export function CodeBlock({ code, label }: CodeBlockProps) {
  const { messages } = useI18n()
  const [copyState, setCopyState] = useState<CopyState>('idle')

  async function handleCopy() {
    try {
      await navigator.clipboard.writeText(code)
      setCopyState('copied')
      window.setTimeout(() => setCopyState('idle'), 2000)
    } catch {
      setCopyState('failed')
      window.setTimeout(() => setCopyState('idle'), 2500)
    }
  }

  const { common } = messages
  const copyLabel =
    copyState === 'copied'
      ? common.copied
      : copyState === 'failed'
        ? common.copyFailed
        : common.copy
  const copyAria =
    copyState === 'copied'
      ? common.copiedAria
      : copyState === 'failed'
        ? common.copyFailedAria
        : common.copyAria

  const copyButtonClass = [
    'code-block__copy',
    copyState === 'copied' ? 'code-block__copy--copied' : '',
    copyState === 'failed' ? 'code-block__copy--failed' : '',
  ]
    .filter(Boolean)
    .join(' ')

  return (
    <div className={`code-block${copyState === 'copied' ? ' code-block--copied' : ''}`}>
      {label ? (
        <div className="code-block__header">
          <span className="code-block__label">{label}</span>
          <button
            type="button"
            className={copyButtonClass}
            onClick={handleCopy}
            aria-label={copyAria}
          >
            {copyState === 'copied' ? <CheckIcon /> : null}
            <span aria-live="polite">{copyLabel}</span>
          </button>
        </div>
      ) : (
        <button
          type="button"
          className={`${copyButtonClass} code-block__copy--solo`}
          onClick={handleCopy}
          aria-label={copyAria}
        >
          {copyState === 'copied' ? <CheckIcon /> : null}
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
