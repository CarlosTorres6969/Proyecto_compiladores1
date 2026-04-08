# Parser para CCODE — análisis sintáctico descendente recursivo.
# Toma la lista de tokens del lexer y construye el AST.

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'lexer'))

from token_types import TipoToken, Token
from nodos import (
    Programa, DeclaracionVariable, DeclaracionConstante, AsignacionIndice,
    DefinicionFuncion, Retornar, LlamadaFuncion, LlamadaMetodo,
    Cuando, Mientras, Repetir, Recorrer, Detener, Continuar,
    Mostrar, Intentar, Lanzar, Agregar, Remover,
    Importar, Exportar,
    ExpresionBinaria, ExpresionUnaria,
    AccesoIndice, AccesoCampo,
    LiteralNumero, LiteralTexto, LiteralLogico, LiteralVacio,
    LiteralColeccion, LiteralDiccionario, Identificador
)


class ErrorSintactico(Exception):
    pass


def _fmt_sint(linea, columna, mensaje, sugerencia=None):
    txt = f"[Error sintactico] Linea {linea}, columna {columna}: {mensaje}"
    if sugerencia:
        txt += f"\n  Sugerencia: {sugerencia}"
    return txt


# Operadores de comparación y lógicos reconocidos en expresiones
_OPS_COMPARACION = {
    TipoToken.ES, TipoToken.NO_ES,
    TipoToken.MAYOR_QUE, TipoToken.MENOR_QUE,
    TipoToken.MAYOR_O_IGUAL, TipoToken.MENOR_O_IGUAL,
}

_OPS_ADITIVOS = {TipoToken.MAS, TipoToken.MENOS}
_OPS_MULTIPLICATIVOS = {TipoToken.POR, TipoToken.ENTRE, TipoToken.RESTO}
_OPS_POTENCIA = {TipoToken.ELEVADO}
_OPS_LOGICOS = {TipoToken.Y_TAMBIEN, TipoToken.O_SINO}

# Tipos de datos válidos para declaraciones
_TIPOS_DATO = {
    TipoToken.NUMERO, TipoToken.TEXTO, TipoToken.LOGICO,
    TipoToken.VACIO, TipoToken.COLECCION, TipoToken.DICCIONARIO,
}


