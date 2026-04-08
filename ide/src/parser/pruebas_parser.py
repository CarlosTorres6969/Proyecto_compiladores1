# Pruebas del parser de CCODE.
# Cada prueba verifica que el AST generado tenga la estructura esperada.

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'lexer'))

from tokenizer import tokenizar_codigo
from parser import parsear_codigo, ErrorSintactico
from nodos import (
    Programa, DeclaracionVariable, DeclaracionConstante,
    DefinicionFuncion, Retornar, LlamadaFuncion,
    Cuando, Mientras, Recorrer, Repetir, Detener,
    Mostrar, Intentar, Lanzar, Agregar, Remover,
    ExpresionBinaria, ExpresionUnaria,
    LiteralNumero, LiteralTexto, LiteralLogico, LiteralVacio,
    LiteralColeccion, LiteralDiccionario, Identificador,
)
from visualizador_ast import visualizar


# ------------------------------------------------------------------
# Mini framework de pruebas
# ------------------------------------------------------------------

_total = 0
_pasadas = 0
_fallidas = []


def prueba(nombre, fn):
    global _total, _pasadas
    _total += 1
    try:
        fn()
        print(f"  [ok]  {nombre}")
        _pasadas += 1
    except AssertionError as e:
        print(f"  [fallo]  {nombre}: {e}")
        _fallidas.append(nombre)
    except Exception as e:
        print(f"  [error]  {nombre}: {e}")
        _fallidas.append(nombre)


def afirmar(condicion, mensaje=''):
    if not condicion:
        raise AssertionError(mensaje)


def parsear(fuente):
    tokens = tokenizar_codigo(fuente)
    return parsear_codigo(tokens)


# ------------------------------------------------------------------
# Pruebas
# ------------------------------------------------------------------

def test_programa_vacio():
    ast = parsear('inicio mi_programa\nfinal\n')
    afirmar(isinstance(ast, Programa))
    afirmar(ast.nombre == 'mi_programa')
    afirmar(ast.cuerpo == [])


def test_declaracion_numero():
    ast = parsear('inicio p\n    guardar x es numero con 42\nfinal\n')
    nodo = ast.cuerpo[0]
    afirmar(isinstance(nodo, DeclaracionVariable))
    afirmar(nodo.nombre == 'x')
    afirmar(nodo.tipo == 'numero')
    afirmar(isinstance(nodo.valor, LiteralNumero))
    afirmar(nodo.valor.valor == 42)


def test_declaracion_texto():
    ast = parsear('inicio p\n    guardar msg es texto con "hola"\nfinal\n')
    nodo = ast.cuerpo[0]
    afirmar(isinstance(nodo, DeclaracionVariable))
    afirmar(nodo.tipo == 'texto')
    afirmar(isinstance(nodo.valor, LiteralTexto))
    afirmar(nodo.valor.valor == 'hola')


def test_declaracion_logico():
    ast = parsear('inicio p\n    guardar ok es logico con verdadero\nfinal\n')
    nodo = ast.cuerpo[0]
    afirmar(isinstance(nodo.valor, LiteralLogico))
    afirmar(nodo.valor.valor is True)


def test_declaracion_constante():
    ast = parsear('inicio p\n    constante PI es numero con 3.14\nfinal\n')
    nodo = ast.cuerpo[0]
    afirmar(isinstance(nodo, DeclaracionConstante))
    afirmar(nodo.nombre == 'PI')
    afirmar(isinstance(nodo.valor, LiteralNumero))


def test_expresion_binaria_suma():
    ast = parsear('inicio p\n    guardar r es numero con 3 mas 4\nfinal\n')
    expr = ast.cuerpo[0].valor
    afirmar(isinstance(expr, ExpresionBinaria))
    afirmar(expr.operador == 'mas')
    afirmar(isinstance(expr.izquierda, LiteralNumero))
    afirmar(isinstance(expr.derecha, LiteralNumero))


def test_expresion_precedencia():
    # 2 mas 3 por 4  =>  2 + (3 * 4)
    ast = parsear('inicio p\n    guardar r es numero con 2 mas 3 por 4\nfinal\n')
    expr = ast.cuerpo[0].valor
    afirmar(isinstance(expr, ExpresionBinaria))
    afirmar(expr.operador == 'mas')
    afirmar(isinstance(expr.derecha, ExpresionBinaria))
    afirmar(expr.derecha.operador == 'por')


def test_expresion_potencia_asociatividad():
    # 2 elevado 3 elevado 2  =>  2 ** (3 ** 2)
    ast = parsear('inicio p\n    guardar r es numero con 2 elevado 3 elevado 2\nfinal\n')
    expr = ast.cuerpo[0].valor
    afirmar(expr.operador == 'elevado')
    afirmar(isinstance(expr.derecha, ExpresionBinaria))
    afirmar(expr.derecha.operador == 'elevado')


