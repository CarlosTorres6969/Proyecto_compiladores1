const TABLES = [
  {
    title: 'Estructura del programa',
    cols: ['Palabra', 'Uso', 'Ejemplo'],
    rows: [
      ['inicio', 'Abre el bloque principal', 'inicio programa_principal'],
      ['final',  'Cierra cualquier bloque abierto', 'final'],
    ],
  },
  {
    title: 'Variables y constantes',
    cols: ['Palabra', 'Uso', 'Ejemplo'],
    rows: [
      ['guardar',   'Declara o reasigna una variable',   'guardar edad es numero con 25'],
      ['constante', 'Declara una constante (inmutable)', 'constante PI es numero con 3.14159'],
      ['es',        'Separador nombre-tipo',             'guardar x es numero con 0'],
      ['con',       'Separador tipo-valor',              'guardar x es numero con 0'],
    ],
  },
  {
    title: 'Tipos de datos',
    cols: ['Tipo', 'Descripción', 'Ejemplo'],
    rows: [
      ['numero',      'Entero o decimal',             'guardar x es numero con 42'],
      ['texto',       'Cadena de caracteres',         'guardar s es texto con "hola"'],
      ['logico',      'Booleano',                     'guardar b es logico con verdadero'],
      ['coleccion',   'Lista ordenada de valores',    'guardar l es coleccion con [1, 2, 3]'],
      ['diccionario', 'Pares clave: valor',           'guardar d es diccionario con {"a": 1}'],
      ['vacio',       'Ausencia de valor (null)',     'guardar n es vacio con vacio'],
    ],
  },
  {
    title: 'Valores literales',
    cols: ['Literal', 'Tipo', 'Equivalente'],
    rows: [
      ['verdadero', 'logico',      'true'],
      ['falso',     'logico',      'false'],
      ['vacio',     'vacio',       'null / None'],
      ['"texto"',   'texto',       'string entre comillas dobles'],
      ['42',        'numero',      'entero'],
      ['3.14',      'numero',      'decimal'],
      ['[1, 2, 3]', 'coleccion',   'lista literal'],
      ['{"k": v}',  'diccionario', 'diccionario literal'],
    ],
  },
  {
    title: 'Entrada y salida',
    cols: ['Palabra', 'Descripción', 'Ejemplo'],
    rows: [
      ['mostrar',  'Imprime uno o más valores separados por espacio', 'mostrar "Resultado:" x'],
      ['capturar', 'Lee entrada del usuario, convierte a número si es posible', 'guardar n es numero con capturar "Valor: "'],
    ],
  },
  {
    title: 'Condicionales',
    cols: ['Palabra', 'Equivalente', 'Uso'],
    rows: [
      ['cuando',  'if',      'Condición principal'],
      ['ademas',  'else if', 'Condición alternativa (puede repetirse)'],
      ['sino',    'else',    'Rama por defecto'],
      ['final',   '}',       'Cierra el bloque cuando'],
    ],
  },
  {
    title: 'Sintaxis — condicional',
    mono: true,
    cols: ['Estructura'],
    rows: [
      ['cuando <condición>'],
      ['    <sentencias>'],
      ['ademas <condición>'],
      ['    <sentencias>'],
      ['sino'],
      ['    <sentencias>'],
      ['final'],
    ],
  },
  {
    title: 'Bucles',
    cols: ['Palabra', 'Equivalente', 'Descripción'],
    rows: [
      ['mientras',  'while',    'Repite mientras la condición sea verdadera'],
      ['repetir',   '—',        'Bucle infinito, salir con detener'],
      ['recorrer',  'for in',   'Itera sobre colección, texto o diccionario'],
      ['en',        'in',       'Separador variable-iterable en recorrer'],
      ['detener',   'break',    'Sale del bucle inmediatamente'],
      ['continuar', 'continue', 'Salta a la siguiente iteración'],
    ],
  },
  {
    title: 'Sintaxis — bucles',
    mono: true,
    cols: ['Estructura'],
    rows: [
      ['# mientras'],
      ['mientras <condición>'],
      ['    <sentencias>'],
      ['final'],
      [''],
      ['# repetir (infinito)'],
      ['repetir'],
      ['    <sentencias>'],
      ['    detener'],
      ['final'],
      [''],
      ['# recorrer'],
      ['recorrer <variable> en <colección>'],
      ['    <sentencias>'],
      ['final'],
    ],
  },
  {
    title: 'Funciones',
    cols: ['Palabra', 'Uso', 'Ejemplo'],
    rows: [
      ['crear funcion', 'Define una función',                      'crear funcion suma con parametros a, b'],
      ['parametros',    'Lista de parámetros (puede estar vacía)', 'crear funcion saludar con parametros nombre'],
      ['invocar',       'Llama a una función',                     'invocar suma con 3, 4'],
      ['retornar',      'Devuelve un valor y termina la función',  'retornar a mas b'],
      ['con',           'Separa nombre de argumentos en invocar',  'invocar f con x, y'],
    ],
  },
  {
    title: 'Sintaxis — funciones',
    mono: true,
    cols: ['Estructura'],
    rows: [
      ['# Definición'],
      ['crear funcion <nombre> con parametros <p1>, <p2>'],
      ['    <sentencias>'],
      ['    retornar <valor>'],
      ['final'],
      [''],
      ['# Llamada como sentencia'],
      ['invocar <nombre> con <arg1>, <arg2>'],
      [''],
      ['# Llamada como expresión'],
      ['guardar r es numero con invocar <nombre> con <arg>'],
      [''],
      ['# Sin parámetros'],
      ['crear funcion saludar con parametros'],
      ['    mostrar "Hola"'],
      ['final'],
      ['invocar saludar con'],
    ],
  },
  {
    title: 'Manejo de errores',
    cols: ['Palabra', 'Equivalente', 'Uso'],
    rows: [
      ['intentar',       'try',     'Bloque que puede lanzar un error'],
      ['capturar_error', 'catch',   'Captura el error si ocurre'],
      ['como',           'as',      'Asigna el mensaje de error a una variable'],
      ['siempre',        'finally', 'Se ejecuta siempre, haya error o no (opcional)'],
      ['lanzar',         'throw',   'Lanza un error manualmente con un mensaje de texto'],
    ],
  },
  {
    title: 'Sintaxis — manejo de errores',
    mono: true,
    cols: ['Estructura'],
    rows: [
      ['intentar'],
      ['    <sentencias>'],
      ['capturar_error como <variable>'],
      ['    mostrar "Error:" <variable>'],
      ['siempre'],
      ['    # opcional, siempre se ejecuta'],
      ['final'],
      [''],
      ['# Lanzar error manualmente'],
      ['lanzar "mensaje de error"'],
    ],
  },
  {
    title: 'Colecciones — operaciones',
    cols: ['Operación', 'Sintaxis', 'Descripción'],
    rows: [
      ['Crear',            'guardar l es coleccion con [1, 2, 3]',   'Lista literal'],
      ['Leer elemento',    'lista[0]',                               'Índice desde 0'],
      ['Escribir elemento','guardar lista[0] es numero con 99',      'Asignación por índice'],
      ['Agregar al final', 'agregar <valor> a <lista>',              'Añade al final de la lista'],
      ['Remover elemento', 'remover <valor> de <lista>',             'Elimina la primera ocurrencia'],
      ['Recorrer',         'recorrer item en lista ... final',       'Itera cada elemento'],
    ],
  },
  {
    title: 'Diccionarios — operaciones',
    cols: ['Operación', 'Sintaxis', 'Descripción'],
    rows: [
      ['Crear',         'guardar d es diccionario con {"k": 1}', 'Diccionario literal'],
      ['Leer clave',    'd["clave"]',                            'Acceso por clave'],
      ['Escribir clave','guardar d["k"] es numero con 5',        'Asignación por clave'],
      ['Método obtener','invocar d.obtener con "clave"',         'Retorna vacio si la clave no existe'],
      ['Recorrer',      'recorrer clave en d ... final',         'Itera las claves del diccionario'],
    ],
  },
  {
    title: 'Operadores aritméticos',
    cols: ['Operador', 'Símbolo', 'Ejemplo', 'Resultado'],
    rows: [
      ['mas',     '+',  '10 mas 3',    '13'],
      ['menos',   '-',  '10 menos 3',  '7'],
      ['por',     '*',  '10 por 3',    '30'],
      ['entre',   '/',  '10 entre 4',  '2.5'],
      ['resto',   '%',  '10 resto 3',  '1'],
      ['elevado', '**', '2 elevado 8', '256'],
    ],
  },
  {
    title: 'Operadores de comparación',
    cols: ['Operador', 'Símbolo', 'Descripción'],
    rows: [
      ['es',            '==', 'Igual a'],
      ['no_es',         '!=', 'Distinto de'],
      ['mayor_que',     '>',  'Mayor que'],
      ['menor_que',     '<',  'Menor que'],
      ['mayor_o_igual', '>=', 'Mayor o igual que'],
      ['menor_o_igual', '<=', 'Menor o igual que'],
    ],
  },
  {
    title: 'Operadores lógicos',
    cols: ['Operador', 'Equivalente', 'Descripción', 'Ejemplo'],
    rows: [
      ['y_tambien', 'and', 'Verdadero si ambos son verdaderos',       'a y_tambien b'],
      ['o_sino',    'or',  'Verdadero si al menos uno es verdadero',  'a o_sino b'],
      ['negar',     'not', 'Invierte un valor lógico',                'negar verdadero'],
    ],
  },
  {
    title: 'Precedencia de operadores (mayor a menor)',
    cols: ['Nivel', 'Operadores'],
    rows: [
      ['1 — mayor', 'negar'],
      ['2',         'elevado  (asociatividad derecha)'],
      ['3',         'por, entre, resto'],
      ['4',         'mas, menos'],
      ['5',         'es, no_es, mayor_que, menor_que, mayor_o_igual, menor_o_igual'],
      ['6 — menor', 'y_tambien, o_sino'],
    ],
  },
  {
    title: 'Módulos',
    cols: ['Palabra', 'Uso', 'Ejemplo'],
    rows: [
      ['importar', 'Importa nombres desde un módulo',      'importar suma desde "matematica"'],
      ['desde',    'Especifica el origen del módulo',      'importar todo desde "utils"'],
      ['todo',     'Importa todos los nombres del módulo', 'importar todo desde "lib"'],
      ['como',     'Alias para el nombre importado',       'importar f desde "mod" como miFuncion'],
      ['exportar', 'Exporta nombres del módulo actual',    'exportar suma, resta'],
    ],
  },
  {
    title: 'Comentarios',
    cols: ['Sintaxis', 'Tipo', 'Notas'],
    rows: [
      ['# texto',     'Línea',      'Desde # hasta el final de la línea'],
      ['#[ texto ]#', 'Multilínea', 'Puede abarcar varias líneas'],
    ],
  },
  {
    title: 'Secuencias de escape en texto',
    cols: ['Secuencia', 'Significado'],
    rows: [
      ['\\n',  'Salto de línea'],
      ['\\t',  'Tabulación horizontal'],
      ['\\"',  'Comilla doble literal dentro de un texto'],
      ['\\\\', 'Barra invertida literal'],
    ],
  },
  {
    title: 'Errores comunes y soluciones',
    cols: ['Error', 'Causa', 'Solución'],
    rows: [
      ['variable no definida',   'Usar una variable antes de declararla',          'Agregar guardar <nombre> es <tipo> con <valor>'],
      ['división por cero',      'Divisor es 0 en entre o resto',                  'Verificar con cuando antes de dividir'],
      ['índice fuera de rango',  'Acceder a lista[n] donde n >= tamaño de la lista','Verificar el tamaño antes de acceder'],
      ['tipo incorrecto',        'Asignar un tipo distinto al declarado',           'Usar el tipo correcto o cambiar la declaración'],
      ['función no definida',    'Invocar una función que no existe',               'Definir la función antes de invocarla'],
      ['argumentos incorrectos', 'Pasar más o menos argumentos de los esperados',  'Verificar la firma de la función'],
      ['bucle infinito',         'La condición de mientras nunca se vuelve falsa',  'Asegurarse de modificar la variable de control'],
      ['cadena sin cerrar',      'Falta la comilla de cierre "',                   'Cerrar la cadena con comilla doble'],
      ['escape inválido',        'Usar \\x donde x no es n, t, " ni \\',           'Usar solo las secuencias de escape válidas'],
    ],
  },
]

