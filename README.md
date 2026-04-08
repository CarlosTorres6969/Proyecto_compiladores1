# CCODE - Lenguaje de Programación

![CCODE Logo]

## 🌟 Descripción

**CCODE** (Arquitectura Unificada de Razonamiento Algorítmico) es un lenguaje de programación completamente original, diseñado desde cero con una filosofía de claridad semántica y expresividad natural.

### Características Principales

- ✨ **Sintaxis Natural**: Palabras reservadas completamente originales
- 🔒 **Seguridad por Diseño**: Manejo explícito de errores
- 🚀 **Híbrido**: Compilado a bytecode y ejecutado en VM
- 📚 **Expresivo**: Código que se lee como narrativa
- 🎯 **Minimalista**: Menos símbolos, más claridad

## 📦 Instalación

```bash
# Clonar el repositorio
git clone https://github.com/CCODE-lang/CCODE.git
cd CCODE

# Instalar dependencias (Python 3.8+)
pip install -r requirements.txt

# Ejecutar un programa
python src/cli/main.py ejecutar ejemplos/hola_mundo.CCODE
```

## 🚀 Inicio Rápido

### Hola Mundo

```CCODE
inicio programa_principal
    mostrar "¡Hola Mundo desde CCODE!"
final
```

### Variables y Operaciones

```CCODE
inicio programa_principal
    guardar edad es numero con 25
    guardar nombre es texto con "Ana"
    guardar activo es logico con verdadero
    
    guardar suma es numero con 10 mas 5
    mostrar "Resultado:" suma
final
```

### Condicionales

```CCODE
inicio programa_principal
    guardar edad es numero con 18
    
    cuando edad mayor_o_igual 18
        mostrar "Eres mayor de edad"
    sino
        mostrar "Eres menor de edad"
    final
final
```

### Bucles

```CCODE
inicio programa_principal
    guardar contador es numero con 0
    
    mientras contador menor_que 5
        mostrar "Contador:" contador
        guardar contador es numero con contador mas 1
    final
final
```

### Funciones

```CCODE
crear funcion saludar con parametros nombre
    mostrar "Hola" nombre
final

inicio programa_principal
    invocar saludar con "Carlos"
final
```

## 📖 Documentación

La documentación completa está disponible en:

- [Manual Completo](LENGUAJE_CCODE.md) - Especificación completa del lenguaje
- [Ejemplos](ejemplos/) - Programas de ejemplo
- [Guía de Implementación](docs/implementacion.md) - Cómo funciona internamente

## 🎯 Palabras Reservadas

CCODE utiliza palabras completamente originales:

| Categoría | Palabras |
|-----------|----------|
| **Estructura** | `inicio`, `final`, `guardar`, `constante` |
| **E/S** | `mostrar`, `capturar` |
| **Control** | `cuando`, `sino`, `ademas`, `mientras`, `repetir` |
| **Funciones** | `crear`, `retornar`, `invocar` |
| **Tipos** | `numero`, `texto`, `logico`, `coleccion`, `diccionario` |
| **Operadores** | `mas`, `menos`, `por`, `entre`, `resto`, `elevado` |
| **Lógicos** | `es`, `no_es`, `mayor_que`, `menor_que`, `y_tambien`, `o_sino` |
| **Valores** | `verdadero`, `falso`, `vacio` |

## 📂 Estructura del Proyecto

```
CCODE/
├── src/
│   ├── lexer/          # Análisis léxico
│   ├── parser/         # Análisis sintáctico
│   ├── compiler/       # Compilador a bytecode
│   ├── vm/             # Máquina virtual
│   └── cli/            # Interfaz de línea de comandos
├── ejemplos/           # Programas de ejemplo
├── tests/              # Tests unitarios
├── docs/               # Documentación
└── stdlib/             # Biblioteca estándar
```

## 🛠️ Comandos

```bash
# Ejecutar un programa
CCODE ejecutar programa.CCODE

# Compilar a bytecode
CCODE compilar programa.CCODE -o programa.CCODEc

# Modo interactivo (REPL)
CCODE interactivo

# Ver versión
CCODE version

# Ayuda
CCODE ayuda
```

## 🎓 Ejemplos

### Calculadora

```CCODE
inicio programa_principal
    guardar num1 es numero con capturar "Primer número: "
    guardar num2 es numero con capturar "Segundo número: "
    
    guardar suma es numero con num1 mas num2
    guardar resta es numero con num1 menos num2
    
    mostrar "Suma:" suma
    mostrar "Resta:" resta
final
```

### Fibonacci

```CCODE
crear funcion fibonacci con parametros n
    cuando n menor_o_igual 1
        retornar n
    final
    
    guardar a es numero con 0
    guardar b es numero con 1
    guardar i es numero con 2
    
    mientras i menor_o_igual n
        guardar temp es numero con a mas b
        guardar a es numero con b
        guardar b es numero con temp
        guardar i es numero con i mas 1
    final
    
    retornar b
final

inicio programa_principal
    guardar resultado es numero con invocar fibonacci con 10
    mostrar "Fibonacci(10):" resultado
final
```

## 🤝 Contribuir

¡Las contribuciones son bienvenidas! Por favor:

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📝 Licencia

Este proyecto está bajo la Licencia MIT. Ver el archivo `LICENSE` para más detalles.

## 👥 Autores

- Diego Alejandro Mejía
- Yeison Roney Blanco
- Carlos Castro Palacios
- Carlos Maynor Romero
- José Carlos Torres 
UNAH- CURC    IS


                    

                            
