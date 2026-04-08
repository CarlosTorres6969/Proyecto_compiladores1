"""
Tipos de tokens para el lenguaje CCODE
"""

from enum import Enum, auto

class TipoToken(Enum):
    # Palabras reservadas
    INICIO = auto()
    FINAL = auto()
    GUARDAR = auto()
    CONSTANTE = auto()
    MOSTRAR = auto()
    CAPTURAR = auto()
    CUANDO = auto()
    SINO = auto()
    ADEMAS = auto()
    REPETIR = auto()
    MIENTRAS = auto()
    RECORRER = auto()
    DETENER = auto()
    CONTINUAR = auto()
    CREAR = auto()
    RETORNAR = auto()
    INVOCAR = auto()
    
    # Tipos de datos
    NUMERO = auto()
    TEXTO = auto()
    LOGICO = auto()
    VACIO = auto()
    COLECCION = auto()
    DICCIONARIO = auto()
    
    # Valores literales
    VERDADERO = auto()
    FALSO = auto()
    
    # Operadores
    ES = auto()
    NO_ES = auto()
    CON = auto()
    MAS = auto()
    MENOS = auto()
    POR = auto()
    ENTRE = auto()
    RESTO = auto()
    ELEVADO = auto()
    MAYOR_QUE = auto()
    MENOR_QUE = auto()
    MAYOR_O_IGUAL = auto()
    MENOR_O_IGUAL = auto()
    Y_TAMBIEN = auto()
    O_SINO = auto()
    NEGAR = auto()
    
    # Estructuras
    AGREGAR = auto()
    REMOVER = auto()
    EN = auto()
    A = auto()
    DE = auto()
    DESDE = auto()
    
    # Manejo de errores
    INTENTAR = auto()
    CAPTURAR_ERROR = auto()
    SIEMPRE = auto()
    LANZAR = auto()
    COMO = auto()
    
    # Módulos
    IMPORTAR = auto()
    EXPORTAR = auto()
    TODO = auto()
    
    # Funciones
    FUNCION = auto()
    PARAMETROS = auto()
    
    # Literales
    LITERAL_NUMERO = auto()
    LITERAL_TEXTO = auto()
    IDENTIFICADOR = auto()
    
    # Delimitadores
    NUEVA_LINEA = auto()
    INDENTACION = auto()
    DEDENTACION = auto()
    CORCHETE_IZQ = auto()
    CORCHETE_DER = auto()
    LLAVE_IZQ = auto()
    LLAVE_DER = auto()
    COMA = auto()
    DOS_PUNTOS = auto()
    PUNTO = auto()
    
    # Especiales
    EOF = auto()
    COMENTARIO = auto()


class Token:
    """Representa un token del lenguaje"""
    
    def __init__(self, tipo, valor, linea, columna):
        self.tipo = tipo
        self.valor = valor
        self.linea = linea
        self.columna = columna
    
    def __repr__(self):
        return f"Token({self.tipo}, {self.valor!r}, L{self.linea}:C{self.columna})"
    
    def __str__(self):
        return self.__repr__()


# Mapeo de palabras reservadas
PALABRAS_RESERVADAS = {
    'inicio': TipoToken.INICIO,
    'final': TipoToken.FINAL,
    'guardar': TipoToken.GUARDAR,
    'constante': TipoToken.CONSTANTE,
    'mostrar': TipoToken.MOSTRAR,
    'capturar': TipoToken.CAPTURAR,
    'cuando': TipoToken.CUANDO,
    'sino': TipoToken.SINO,
    'ademas': TipoToken.ADEMAS,
    'repetir': TipoToken.REPETIR,
    'mientras': TipoToken.MIENTRAS,
    'recorrer': TipoToken.RECORRER,
    'detener': TipoToken.DETENER,
    'continuar': TipoToken.CONTINUAR,
    'crear': TipoToken.CREAR,
    'retornar': TipoToken.RETORNAR,
    'invocar': TipoToken.INVOCAR,
    'numero': TipoToken.NUMERO,
    'texto': TipoToken.TEXTO,
    'logico': TipoToken.LOGICO,
    'vacio': TipoToken.VACIO,
    'coleccion': TipoToken.COLECCION,
    'diccionario': TipoToken.DICCIONARIO,
    'verdadero': TipoToken.VERDADERO,
    'falso': TipoToken.FALSO,
    'es': TipoToken.ES,
    'no_es': TipoToken.NO_ES,
    'con': TipoToken.CON,
    'mas': TipoToken.MAS,
    'menos': TipoToken.MENOS,
    'por': TipoToken.POR,
    'entre': TipoToken.ENTRE,
    'resto': TipoToken.RESTO,
    'elevado': TipoToken.ELEVADO,
    'mayor_que': TipoToken.MAYOR_QUE,
    'menor_que': TipoToken.MENOR_QUE,
    'mayor_o_igual': TipoToken.MAYOR_O_IGUAL,
    'menor_o_igual': TipoToken.MENOR_O_IGUAL,
    'y_tambien': TipoToken.Y_TAMBIEN,
    'o_sino': TipoToken.O_SINO,
    'negar': TipoToken.NEGAR,
    'agregar': TipoToken.AGREGAR,
    'remover': TipoToken.REMOVER,
    'en': TipoToken.EN,
    # 'a' y 'de' se resuelven contextualmente en el parser
    # para no colisionar con nombres de variables de una sola letra
    'de': TipoToken.DE,
    'desde': TipoToken.DESDE,
    'intentar': TipoToken.INTENTAR,
    'capturar_error': TipoToken.CAPTURAR_ERROR,
    'siempre': TipoToken.SIEMPRE,
    'lanzar': TipoToken.LANZAR,
    'como': TipoToken.COMO,
    'importar': TipoToken.IMPORTAR,
    'exportar': TipoToken.EXPORTAR,
    'todo': TipoToken.TODO,
    'funcion': TipoToken.FUNCION,
    'parametros': TipoToken.PARAMETROS,
}
