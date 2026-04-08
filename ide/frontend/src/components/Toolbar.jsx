const EXAMPLES = [
  { label: 'Hola Mundo',   file: 'hola_mundo' },
  { label: 'Calculadora',  file: 'calculadora' },
  { label: 'Fibonacci',    file: 'fibonacci' },
  { label: 'Par / Impar',  file: 'par_impar' },
  { label: 'Promedio',     file: 'promedio' },
]

export default function Toolbar({ status, onRun, onClear, onLoadExample, onReference }) {
  const running = status === 'running'

  function handleExample(e) {
    const val = e.target.value
    if (val) onLoadExample(val)
    e.target.value = ''   // resetear para poder cargar el mismo ejemplo de nuevo
  }

  return (
    <header className="toolbar">
      <div className="toolbar-brand">
        <span className="toolbar-logo">✦</span>
        <span className="toolbar-title">CCODE IDE</span>
        <span className="toolbar-version">v1.0</span>
      </div>

      <div className="toolbar-actions">
        <select
          className="toolbar-select"
          defaultValue=""
          onChange={handleExample}
        >
          <option value="" disabled>Ejemplos</option>
          {EXAMPLES.map(ex => (
            <option key={ex.file} value={ex.file}>{ex.label}</option>
          ))}
        </select>

        <button className="btn btn--ghost" onClick={onClear} disabled={running}>
          Limpiar consola
        </button>

        <button className="btn btn--ghost" onClick={onReference}>
          ? Referencia
        </button>

        <button className="btn btn--run" onClick={onRun} disabled={running}>
          {running
            ? <><span className="spinner" /> Ejecutando...</>
            : <><span className="run-icon">▶</span> Ejecutar</>
          }
        </button>
      </div>

      <div className={`status-dot status-dot--${status}`} title={status} />
    </header>
  )
}
