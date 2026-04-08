#!/usr/bin/env python3
# Punto de entrada del lenguaje CCODE.
# Uso: python src/cli/main.py ejecutar <archivo.aura>
#      python src/cli/main.py ast      <archivo.aura>
#      python src/cli/main.py tokens   <archivo.aura>
#      python src/cli/main.py version

import sys
import os

# Rutas de los módulos
_BASE = os.path.dirname(__file__)
sys.path.insert(0, os.path.join(_BASE, '..', 'lexer'))
sys.path.insert(0, os.path.join(_BASE, '..', 'parser'))

from tokenizer import tokenizar_codigo, ErrorLexico
from parser import parsear_codigo, ErrorSintactico
from visualizador_ast import visualizar
from interprete import Interprete, ErrorEjecucion


VERSION = '1.0.0'

AYUDA = f"""
CCODE v{VERSION} — intérprete del lenguaje CCODE

Uso:
  python src/cli/main.py ejecutar <archivo.aura>   Ejecuta un programa
  python src/cli/main.py ast      <archivo.aura>   Muestra el AST
  python src/cli/main.py tokens   <archivo.aura>   Muestra los tokens
  python src/cli/main.py version                   Muestra la versión
  python src/cli/main.py ayuda                     Muestra esta ayuda
""".strip()


def leer_archivo(ruta):
    if not os.path.exists(ruta):
        print(f"Error: no se encontró el archivo '{ruta}'")
        sys.exit(1)
    with open(ruta, 'r', encoding='utf-8-sig') as f:
        return f.read()


def cmd_tokens(ruta):
    codigo = leer_archivo(ruta)
    try:
        tokens = tokenizar_codigo(codigo)
        for tok in tokens:
            print(tok)
    except ErrorLexico as e:
        print(e)
        sys.exit(1)


def cmd_ast(ruta):
    codigo = leer_archivo(ruta)
    try:
        tokens = tokenizar_codigo(codigo)
        ast = parsear_codigo(tokens)
        visualizar(ast)
    except (ErrorLexico, ErrorSintactico) as e:
        print(e)
        sys.exit(1)


def cmd_ejecutar(ruta):
    codigo = leer_archivo(ruta)
    try:
        tokens = tokenizar_codigo(codigo)
        ast = parsear_codigo(tokens)
        interprete = Interprete()
        interprete.ejecutar(ast)
    except ErrorLexico as e:
        print(e, file=sys.stderr)
        sys.exit(1)
    except ErrorSintactico as e:
        print(e, file=sys.stderr)
        sys.exit(1)
    except ErrorEjecucion as e:
        print(f"[Error de ejecucion] {e}", file=sys.stderr)
        sys.exit(1)
    except KeyboardInterrupt:
        print("\nEjecucion interrumpida por el usuario.")
        sys.exit(0)


def main():
    args = sys.argv[1:]

    if not args or args[0] in ('ayuda', '--ayuda', '-h'):
        print(AYUDA)
        return

    if args[0] == 'version':
        print(f"CCODE v{VERSION}")
        return

    if len(args) < 2:
        print(AYUDA)
        sys.exit(1)

    comando, ruta = args[0], args[1]

    if comando == 'tokens':
        cmd_tokens(ruta)
    elif comando == 'ast':
        cmd_ast(ruta)
    elif comando == 'ejecutar':
        cmd_ejecutar(ruta)
    else:
        print(f"Comando desconocido: '{comando}'")
        print(AYUDA)
        sys.exit(1)


if __name__ == '__main__':
    main()
