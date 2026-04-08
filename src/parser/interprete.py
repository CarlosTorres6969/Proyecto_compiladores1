# Interprete de arbol (tree-walk) para CCODE.
# Recorre el AST y ejecuta cada nodo directamente.

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'lexer'))

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


class ErrorEjecucion(Exception):
    pass


class _Retorno(Exception):
    def __init__(self, valores):
        self.valores = valores


class _Detener(Exception):
    pass


class _Continuar(Exception):
    pass


# ------------------------------------------------------------------
# Entorno (tabla de simbolos)
# ------------------------------------------------------------------

class Entorno:
    def __init__(self, padre=None):
        self.vars = {}
        self.padre = padre

    def definir(self, nombre, valor):
        self.vars[nombre] = valor

    def asignar(self, nombre, valor):
        """Busca la variable hacia arriba y la actualiza donde vive."""
        if nombre in self.vars:
            self.vars[nombre] = valor
        elif self.padre:
            self.padre.asignar(nombre, valor)
        else:
            self.vars[nombre] = valor

    def reasignar(self, nombre, valor):
        """Igual que asignar pero devuelve True si encontró la variable."""
        if nombre in self.vars:
            self.vars[nombre] = valor
            return True
        if self.padre:
            return self.padre.reasignar(nombre, valor)
        return False

    def obtener(self, nombre):
        if nombre in self.vars:
            return self.vars[nombre]
        if self.padre:
            return self.padre.obtener(nombre)
        raise ErrorEjecucion(
            f"la variable '{nombre}' no esta definida.\n"
            f"  Asegurate de declararla antes de usarla con:\n"
            f"  guardar {nombre} es <tipo> con <valor>"
        )


# ------------------------------------------------------------------
# Funcion definida por el usuario
# ------------------------------------------------------------------

class Funcion:
    def __init__(self, nodo, entorno_cierre):
        self.nodo = nodo
        self.entorno_cierre = entorno_cierre

    def __repr__(self):
        return f"<funcion {self.nodo.nombre}>"


# ------------------------------------------------------------------
# Interprete principal
# ------------------------------------------------------------------

