import { useEffect, useRef } from 'react'
import { EditorView, keymap, lineNumbers, highlightActiveLine, drawSelection } from '@codemirror/view'
import { EditorState } from '@codemirror/state'
import { defaultKeymap, indentWithTab, history, historyKeymap } from '@codemirror/commands'
import { indentOnInput, syntaxHighlighting, HighlightStyle, bracketMatching } from '@codemirror/language'
import { autocompletion, completionKeymap } from '@codemirror/autocomplete'
import { tags as t } from '@lezer/highlight'
import { StreamLanguage } from '@codemirror/language'

// ── Syntax highlighting ───────────────────────────────
const KEYWORDS = new Set([
  'inicio','final','guardar','constante','mostrar','capturar',
  'cuando','sino','ademas','mientras','repetir','recorrer',
  'detener','continuar','crear','retornar','invocar',
  'intentar','capturar_error','siempre','lanzar','como',
  'importar','exportar','todo','funcion','parametros',
  'agregar','remover','en','de','desde',
])
const TYPES     = new Set(['numero','texto','logico','vacio','coleccion','diccionario'])
const OPERATORS = new Set(['es','no_es','con','mas','menos','por','entre','resto','elevado',
  'mayor_que','menor_que','mayor_o_igual','menor_o_igual','y_tambien','o_sino','negar'])
const BOOLEANS  = new Set(['verdadero','falso'])

const ccodeStream = StreamLanguage.define({
  name: 'ccode',
  token(stream) {
    if (stream.match(/^#\[/)) {
      while (!stream.eol()) {
        if (stream.match(/\]#/)) break
        stream.next()
      }
      return 'comment'
    }
    if (stream.match(/^#/)) { stream.skipToEnd(); return 'comment' }
    if (stream.match(/^"/)) {
      while (!stream.eol()) { if (stream.next() === '"') break }
      return 'string'
    }
    if (stream.match(/^\d+(\.\d+)?/)) return 'number'
    if (stream.match(/^[a-zA-ZáéíóúÁÉÍÓÚñÑüÜ_][a-zA-ZáéíóúÁÉÍÓÚñÑüÜ_0-9]*/)) {
      const w = stream.current()
      if (KEYWORDS.has(w))  return 'keyword'
      if (TYPES.has(w))     return 'typeName'
      if (OPERATORS.has(w)) return 'operator'
      if (BOOLEANS.has(w))  return 'atom'
      return 'variableName'
    }
    if (stream.match(/^[\[\]{},.:]/)) return 'punctuation'
    stream.next()
    return null
  },
  languageData: { commentTokens: { line: '#' } },
})

const ccodeHighlight = HighlightStyle.define([
  { tag: t.keyword,       color: '#a78bfa', fontWeight: '600' },
  { tag: t.typeName,      color: '#34d399' },
  { tag: t.operator,      color: '#f472b6' },
  { tag: t.string,        color: '#fbbf24' },
  { tag: t.number,        color: '#60a5fa' },
  { tag: t.atom,          color: '#f97316' },
  { tag: t.comment,       color: '#4a5568', fontStyle: 'italic' },
  { tag: t.variableName,  color: '#e2e8f0' },
  { tag: t.punctuation,   color: '#94a3b8' },
])

// ── Theme ─────────────────────────────────────────────
const darkTheme = EditorView.theme({
  '&': { backgroundColor: '#0f1117', color: '#e2e8f0', height: '100%',
         fontSize: '14px', fontFamily: "'JetBrains Mono', monospace" },
  '.cm-content':    { caretColor: '#7c3aed', padding: '12px 0' },
  '.cm-cursor':     { borderLeftColor: '#7c3aed', borderLeftWidth: '2px' },
  '.cm-gutters':    { backgroundColor: '#0f1117', borderRight: '1px solid #1e2130', color: '#4a5568' },
  '.cm-lineNumbers .cm-gutterElement': { padding: '0 12px 0 8px', minWidth: '40px' },
  '.cm-activeLine': { backgroundColor: '#1a1f2e' },
  '.cm-activeLineGutter': { backgroundColor: '#1a1f2e' },
  '.cm-selectionBackground, ::selection': { backgroundColor: '#3730a3 !important' },
  '.cm-matchingBracket': { backgroundColor: '#3730a3', outline: '1px solid #7c3aed' },
}, { dark: true })

// ── Autocomplete ──────────────────────────────────────
const ALL_WORDS = [...KEYWORDS, ...TYPES, ...OPERATORS, ...BOOLEANS]
  .map(label => ({ label, type: 'keyword' }))

function ccodeComplete(context) {
  const word = context.matchBefore(/[\wáéíóúÁÉÍÓÚñÑüÜ_]+/)
  if (!word || (word.from === word.to && !context.explicit)) return null
  return { from: word.from, options: ALL_WORDS }
}

// ── Component ─────────────────────────────────────────
export default function Editor({ value, onChange }) {
  const containerRef = useRef(null)
  const viewRef      = useRef(null)
  const onChangeRef  = useRef(onChange)
  onChangeRef.current = onChange

  useEffect(() => {
    if (!containerRef.current) return
    // Evitar doble montaje en StrictMode
    if (viewRef.current) { viewRef.current.destroy(); viewRef.current = null }

    const view = new EditorView({
      state: EditorState.create({
        doc: value,
        extensions: [
          lineNumbers(),
          highlightActiveLine(),
          drawSelection(),
          history(),
          indentOnInput(),
          bracketMatching(),
          autocompletion({ override: [ccodeComplete] }),
          keymap.of([...defaultKeymap, ...historyKeymap, ...completionKeymap, indentWithTab]),
          ccodeStream,
          syntaxHighlighting(ccodeHighlight),
          darkTheme,
          EditorView.lineWrapping,
          EditorView.updateListener.of(u => {
            if (u.docChanged) onChangeRef.current(u.state.doc.toString())
          }),
        ],
      }),
      parent: containerRef.current,
    })
    viewRef.current = view
    return () => { view.destroy(); viewRef.current = null }
  }, []) // eslint-disable-line react-hooks/exhaustive-deps

  // Sync value from outside (cargar ejemplo)
  useEffect(() => {
    const view = viewRef.current
    if (!view) return
    const cur = view.state.doc.toString()
    if (cur !== value) {
      view.dispatch({ changes: { from: 0, to: cur.length, insert: value } })
    }
  }, [value])

  return <div ref={containerRef} style={{ height: '100%' }} />
}