class Parser:
    def __init__(self, tokens):
        # Filtramos nueva línea y comentarios para simplificar el recorrido.
        # La indentación ya fue procesada por el lexer.
        self.tokens = [
            t for t in tokens
            if t.tipo not in (TipoToken.NUEVA_LINEA, TipoToken.COMENTARIO)
        ]
        self.pos = 0

    # ------------------------------------------------------------------
    # Utilidades de navegación
    # ------------------------------------------------------------------

    def actual(self):
        return self.tokens[self.pos]

    def linea_actual(self):
        return self.actual().linea

    def avanzar(self):
        tok = self.tokens[self.pos]
        if self.pos < len(self.tokens) - 1:
            self.pos += 1
        return tok

    def verificar(self, *tipos):
        return self.actual().tipo in tipos

    def consumir(self, tipo, mensaje=None):
        if self.actual().tipo == tipo:
            return self.avanzar()
        tok = self.actual()
        if mensaje:
            msg = mensaje
        else:
            msg = _mensaje_esperado(tipo, tok)
        raise ErrorSintactico(
            _fmt_sint(tok.linea, tok.columna, msg,
                      _sugerir_sintaxis(tipo, tok))
        )

    def consumir_cualquiera(self, tipos, mensaje=None):
        if self.actual().tipo in tipos:
            return self.avanzar()
        tok = self.actual()
        nombres = ' | '.join(_nombre_legible(t) for t in tipos)
        msg = mensaje or f"se esperaba un tipo de dato ({nombres}) pero se encontro '{tok.valor}'"
        raise ErrorSintactico(
            _fmt_sint(tok.linea, tok.columna, msg,
                      "los tipos validos son: numero, texto, logico, coleccion, diccionario, vacio")
        )

    def saltar_indentacion(self):
        while self.verificar(TipoToken.INDENTACION, TipoToken.DEDENTACION):
            self.avanzar()

    # ------------------------------------------------------------------
    # Punto de entrada
    # ------------------------------------------------------------------

    def parsear(self):
        self.saltar_indentacion()

        # Permitir definiciones de funciones e importaciones antes del bloque inicio
        preambulo = []
        while not self.verificar(TipoToken.INICIO, TipoToken.EOF):
            self.saltar_indentacion()
            if self.verificar(TipoToken.INICIO, TipoToken.EOF):
                break
            if self.verificar(TipoToken.CREAR):
                preambulo.append(self.parsear_funcion())
            elif self.verificar(TipoToken.IMPORTAR):
                preambulo.append(self.parsear_importar())
            elif self.verificar(TipoToken.EXPORTAR):
                preambulo.append(self.parsear_exportar())
            else:
                tok = self.actual()
                raise ErrorSintactico(
                    f"Error sintáctico en línea {tok.linea}: "
                    f"solo se permiten funciones antes de 'inicio', se encontró '{tok.valor}'"
                )
            self.saltar_indentacion()

        self.consumir(TipoToken.INICIO, "el programa debe tener un bloque 'inicio'")
        nombre = self.consumir(TipoToken.IDENTIFICADOR, "se esperaba el nombre del programa").valor
        self.saltar_indentacion()

        cuerpo = self.parsear_bloque()

        self.consumir(TipoToken.FINAL, "se esperaba 'final' para cerrar el programa")
        self.consumir(TipoToken.EOF, "se esperaba fin de archivo")

        return Programa(nombre, preambulo + cuerpo)

    # ------------------------------------------------------------------
    # Bloques y sentencias
    # ------------------------------------------------------------------

    def parsear_bloque(self):
        sentencias = []
        self.saltar_indentacion()

        while not self.verificar(TipoToken.FINAL, TipoToken.SINO, TipoToken.ADEMAS,
                                  TipoToken.CAPTURAR_ERROR, TipoToken.SIEMPRE,
                                  TipoToken.EOF):
            self.saltar_indentacion()
            if self.verificar(TipoToken.FINAL, TipoToken.SINO, TipoToken.ADEMAS,
                               TipoToken.CAPTURAR_ERROR, TipoToken.SIEMPRE, TipoToken.EOF):
                break
            sentencias.append(self.parsear_sentencia())
            self.saltar_indentacion()

        return sentencias

    def parsear_sentencia(self):
        tok = self.actual()

        if tok.tipo == TipoToken.GUARDAR:
            return self.parsear_guardar()
        if tok.tipo == TipoToken.CONSTANTE:
            return self.parsear_constante()
        if tok.tipo == TipoToken.MOSTRAR:
            return self.parsear_mostrar()
        if tok.tipo == TipoToken.CUANDO:
            return self.parsear_cuando()
        if tok.tipo == TipoToken.MIENTRAS:
            return self.parsear_mientras()
        if tok.tipo == TipoToken.REPETIR:
            return self.parsear_repetir()
        if tok.tipo == TipoToken.RECORRER:
            return self.parsear_recorrer()
        if tok.tipo == TipoToken.DETENER:
            self.avanzar()
            return Detener(tok.linea)
        if tok.tipo == TipoToken.CONTINUAR:
            self.avanzar()
            return Continuar(tok.linea)
        if tok.tipo == TipoToken.CREAR:
            return self.parsear_funcion()
        if tok.tipo == TipoToken.RETORNAR:
            return self.parsear_retornar()
        if tok.tipo == TipoToken.INVOCAR:
            return self.parsear_invocar_sentencia()
        if tok.tipo == TipoToken.INTENTAR:
            return self.parsear_intentar()
        if tok.tipo == TipoToken.LANZAR:
            return self.parsear_lanzar()
        if tok.tipo == TipoToken.AGREGAR:
            return self.parsear_agregar()
        if tok.tipo == TipoToken.REMOVER:
            return self.parsear_remover()
        if tok.tipo == TipoToken.IMPORTAR:
            return self.parsear_importar()
        if tok.tipo == TipoToken.EXPORTAR:
            return self.parsear_exportar()

        raise ErrorSintactico(
            _fmt_sint(tok.linea, tok.columna,
                      f"sentencia inesperada '{tok.valor}'",
                      _sugerir_sentencia(tok.valor))
        )

    # ------------------------------------------------------------------
    # Declaraciones de variables
    # ------------------------------------------------------------------

    def parsear_guardar(self):
        linea = self.linea_actual()
        self.consumir(TipoToken.GUARDAR)
        nombre = self.consumir(TipoToken.IDENTIFICADOR).valor

        # Acceso a índice: guardar lista[0] es tipo con valor
        if self.verificar(TipoToken.CORCHETE_IZQ):
            self.avanzar()
            indice = self.parsear_expresion()
            self.consumir(TipoToken.CORCHETE_DER)
            self.consumir(TipoToken.ES)
            tipo = self.consumir_cualquiera(_TIPOS_DATO).valor
            self.consumir(TipoToken.CON)
            valor = self.parsear_expresion()
            return AsignacionIndice(nombre, indice, tipo, valor, linea)

        self.consumir(TipoToken.ES)
        tipo = self.consumir_cualquiera(_TIPOS_DATO).valor
        self.consumir(TipoToken.CON)
        valor = self.parsear_expresion()
        return DeclaracionVariable(nombre, tipo, valor, linea)

    def parsear_constante(self):
        linea = self.linea_actual()
        self.consumir(TipoToken.CONSTANTE)
        nombre = self.consumir(TipoToken.IDENTIFICADOR).valor
        self.consumir(TipoToken.ES)
        tipo = self.consumir_cualquiera(_TIPOS_DATO).valor
        self.consumir(TipoToken.CON)
        valor = self.parsear_expresion()
        return DeclaracionConstante(nombre, tipo, valor, linea)

    # ------------------------------------------------------------------
    # Entrada / Salida
    # ------------------------------------------------------------------

    def parsear_mostrar(self):
        linea = self.linea_actual()
        self.consumir(TipoToken.MOSTRAR)
        expresiones = []

        # mostrar acepta una o más expresiones seguidas
        while not self.verificar(TipoToken.FINAL, TipoToken.SINO, TipoToken.ADEMAS,
                                   TipoToken.CUANDO, TipoToken.MIENTRAS, TipoToken.REPETIR,
                                   TipoToken.RECORRER, TipoToken.GUARDAR, TipoToken.CONSTANTE,
                                   TipoToken.MOSTRAR, TipoToken.CREAR, TipoToken.RETORNAR,
                                   TipoToken.INVOCAR, TipoToken.INTENTAR, TipoToken.LANZAR,
                                   TipoToken.AGREGAR, TipoToken.REMOVER, TipoToken.IMPORTAR,
                                   TipoToken.EXPORTAR, TipoToken.DETENER, TipoToken.CONTINUAR,
                                   TipoToken.INDENTACION, TipoToken.DEDENTACION,
                                   TipoToken.CAPTURAR_ERROR, TipoToken.SIEMPRE, TipoToken.EOF):
            expresiones.append(self.parsear_expresion())

        return Mostrar(expresiones, linea)

    # ------------------------------------------------------------------
    # Condicionales
    # ------------------------------------------------------------------

    def parsear_cuando(self):
        linea = self.linea_actual()
        ramas = []

        self.consumir(TipoToken.CUANDO)
        condicion = self.parsear_expresion()
        self.saltar_indentacion()
        cuerpo = self.parsear_bloque()
        ramas.append((condicion, cuerpo))

        # ademas ... (else if)
        while self.verificar(TipoToken.ADEMAS):
            self.avanzar()
            cond_extra = self.parsear_expresion()
            self.saltar_indentacion()
            cuerpo_extra = self.parsear_bloque()
            ramas.append((cond_extra, cuerpo_extra))

        # sino (else)
        rama_sino = None
        if self.verificar(TipoToken.SINO):
            self.avanzar()
            self.saltar_indentacion()
            rama_sino = self.parsear_bloque()

        self.consumir(TipoToken.FINAL)
        return Cuando(ramas, rama_sino, linea)

    # ------------------------------------------------------------------
    # Bucles
    # ------------------------------------------------------------------

    def parsear_mientras(self):
        linea = self.linea_actual()
        self.consumir(TipoToken.MIENTRAS)
        condicion = self.parsear_expresion()
        self.saltar_indentacion()
        cuerpo = self.parsear_bloque()
        self.consumir(TipoToken.FINAL)
        return Mientras(condicion, cuerpo, linea)

    def parsear_repetir(self):
        linea = self.linea_actual()
        self.consumir(TipoToken.REPETIR)
        self.saltar_indentacion()
        cuerpo = self.parsear_bloque()
        self.consumir(TipoToken.FINAL)
        return Repetir(cuerpo, linea)

    def parsear_recorrer(self):
        linea = self.linea_actual()
        self.consumir(TipoToken.RECORRER)
        variable = self.consumir(TipoToken.IDENTIFICADOR).valor
        self.consumir(TipoToken.EN)
        iterable = self.parsear_expresion()
        self.saltar_indentacion()
        cuerpo = self.parsear_bloque()
        self.consumir(TipoToken.FINAL)
        return Recorrer(variable, iterable, cuerpo, linea)

    # ------------------------------------------------------------------
    # Funciones
    # ------------------------------------------------------------------

    def parsear_funcion(self):
        linea = self.linea_actual()
        self.consumir(TipoToken.CREAR)
        self.consumir(TipoToken.FUNCION)
        nombre = self.consumir(TipoToken.IDENTIFICADOR).valor
        self.consumir(TipoToken.CON)
        self.consumir(TipoToken.PARAMETROS)

        parametros = []
        # Los parámetros son identificadores separados por coma.
        # Si no hay parámetros la línea termina directamente.
        while self.verificar(TipoToken.IDENTIFICADOR):
            parametros.append(self.avanzar().valor)
            if self.verificar(TipoToken.COMA):
                self.avanzar()

        self.saltar_indentacion()
        cuerpo = self.parsear_bloque()
        self.consumir(TipoToken.FINAL)
        return DefinicionFuncion(nombre, parametros, cuerpo, linea)

    def parsear_retornar(self):
        linea = self.linea_actual()
        self.consumir(TipoToken.RETORNAR)
        valores = [self.parsear_expresion()]

        # retornar puede devolver múltiples valores separados por coma
        while self.verificar(TipoToken.COMA):
            self.avanzar()
            valores.append(self.parsear_expresion())

        return Retornar(valores, linea)

    def parsear_invocar_sentencia(self):
        # invocar usado como sentencia (sin asignación)
        linea = self.linea_actual()
        return self._parsear_invocar(linea)

    def _parsear_invocar(self, linea=None):
        if linea is None:
            linea = self.linea_actual()
        self.consumir(TipoToken.INVOCAR)

        nombre = self.consumir(TipoToken.IDENTIFICADOR).valor

        # Llamada a método: invocar objeto.metodo con args
        if self.verificar(TipoToken.PUNTO):
            self.avanzar()
            metodo = self.consumir(TipoToken.IDENTIFICADOR).valor
            argumentos = self._parsear_argumentos()
            return LlamadaMetodo(nombre, metodo, argumentos, linea)

        argumentos = self._parsear_argumentos()
        return LlamadaFuncion(nombre, argumentos, linea)

    def _parsear_argumentos(self):
        argumentos = []
        if self.verificar(TipoToken.CON):
            self.avanzar()
            argumentos.append(self.parsear_expresion())
            while self.verificar(TipoToken.COMA):
                self.avanzar()
                argumentos.append(self.parsear_expresion())
        return argumentos

    # ------------------------------------------------------------------
    # Manejo de errores
    # ------------------------------------------------------------------

    def parsear_intentar(self):
        linea = self.linea_actual()
        self.consumir(TipoToken.INTENTAR)
        self.saltar_indentacion()
        cuerpo = self.parsear_bloque()

        self.consumir(TipoToken.CAPTURAR_ERROR)
        self.consumir(TipoToken.COMO)
        nombre_error = self.consumir(TipoToken.IDENTIFICADOR).valor
        self.saltar_indentacion()
        cuerpo_error = self.parsear_bloque()

        cuerpo_siempre = None
        if self.verificar(TipoToken.SIEMPRE):
            self.avanzar()
            self.saltar_indentacion()
            cuerpo_siempre = self.parsear_bloque()

        self.consumir(TipoToken.FINAL)
        return Intentar(cuerpo, nombre_error, cuerpo_error, cuerpo_siempre, linea)

    def parsear_lanzar(self):
        linea = self.linea_actual()
        self.consumir(TipoToken.LANZAR)
        expresion = self.parsear_expresion()
        return Lanzar(expresion, linea)

    # ------------------------------------------------------------------
    # Colecciones
    # ------------------------------------------------------------------

    def parsear_agregar(self):
        linea = self.linea_actual()
        self.consumir(TipoToken.AGREGAR)
        elemento = self.parsear_expresion()
        # 'a' puede llegar como TipoToken.A o como IDENTIFICADOR con valor 'a'
        tok = self.actual()
        if tok.tipo == TipoToken.A or (tok.tipo == TipoToken.IDENTIFICADOR and tok.valor == 'a'):
            self.avanzar()
        else:
            self.consumir(TipoToken.A, "se esperaba 'a' después del elemento")
        coleccion = self.consumir(TipoToken.IDENTIFICADOR).valor
        return Agregar(elemento, coleccion, linea)

    def parsear_remover(self):
        linea = self.linea_actual()
        self.consumir(TipoToken.REMOVER)
        elemento = self.parsear_expresion()
        self.consumir(TipoToken.DE)
        coleccion = self.consumir(TipoToken.IDENTIFICADOR).valor
        return Remover(elemento, coleccion, linea)

    # ------------------------------------------------------------------
    # Módulos
    # ------------------------------------------------------------------

    def parsear_importar(self):
        linea = self.linea_actual()
        self.consumir(TipoToken.IMPORTAR)

        nombres = []
        if self.verificar(TipoToken.TODO):
            self.avanzar()
            nombres = ['todo']
        else:
            nombres.append(self.consumir(TipoToken.IDENTIFICADOR).valor)
            while self.verificar(TipoToken.COMA):
                self.avanzar()
                nombres.append(self.consumir(TipoToken.IDENTIFICADOR).valor)

        self.consumir(TipoToken.DESDE)
        origen = self.consumir(TipoToken.LITERAL_TEXTO).valor

        alias = None
        if self.verificar(TipoToken.COMO):
            self.avanzar()
            alias = self.consumir(TipoToken.IDENTIFICADOR).valor

        return Importar(nombres, origen, alias, linea)

    def parsear_exportar(self):
        linea = self.linea_actual()
        self.consumir(TipoToken.EXPORTAR)
        nombres = [self.consumir(TipoToken.IDENTIFICADOR).valor]
        while self.verificar(TipoToken.COMA):
            self.avanzar()
            nombres.append(self.consumir(TipoToken.IDENTIFICADOR).valor)
        return Exportar(nombres, linea)

    # ------------------------------------------------------------------
    # Expresiones — precedencia ascendente
    # ------------------------------------------------------------------
    # Nivel 1 (más bajo): lógico  (y_tambien, o_sino)
    # Nivel 2: comparación        (es, no_es, mayor_que, ...)
    # Nivel 3: aditivo            (mas, menos)
    # Nivel 4: multiplicativo     (por, entre, resto)
    # Nivel 5: potencia           (elevado)
    # Nivel 6 (más alto): unario  (negar)
    # Nivel 7: primario           (literales, identificadores, invocar, ...)

    def parsear_expresion(self):
        return self._logico()

    def _logico(self):
        izq = self._comparacion()
        while self.verificar(*_OPS_LOGICOS):
            op = self.avanzar().valor
            der = self._comparacion()
            izq = ExpresionBinaria(izq, op, der, izq.linea)
        return izq

    def _comparacion(self):
        izq = self._aditivo()
        while self.verificar(*_OPS_COMPARACION):
            op = self.avanzar().valor
            der = self._aditivo()
            izq = ExpresionBinaria(izq, op, der, izq.linea)
        return izq

    def _aditivo(self):
        izq = self._multiplicativo()
        while self.verificar(*_OPS_ADITIVOS):
            op = self.avanzar().valor
            der = self._multiplicativo()
            izq = ExpresionBinaria(izq, op, der, izq.linea)
        return izq

    def _multiplicativo(self):
        izq = self._potencia()
        while self.verificar(*_OPS_MULTIPLICATIVOS):
            op = self.avanzar().valor
            der = self._potencia()
            izq = ExpresionBinaria(izq, op, der, izq.linea)
        return izq

    def _potencia(self):
        base = self._unario()
        if self.verificar(*_OPS_POTENCIA):
            op = self.avanzar().valor
            exp = self._potencia()   # asociatividad derecha
            return ExpresionBinaria(base, op, exp, base.linea)
        return base

    def _unario(self):
        if self.verificar(TipoToken.NEGAR):
            linea = self.linea_actual()
            op = self.avanzar().valor
            operando = self._unario()
            return ExpresionUnaria(op, operando, linea)
        return self._primario()

    def _primario(self):
        tok = self.actual()

        # Literales simples
        if tok.tipo == TipoToken.LITERAL_NUMERO:
            self.avanzar()
            return LiteralNumero(tok.valor, tok.linea)

        if tok.tipo == TipoToken.LITERAL_TEXTO:
            self.avanzar()
            return LiteralTexto(tok.valor, tok.linea)

        if tok.tipo == TipoToken.VERDADERO:
            self.avanzar()
            return LiteralLogico(True, tok.linea)

        if tok.tipo == TipoToken.FALSO:
            self.avanzar()
            return LiteralLogico(False, tok.linea)

        if tok.tipo == TipoToken.VACIO:
            self.avanzar()
            return LiteralVacio(tok.linea)

        # Colección literal: [1, 2, 3]
        if tok.tipo == TipoToken.CORCHETE_IZQ:
            return self._literal_coleccion()

        # Diccionario literal: {"clave": valor}
        if tok.tipo == TipoToken.LLAVE_IZQ:
            return self._literal_diccionario()

        # Llamada a función como expresión: invocar nombre con args
        if tok.tipo == TipoToken.INVOCAR:
            return self._parsear_invocar()

        # Capturar entrada del usuario: capturar "mensaje"
        if tok.tipo == TipoToken.CAPTURAR:
            linea = tok.linea
            self.avanzar()
            mensaje = self.parsear_expresion()
            # Representamos capturar como una llamada especial
            return LlamadaFuncion('__capturar__', [mensaje], linea)

        # Identificador: variable, acceso a índice o campo
        if tok.tipo == TipoToken.IDENTIFICADOR:
            self.avanzar()
            nodo = Identificador(tok.valor, tok.linea)

            # acceso a índice: nombre[expr]
            if self.verificar(TipoToken.CORCHETE_IZQ):
                self.avanzar()
                indice = self.parsear_expresion()
                self.consumir(TipoToken.CORCHETE_DER)
                nodo = AccesoIndice(tok.valor, indice, tok.linea)

            # acceso a campo: nombre.campo
            elif self.verificar(TipoToken.PUNTO):
                self.avanzar()
                campo = self.consumir(TipoToken.IDENTIFICADOR).valor
                nodo = AccesoCampo(tok.valor, campo, tok.linea)

            return nodo

        raise ErrorSintactico(
            _fmt_sint(tok.linea, tok.columna,
                      f"expresion inesperada '{tok.valor}'",
                      _sugerir_expresion(tok))
        )

    def _literal_coleccion(self):
        linea = self.linea_actual()
        self.consumir(TipoToken.CORCHETE_IZQ)
        elementos = []

        if not self.verificar(TipoToken.CORCHETE_DER):
            elementos.append(self.parsear_expresion())
            while self.verificar(TipoToken.COMA):
                self.avanzar()
                if self.verificar(TipoToken.CORCHETE_DER):
                    break
                elementos.append(self.parsear_expresion())

        self.consumir(TipoToken.CORCHETE_DER)
        return LiteralColeccion(elementos, linea)

    def _literal_diccionario(self):
        linea = self.linea_actual()
        self.consumir(TipoToken.LLAVE_IZQ)
        pares = []

        if not self.verificar(TipoToken.LLAVE_DER):
            clave = self.parsear_expresion()
            self.consumir(TipoToken.DOS_PUNTOS)
            valor = self.parsear_expresion()
            pares.append((clave, valor))

            while self.verificar(TipoToken.COMA):
                self.avanzar()
                if self.verificar(TipoToken.LLAVE_DER):
                    break
                clave = self.parsear_expresion()
                self.consumir(TipoToken.DOS_PUNTOS)
                valor = self.parsear_expresion()
                pares.append((clave, valor))

        self.consumir(TipoToken.LLAVE_DER)
        return LiteralDiccionario(pares, linea)