export default function Reference({ open, onClose }) {
  if (!open) return null

  return (
    <div className="ref-overlay" onClick={onClose}>
      <aside className="ref-panel" onClick={e => e.stopPropagation()}>
        <div className="ref-header">
          <span className="ref-title">Referencia del lenguaje CCODE</span>
          <button className="ref-close" onClick={onClose}>✕</button>
        </div>
        <div className="ref-body">
          {TABLES.map(table => (
            <div key={table.title} className="ref-section">
              <h3 className="ref-section-title">{table.title}</h3>
              {table.mono
                ? (
                  <pre className="ref-mono-block">
                    {table.rows.map(r => r[0]).join('\n')}
                  </pre>
                )
                : (
                  <table className="ref-table">
                    <thead>
                      <tr>{table.cols.map(c => <th key={c}>{c}</th>)}</tr>
                    </thead>
                    <tbody>
                      {table.rows.map((row, i) => (
                        <tr key={i}>
                          {row.map((cell, j) => (
                            <td key={j}>
                              {j === 0 || table.cols[j] === 'Ejemplo' || table.cols[j] === 'Símbolo' || table.cols[j] === 'Equivalente' || table.cols[j] === 'Sintaxis' || table.cols[j] === 'Resultado'
                                ? <code>{cell}</code>
                                : cell}
                            </td>
                          ))}
                        </tr>
                      ))}
                    </tbody>
                  </table>
                )
              }
            </div>
          ))}
        </div>
      </aside>
    </div>
  )
}
