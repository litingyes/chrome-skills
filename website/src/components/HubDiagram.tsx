import { useCallback, useId, useState, type CSSProperties } from 'react'
import { useI18n } from '../i18n/context'
import {
  hubCompositions,
  isRecipeId,
  recipeIds,
  type RecipeId,
} from '../lib/hubCompositions'

const layerOrder = ['l3', 'l2', 'l1'] as const

const layerItems = {
  l3: recipeIds,
  l2: ['article', 'serp', 'layout', 'a11y'],
  l1: ['launch', 'navigate', 'wait', 'evaluate', 'snapshot', 'close'],
} as const

const layerTone = {
  l3: 'recipe',
  l2: 'extract',
  l1: 'cdp',
} as const

export function HubDiagram() {
  const { messages } = useI18n()
  const { layers, composes, note, diagramCaption, interactiveHint, flowLabel } =
    messages.architecture
  const flowId = useId()
  const [hoverRecipe, setHoverRecipe] = useState<RecipeId | null>(null)
  const [pinnedRecipe, setPinnedRecipe] = useState<RecipeId | null>(null)
  const activeRecipe = pinnedRecipe ?? hoverRecipe

  const composition = activeRecipe ? hubCompositions[activeRecipe] : null

  const isLit = useCallback(
    (layer: 'l3' | 'l2' | 'l1', item: string) => {
      if (!composition) return false
      if (layer === 'l3') return item === activeRecipe
      if (layer === 'l2') return composition.l2.includes(item)
      return composition.l1.includes(item)
    },
    [activeRecipe, composition],
  )

  const flowSteps = composition
    ? [activeRecipe!, ...composition.l2, ...composition.l1]
    : []

  function activateRecipe(id: RecipeId) {
    setHoverRecipe(id)
  }

  function clearHover() {
    setHoverRecipe(null)
  }

  function togglePin(id: RecipeId) {
    setPinnedRecipe((current) => (current === id ? null : id))
    setHoverRecipe(null)
  }

  return (
    <figure
      className={`hub-diagram${activeRecipe ? ' hub-diagram--active' : ''}`}
      aria-labelledby="hub-diagram-title"
      onMouseLeave={clearHover}
    >
      <figcaption id="hub-diagram-title" className="visually-hidden">
        {diagramCaption}
      </figcaption>
      <p className="hub-diagram__hint">{interactiveHint}</p>
      <div className="hub-diagram__stack">
        {layerOrder.map((id, index) => {
          const layer = layers[id]
          const tone = layerTone[id]
          const items = layerItems[id]

          return (
            <div
              key={id}
              className={`hub-diagram__layer hub-diagram__layer--${tone}`}
              style={{ '--layer-index': index } as CSSProperties}
            >
              <div className="hub-diagram__meta">
                <span className={`hub-diagram__tag hub-diagram__tag--${tone}`}>
                  {layer.label}
                </span>
                <span className="hub-diagram__desc">{layer.desc}</span>
              </div>
              <ul className="hub-diagram__commands" aria-label={layer.label}>
                {items.map((item) => {
                  const lit = isLit(id, item)
                  const isRecipe = id === 'l3' && isRecipeId(item)

                  if (isRecipe) {
                    return (
                      <li key={item}>
                        <button
                          type="button"
                          className={`hub-diagram__chip hub-diagram__chip--${tone}${lit ? ' hub-diagram__chip--lit' : ''}`}
                          aria-pressed={pinnedRecipe === item}
                          aria-describedby={activeRecipe === item ? flowId : undefined}
                          onMouseEnter={() => activateRecipe(item)}
                          onFocus={() => activateRecipe(item)}
                          onBlur={() => setHoverRecipe(null)}
                          onClick={() => togglePin(item)}
                        >
                          <code>{item}</code>
                        </button>
                      </li>
                    )
                  }

                  return (
                    <li
                      key={item}
                      className={lit ? 'hub-diagram__command--lit' : undefined}
                    >
                      <code className={lit ? 'hub-diagram__chip--lit' : undefined}>{item}</code>
                    </li>
                  )
                })}
              </ul>
              {index < layerOrder.length - 1 ? (
                <div
                  className={`hub-diagram__connector${composition ? ' hub-diagram__connector--lit' : ''}`}
                  aria-hidden="true"
                >
                  <span>{composes}</span>
                </div>
              ) : null}
            </div>
          )
        })}
      </div>

      <div
        id={flowId}
        className={`hub-diagram__flow${composition ? ' hub-diagram__flow--visible' : ''}`}
        aria-live="polite"
        aria-atomic="true"
      >
        <span className="hub-diagram__flow-label">{flowLabel}</span>
        {composition ? (
          <ol className="hub-diagram__flow-steps">
            {flowSteps.map((step, stepIndex) => (
              <li
                key={`${step}-${stepIndex}`}
                className="hub-diagram__flow-step"
                style={{ '--step-index': stepIndex } as CSSProperties}
              >
                <code>{step}</code>
              </li>
            ))}
          </ol>
        ) : (
          <p className="hub-diagram__flow-idle">{messages.architecture.flowIdle}</p>
        )}
      </div>

      <p className="hub-diagram__note">
        {note.split('/chrome').map((part, i, arr) =>
          i < arr.length - 1 ? (
            <span key={i}>
              {part}
              <code>/chrome</code>
            </span>
          ) : (
            <span key={i}>{part}</span>
          ),
        )}
      </p>
    </figure>
  )
}