# ------------------------------------------------------------------
# Helpers para mensajes de error descriptivos
# ------------------------------------------------------------------

def _nombre_legible(tipo):
    nombres = {
        TipoToken.NUMERO: 'numero', TipoToken.TEXTO: 'texto',
        TipoToken.LOGICO: 'logico', TipoToken.VACIO: 'vacio',
        TipoToken.COLECCION: 'coleccion', TipoToken.DICCIONARIO: 'diccionario',
        TipoToken.IDENTIFICADOR: '<nombre>', TipoToken.LITERAL_NUMERO: '<numero>',
        TipoToken.LITERAL_TEXTO: '<texto>', TipoToken.ES: 'es',
        TipoToken.CON: 'con', TipoToken.FINAL: 'final',
        TipoToken.INICIO: 'inicio', TipoToken.PARAMETROS: 'parametros',
        TipoToken.FUNCION: 'funcion', TipoToken.EN: 'en',
        TipoToken.COMO: 'como', TipoToken.DESDE: 'desde',
    }
    return nombres.get(tipo, tipo.name.lower())


def _mensaje_esperado(tipo, tok):
    """Genera un mensaje de error claro segun el token esperado."""
    esperado = _nombre_legible(tipo)
    encontrado = tok.valor if tok.valor is not None else 'fin de archivo'
    return f"se esperaba '{esperado}' pero se encontro '{encontrado}'"