def test_expresion_unaria_negar():
    ast = parsear('inicio p\n    guardar r es logico con negar verdadero\nfinal\n')
    expr = ast.cuerpo[0].valor
    afirmar(isinstance(expr, ExpresionUnaria))
    afirmar(expr.operador == 'negar')
    afirmar(isinstance(expr.operando, LiteralLogico))


def test_mostrar():
    ast = parsear('inicio p\n    mostrar "hola" x\nfinal\n')
    nodo = ast.cuerpo[0]
    afirmar(isinstance(nodo, Mostrar))
    afirmar(len(nodo.expresiones) == 2)


def test_cuando_simple():
    fuente = (
        'inicio p\n'
        '    cuando x es 1\n'
        '        mostrar "uno"\n'
        '    final\n'
        'final\n'
    )
    ast = parsear(fuente)
    nodo = ast.cuerpo[0]
    afirmar(isinstance(nodo, Cuando))
    afirmar(len(nodo.ramas) == 1)
    afirmar(nodo.rama_sino is None)


def test_cuando_sino():
    fuente = (
        'inicio p\n'
        '    cuando x es 1\n'
        '        mostrar "uno"\n'
        '    sino\n'
        '        mostrar "otro"\n'
        '    final\n'
        'final\n'
    )
    ast = parsear(fuente)
    nodo = ast.cuerpo[0]
    afirmar(nodo.rama_sino is not None)
    afirmar(len(nodo.rama_sino) == 1)


def test_cuando_ademas():
    fuente = (
        'inicio p\n'
        '    cuando x es 1\n'
        '        mostrar "uno"\n'
        '    ademas x es 2\n'
        '        mostrar "dos"\n'
        '    sino\n'
        '        mostrar "otro"\n'
        '    final\n'
        'final\n'
    )
    ast = parsear(fuente)
    nodo = ast.cuerpo[0]
    afirmar(len(nodo.ramas) == 2)
    afirmar(nodo.rama_sino is not None)


def test_mientras():
    fuente = (
        'inicio p\n'
        '    mientras i menor_que 10\n'
        '        mostrar i\n'
        '    final\n'
        'final\n'
    )
    ast = parsear(fuente)
    nodo = ast.cuerpo[0]
    afirmar(isinstance(nodo, Mientras))
    afirmar(isinstance(nodo.condicion, ExpresionBinaria))
    afirmar(nodo.condicion.operador == 'menor_que')


def test_repetir_con_detener():
    fuente = (
        'inicio p\n'
        '    repetir\n'
        '        detener\n'
        '    final\n'
        'final\n'
    )
    ast = parsear(fuente)
    nodo = ast.cuerpo[0]
    afirmar(isinstance(nodo, Repetir))
    afirmar(isinstance(nodo.cuerpo[0], Detener))


def test_recorrer():
    fuente = (
        'inicio p\n'
        '    recorrer item en lista\n'
        '        mostrar item\n'
        '    final\n'
        'final\n'
    )
    ast = parsear(fuente)
    nodo = ast.cuerpo[0]
    afirmar(isinstance(nodo, Recorrer))
    afirmar(nodo.variable == 'item')
    afirmar(isinstance(nodo.iterable, Identificador))


def test_funcion_sin_parametros():
    fuente = (
        'inicio p\n'
        '    crear funcion saludar con parametros\n'
        '        mostrar "hola"\n'
        '    final\n'
        'final\n'
    )
    ast = parsear(fuente)
    nodo = ast.cuerpo[0]
    afirmar(isinstance(nodo, DefinicionFuncion))
    afirmar(nodo.nombre == 'saludar')
    afirmar(nodo.parametros == [])


def test_funcion_con_parametros():
    fuente = (
        'inicio p\n'
        '    crear funcion sumar con parametros a, b\n'
        '        retornar a mas b\n'
        '    final\n'
        'final\n'
    )
    ast = parsear(fuente)
    nodo = ast.cuerpo[0]
    afirmar(nodo.parametros == ['a', 'b'])
    retorno = nodo.cuerpo[0]
    afirmar(isinstance(retorno, Retornar))
    afirmar(len(retorno.valores) == 1)


def test_invocar_funcion():
    fuente = (
        'inicio p\n'
        '    invocar saludar con "mundo"\n'
        'final\n'
    )
    ast = parsear(fuente)
    nodo = ast.cuerpo[0]
    afirmar(isinstance(nodo, LlamadaFuncion))
    afirmar(nodo.nombre == 'saludar')
    afirmar(len(nodo.argumentos) == 1)


def test_intentar_capturar():
    fuente = (
        'inicio p\n'
        '    intentar\n'
        '        mostrar "ok"\n'
        '    capturar_error como e\n'
        '        mostrar e\n'
        '    final\n'
        'final\n'
    )
    ast = parsear(fuente)
    nodo = ast.cuerpo[0]
    afirmar(isinstance(nodo, Intentar))
    afirmar(nodo.nombre_error == 'e')
    afirmar(nodo.cuerpo_siempre is None)


