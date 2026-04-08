import { useEffect, useRef, useState, useCallback } from 'react'
import { io } from 'socket.io-client'
import Editor from './components/Editor'
import Console from './components/Console'
import Toolbar from './components/Toolbar'
import Reference from './components/Reference'

// Ejemplos embebidos para no depender de fetch al filesystem
const EXAMPLES = {
  hola_mundo: `#[
    Programa: Hola Mundo
    Descripción: Primer programa en CCODE
]#

inicio programa_principal
    mostrar "¡Bienvenido a CCODE!"
    mostrar "Este es tu primer programa"
final
`,
  calculadora: `#[
    Programa: Calculadora Completa
    Descripcion: Calculadora con operaciones basicas
]#

inicio programa_principal
    mostrar "=== CALCULADORA CCODE v1.0 ==="
    mostrar ""

    intentar
        guardar numero1 es numero con capturar "Ingresa el primer numero: "
        guardar numero2 es numero con capturar "Ingresa el segundo numero: "

        guardar suma es numero con numero1 mas numero2
        guardar resta es numero con numero1 menos numero2
        guardar multiplicacion es numero con numero1 por numero2

        mostrar ""
        mostrar "=== RESULTADOS ==="
        mostrar "Suma:" suma
        mostrar "Resta:" resta
        mostrar "Multiplicacion:" multiplicacion

        intentar
            guardar division es numero con numero1 entre numero2
            guardar residuo es numero con numero1 resto numero2
            guardar potencia es numero con numero1 elevado numero2
            mostrar "Division:" division
            mostrar "Modulo:" residuo
            mostrar "Potencia:" potencia
        capturar_error como e
            mostrar "Operacion no valida:" e
        final
    capturar_error como e
        mostrar "Error de entrada:" e
        mostrar "Asegurate de ingresar numeros validos"
    final
final
`,
  fibonacci: `#[
    Programa: Secuencia de Fibonacci
]#

crear funcion fibonacci con parametros n
    cuando n menor_o_igual 1
        retornar n
    final

    guardar a es numero con 0
    guardar b es numero con 1
    guardar contador es numero con 2

    mientras contador menor_o_igual n
        guardar temp es numero con a mas b
        guardar a es numero con b
        guardar b es numero con temp
        guardar contador es numero con contador mas 1
    final

    retornar b
final

inicio programa_principal
    mostrar "=== SECUENCIA DE FIBONACCI ==="
    mostrar ""

    intentar
        guardar cantidad es numero con capturar "¿Cuántos números de Fibonacci deseas? "

        cuando cantidad menor_o_igual 0
            lanzar "Ingresa un número mayor a 0"
        final

        guardar i es numero con 0
        mientras i menor_que cantidad
            guardar resultado es numero con invocar fibonacci con i
            mostrar "F(" i ") =" resultado
            guardar i es numero con i mas 1
        final
    capturar_error como e
        mostrar "Error:" e
    final
final
`,
  par_impar: `inicio programa_principal
    mostrar "=== DETECTOR PAR O IMPAR ==="
    mostrar "Ingresa 0 para salir"
    mostrar ""

    repetir
        intentar
            guardar valor es numero con capturar "Ingresa un numero: "

            cuando valor es 0
                mostrar "Hasta luego!"
                detener
            final

            guardar residuo es numero con valor resto 2

            cuando residuo es 0
                mostrar valor "es PAR"
            sino
                mostrar valor "es IMPAR"
            final
        capturar_error como e
            mostrar "Error:" e
            mostrar "Intenta de nuevo o ingresa 0 para salir"
        final

        mostrar ""
    final
final
`,
  promedio: `inicio programa_principal
    mostrar "=== CALCULADORA DE PROMEDIO ==="

    intentar
        guardar cantidad es numero con capturar "¿Cuántos números? "

        cuando cantidad menor_o_igual 0
            lanzar "La cantidad debe ser mayor a 0"
        final

        guardar suma es numero con 0
        guardar i es numero con 0

        mientras i menor_que cantidad
            guardar valor es numero con capturar "Número: "
            guardar suma es numero con suma mas valor
            guardar i es numero con i mas 1
        final

        guardar promedio es numero con suma entre cantidad
        mostrar "Promedio:" promedio
    capturar_error como e
        mostrar "Error:" e
    final
final
`,
}

const DEFAULT_CODE = EXAMPLES.hola_mundo

export default function App() {
  const [code, setCode]            = useState(DEFAULT_CODE)
  const [lines, setLines]          = useState([])
  const [status, setStatus]        = useState('idle')
  const [waitingInput, setWaiting] = useState(false)
  const [refOpen, setRefOpen]      = useState(false)
  const socketRef = useRef(null)

  // Conectar socket una sola vez
  useEffect(() => {
    // En producción conecta al mismo origen, en dev apunta al servidor Flask
    const URL = import.meta.env.DEV ? 'http://127.0.0.1:5000' : window.location.origin
    const socket = io(URL, {
      transports: ['websocket', 'polling'],
    })
    socketRef.current = socket

    socket.on('output', ({ text, stream }) => {
      setLines(prev => [...prev, { text, stream }])
    })

    socket.on('input_request', () => {
      setWaiting(true)
    })

    socket.on('done', ({ exitCode }) => {
      setStatus(exitCode === 0 ? 'done' : 'error')
      setWaiting(false)
      setLines(prev => [
        ...prev,
        {
          text: exitCode === 0
            ? '\n— Programa finalizado correctamente —\n'
            : '\n— Programa finalizado con errores —\n',
          stream: exitCode === 0 ? 'info' : 'stderr',
        },
      ])
    })

    return () => socket.disconnect()
  }, [])

  const handleRun = useCallback(() => {
    setLines([])
    setStatus('running')
    setWaiting(false)
    socketRef.current?.emit('ejecutar', { codigo: code })
  }, [code])

  const handleInput = useCallback((value) => {
    setWaiting(false)
    socketRef.current?.emit('input_response', { value })
  }, [])

  const handleLoadExample = useCallback((file) => {
    setCode(EXAMPLES[file] ?? '')
    setLines([])
    setStatus('idle')
  }, [])

  const handleClear = useCallback(() => {
    setLines([])
    setStatus('idle')
  }, [])

  return (
    <div className="app">
      <Toolbar
        status={status}
        onRun={handleRun}
        onClear={handleClear}
        onLoadExample={handleLoadExample}
        onReference={() => setRefOpen(true)}
      />
      <Reference open={refOpen} onClose={() => setRefOpen(false)} />
      <div className="workspace">
        <div className="pane pane--editor">
          <div className="pane-header">
            <span className="pane-dot red" />
            <span className="pane-dot yellow" />
            <span className="pane-dot green" />
            <span className="pane-label">programa.aura</span>
          </div>
          <Editor value={code} onChange={setCode} />
        </div>

        <div className="pane pane--console">
          <div className="pane-header">
            <span className="pane-dot red" />
            <span className="pane-dot yellow" />
            <span className="pane-dot green" />
            <span className="pane-label">Consola</span>
            {status === 'running' && <span className="pane-badge running">ejecutando</span>}
            {status === 'done'    && <span className="pane-badge done">listo</span>}
            {status === 'error'   && <span className="pane-badge error">error</span>}
          </div>
          <Console lines={lines} waitingInput={waitingInput} onInput={handleInput} />
        </div>
      </div>
    </div>
  )
}