def _sugerir_sintaxis(tipo_esperado, tok_encontrado):
    """Devuelve una sugerencia especifica segun el contexto del error."""
    val = tok_encontrado.valor

    if tipo_esperado == TipoToken.ES:
        return (
            "la sintaxis correcta es: guardar <nombre> es <tipo> con <valor>\n"
            "  Ejemplo: guardar edad es numero con 25"
        )
    if tipo_esperado == TipoToken.CON:
        return (
            "falta la palabra 'con' antes del valor\n"
            "  Ejemplo: guardar nombre es texto con \"Ana\""
        )
    if tipo_esperado == TipoToken.FINAL:
        return (
            "todo bloque (cuando, mientras, crear funcion, intentar) debe cerrarse con 'final'\n"
            "  Revisa que cada bloque abierto tenga su 'final' correspondiente"
        )
    if tipo_esperado == TipoToken.IDENTIFICADOR:
        if val in ('numero', 'texto', 'logico', 'coleccion', 'diccionario', 'vacio'):
            return (
                f"'{val}' es una palabra reservada de tipo, no puede usarse como nombre de variable.\n"
                f"  Usa un nombre diferente, por ejemplo: mi_{val}, valor_{val}"
            )
        return "se esperaba un nombre de variable o funcion (letras, numeros y guion bajo)"
    if tipo_esperado == TipoToken.PARAMETROS:
        return (
            "la sintaxis para definir una funcion es:\n"
            "  crear funcion <nombre> con parametros <p1>, <p2>\n"
            "  Si no tiene parametros: crear funcion <nombre> con parametros"
        )
    if tipo_esperado == TipoToken.FUNCION:
        return "para definir una funcion: crear funcion <nombre> con parametros ..."
    if tipo_esperado == TipoToken.EN:
        return "la sintaxis del bucle es: recorrer <variable> en <coleccion>"
    if tipo_esperado == TipoToken.COMO:
        return "la sintaxis es: capturar_error como <nombre_variable>"
    if tipo_esperado == TipoToken.DESDE:
        return "la sintaxis es: importar <nombre> desde \"ruta/modulo\""
    return None