def test_intentar_siempre():
    fuente = (
        'inicio p\n'
        '    intentar\n'
        '        mostrar "ok"\n'
        '    capturar_error como e\n'
        '        mostrar e\n'
        '    siempre\n'
        '        mostrar "listo"\n'
        '    final\n'
        'final\n'
    )
    ast = parsear(fuente)
    nodo = ast.cuerpo[0]
    afirmar(nodo.cuerpo_siempre is not None)


def test_lanzar():
    fuente = (
        'inicio p\n'
        '    lanzar "algo salio mal"\n'
        'final\n'
    )
    ast = parsear(fuente)
    nodo = ast.cuerpo[0]
    afirmar(isinstance(nodo, Lanzar))
    afirmar(isinstance(nodo.expresion, LiteralTexto))


def test_coleccion_literal():
    fuente = (
        'inicio p\n'
        '    guardar nums es coleccion con [1, 2, 3]\n'
        'final\n'
    )
    ast = parsear(fuente)
    nodo = ast.cuerpo[0].valor
    afirmar(isinstance(nodo, LiteralColeccion))
    afirmar(len(nodo.elementos) == 3)


def test_diccionario_literal():
    fuente = (
        'inicio p\n'
        '    guardar d es diccionario con {"a": 1, "b": 2}\n'
        'final\n'
    )
    ast = parsear(fuente)
    nodo = ast.cuerpo[0].valor
    afirmar(isinstance(nodo, LiteralDiccionario))
    afirmar(len(nodo.pares) == 2)


def test_agregar_remover():
    fuente = (
        'inicio p\n'
        '    agregar 5 a lista\n'
        '    remover 5 de lista\n'
        'final\n'
    )
    ast = parsear(fuente)
    afirmar(isinstance(ast.cuerpo[0], Agregar))
    afirmar(isinstance(ast.cuerpo[1], Remover))


def test_importar():
    fuente = (
        'inicio p\n'
        '    importar sumar, restar desde "matematicas"\n'
        'final\n'
    )
    ast = parsear(fuente)
    from nodos import Importar
    nodo = ast.cuerpo[0]
    afirmar(isinstance(nodo, Importar))
    afirmar(nodo.nombres == ['sumar', 'restar'])
    afirmar(nodo.origen == 'matematicas')


def test_error_sintactico():
    fuente = 'inicio p\n    guardar x es numero\nfinal\n'
    lanzado = False
    try:
        parsear(fuente)
    except ErrorSintactico:
        lanzado = True
    afirmar(lanzado, "debería lanzar ErrorSintactico cuando falta 'con'")


def test_ast_completo_visualizado():
    fuente = '''
inicio demo
    guardar n es numero con 5
    crear funcion factorial con parametros x
        cuando x menor_o_igual 1
            retornar 1
        final
        retornar x por invocar factorial con x menos 1
    final
    guardar resultado es numero con invocar factorial con n
    mostrar "factorial:" resultado
final
'''
    ast = parsear(fuente)
    print()
    visualizar(ast)
    afirmar(isinstance(ast, Programa))


# ------------------------------------------------------------------
# Ejecutar todas las pruebas
# ------------------------------------------------------------------

if __name__ == '__main__':
    print("Pruebas del parser de CCODE")
    print("=" * 40)

    prueba("programa vacío", test_programa_vacio)
    prueba("declaración número", test_declaracion_numero)
    prueba("declaración texto", test_declaracion_texto)
    prueba("declaración lógico", test_declaracion_logico)
    prueba("declaración constante", test_declaracion_constante)
    prueba("expresión binaria suma", test_expresion_binaria_suma)
    prueba("precedencia de operadores", test_expresion_precedencia)
    prueba("potencia asociatividad derecha", test_expresion_potencia_asociatividad)
    prueba("expresión unaria negar", test_expresion_unaria_negar)
    prueba("mostrar múltiples expresiones", test_mostrar)
    prueba("cuando simple", test_cuando_simple)
    prueba("cuando con sino", test_cuando_sino)
    prueba("cuando con ademas", test_cuando_ademas)
    prueba("mientras", test_mientras)
    prueba("repetir con detener", test_repetir_con_detener)
    prueba("recorrer", test_recorrer)
    prueba("función sin parámetros", test_funcion_sin_parametros)
    prueba("función con parámetros", test_funcion_con_parametros)
    prueba("invocar función", test_invocar_funcion)
    prueba("intentar/capturar_error", test_intentar_capturar)
    prueba("intentar/siempre", test_intentar_siempre)
    prueba("lanzar error", test_lanzar)
    prueba("colección literal", test_coleccion_literal)
    prueba("diccionario literal", test_diccionario_literal)
    prueba("agregar y remover", test_agregar_remover)
    prueba("importar módulo", test_importar)
    prueba("error sintáctico detectado", test_error_sintactico)
    prueba("AST completo (factorial)", test_ast_completo_visualizado)

    print()
    print("=" * 40)
    print(f"Resultado: {_pasadas}/{_total} pruebas pasadas")
    if _fallidas:
        print("Fallidas:")
        for f in _fallidas:
            print(f"  - {f}")
