"""
Lexer/Tokenizer para el lenguaje CCODE
Convierte codigo fuente en tokens
"""

from __future__ import annotations

import io
import sys
from typing import Optional

try:
    from .token_types import Token, TipoToken, PALABRAS_RESERVADAS
except ImportError:
    from token_types import Token, TipoToken, PALABRAS_RESERVADAS  # ejecucion directa

# Caracteres validos para iniciar un identificador
_INICIO_ID: frozenset[str] = frozenset(
    'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ_'
    'áéíóúÁÉÍÓÚñÑüÜ'
)
_CUERPO_ID: frozenset[str] = _INICIO_ID | frozenset('0123456789')

# Sugerencias para caracteres invalidos comunes
_SUGERENCIAS: dict[str, str] = {
    ';': "CCODE no usa ';' para terminar sentencias",
    '(': "CCODE no usa parentesis. Escribe la expresion directamente",
    ')': "CCODE no usa parentesis",
    '=': "para comparar usa 'es', para asignar usa 'guardar x es tipo con valor'",
    '+': "para sumar usa la palabra 'mas'",
    '-': "para restar usa la palabra 'menos'",
    '*': "para multiplicar usa la palabra 'por'",
    '/': "para dividir usa la palabra 'entre'",
    '%': "para el modulo usa la palabra 'resto'",
    '!': "para negar usa la palabra 'negar'",
    '&': "para AND logico usa 'y_tambien'",
    '|': "para OR logico usa 'o_sino'",
    "'": "las cadenas de texto usan comillas dobles '\"', no simples",
}


class ErrorLexico(Exception):
    pass


def _fmt(linea: int, columna: int, mensaje: str, fragmento: Optional[str] = None) -> str:
    base = f"[Error lexico] Linea {linea}, columna {columna}: {mensaje}"
    if fragmento:
        base += f"\n  --> {fragmento}"
    return base


