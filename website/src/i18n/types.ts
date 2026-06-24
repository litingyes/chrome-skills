export type HubLayer = {
  label: string
  desc: string
}

export type CommandRow = {
  when: string
}

export type Example = {
  id: string
  title: string
  cmd: string
  note: string
}

export type CommandExpand = {
  title: string
  cmd: string
  note: string
}

export type Messages = {
  meta: {
    title: string
    description: string
  }
  common: {
    copy: string
    copied: string
    copyFailed: string
    copyAria: string
    copiedAria: string
    copyFailedAria: string
    skipToContent: string
    opensNewTab: string
  }
  header: {
    navAria: string
    architecture: string
    commands: string
    install: string
    starGithub: string
    languageAria: string
  }
  hero: {
    ledeAfterProject: string
    ledeAfterSkill: string
    title: string
    sub: string
    asideAria: string
    factProject: string
    factSkill: string
    factInvocation: string
    factInvocationValue: string
    factRuntime: string
    runtimeValue: string
  }
  architecture: {
    title: string
    lead: string
    diagramCaption: string
    interactiveHint: string
    flowLabel: string
    flowIdle: string
    layers: {
      l3: HubLayer
      l2: HubLayer
      l1: HubLayer
    }
    composes: string
    note: string
  }
  commands: {
    title: string
    lead: string
    colCommand: string
    colLayer: string
    colWhen: string
    rows: {
      fetch: CommandRow
      search: CommandRow
      audit: CommandRow
      extract: CommandRow
      cdp: CommandRow
    }
    expandExample: string
    collapseExample: string
    expanded: {
      fetch: CommandExpand
      search: CommandExpand
      audit: CommandExpand
      extract: CommandExpand
      cdp: CommandExpand
    }
    examples: Example[]
  }
  install: {
    title: string
    lead: string
    step1Title: string
    step1Label: string
    step2Title: string
    step2Lead: string
    step2Label: string
    step2Note: string
    step3Title: string
    step3Label: string
  }
  footer: {
    license: string
    note: string
  }
}