class Interprete:
    def __init__(self):
        self.entorno_global = Entorno()

    def ejecutar(self, programa):
        self._exec_bloque(programa.cuerpo, self.entorno_global)

    # ------------------------------------------------------------------
    # Ejecucion de bloques y sentencias
    # ------------------------------------------------------------------

    def _exec_bloque(self, sentencias, entorno):
        for s in sentencias:
            self._exec(s, entorno)

    def _exec(self, nodo, entorno):
        tipo = type(nodo).__name__
        metodo = getattr(self, f'_exec_{tipo}', None)
        if metodo is None:
            raise ErrorEjecucion(f"nodo de ejecucion no soportado: {tipo}")
        return metodo(nodo, entorno)

    def _exec_DeclaracionVariable(self, nodo, entorno):
        valor = self._eval(nodo.valor, entorno)
        valor = self._convertir_tipo(valor, nodo.tipo, nodo.nombre, nodo.linea)
        # Si la variable ya existe en algún entorno padre, la actualiza allí.
        # Si no existe en ningún lado, la crea en el entorno actual.
        if not entorno.reasignar(nodo.nombre, valor):
            entorno.definir(nodo.nombre, valor)

    def _exec_DeclaracionConstante(self, nodo, entorno):
        valor = self._eval(nodo.valor, entorno)
        valor = self._convertir_tipo(valor, nodo.tipo, nodo.nombre, nodo.linea)
        entorno.definir(nodo.nombre, valor)

    def _exec_AsignacionIndice(self, nodo, entorno):
        coleccion = entorno.obtener(nodo.nombre)
        indice = self._eval(nodo.indice, entorno)
        valor = self._eval(nodo.valor, entorno)

        if isinstance(coleccion, list):
            if not isinstance(indice, (int, float)):
                raise ErrorEjecucion(
                    f"el indice de una coleccion debe ser un numero entero, "
                    f"se recibio '{self._str(indice)}' (linea {nodo.linea})"
                )
            idx = int(indice)
            if idx < 0 or idx >= len(coleccion):
                raise ErrorEjecucion(
                    f"indice {idx} fuera de rango en '{nodo.nombre}' "
                    f"(la coleccion tiene {len(coleccion)} elementos, indices validos: 0 a {len(coleccion)-1})"
                    f" (linea {nodo.linea})"
                )
            coleccion[idx] = valor
        elif isinstance(coleccion, dict):
            coleccion[indice] = valor
        else:
            raise ErrorEjecucion(
                f"'{nodo.nombre}' no es una coleccion ni un diccionario, "
                f"no se puede asignar por indice (linea {nodo.linea})"
            )

    def _exec_Mostrar(self, nodo, entorno):
        partes = [self._str(self._eval(e, entorno)) for e in nodo.expresiones]
        print(' '.join(partes))

    def _exec_Cuando(self, nodo, entorno):
        for condicion, cuerpo in nodo.ramas:
            resultado = self._eval(condicion, entorno)
            if not isinstance(resultado, bool):
                raise ErrorEjecucion(
                    f"la condicion de 'cuando' debe ser verdadero o falso, "
                    f"pero se obtuvo '{self._str(resultado)}' (linea {nodo.linea}).\n"
                    f"  Usa operadores de comparacion: es, no_es, mayor_que, menor_que, etc."
                )
            if resultado:
                self._exec_bloque(cuerpo, Entorno(entorno))
                return
        if nodo.rama_sino is not None:
            self._exec_bloque(nodo.rama_sino, Entorno(entorno))

    def _exec_Mientras(self, nodo, entorno):
        iteraciones = 0
        limite = 100_000
        while True:
            resultado = self._eval(nodo.condicion, entorno)
            if not self._verdadero(resultado):
                break
            iteraciones += 1
            if iteraciones > limite:
                raise ErrorEjecucion(
                    f"bucle 'mientras' ejecutado mas de {limite} veces (linea {nodo.linea}).\n"
                    f"  Posible bucle infinito. Revisa que la condicion pueda volverse falsa."
                )
            try:
                self._exec_bloque(nodo.cuerpo, Entorno(entorno))
            except _Detener:
                break
            except _Continuar:
                continue

    def _exec_Repetir(self, nodo, entorno):
        iteraciones = 0
        limite = 100_000
        while True:
            iteraciones += 1
            if iteraciones > limite:
                raise ErrorEjecucion(
                    f"bucle 'repetir' ejecutado mas de {limite} veces (linea {nodo.linea}).\n"
                    f"  Posible bucle infinito. Asegurate de usar 'detener' para salir."
                )
            try:
                self._exec_bloque(nodo.cuerpo, Entorno(entorno))
            except _Detener:
                break
            except _Continuar:
                continue

    def _exec_Recorrer(self, nodo, entorno):
        iterable = self._eval(nodo.iterable, entorno)
        if not isinstance(iterable, (list, str, dict)):
            raise ErrorEjecucion(
                f"'recorrer' requiere una coleccion, texto o diccionario, "
                f"pero '{nodo.variable}' recibio '{self._str(iterable)}' "
                f"de tipo {self._tipo_nombre(iterable)} (linea {nodo.linea})"
            )
        for elemento in iterable:
            sub = Entorno(entorno)
            sub.definir(nodo.variable, elemento)
            try:
                self._exec_bloque(nodo.cuerpo, sub)
            except _Detener:
                break
            except _Continuar:
                continue

    def _exec_Detener(self, nodo, entorno):
        raise _Detener()

    def _exec_Continuar(self, nodo, entorno):
        raise _Continuar()

    def _exec_DefinicionFuncion(self, nodo, entorno):
        entorno.definir(nodo.nombre, Funcion(nodo, entorno))

    def _exec_Retornar(self, nodo, entorno):
        valores = [self._eval(v, entorno) for v in nodo.valores]
        raise _Retorno(valores)

    def _exec_LlamadaFuncion(self, nodo, entorno):
        self._eval(nodo, entorno)

    def _exec_LlamadaMetodo(self, nodo, entorno):
        self._eval(nodo, entorno)

    def _exec_Intentar(self, nodo, entorno):
        try:
            self._exec_bloque(nodo.cuerpo, Entorno(entorno))
        except ErrorEjecucion as e:
            sub = Entorno(entorno)
            sub.definir(nodo.nombre_error, str(e))
            self._exec_bloque(nodo.cuerpo_error, sub)
        except _Retorno:
            raise
        finally:
            if nodo.cuerpo_siempre:
                self._exec_bloque(nodo.cuerpo_siempre, Entorno(entorno))

    def _exec_Lanzar(self, nodo, entorno):
        mensaje = self._eval(nodo.expresion, entorno)
        raise ErrorEjecucion(str(mensaje))

    def _exec_Agregar(self, nodo, entorno):
        elemento = self._eval(nodo.elemento, entorno)
        coleccion = entorno.obtener(nodo.coleccion)
        if not isinstance(coleccion, list):
            raise ErrorEjecucion(
                f"'agregar' solo funciona con colecciones, pero '{nodo.coleccion}' "
                f"es de tipo {self._tipo_nombre(coleccion)} (linea {nodo.linea})"
            )
        coleccion.append(elemento)

    def _exec_Remover(self, nodo, entorno):
        elemento = self._eval(nodo.elemento, entorno)
        coleccion = entorno.obtener(nodo.coleccion)
        if not isinstance(coleccion, list):
            raise ErrorEjecucion(
                f"'remover' solo funciona con colecciones, pero '{nodo.coleccion}' "
                f"es de tipo {self._tipo_nombre(coleccion)} (linea {nodo.linea})"
            )
        if elemento not in coleccion:
            raise ErrorEjecucion(
                f"no se puede remover '{self._str(elemento)}' de '{nodo.coleccion}': "
                f"el elemento no existe en la coleccion (linea {nodo.linea})"
            )
        coleccion.remove(elemento)

    def _exec_Importar(self, nodo, entorno):
        pass

    def _exec_Exportar(self, nodo, entorno):
        pass

    # ------------------------------------------------------------------
    # Evaluacion de expresiones
    # ------------------------------------------------------------------

    def _eval(self, nodo, entorno):
        tipo = type(nodo).__name__
        metodo = getattr(self, f'_eval_{tipo}', None)
        if metodo is None:
            raise ErrorEjecucion(f"expresion no soportada: {tipo}")
        return metodo(nodo, entorno)

    def _eval_LiteralNumero(self, nodo, _):
        return nodo.valor

    def _eval_LiteralTexto(self, nodo, _):
        return nodo.valor

    def _eval_LiteralLogico(self, nodo, _):
        return nodo.valor

    def _eval_LiteralVacio(self, nodo, _):
        return None

    def _eval_LiteralColeccion(self, nodo, entorno):
        return [self._eval(e, entorno) for e in nodo.elementos]

    def _eval_LiteralDiccionario(self, nodo, entorno):
        return {self._eval(k, entorno): self._eval(v, entorno) for k, v in nodo.pares}

    def _eval_Identificador(self, nodo, entorno):
        return entorno.obtener(nodo.nombre)

    def _eval_AccesoIndice(self, nodo, entorno):
        coleccion = entorno.obtener(nodo.nombre)
        indice = self._eval(nodo.indice, entorno)

        if isinstance(coleccion, list):
            if not isinstance(indice, (int, float)):
                raise ErrorEjecucion(
                    f"el indice debe ser un numero entero, "
                    f"se recibio '{self._str(indice)}' (linea {nodo.linea})"
                )
            idx = int(indice)
            largo = len(coleccion)
            if largo == 0:
                raise ErrorEjecucion(
                    f"no se puede acceder a '{nodo.nombre}[{idx}]': la coleccion esta vacia (linea {nodo.linea})"
                )
            if idx < 0 or idx >= largo:
                raise ErrorEjecucion(
                    f"indice {idx} fuera de rango en '{nodo.nombre}' "
                    f"(indices validos: 0 a {largo - 1}) (linea {nodo.linea})"
                )
            return coleccion[idx]

        if isinstance(coleccion, dict):
            if indice not in coleccion:
                claves = ', '.join(repr(k) for k in coleccion.keys())
                raise ErrorEjecucion(
                    f"la clave '{self._str(indice)}' no existe en el diccionario '{nodo.nombre}'.\n"
                    f"  Claves disponibles: {claves} (linea {nodo.linea})"
                )
            return coleccion[indice]

        raise ErrorEjecucion(
            f"'{nodo.nombre}' no es una coleccion ni un diccionario "
            f"(es {self._tipo_nombre(coleccion)}), no se puede acceder por indice (linea {nodo.linea})"
        )

    def _eval_AccesoCampo(self, nodo, entorno):
        obj = entorno.obtener(nodo.objeto)
        if isinstance(obj, dict):
            if nodo.campo not in obj:
                claves = ', '.join(repr(k) for k in obj.keys())
                raise ErrorEjecucion(
                    f"el campo '{nodo.campo}' no existe en '{nodo.objeto}'.\n"
                    f"  Campos disponibles: {claves}"
                )
            return obj[nodo.campo]
        raise ErrorEjecucion(
            f"acceso a campo '.{nodo.campo}' no soportado en '{nodo.objeto}' "
            f"(tipo: {self._tipo_nombre(obj)})"
        )

    def _eval_ExpresionUnaria(self, nodo, entorno):
        val = self._eval(nodo.operando, entorno)
        if nodo.operador == 'negar':
            if not isinstance(val, bool):
                raise ErrorEjecucion(
                    f"'negar' solo aplica a valores logicos (verdadero/falso), "
                    f"se recibio '{self._str(val)}' de tipo {self._tipo_nombre(val)} (linea {nodo.linea})"
                )
            return not val
        raise ErrorEjecucion(f"operador unario desconocido: '{nodo.operador}'")

    def _eval_ExpresionBinaria(self, nodo, entorno):
        izq = self._eval(nodo.izquierda, entorno)
        der = self._eval(nodo.derecha, entorno)
        op  = nodo.operador
        lin = nodo.linea

        # --- operadores aritmeticos ---
        if op == 'mas':
            if isinstance(izq, str) or isinstance(der, str):
                # concatenacion de texto
                return self._str(izq) + self._str(der)
            self._verificar_numericos(izq, der, op, lin)
            return izq + der

        if op == 'menos':
            self._verificar_numericos(izq, der, op, lin)
            return izq - der

        if op == 'por':
            self._verificar_numericos(izq, der, op, lin)
            return izq * der

        if op == 'entre':
            self._verificar_numericos(izq, der, op, lin)
            if der == 0:
                raise ErrorEjecucion(
                    f"division por cero en linea {lin}.\n"
                    f"  El divisor '{self._str(der)}' no puede ser cero."
                )
            resultado = izq / der
            # si ambos son enteros y el resultado es exacto, devolver entero
            if isinstance(izq, int) and isinstance(der, int) and resultado == int(resultado):
                return int(resultado)
            return resultado

        if op == 'resto':
            self._verificar_numericos(izq, der, op, lin)
            if der == 0:
                raise ErrorEjecucion(
                    f"modulo por cero en linea {lin}.\n"
                    f"  El divisor del operador 'resto' no puede ser cero."
                )
            return izq % der

        if op == 'elevado':
            self._verificar_numericos(izq, der, op, lin)
            try:
                resultado = izq ** der
            except OverflowError:
                raise ErrorEjecucion(
                    f"resultado de '{self._str(izq)} elevado {self._str(der)}' "
                    f"es demasiado grande (linea {lin})"
                )
            return resultado

        # --- operadores de comparacion ---
        if op == 'es':
            return izq == der

        if op == 'no_es':
            return izq != der

        if op in ('mayor_que', 'menor_que', 'mayor_o_igual', 'menor_o_igual'):
            if type(izq) != type(der) and not (
                isinstance(izq, (int, float)) and isinstance(der, (int, float))
            ):
                raise ErrorEjecucion(
                    f"no se puede comparar '{self._str(izq)}' ({self._tipo_nombre(izq)}) "
                    f"con '{self._str(der)}' ({self._tipo_nombre(der)}) "
                    f"usando '{op}' (linea {lin})"
                )
            if op == 'mayor_que':
                return izq > der
            if op == 'menor_que':
                return izq < der
            if op == 'mayor_o_igual':
                return izq >= der
            if op == 'menor_o_igual':
                return izq <= der

        # --- operadores logicos ---
        if op == 'y_tambien':
            if not isinstance(izq, bool) or not isinstance(der, bool):
                raise ErrorEjecucion(
                    f"'y_tambien' requiere valores logicos (verdadero/falso) en ambos lados.\n"
                    f"  Izquierda: '{self._str(izq)}' ({self._tipo_nombre(izq)})\n"
                    f"  Derecha:   '{self._str(der)}' ({self._tipo_nombre(der)}) (linea {lin})"
                )
            return izq and der

        if op == 'o_sino':
            if not isinstance(izq, bool) or not isinstance(der, bool):
                raise ErrorEjecucion(
                    f"'o_sino' requiere valores logicos (verdadero/falso) en ambos lados.\n"
                    f"  Izquierda: '{self._str(izq)}' ({self._tipo_nombre(izq)})\n"
                    f"  Derecha:   '{self._str(der)}' ({self._tipo_nombre(der)}) (linea {lin})"
                )
            return izq or der

        raise ErrorEjecucion(f"operador desconocido: '{op}' (linea {lin})")

    def _eval_LlamadaFuncion(self, nodo, entorno):
        # builtin: capturar entrada del usuario
        if nodo.nombre == '__capturar__':
            return self._builtin_capturar(nodo, entorno)

        try:
            funcion = entorno.obtener(nodo.nombre)
        except ErrorEjecucion:
            raise ErrorEjecucion(
                f"la funcion '{nodo.nombre}' no esta definida (linea {nodo.linea}).\n"
                f"  Asegurate de definirla con: crear funcion {nodo.nombre} con parametros ..."
            )

        if not isinstance(funcion, Funcion):
            raise ErrorEjecucion(
                f"'{nodo.nombre}' no es una funcion, es {self._tipo_nombre(funcion)} (linea {nodo.linea})"
            )

        args = [self._eval(a, entorno) for a in nodo.argumentos]
        return self._llamar_funcion(funcion, args, nodo.linea)

    def _eval_LlamadaMetodo(self, nodo, entorno):
        obj = entorno.obtener(nodo.objeto)
        args = [self._eval(a, entorno) for a in nodo.argumentos]

        if isinstance(obj, dict):
            if nodo.metodo == 'obtener':
                if not args:
                    raise ErrorEjecucion(
                        f"'obtener' requiere una clave como argumento (linea {nodo.linea})"
                    )
                return obj.get(args[0])
            raise ErrorEjecucion(
                f"el diccionario no tiene el metodo '{nodo.metodo}' (linea {nodo.linea}).\n"
                f"  Metodos disponibles: obtener"
            )

        raise ErrorEjecucion(
            f"metodo '{nodo.metodo}' no soportado en tipo {self._tipo_nombre(obj)} (linea {nodo.linea})"
        )

    def _llamar_funcion(self, funcion, args, linea=None):
        nodo = funcion.nodo
        esperados = len(nodo.parametros)
        recibidos = len(args)
        if esperados != recibidos:
            raise ErrorEjecucion(
                f"la funcion '{nodo.nombre}' espera {esperados} argumento(s) "
                f"pero se enviaron {recibidos}"
                + (f" (linea {linea})" if linea else "") + ".\n"
                f"  Parametros: {', '.join(nodo.parametros) if nodo.parametros else '(ninguno)'}"
            )
        sub = Entorno(funcion.entorno_cierre)
        for param, val in zip(nodo.parametros, args):
            sub.definir(param, val)
        try:
            self._exec_bloque(nodo.cuerpo, sub)
        except _Retorno as r:
            return r.valores[0] if len(r.valores) == 1 else tuple(r.valores)
        return None

    # ------------------------------------------------------------------
    # Builtin: capturar
    # ------------------------------------------------------------------

    def _builtin_capturar(self, nodo, entorno):
        mensaje = self._eval(nodo.argumentos[0], entorno) if nodo.argumentos else ''
        try:
            entrada = input(str(mensaje))
        except EOFError:
            return ''

        # intentar convertir a numero
        entrada = entrada.strip()
        try:
            return int(entrada)
        except ValueError:
            pass
        try:
            return float(entrada)
        except ValueError:
            pass
        return entrada

    # ------------------------------------------------------------------
    # Conversion de tipos
    # ------------------------------------------------------------------

    def _convertir_tipo(self, valor, tipo_declarado, nombre, linea):
        """Verifica y convierte el valor al tipo declarado."""
        if tipo_declarado == 'numero':
            if isinstance(valor, bool):
                raise ErrorEjecucion(
                    f"no se puede asignar un valor logico a la variable '{nombre}' de tipo numero (linea {linea})"
                )
            if not isinstance(valor, (int, float)):
                try:
                    return float(valor) if '.' in str(valor) else int(valor)
                except (ValueError, TypeError):
                    raise ErrorEjecucion(
                        f"no se puede convertir '{self._str(valor)}' a numero "
                        f"para la variable '{nombre}' (linea {linea})"
                    )
            return valor

        if tipo_declarado == 'texto':
            if not isinstance(valor, str):
                return self._str(valor)
            return valor

        if tipo_declarado == 'logico':
            if not isinstance(valor, bool):
                raise ErrorEjecucion(
                    f"la variable '{nombre}' es de tipo logico pero se asigno "
                    f"'{self._str(valor)}' ({self._tipo_nombre(valor)}) (linea {linea}).\n"
                    f"  Solo se aceptan: verdadero, falso"
                )
            return valor

        if tipo_declarado == 'coleccion':
            if not isinstance(valor, list):
                raise ErrorEjecucion(
                    f"la variable '{nombre}' es de tipo coleccion pero se asigno "
                    f"'{self._str(valor)}' ({self._tipo_nombre(valor)}) (linea {linea})"
                )
            return valor

        if tipo_declarado == 'diccionario':
            if not isinstance(valor, dict):
                raise ErrorEjecucion(
                    f"la variable '{nombre}' es de tipo diccionario pero se asigno "
                    f"'{self._str(valor)}' ({self._tipo_nombre(valor)}) (linea {linea})"
                )
            return valor

        # vacio: acepta cualquier cosa
        return valor

    # ------------------------------------------------------------------
    # Utilidades
    # ------------------------------------------------------------------

    def _verificar_numericos(self, izq, der, op, linea):
        if not isinstance(izq, (int, float)) or isinstance(izq, bool):
            raise ErrorEjecucion(
                f"el operador '{op}' requiere numeros, pero el lado izquierdo es "
                f"'{self._str(izq)}' ({self._tipo_nombre(izq)}) (linea {linea})"
            )
        if not isinstance(der, (int, float)) or isinstance(der, bool):
            raise ErrorEjecucion(
                f"el operador '{op}' requiere numeros, pero el lado derecho es "
                f"'{self._str(der)}' ({self._tipo_nombre(der)}) (linea {linea})"
            )

    def _verdadero(self, valor):
        if valor is None:
            return False
        if isinstance(valor, bool):
            return valor
        if isinstance(valor, (int, float)):
            return valor != 0
        if isinstance(valor, str):
            return len(valor) > 0
        if isinstance(valor, (list, dict)):
            return len(valor) > 0
        return True

    def _tipo_nombre(self, valor):
        if valor is None:
            return 'vacio'
        if isinstance(valor, bool):
            return 'logico'
        if isinstance(valor, (int, float)):
            return 'numero'
        if isinstance(valor, str):
            return 'texto'
        if isinstance(valor, list):
            return 'coleccion'
        if isinstance(valor, dict):
            return 'diccionario'
        if isinstance(valor, Funcion):
            return 'funcion'
        return type(valor).__name__

    def _str(self, valor):
        if valor is None:
            return 'vacio'
        if isinstance(valor, bool):
            return 'verdadero' if valor else 'falso'
        if isinstance(valor, float):
            if valor == int(valor):
                return str(int(valor))
            # máximo 10 decimales significativos, sin ceros finales
            return f"{valor:.10g}"
        return str(valor)
