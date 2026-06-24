import { Fragment, useCallback, useRef, useState, type CSSProperties } from 'react'
import { CodeBlock } from './components/CodeBlock'
import { HubDiagram } from './components/HubDiagram'
import { LanguageSwitcher } from './components/LanguageSwitcher'
import { useChromeShortcut, useHeaderScroll, useScrollSpy } from './hooks/useSiteDelight'
import { useI18n } from './i18n/context'
import { withViewTransition } from './lib/viewTransition'
import './App.css'

const GITHUB_REPO = 'https://github.com/litingyes/chrome-skills'
const INSTALL_CMD = 'npx skills add litingyes/chrome-skills'
const SETUP_CMD = 'skills/chrome/scripts/setup'
const FIRST_CMD = '/chrome fetch "https://example.com"'

const SECTION_IDS = ['architecture', 'commands', 'install'] as const

type CommandId = 'fetch' | 'search' | 'audit' | 'extract' | 'cdp'

const commandRows: { id: CommandId; layer: string; tone: 'recipe' | 'extract' | 'cdp' }[] = [
  { id: 'fetch', layer: 'L3', tone: 'recipe' },
  { id: 'search', layer: 'L3', tone: 'recipe' },
  { id: 'audit', layer: 'L3', tone: 'recipe' },
  { id: 'extract', layer: 'L2', tone: 'extract' },
  { id: 'cdp', layer: 'L1', tone: 'cdp' },
]

