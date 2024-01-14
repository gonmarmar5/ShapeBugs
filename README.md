# ShapeBugs
# Simulación de Agentes en Entorno Bidimensional

Este proyecto implementa un modelo de simulación para estudiar el comportamiento de agentes en un entorno bidimensional con restricciones espaciales. Los agentes se mueven en un mundo de cuadrícula, y la simulación incluye diversas funciones y escenarios para explorar su dinámica.

## Estructura del Proyecto

- `Solver_model.py`: Contiene la implementación del modelo de simulación, incluyendo la lógica de movimiento de los agentes y funciones específicas de manipulación del entorno.
- `gworld.py`: Archivo que define la clase `GridWorld` que representa el mundo de cuadrícula donde se desarrolla la simulación.
- `visualize.py`: Implementa la visualización del entorno y el movimiento de los agentes.
- `macros.py`: Archivo con definiciones de constantes utilizadas en la simulación.

## Instrucciones de Ejecución

1. Asegúrate de tener Python instalado en tu sistema.
2. Ejecuta el archivo `Solver_model.py` para iniciar la simulación.

## Experimentación

La simulación permite llevar a cabo experimentos para explorar el comportamiento de los agentes. Algunos de los experimentos sugeridos incluyen variaciones en el número de agentes, ajustes en la probabilidad de movimiento hacia el objetivo y la observación de cómo la forma central del cuadrado impacta en la distribución de agentes.

## Resultados Imaginarios

En los resultados imaginarios obtenidos, se observó que configuraciones con densidades poblacionales moderadas mostraron una mayor eficiencia en la convergencia hacia posiciones objetivo. Un aumento en la probabilidad de movimiento hacia el objetivo mejoró significativamente la tasa de éxito de los agentes. Las funciones específicas, como `agents_translation` y `agents_death`, tuvieron impactos notables en la dinámica poblacional y la capacidad de los agentes para superar obstáculos.

## Contribuciones

Las contribuciones a este proyecto son bienvenidas. Si encuentras problemas, mejoras o nuevas características, por favor, crea un "issue" o una "pull request" en el repositorio.

## Licencia

Este proyecto está bajo la Licencia MIT. Consulta el archivo `LICENSE` para más detalles.