def _sugerir_sentencia(valor):
    """Sugerencias cuando se encuentra un token inesperado al inicio de sentencia."""
    sugerencias = {
        'print':   "en CCODE se usa 'mostrar' en lugar de 'print'",
        'var':     "en CCODE se usa 'guardar nombre es tipo con valor'",
        'let':     "en CCODE se usa 'guardar nombre es tipo con valor'",
        'def':     "en CCODE se usa 'crear funcion nombre con parametros ...'",
        'function':"en CCODE se usa 'crear funcion nombre con parametros ...'",
        'if':      "en CCODE se usa 'cuando condicion ... final'",
        'for':     "en CCODE se usa 'recorrer elemento en coleccion ... final'",
        'while':   "en CCODE se usa 'mientras condicion ... final'",
        'return':  "en CCODE se usa 'retornar valor'",
        'break':   "en CCODE se usa 'detener'",
        'continue':"en CCODE se usa 'continuar'",
        'try':     "en CCODE se usa 'intentar ... capturar_error como e ... final'",
        'catch':   "en CCODE se usa 'capturar_error como <nombre>'",
        'throw':   "en CCODE se usa 'lanzar \"mensaje\"'",
        'import':  "en CCODE se usa 'importar nombre desde \"ruta\"'",
    }
    return sugerencias.get(valor)