export default function App() {
  const { messages } = useI18n()
  const { header, hero, architecture, commands, install, footer } = messages
  const commandsRef = useRef<HTMLElement>(null)
  const [commandsPing, setCommandsPing] = useState(false)
  const [expandedCommand, setExpandedCommand] = useState<CommandId | null>(null)
  const activeSection = useScrollSpy(SECTION_IDS)
  const headerScrolled = useHeaderScroll()

  const toggleCommandRow = useCallback((id: CommandId) => {
    withViewTransition(() => {
      setExpandedCommand((current) => (current === id ? null : id))
    })
  }, [])

  const focusCommands = useCallback(() => {
    const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches
    commandsRef.current?.scrollIntoView({
      behavior: prefersReducedMotion ? 'auto' : 'smooth',
      block: 'start',
    })
    setCommandsPing(true)
    window.setTimeout(() => setCommandsPing(false), 1100)
  }, [])

  useChromeShortcut(focusCommands)

  return (
    <div className="page">
      <a className="skip-link" href="#main-content">
        {messages.common.skipToContent}
      </a>
      <header className={`site-header${headerScrolled ? ' site-header--scrolled' : ''}`}>
        <a className="site-logo" href="/">
          <img src="/favicon.svg" width="28" height="28" alt="" aria-hidden="true" />
          <span>chrome-skills</span>
        </a>
        <nav className="site-nav" aria-label={header.navAria}>
          <a
            href="#architecture"
            className={activeSection === 'architecture' ? 'site-nav__link--active' : undefined}
            aria-current={activeSection === 'architecture' ? 'location' : undefined}
          >
            {header.architecture}
          </a>
          <a
            href="#commands"
            className={activeSection === 'commands' ? 'site-nav__link--active' : undefined}
            aria-current={activeSection === 'commands' ? 'location' : undefined}
          >
            {header.commands}
          </a>
          <a
            href="#install"
            className={activeSection === 'install' ? 'site-nav__link--active' : undefined}
            aria-current={activeSection === 'install' ? 'location' : undefined}
          >
            {header.install}
          </a>
        </nav>
        <LanguageSwitcher />
        <a
          className="btn btn--primary"
          href={GITHUB_REPO}
          target="_blank"
          rel="noopener noreferrer"
        >
          <GitHubIcon />
          {header.starGithub}
          <span className="visually-hidden"> {messages.common.opensNewTab}</span>
        </a>
      </header>

      <main id="main-content" tabIndex={-1}>
        <section className="hero" aria-labelledby="hero-title">
          <div className="hero__copy">
            <p className="hero__lede">
              <strong>chrome-skills</strong> {hero.ledeAfterProject}{' '}
              <code className="inline-code">chrome</code> {hero.ledeAfterSkill}
            </p>
            <h1 id="hero-title">{hero.title}</h1>
            <p className="hero__sub">{hero.sub}</p>
          </div>
          <aside className="hero__aside" aria-label={hero.asideAria}>
            <dl className="hero__facts">
              {[
                { label: hero.factProject, value: 'chrome-skills', mono: false },
                { label: hero.factSkill, value: 'chrome', mono: true },
                {
                  label: hero.factInvocation,
                  value: hero.factInvocationValue,
                  mono: true,
                },
                { label: hero.factRuntime, value: hero.runtimeValue, mono: false },
              ].map((fact, index) => (
                <div
                  key={fact.label}
                  className="hero__fact"
                  style={{ '--i': index } as CSSProperties}
                >
                  <dt>{fact.label}</dt>
                  <dd>{fact.mono ? <code>{fact.value}</code> : fact.value}</dd>
                </div>
              ))}
            </dl>
          </aside>
        </section>

        <section id="architecture" className="section section--architecture" aria-labelledby="arch-title">
          <div className="section__intro">
            <h2 id="arch-title">{architecture.title}</h2>
            <p className="section__lead">{architecture.lead}</p>
          </div>
          <HubDiagram />
        </section>

        <section
          id="commands"
          ref={commandsRef}
          className={`section section--commands${commandsPing ? ' section--ping' : ''}`}
          aria-labelledby="commands-title"
        >
          <div className="section__intro">
            <h2 id="commands-title">{commands.title}</h2>
            <p className="section__lead">{commands.lead}</p>
          </div>
          <div className="command-table-wrap">
            <table className="command-table">
              <thead>
                <tr>
                  <th scope="col">{commands.colCommand}</th>
                  <th scope="col">{commands.colLayer}</th>
                  <th scope="col">{commands.colWhen}</th>
                  <th scope="col" className="visually-hidden">
                    {commands.expandExample}
                  </th>
                </tr>
              </thead>
              <tbody>
                {commandRows.map(({ id, layer, tone }) => {
                  const expanded = expandedCommand === id
                  const example = commands.expanded[id]
                  const expandLabel = expanded ? commands.collapseExample : commands.expandExample

                  return (
                    <Fragment key={id}>
                      <tr
                        className={`command-table__row command-table__row--${tone}${expanded ? ' command-table__row--expanded' : ''}`}
                      >
                        <td>
                          <code>{id}</code>
                        </td>
                        <td>
                          <span className={`command-table__layer command-table__layer--${tone}`}>
                            {layer}
                          </span>
                        </td>
                        <td>{commands.rows[id].when}</td>
                        <td className="command-table__action">
                          <button
                            type="button"
                            className="command-table__toggle"
                            aria-expanded={expanded}
                            aria-controls={`command-expand-${id}`}
                            onClick={() => toggleCommandRow(id)}
                          >
                            <span className="command-table__toggle-label">{expandLabel}</span>
                            <ChevronIcon expanded={expanded} />
                          </button>
                        </td>
                      </tr>
                      <tr
                        className={`command-table__expand command-table__expand--${tone}`}
                        hidden={!expanded}
                      >
                        <td colSpan={4} id={`command-expand-${id}`}>
                          {expanded ? (
                            <div
                              className="command-table__expand-panel"
                              style={{ viewTransitionName: `command-expand-${id}` }}
                            >
                              <h3 className="command-table__expand-title">{example.title}</h3>
                              <CodeBlock code={example.cmd} label={example.title} />
                              <p className="command-table__expand-note">{example.note}</p>
                            </div>
                          ) : null}
                        </td>
                      </tr>
                    </Fragment>
                  )
                })}
              </tbody>
            </table>
          </div>
          <ul className="example-list">
            {commands.examples.map((ex, index) => (
              <li
                key={ex.id}
                className="example-item"
                style={{ '--i': index } as CSSProperties}
              >
                <h3>{ex.title}</h3>
                <CodeBlock code={ex.cmd} label={ex.title} />
                <p>{ex.note}</p>
              </li>
            ))}
          </ul>
        </section>

        <section id="install" className="section section--install" aria-labelledby="install-title">
          <div className="section__intro">
            <h2 id="install-title">{install.title}</h2>
            <p className="section__lead">{install.lead}</p>
          </div>
          <ol className="install-steps">
            {[
              {
                title: install.step1Title,
                body: <CodeBlock code={INSTALL_CMD} label={install.step1Label} />,
              },
              {
                title: install.step2Title,
                body: (
                  <>
                    <p>{install.step2Lead}</p>
                    <CodeBlock code={SETUP_CMD} label={install.step2Label} />
                    <p className="install-note">{install.step2Note}</p>
                  </>
                ),
              },
              {
                title: install.step3Title,
                body: <CodeBlock code={FIRST_CMD} label={install.step3Label} />,
              },
            ].map((step, index) => (
              <li
                key={step.title}
                className="install-step"
                style={{ '--i': index } as CSSProperties}
              >
                <h3>{step.title}</h3>
                {step.body}
              </li>
            ))}
          </ol>
        </section>
      </main>

      <footer className="site-footer">
        <p>
          <a href={GITHUB_REPO} target="_blank" rel="noopener noreferrer">
            litingyes/chrome-skills
            <span className="visually-hidden"> {messages.common.opensNewTab}</span>
          </a>
          <span aria-hidden="true"> · </span>
          {footer.license}
        </p>
        <p className="site-footer__note">
          {footer.note}{' '}
          <a href={`${GITHUB_REPO}/tree/main/skills/chrome`}>skills/chrome/</a>
        </p>
      </footer>
    </div>
  )
}

