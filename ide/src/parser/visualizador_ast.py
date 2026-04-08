# Visualizador del AST de CCODE.
# Imprime el arbol de forma legible en la terminal usando solo ASCII.

from nodos import (
    Programa, DeclaracionVariable, DeclaracionConstante, AsignacionIndice,
    DefinicionFuncion, Retornar, LlamadaFuncion, LlamadaMetodo,
    Cuando, Mientras, Repetir, Recorrer, Detener, Continuar,
    Mostrar, Intentar, Lanzar, Agregar, Remover,
    Importar, Exportar,
    ExpresionBinaria, ExpresionUnaria,
    AccesoIndice, AccesoCampo,
    LiteralNumero, LiteralTexto, LiteralLogico, LiteralVacio,
    LiteralColeccion, LiteralDiccionario, Identificador,
)

_RAMA = '+-- '
_PIPE  = '|   '
_VACIO = '    '


def _sub(prefijo, ultimo):
    return prefijo + (_VACIO if ultimo else _PIPE)


def visualizar(nodo, prefijo='', ultimo=True):
    rama = _RAMA
    ext  = _sub(prefijo, ultimo)

    if isinstance(nodo, Programa):
        print(f"Programa: {nodo.nombre}")
        for i, hijo in enumerate(nodo.cuerpo):
            visualizar(hijo, prefijo, i == len(nodo.cuerpo) - 1)

    elif isinstance(nodo, DeclaracionVariable):
        print(f"{prefijo}{rama}guardar {nodo.nombre} [{nodo.tipo}]  (L{nodo.linea})")
        visualizar(nodo.valor, ext, True)

    elif isinstance(nodo, DeclaracionConstante):
        print(f"{prefijo}{rama}constante {nodo.nombre} [{nodo.tipo}]  (L{nodo.linea})")
        visualizar(nodo.valor, ext, True)

    elif isinstance(nodo, AsignacionIndice):
        print(f"{prefijo}{rama}asignar {nodo.nombre}[...] [{nodo.tipo}]  (L{nodo.linea})")
        print(f"{ext}+-- indice:")
        visualizar(nodo.indice, ext + _PIPE, True)
        print(f"{ext}+-- valor:")
        visualizar(nodo.valor, ext + _VACIO, True)

    elif isinstance(nodo, DefinicionFuncion):
        params = ', '.join(nodo.parametros) if nodo.parametros else '(sin parametros)'
        print(f"{prefijo}{rama}crear funcion {nodo.nombre}  params: [{params}]  (L{nodo.linea})")
        for i, hijo in enumerate(nodo.cuerpo):
            visualizar(hijo, ext, i == len(nodo.cuerpo) - 1)

    elif isinstance(nodo, Retornar):
        print(f"{prefijo}{rama}retornar  (L{nodo.linea})")
        for i, v in enumerate(nodo.valores):
            visualizar(v, ext, i == len(nodo.valores) - 1)

    elif isinstance(nodo, LlamadaFuncion):
        print(f"{prefijo}{rama}invocar {nodo.nombre}  (L{nodo.linea})")
        for i, arg in enumerate(nodo.argumentos):
            visualizar(arg, ext, i == len(nodo.argumentos) - 1)

    elif isinstance(nodo, LlamadaMetodo):
        print(f"{prefijo}{rama}invocar {nodo.objeto}.{nodo.metodo}  (L{nodo.linea})")
        for i, arg in enumerate(nodo.argumentos):
            visualizar(arg, ext, i == len(nodo.argumentos) - 1)

    elif isinstance(nodo, Cuando):
        print(f"{prefijo}{rama}cuando  (L{nodo.linea})")
        for idx, (cond, cuerpo) in enumerate(nodo.ramas):
            etiqueta = 'cuando' if idx == 0 else 'ademas'
            print(f"{ext}+-- {etiqueta} condicion:")
            visualizar(cond, ext + _PIPE, True)
            print(f"{ext}|   cuerpo:")
            for i, s in enumerate(cuerpo):
                visualizar(s, ext + _PIPE, i == len(cuerpo) - 1)
        if nodo.rama_sino:
            print(f"{ext}+-- sino:")
            for i, s in enumerate(nodo.rama_sino):
                visualizar(s, ext + _VACIO, i == len(nodo.rama_sino) - 1)

    elif isinstance(nodo, Mientras):
        print(f"{prefijo}{rama}mientras  (L{nodo.linea})")
        print(f"{ext}+-- condicion:")
        visualizar(nodo.condicion, ext + _PIPE, True)
        print(f"{ext}+-- cuerpo:")
        for i, s in enumerate(nodo.cuerpo):
            visualizar(s, ext + _VACIO, i == len(nodo.cuerpo) - 1)

    elif isinstance(nodo, Repetir):
        print(f"{prefijo}{rama}repetir  (L{nodo.linea})")
        for i, s in enumerate(nodo.cuerpo):
            visualizar(s, ext, i == len(nodo.cuerpo) - 1)

    elif isinstance(nodo, Recorrer):
        print(f"{prefijo}{rama}recorrer {nodo.variable} en ...  (L{nodo.linea})")
        print(f"{ext}+-- iterable:")
        visualizar(nodo.iterable, ext + _PIPE, True)
        print(f"{ext}+-- cuerpo:")
        for i, s in enumerate(nodo.cuerpo):
            visualizar(s, ext + _VACIO, i == len(nodo.cuerpo) - 1)

    elif isinstance(nodo, Detener):
        print(f"{prefijo}{rama}detener  (L{nodo.linea})")

    elif isinstance(nodo, Continuar):
        print(f"{prefijo}{rama}continuar  (L{nodo.linea})")

    elif isinstance(nodo, Mostrar):
        print(f"{prefijo}{rama}mostrar  (L{nodo.linea})")
        for i, expr in enumerate(nodo.expresiones):
            visualizar(expr, ext, i == len(nodo.expresiones) - 1)

    elif isinstance(nodo, Intentar):
        print(f"{prefijo}{rama}intentar  (L{nodo.linea})")
        print(f"{ext}+-- cuerpo:")
        for i, s in enumerate(nodo.cuerpo):
            visualizar(s, ext + _PIPE, i == len(nodo.cuerpo) - 1)
        print(f"{ext}+-- capturar_error como {nodo.nombre_error}:")
        for i, s in enumerate(nodo.cuerpo_error):
            visualizar(s, ext + _PIPE, i == len(nodo.cuerpo_error) - 1)
        if nodo.cuerpo_siempre:
            print(f"{ext}+-- siempre:")
            for i, s in enumerate(nodo.cuerpo_siempre):
                visualizar(s, ext + _VACIO, i == len(nodo.cuerpo_siempre) - 1)

    elif isinstance(nodo, Lanzar):
        print(f"{prefijo}{rama}lanzar  (L{nodo.linea})")
        visualizar(nodo.expresion, ext, True)

    elif isinstance(nodo, Agregar):
        print(f"{prefijo}{rama}agregar a {nodo.coleccion}  (L{nodo.linea})")
        visualizar(nodo.elemento, ext, True)

    elif isinstance(nodo, Remover):
        print(f"{prefijo}{rama}remover de {nodo.coleccion}  (L{nodo.linea})")
        visualizar(nodo.elemento, ext, True)

    elif isinstance(nodo, Importar):
        nombres = ', '.join(nodo.nombres)
        alias = f' como {nodo.alias}' if nodo.alias else ''
        print(f"{prefijo}{rama}importar [{nombres}] desde \"{nodo.origen}\"{alias}  (L{nodo.linea})")

    elif isinstance(nodo, Exportar):
        print(f"{prefijo}{rama}exportar [{', '.join(nodo.nombres)}]  (L{nodo.linea})")

    elif isinstance(nodo, ExpresionBinaria):
        print(f"{prefijo}{rama}op: {nodo.operador}  (L{nodo.linea})")
        visualizar(nodo.izquierda, ext, False)
        visualizar(nodo.derecha,   ext, True)

    elif isinstance(nodo, ExpresionUnaria):
        print(f"{prefijo}{rama}unario: {nodo.operador}  (L{nodo.linea})")
        visualizar(nodo.operando, ext, True)

    elif isinstance(nodo, AccesoIndice):
        print(f"{prefijo}{rama}{nodo.nombre}[...]  (L{nodo.linea})")
        visualizar(nodo.indice, ext, True)

    elif isinstance(nodo, AccesoCampo):
        print(f"{prefijo}{rama}{nodo.objeto}.{nodo.campo}  (L{nodo.linea})")

    elif isinstance(nodo, LiteralNumero):
        print(f"{prefijo}{rama}{nodo.valor}  (L{nodo.linea})")

    elif isinstance(nodo, LiteralTexto):
        print(f'{prefijo}{rama}"{nodo.valor}"  (L{nodo.linea})')

    elif isinstance(nodo, LiteralLogico):
        print(f"{prefijo}{rama}{'verdadero' if nodo.valor else 'falso'}  (L{nodo.linea})")

    elif isinstance(nodo, LiteralVacio):
        print(f"{prefijo}{rama}vacio  (L{nodo.linea})")

    elif isinstance(nodo, LiteralColeccion):
        print(f"{prefijo}{rama}coleccion[{len(nodo.elementos)}]  (L{nodo.linea})")
        for i, elem in enumerate(nodo.elementos):
            visualizar(elem, ext, i == len(nodo.elementos) - 1)

    elif isinstance(nodo, LiteralDiccionario):
        print(f"{prefijo}{rama}diccionario{{{len(nodo.pares)}}}  (L{nodo.linea})")
        for i, (k, v) in enumerate(nodo.pares):
            u = i == len(nodo.pares) - 1
            print(f"{ext}+-- par {i}:")
            sub = ext + (_VACIO if u else _PIPE)
            visualizar(k, sub, False)
            visualizar(v, sub, True)

    elif isinstance(nodo, Identificador):
        print(f"{prefijo}{rama}id: {nodo.nombre}  (L{nodo.linea})")

    else:
        print(f"{prefijo}{rama}[nodo desconocido: {type(nodo).__name__}]")