def _sugerir_expresion(tok):
    """Sugerencias cuando se encuentra un token inesperado en una expresion."""
    if tok.tipo == TipoToken.FINAL:
        return "parece que falta el valor de la expresion antes de 'final'"
    if tok.valor == 'True':
        return "en CCODE el valor verdadero se escribe 'verdadero'"
    if tok.valor == 'False':
        return "en CCODE el valor falso se escribe 'falso'"
    if tok.valor == 'None' or tok.valor == 'null':
        return "en CCODE el valor nulo se escribe 'vacio'"
    if tok.valor == 'and':
        return "en CCODE el operador AND se escribe 'y_tambien'"
    if tok.valor == 'or':
        return "en CCODE el operador OR se escribe 'o_sino'"
    if tok.valor == 'not':
        return "en CCODE el operador NOT se escribe 'negar'"
    return None


# ------------------------------------------------------------------
# Funcion de utilidad
# ------------------------------------------------------------------

def parsear_codigo(tokens):
    p = Parser(tokens)
    return p.parsear()


if __name__ == '__main__':
    import sys
    import os
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'lexer'))
    from tokenizer import tokenizar_codigo

    fuente = '''
inicio programa_principal
    guardar x es numero con 10 mas 5
    guardar nombre es texto con "CCODE"
    mostrar "Resultado:" x
    cuando x mayor_que 10
        mostrar "x es grande"
    sino
        mostrar "x es chico"
    final
final
'''

    try:
        tokens = tokenizar_codigo(fuente)
        ast = parsear_codigo(tokens)
        print("AST generado:")
        for nodo in ast.cuerpo:
            print(' ', nodo)
    except Exception as e:
        print(f"Error: {e}")