function ChevronIcon({ expanded }: { expanded: boolean }) {
  return (
    <svg
      className={`command-table__chevron${expanded ? ' command-table__chevron--expanded' : ''}`}
      width="14"
      height="14"
      viewBox="0 0 14 14"
      aria-hidden="true"
    >
      <path d="M3.5 5.25 7 8.75l3.5-3.5" fill="none" stroke="currentColor" strokeWidth="1.5" />
    </svg>
  )
}

function GitHubIcon() {
  return (
    <svg width="18" height="18" viewBox="0 0 24 24" aria-hidden="true" fill="currentColor">
      <path d="M12 0C5.37 0 0 5.37 0 12c0 5.31 3.435 9.795 8.205 11.385.6.105.825-.255.825-.57 0-.285-.015-1.23-.015-2.235-3.015.555-3.795-.735-4.035-1.395-.135-.345-.72-1.395-1.23-1.89-.42-.405-1.02-.705-.015-.72.945-.015 1.62.87 1.845 1.23 1.08 1.815 2.805 1.305 3.495.99.105-.78.42-1.305.765-1.605-2.67-.3-5.46-1.335-5.46-5.925 0-1.305.465-2.385 1.23-3.225-.12-.3-.54-1.53.12-3.18 0 0 1.005-.315 3.3 1.23.96-.27 1.98-.405 3-.405s2.04.135 3 .405c2.295-1.56 3.3-1.23 3.3-1.23.66 1.65.24 2.88.12 3.18.765.84 1.23 1.905 1.23 3.225 0 4.605-2.805 5.625-5.475 5.925.435.375.81 1.095.81 2.22 0 1.605-.015 2.895-.015 3.3 0 .315.225.69.825.57A12.02 12.02 0 0 0 24 12c0-6.63-5.37-12-12-12z" />
    </svg>
  )
}
