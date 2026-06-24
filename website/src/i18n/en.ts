import type { Messages } from './types'

export const en: Messages = {
  meta: {
    title: 'chrome-skills — Chrome automation for AI agents',
    description:
      'chrome-skills publishes the chrome hub skill — one agent skill with composable CDP, extract, search, and fetch commands for browser automation.',
  },
  common: {
    copy: 'Copy',
    copied: 'Copied',
    copyAria: 'Copy command',
    copiedAria: 'Copied',
    skipToContent: 'Skip to content',
  },
  header: {
    navAria: 'Page sections',
    architecture: 'Architecture',
    commands: 'Commands',
    install: 'Install',
    starGithub: 'Star on GitHub',
    languageAria: 'Language',
  },
  hero: {
    ledeAfterProject: 'is the project.',
    ledeAfterSkill: 'is the hub skill you install and invoke.',
    title: 'One skill for Chrome automation',
    sub: 'Instead of loading many separate skills into agent context, chrome-skills publishes a single chrome hub with composable commands — atomic CDP actions, extract modes, and ready-made recipes.',
    asideAria: 'Hub skill at a glance',
    factProject: 'Project',
    factSkill: 'Skill name',
    factInvocation: 'Invocation',
    factRuntime: 'Runtime',
    runtimeValue: 'Local Chrome + Python CDP scripts',
  },
  architecture: {
    title: 'Why a hub skill?',
    lead: 'Agents pay for every skill file in context. chrome-skills keeps one lean SKILL.md router and loads per-command references only when needed. Capabilities stay atomic and composable — without multiplying top-level skills.',
    diagramCaption: 'chrome hub skill command layers from recipes down to CDP atoms',
    interactiveHint: 'Hover or focus an L3 recipe to see how it composes lower layers.',
    flowLabel: 'Composition flow',
    flowIdle: 'Pick a recipe above to trace launch → extract → close.',
    layers: {
      l3: { label: 'L3 · Recipes', desc: 'One-shot workflows' },
      l2: { label: 'L2 · Extract', desc: 'Structured data from the current page' },
      l1: { label: 'L1 · CDP', desc: 'Browser session atoms' },
    },
    composes: 'composes',
    note: 'Invoke with /chrome — the agent loads only the reference for the command you ask for.',
  },
  commands: {
    title: 'Commands you invoke',
    lead: 'Five top-level tokens after /chrome. Recipes wrap lower layers; sessions let you compose your own flows.',
    colCommand: 'Command',
    colLayer: 'Layer',
    colWhen: 'When to use',
    expandExample: 'Show example',
    collapseExample: 'Hide example',
    expanded: {
      fetch: {
        title: 'Fetch an article',
        cmd: '/chrome fetch "https://example.com"',
        note: 'One-shot URL extraction — launch, navigate, extract article, close.',
      },
      search: {
        title: 'Search Google',
        cmd: '/chrome search "python asyncio"',
        note: 'Structured SERP results as JSON for the agent.',
      },
      audit: {
        title: 'Audit a dev URL',
        cmd: '/chrome audit "http://localhost:5173" --viewports 375,1280',
        note: 'Multi-viewport layout checks with factual issue reports.',
      },
      extract: {
        title: 'Extract from the current page',
        cmd: '/chrome extract article --session $SESSION',
        note: 'Requires an open session — use after cdp launch and navigate.',
      },
      cdp: {
        title: 'Compose a session',
        cmd: '/chrome cdp launch → navigate → extract article → cdp close',
        note: 'L1 atoms when you need multiple pages in one browser.',
      },
    },
    rows: {
      fetch: { when: 'Single URL → article JSON' },
      search: { when: 'Google search one-shot' },
      audit: { when: 'Multi-viewport UI layout on a dev URL' },
      extract: { when: 'Structured extraction from the current page (needs session)' },
      cdp: { when: 'Launch, navigate, evaluate, snapshot — build custom flows' },
    },
    examples: [
      {
        id: 'fetch',
        title: 'Fetch an article',
        cmd: '/chrome fetch "https://example.com"',
        note: 'One-shot URL extraction — launch, navigate, extract, close.',
      },
      {
        id: 'search',
        title: 'Search Google',
        cmd: '/chrome search "python asyncio"',
        note: 'Structured SERP results as JSON for the agent.',
      },
      {
        id: 'audit',
        title: 'Audit a dev URL',
        cmd: '/chrome audit "http://localhost:5173" --viewports 375,1280',
        note: 'Multi-viewport layout checks with factual issue reports.',
      },
      {
        id: 'session',
        title: 'Compose a session',
        cmd: '/chrome cdp launch → navigate → extract article → cdp close',
        note: 'L1 atoms when you need multiple pages in one browser.',
      },
    ],
  },
  install: {
    title: 'Install',
    lead: 'Add the skill with Skills CLI, install Python dependencies once, then invoke /chrome in your agent.',
    step1Title: '1. Add the skill',
    step1Label: 'Skills CLI',
    step2Title: '2. Install script dependencies',
    step2Lead: 'From the cloned repo root:',
    step2Label: 'Setup',
    step2Note:
      'Requires Chrome or Chromium and Python 3.10+. Optional: set CHROME_PATH to override binary discovery.',
    step3Title: '3. Invoke in your agent',
    step3Label: 'First command',
  },
  footer: {
    license: 'Apache 2.0',
    note: 'Docs and skill source live in the repository —',
  },
}
