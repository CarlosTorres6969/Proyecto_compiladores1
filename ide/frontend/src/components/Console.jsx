import { useEffect, useRef, useState } from 'react'

export default function Console({ lines, waitingInput, onInput }) {
  const bottomRef = useRef(null)
  const [inputVal, setInputVal] = useState('')

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [lines, waitingInput])

  function handleSubmit(e) {
    e.preventDefault()
    onInput(inputVal)
    setInputVal('')
  }

  return (
    <div className="console">
      <div className="console-output">
        {lines.map((line, i) => (
          <span key={i} className={`console-line console-line--${line.stream}`}>
            {line.text}
          </span>
        ))}
        {waitingInput && (
          <form className="console-input-form" onSubmit={handleSubmit}>
            <span className="console-prompt">▶</span>
            <input
              autoFocus
              className="console-input"
              value={inputVal}
              onChange={e => setInputVal(e.target.value)}
              placeholder="Escribe y presiona Enter..."
            />
          </form>
        )}
        <div ref={bottomRef} />
      </div>
    </div>
  )
}
