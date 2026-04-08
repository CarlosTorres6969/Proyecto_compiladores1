# Nodos del árbol sintáctico abstracto para CCODE.
# Cada clase representa una construcción del lenguaje.

class Nodo:
    def __repr__(self):
        campos = ', '.join(f'{k}={v!r}' for k, v in self.__dict__.items())
        return f'{self.__class__.__name__}({campos})'


# --- Raíz ---

class Programa(Nodo):
    def __init__(self, nombre, cuerpo):
        self.nombre = nombre    # nombre del bloque principal
        self.cuerpo = cuerpo    # lista de sentencias


# --- Declaraciones ---

class DeclaracionVariable(Nodo):
    def __init__(self, nombre, tipo, valor, linea):
        self.nombre = nombre
        self.tipo = tipo        # 'numero', 'texto', etc.
        self.valor = valor      # expresión
        self.linea = linea

class DeclaracionConstante(Nodo):
    def __init__(self, nombre, tipo, valor, linea):
        self.nombre = nombre
        self.tipo = tipo
        self.valor = valor
        self.linea = linea

class AsignacionIndice(Nodo):
    # guardar coleccion[indice] es tipo con valor
    def __init__(self, nombre, indice, tipo, valor, linea):
        self.nombre = nombre
        self.indice = indice
        self.tipo = tipo
        self.valor = valor
        self.linea = linea


# --- Funciones ---

class DefinicionFuncion(Nodo):
    def __init__(self, nombre, parametros, cuerpo, linea):
        self.nombre = nombre
        self.parametros = parametros    # lista de strings
        self.cuerpo = cuerpo
        self.linea = linea

class Retornar(Nodo):
    def __init__(self, valores, linea):
        self.valores = valores  # lista de expresiones (puede ser múltiple)
        self.linea = linea

class LlamadaFuncion(Nodo):
    def __init__(self, nombre, argumentos, linea):
        self.nombre = nombre
        self.argumentos = argumentos
        self.linea = linea

class LlamadaMetodo(Nodo):
    # invocar objeto.metodo con args
    def __init__(self, objeto, metodo, argumentos, linea):
        self.objeto = objeto
        self.metodo = metodo
        self.argumentos = argumentos
        self.linea = linea


# --- Control de flujo ---

class Cuando(Nodo):
    # cuando ... / ademas ... / sino
    def __init__(self, ramas, rama_sino, linea):
        self.ramas = ramas          # lista de (condicion, cuerpo)
        self.rama_sino = rama_sino  # cuerpo o None
        self.linea = linea

class Mientras(Nodo):
    def __init__(self, condicion, cuerpo, linea):
        self.condicion = condicion
        self.cuerpo = cuerpo
        self.linea = linea

class Repetir(Nodo):
    def __init__(self, cuerpo, linea):
        self.cuerpo = cuerpo
        self.linea = linea

class Recorrer(Nodo):
    def __init__(self, variable, iterable, cuerpo, linea):
        self.variable = variable    # nombre de la variable de iteración
        self.iterable = iterable    # expresión
        self.cuerpo = cuerpo
        self.linea = linea

class Detener(Nodo):
    def __init__(self, linea):
        self.linea = linea

class Continuar(Nodo):
    def __init__(self, linea):
        self.linea = linea


# --- Entrada / Salida ---

class Mostrar(Nodo):
    def __init__(self, expresiones, linea):
        self.expresiones = expresiones  # lista de expresiones
        self.linea = linea


# --- Manejo de errores ---

class Intentar(Nodo):
    def __init__(self, cuerpo, nombre_error, cuerpo_error, cuerpo_siempre, linea):
        self.cuerpo = cuerpo
        self.nombre_error = nombre_error        # variable que recibe el error
        self.cuerpo_error = cuerpo_error
        self.cuerpo_siempre = cuerpo_siempre    # puede ser None
        self.linea = linea

class Lanzar(Nodo):
    def __init__(self, expresion, linea):
        self.expresion = expresion
        self.linea = linea


# --- Colecciones ---

class Agregar(Nodo):
    def __init__(self, elemento, coleccion, linea):
        self.elemento = elemento
        self.coleccion = coleccion
        self.linea = linea

class Remover(Nodo):
    def __init__(self, elemento, coleccion, linea):
        self.elemento = elemento
        self.coleccion = coleccion
        self.linea = linea


# --- Módulos ---

class Importar(Nodo):
    def __init__(self, nombres, origen, alias, linea):
        self.nombres = nombres  # lista de nombres o ['todo']
        self.origen = origen    # ruta del módulo
        self.alias = alias      # alias opcional (como X)
        self.linea = linea

class Exportar(Nodo):
    def __init__(self, nombres, linea):
        self.nombres = nombres
        self.linea = linea


# --- Expresiones ---

class ExpresionBinaria(Nodo):
    def __init__(self, izquierda, operador, derecha, linea):
        self.izquierda = izquierda
        self.operador = operador    # string: 'mas', 'menos', 'es', etc.
        self.derecha = derecha
        self.linea = linea

class ExpresionUnaria(Nodo):
    def __init__(self, operador, operando, linea):
        self.operador = operador    # 'negar'
        self.operando = operando
        self.linea = linea

class AccesoIndice(Nodo):
    def __init__(self, nombre, indice, linea):
        self.nombre = nombre
        self.indice = indice
        self.linea = linea

class AccesoCampo(Nodo):
    # objeto.campo
    def __init__(self, objeto, campo, linea):
        self.objeto = objeto
        self.campo = campo
        self.linea = linea


# --- Literales ---

class LiteralNumero(Nodo):
    def __init__(self, valor, linea):
        self.valor = valor
        self.linea = linea

class LiteralTexto(Nodo):
    def __init__(self, valor, linea):
        self.valor = valor
        self.linea = linea

class LiteralLogico(Nodo):
    def __init__(self, valor, linea):
        self.valor = valor  # True o False
        self.linea = linea

class LiteralVacio(Nodo):
    def __init__(self, linea):
        self.linea = linea

class LiteralColeccion(Nodo):
    def __init__(self, elementos, linea):
        self.elementos = elementos
        self.linea = linea

class LiteralDiccionario(Nodo):
    def __init__(self, pares, linea):
        self.pares = pares  # lista de (clave, valor)
        self.linea = linea

class Identificador(Nodo):
    def __init__(self, nombre, linea):
        self.nombre = nombre
        self.linea = linea
