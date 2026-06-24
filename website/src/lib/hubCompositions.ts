export type RecipeId = 'fetch' | 'search' | 'audit'

export type HubComposition = {
  l2: readonly string[]
  l1: readonly string[]
}

/** Recipe → lower-layer composition (matches skills/chrome/references/*.md) */
export const hubCompositions: Record<RecipeId, HubComposition> = {
  fetch: {
    l2: ['article'],
    l1: ['launch', 'navigate', 'wait', 'close'],
  },
  search: {
    l2: ['serp'],
    l1: ['launch', 'navigate', 'wait', 'close'],
  },
  audit: {
    l2: ['layout', 'a11y'],
    l1: ['launch', 'navigate', 'evaluate', 'snapshot', 'close'],
  },
}

export const recipeIds = Object.keys(hubCompositions) as RecipeId[]

export function isRecipeId(value: string): value is RecipeId {
  return value in hubCompositions
}