class Lexer:
    """Analizador lexico para el lenguaje CCODE."""

    def __init__(self, codigo: str) -> None:
        self.codigo = codigo
        self.lineas = codigo.splitlines()   # para mostrar contexto en errores
        self.posicion = 0
        self.linea = 1
        self.columna = 1
        self.tokens: list[Token] = []
        self.niveles_indentacion: list[int] = [0]

    # ------------------------------------------------------------------
    # Utilidades internas
    # ------------------------------------------------------------------

    def _error(self, mensaje: str) -> None:
        fragmento = self._fragmento_linea()
        raise ErrorLexico(_fmt(self.linea, self.columna, mensaje, fragmento))

    def _fragmento_linea(self) -> Optional[str]:
        """Devuelve la linea actual del codigo para mostrar en el error."""
        idx = self.linea - 1
        if 0 <= idx < len(self.lineas):
            linea_txt = self.lineas[idx]
            puntero = ' ' * (self.columna - 1) + '^'
            return f"{linea_txt}\n  {puntero}"
        return None

    def _avanzar(self) -> None:
        if self.posicion < len(self.codigo):
            if self.codigo[self.posicion] == '\n':
                self.linea += 1
                self.columna = 1
            else:
                self.columna += 1
            self.posicion += 1

    def _actual(self) -> Optional[str]:
        if self.posicion < len(self.codigo):
            return self.codigo[self.posicion]
        return None

    def _siguiente(self, n: int = 1) -> Optional[str]:
        pos = self.posicion + n
        if pos < len(self.codigo):
            return self.codigo[pos]
        return None

    def _saltar_espacios(self) -> None:
        while self._actual() in (' ', '\t'):
            self._avanzar()

    # ------------------------------------------------------------------
    # Lectores
    # ------------------------------------------------------------------

    def _leer_comentario(self) -> None:
        self._avanzar()  # saltar #
        if self._actual() == '[':
            # comentario multilinea  #[ ... ]#
            linea_inicio = self.linea
            col_inicio = self.columna
            self._avanzar()  # saltar [
            while True:
                if self._actual() is None:
                    raise ErrorLexico(
                        _fmt(linea_inicio, col_inicio,
                             "comentario multilinea abierto con '#[' nunca fue cerrado con ']#'")
                    )
                if self._actual() == ']' and self._siguiente() == '#':
                    self._avanzar()
                    self._avanzar()
                    break
                self._avanzar()
        else:
            # comentario de una linea
            while self._actual() not in ('\n', None):
                self._avanzar()

    def _leer_numero(self) -> Token:
        linea, col = self.linea, self.columna
        buf = io.StringIO()

        while self._actual() and self._actual().isdigit():
            buf.write(self._actual())
            self._avanzar()

        # parte decimal
        if self._actual() == '.' and self._siguiente() and self._siguiente().isdigit():
            buf.write('.')
            self._avanzar()
            while self._actual() and self._actual().isdigit():
                buf.write(self._actual())
                self._avanzar()
        elif self._actual() == '.' and (self._siguiente() is None or not self._siguiente().isdigit()):
            numero = buf.getvalue()
            self._error(
                f"numero mal formado '{numero}.': despues del punto se esperaban digitos"
            )

        numero = buf.getvalue()
        valor: int | float = float(numero) if '.' in numero else int(numero)
        return Token(TipoToken.LITERAL_NUMERO, valor, linea, col)

    def _leer_texto(self) -> Token:
        linea, col = self.linea, self.columna
        self._avanzar()  # saltar comilla inicial
        buf = io.StringIO()

        while self._actual() and self._actual() != '"':
            if self._actual() == '\n':
                raise ErrorLexico(
                    _fmt(linea, col,
                         "cadena de texto sin cerrar: no se puede usar salto de linea dentro de una cadena",
                         self._fragmento_linea())
                )
            if self._actual() == '\\':
                self._avanzar()
                esc = self._actual()
                secuencias = {'n': '\n', 't': '\t', '"': '"', '\\': '\\'}
                if esc in secuencias:
                    buf.write(secuencias[esc])
                elif esc is None:
                    raise ErrorLexico(
                        _fmt(linea, col, "secuencia de escape incompleta al final del archivo")
                    )
                else:
                    raise ErrorLexico(
                        _fmt(self.linea, self.columna,
                             f"secuencia de escape desconocida '\\{esc}'. "
                             f"Las validas son: \\n, \\t, \\\", \\\\")
                    )
                self._avanzar()
            else:
                buf.write(self._actual())
                self._avanzar()

        # FIX: la condicion original `!= '"'` era imposible aqui;
        # el while ya sale cuando actual es None o '"'.
        # Verificamos EOF correctamente.
        if self._actual() is None:
            raise ErrorLexico(
                _fmt(linea, col,
                     "cadena de texto sin cerrar: falta la comilla de cierre '\"'")
            )
        self._avanzar()
        return Token(TipoToken.LITERAL_TEXTO, buf.getvalue(), linea, col)

    def _leer_identificador(self) -> Token:
        linea, col = self.linea, self.columna
        buf = io.StringIO()
        while self._actual() and self._actual() in _CUERPO_ID:
            buf.write(self._actual())
            self._avanzar()
        ident = buf.getvalue()
        tipo = PALABRAS_RESERVADAS.get(ident, TipoToken.IDENTIFICADOR)
        return Token(tipo, ident, linea, col)

    def _manejar_indentacion(self) -> list[Token]:
        """Calcula el nivel de indentacion y emite INDENTACION/DEDENTACION."""
        espacios = 0
        while self._actual() in (' ', '\t'):
            espacios += 4 if self._actual() == '\t' else 1
            self._avanzar()

        # linea vacia o solo comentario: ignorar
        if self._actual() in ('\n', None, '#'):
            return []

        nivel_actual = self.niveles_indentacion[-1]
        tokens_ind: list[Token] = []

        if espacios > nivel_actual:
            if (espacios - nivel_actual) % 4 != 0:
                raise ErrorLexico(
                    _fmt(self.linea, 1,
                         f"indentacion incorrecta: se esperaba un multiplo de 4 espacios "
                         f"(nivel anterior: {nivel_actual}, encontrado: {espacios})",
                         self._fragmento_linea())
                )
            self.niveles_indentacion.append(espacios)
            tokens_ind.append(Token(TipoToken.INDENTACION, espacios, self.linea, 1))

        elif espacios < nivel_actual:
            while self.niveles_indentacion[-1] > espacios:
                self.niveles_indentacion.pop()
                tokens_ind.append(Token(TipoToken.DEDENTACION, espacios, self.linea, 1))
            if self.niveles_indentacion[-1] != espacios:
                raise ErrorLexico(
                    _fmt(self.linea, 1,
                         f"indentacion inconsistente: el nivel {espacios} no coincide "
                         f"con ningun bloque abierto anteriormente",
                         self._fragmento_linea())
                )

        return tokens_ind

    # ------------------------------------------------------------------
    # Tokenizacion principal
    # ------------------------------------------------------------------

    def tokenizar(self) -> list[Token]:
        inicio_linea = True

        while self._actual() is not None:
            if inicio_linea:
                self.tokens.extend(self._manejar_indentacion())
                inicio_linea = False

            char = self._actual()
            if char is None:
                break

            if char in (' ', '\t'):
                self._saltar_espacios()
            elif char == '\n':
                self.tokens.append(
                    Token(TipoToken.NUEVA_LINEA, '\\n', self.linea, self.columna)
                )
                self._avanzar()
                inicio_linea = True
            elif char == '#':
                self._leer_comentario()
            elif char.isdigit():
                self.tokens.append(self._leer_numero())
            elif char == '"':
                self.tokens.append(self._leer_texto())
            elif char in _INICIO_ID:
                self.tokens.append(self._leer_identificador())
            elif char == '[':
                self.tokens.append(Token(TipoToken.CORCHETE_IZQ, '[', self.linea, self.columna))
                self._avanzar()
            elif char == ']':
                self.tokens.append(Token(TipoToken.CORCHETE_DER, ']', self.linea, self.columna))
                self._avanzar()
            elif char == '{':
                self.tokens.append(Token(TipoToken.LLAVE_IZQ, '{', self.linea, self.columna))
                self._avanzar()
            elif char == '}':
                self.tokens.append(Token(TipoToken.LLAVE_DER, '}', self.linea, self.columna))
                self._avanzar()
            elif char == ',':
                self.tokens.append(Token(TipoToken.COMA, ',', self.linea, self.columna))
                self._avanzar()
            elif char == ':':
                self.tokens.append(Token(TipoToken.DOS_PUNTOS, ':', self.linea, self.columna))
                self._avanzar()
            elif char == '.':
                self.tokens.append(Token(TipoToken.PUNTO, '.', self.linea, self.columna))
                self._avanzar()
            else:
                sugerencia = _SUGERENCIAS.get(char)
                self._error(
                    f"caracter inesperado '{char}'"
                    + (f". {sugerencia}" if sugerencia else "")
                )

        # cerrar bloques abiertos al llegar al EOF
        while len(self.niveles_indentacion) > 1:
            self.niveles_indentacion.pop()
            self.tokens.append(Token(TipoToken.DEDENTACION, 0, self.linea, self.columna))

        self.tokens.append(Token(TipoToken.EOF, None, self.linea, self.columna))
        return self.tokens


def tokenizar_codigo(codigo: str) -> list[Token]:
    """Punto de entrada publico: tokeniza una cadena de codigo CCODE."""
    return Lexer(codigo).tokenizar()


if __name__ == '__main__':
    if len(sys.argv) < 2:
        fuente = sys.stdin.read()
    else:
        with open(sys.argv[1], encoding='utf-8') as f:
            fuente = f.read()

    try:
        for tok in tokenizar_codigo(fuente):
            print(tok)
    except ErrorLexico as e:
        print(e)
        sys.exit(1)
