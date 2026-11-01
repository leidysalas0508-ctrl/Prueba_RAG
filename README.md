
# Sistema de preguntas y respuestas sobre documentos PDF utilizando inteligencia artificial

## 1. ¿De qué trata este proyecto?

Este proyecto consiste en una aplicación web que permite subir documentos PDF y hacer preguntas sobre la información que contienen.

Por ejemplo, si una persona sube un documento de varias páginas, no necesita leerlo completamente para encontrar un dato específico. Puede escribir una pregunta y el sistema intenta localizar la información relacionada dentro del PDF.

Para conseguirlo, utilizamos una técnica llamada RAG, que combina la búsqueda de información con un modelo de inteligencia artificial.

Además de mostrar la respuesta, la aplicación indica de qué documento y página se obtuvo la información. También permite visualizar imágenes que fueron extraídas del PDF.

Este sistema fue desarrollado como parte de una prueba técnica para demostrar conocimientos de programación, bases de datos e integración de inteligencia artificial.

## 2. ¿Qué significa RAG?

RAG significa *Retrieval-Augmented Generation*, que en español se puede entender como **generación de respuestas apoyada en la búsqueda de información**.

La idea es sencilla:

Normalmente, cuando hacemos una pregunta a una inteligencia artificial, esta responde utilizando los conocimientos que aprendió durante su entrenamiento.

En un sistema RAG hacemos algo diferente: primero buscamos información dentro de nuestros propios documentos y después se la entregamos a la inteligencia artificial para que responda utilizando ese contenido.

En nuestro proyecto seguimos estos pasos:

1. El usuario sube un PDF.
2. El sistema extrae su contenido.
3. El texto se divide en partes más pequeñas.
4. Esas partes se guardan para poder buscarlas.
5. El usuario escribe una pregunta.
6. El sistema busca las partes del documento más relacionadas con la pregunta.
7. Google Gemini recibe la pregunta y la información encontrada.
8. La aplicación muestra la respuesta y las fuentes utilizadas.

**¿Por qué utilizamos RAG?**

Porque queremos que las respuestas estén relacionadas con los documentos proporcionados por el usuario y no dependan únicamente de lo que la inteligencia artificial sabe de manera general.

Esto ayuda a obtener respuestas más enfocadas, aunque no garantiza que siempre sean correctas.

## 3. Herramientas utilizadas y para qué sirve cada una

### Python

Python es el lenguaje de programación principal del proyecto.

Lo utilizamos para escribir las instrucciones que permiten recibir los PDF, procesar su contenido, realizar búsquedas y comunicarnos con Gemini.

### FastAPI

FastAPI es una herramienta de Python que permite crear una API.

Una API funciona como un medio de comunicación entre dos aplicaciones.

En nuestro caso, cuando el usuario sube un PDF desde la pantalla, la interfaz necesita enviar ese archivo al sistema encargado de procesarlo. FastAPI recibe esa solicitud y coordina el trabajo.

También permite consultar el estado de un documento y enviar preguntas.

### Streamlit

Streamlit es una herramienta que permite crear interfaces web utilizando Python.

La usamos para construir la parte visual de nuestra aplicación.

Gracias a Streamlit, el usuario puede:

- Subir un documento PDF.
- Consultar si el documento terminó de procesarse.
- Escribir preguntas.
- Leer las respuestas.
- Consultar las páginas utilizadas como fuentes.
- Visualizar imágenes extraídas del documento.

Elegimos Streamlit porque permite construir una interfaz sencilla sin desarrollar por separado una aplicación completa con HTML, CSS y JavaScript.

### Google Gemini

Gemini es el servicio de inteligencia artificial de Google que utilizamos en el proyecto.

Cumple dos funciones principales:

**Primera función: generar respuestas.**

Cuando el sistema encuentra información relacionada con una pregunta, se la envía a Gemini para que redacte una respuesta.

**Segunda función: generar embeddings.**

Los embeddings son representaciones numéricas del texto que permiten comparar su significado.

Por ejemplo, las expresiones "cómo instalar el programa" y "pasos para configurar la aplicación" tienen palabras diferentes, pero pueden tratar sobre un tema parecido.

Los embeddings ayudan a encontrar esa relación.

Para utilizar Gemini necesitamos una clave de API, que guardamos en un archivo privado llamado `.env`.

### PyMuPDF

PyMuPDF es una librería que permite trabajar con archivos PDF desde Python.

La utilizamos para abrir los documentos y extraer su texto e imágenes.

También recuperamos información sobre las páginas y la posición de algunos elementos.

Esta es una de las primeras tareas que realiza nuestro sistema cuando se carga un documento.

### ChromaDB

ChromaDB es una base de datos diseñada para guardar y consultar información vectorial.

En una base de datos tradicional podemos buscar registros mediante condiciones, por ejemplo, encontrar un usuario por su identificación.

En una base de datos vectorial podemos buscar fragmentos de texto que tengan un significado parecido a una pregunta.

En nuestro proyecto guardamos los embeddings de los fragmentos del PDF en ChromaDB. Después los utilizamos para buscar información relacionada con las preguntas del usuario.

### BM25

BM25 es un método para buscar información utilizando las palabras de una consulta.

Por ejemplo, si preguntamos por "instalación de Python", BM25 puede identificar fragmentos del documento donde aparezcan esas palabras y darles una puntuación según su relevancia.

Su función es diferente de la búsqueda vectorial:

- BM25 se concentra principalmente en las palabras.
- La búsqueda vectorial intenta encontrar similitud de significado.

### Búsqueda híbrida

La búsqueda híbrida consiste en combinar dos formas de buscar información.

En nuestro proyecto utilizamos BM25 y la búsqueda vectorial de ChromaDB.

Después combinamos sus resultados mediante un método llamado RRF (*Reciprocal Rank Fusion*), que considera las posiciones de los fragmentos en las listas de resultados.

Decidimos utilizar ambas búsquedas porque pueden complementarse: una ayuda a encontrar palabras específicas y la otra a reconocer información relacionada por su significado.

### Pytest

Pytest es una herramienta para realizar pruebas automáticas en Python.

Nos permite comprobar si algunas partes del código funcionan como esperamos.

Por ejemplo, podemos probar la gestión del estado de un documento sin necesidad de ejecutar toda la aplicación.

También podemos simular respuestas de servicios externos para probar nuestra lógica sin hacer llamadas reales a Gemini.

### Docker y Docker Compose

Docker permite ejecutar aplicaciones dentro de contenedores.

Un contenedor reúne el programa y las dependencias necesarias para que pueda funcionar en un entorno preparado.

Docker Compose sirve para configurar y ejecutar varios contenedores juntos.

En nuestro proyecto tenemos una configuración para dos servicios:

- El backend, desarrollado con FastAPI.
- El frontend, desarrollado con Streamlit.

La configuración de Docker está creada, pero todavía está pendiente comprobar que los contenedores se construyan y ejecuten correctamente.

## 4. ¿Cómo funciona nuestra aplicación?

### Primera parte: cargar y procesar el documento

Cuando una persona carga un PDF desde Streamlit, el archivo se envía al backend mediante FastAPI.

El sistema crea un identificador para ese trabajo. Este identificador permite consultar cómo avanza el procesamiento.

Los estados utilizados son:

- Pending: el trabajo está pendiente.
- Processing: el documento se está procesando.
- Completed: el procesamiento terminó correctamente.
- Failed: ocurrió un error.

Mientras se procesa el documento, el sistema utiliza PyMuPDF para extraer el contenido.

Después divide el texto en fragmentos más pequeños.

Esto es importante porque resulta más práctico buscar información dentro de partes de un documento que enviar todas sus páginas a la inteligencia artificial en cada pregunta.

Finalmente, se generan embeddings para esos fragmentos y se almacenan en ChromaDB.

### Segunda parte: hacer una pregunta

Cuando el documento está procesado, el usuario puede escribir una pregunta.

El sistema realiza una búsqueda utilizando BM25 y ChromaDB.

Los resultados se combinan para seleccionar fragmentos relacionados con la pregunta.

Después enviamos esos fragmentos a Gemini junto con instrucciones para responder utilizando la información recuperada.

La aplicación presenta la respuesta y las fuentes correspondientes.

### Tercera parte: mostrar imágenes

Durante el procesamiento también extraemos imágenes del PDF.

Estas imágenes se guardan por separado y pueden consultarse desde la interfaz.

Cuando una respuesta tiene fuentes relacionadas con determinadas páginas, la aplicación puede mostrar imágenes extraídas de esas páginas.

Actualmente, la relación entre las imágenes y las respuestas se basa principalmente en las páginas del documento. No estamos realizando un análisis completo del significado visual de cada imagen.

## 5. Organización del proyecto

El proyecto está organizado principalmente en las siguientes carpetas:

```text
Prueba_RAG/
|
|-- backend/
|   |-- app/
|       |-- main.py
|       |-- services/
|
|-- frontend/
|   |-- app.py
|
|-- tests/
|
|-- Dockerfile
|-- docker-compose.yml
|-- requirements.txt
|-- requirements-docker.txt
|-- .env.example
|-- README.md
```

**Carpeta backend:** contiene la API y los servicios encargados de procesar los documentos, almacenar información y responder preguntas.

**Carpeta frontend:** contiene la interfaz que utiliza la persona para interactuar con el sistema.

**Carpeta tests:** contiene las pruebas automáticas.

**Archivo Dockerfile:** describe cómo preparar la imagen que utiliza la aplicación.

**Archivo docker-compose.yml:** configura los servicios del frontend y el backend para ejecutarlos mediante Docker Compose.

**Archivo requirements.txt:** contiene las dependencias utilizadas en el entorno local de desarrollo.

**Archivo requirements-docker.txt:** contiene las dependencias principales seleccionadas para preparar los contenedores.

**Archivo .env.example:** muestra qué variable debe configurar una persona que quiera ejecutar el proyecto, sin incluir claves privadas.

## 6. ¿Cómo ejecutar el proyecto en un computador?

Para ejecutar el proyecto localmente se necesita Python y una clave de API de Google Gemini.

### Paso 1. Descargar el proyecto

Descargar el código desde el repositorio de GitHub o clonarlo utilizando Git.

### Paso 2. Crear un entorno virtual

El entorno virtual permite instalar las librerías del proyecto de forma separada de otros programas de Python.

En Windows, dentro de la carpeta del proyecto, ejecutar:

```powershell
python -m venv .venv
```

Activarlo:

```powershell
.\.venv\Scripts\Activate.ps1
```

### Paso 3. Instalar las dependencias

```powershell
python -m pip install -r requirements.txt
```

### Paso 4. Configurar Gemini

Crear un archivo llamado `.env` en la carpeta principal.

Agregar la variable:

```dotenv
GEMINI_API_KEY=tu_clave_de_gemini
```

Es necesario reemplazar el valor de ejemplo por una clave propia.

No se debe publicar este archivo en GitHub.

### Paso 5. Ejecutar el backend

En una terminal, ejecutar:

```powershell
python -m uvicorn backend.app.main:aplicacion --reload
```

El backend estará disponible en:

http://localhost:8000

FastAPI también ofrece una página para consultar y probar los endpoints:

http://localhost:8000/docs

### Paso 6. Ejecutar el frontend

Abrir otra terminal y ejecutar:

```powershell
python -m streamlit run frontend/app.py
```

La interfaz estará disponible en:

http://localhost:8501

Es necesario mantener el backend y el frontend en ejecución para utilizar la aplicación.

## 7. Ejecución con Docker Compose

El proyecto incluye archivos de configuración para ejecutar el backend y el frontend mediante contenedores.

Con Docker y Docker Compose instalados, y después de crear el archivo `.env`, el comando previsto es:

```bash
docker compose up --build
```

Este comando indica que Docker debe construir las imágenes necesarias y ejecutar los servicios.

La configuración está preparada, pero todavía no ha sido verificada mediante una ejecución completa en Docker.

## 8. Pruebas realizadas

Se crearon tres pruebas automatizadas utilizando Pytest.

Estas pruebas revisan:

1. El funcionamiento básico del gestor de trabajos.
2. La lógica de integración con Gemini utilizando una respuesta simulada.
3. La búsqueda híbrida utilizando componentes simulados.

Para ejecutarlas:

```powershell
python -m pytest tests -v
```

Durante el desarrollo, las tres pruebas terminaron correctamente.

También realizamos comprobaciones manuales del procesamiento de PDF, las búsquedas y la visualización de imágenes.

Es importante aclarar que tres pruebas no cubren toda la aplicación. Todavía podrían existir errores en situaciones que no hemos probado.

## 9. Dificultades encontradas

Durante el desarrollo aparecieron algunos inconvenientes que nos permitieron aprender sobre la integración de herramientas.

Uno de ellos fue la disponibilidad de Gemini. En algunas consultas el servicio respondió con errores temporales, por lo que incorporamos reintentos para ciertos errores.

También trabajamos en la organización de los documentos y la identificación de fragmentos, para poder relacionar las búsquedas con el archivo seleccionado.

Otra dificultad fue preparar Docker, debido a que nuestro computador de desarrollo no cumple cómodamente con los requisitos para ejecutarlo. Por eso preparamos los archivos de configuración y dejamos pendiente su validación en un entorno compatible.

## 10. Limitaciones del proyecto

Este proyecto es un prototipo funcional desarrollado con fines de evaluación técnica.

Actualmente presenta algunas limitaciones:

- Depende de la disponibilidad del servicio de Gemini para generar respuestas y embeddings.
- La extracción de tablas como estructuras independientes no está implementada completamente.
- Las imágenes se relacionan principalmente con las páginas del PDF, sin interpretar todo su contenido visual.
- El procesamiento de documentos utiliza tareas en segundo plano de FastAPI, no una cola de trabajos distribuida.
- Algunas funcionalidades se han probado manualmente, pero no todas cuentan con pruebas automáticas.
- La ejecución mediante Docker Compose todavía requiere validación.

## 11. Posibles mejoras

En una siguiente versión sería posible:

- Mejorar la extracción de tablas.
- Implementar una cola de trabajos para procesar documentos de manera más robusta.
- Ampliar la cobertura de las pruebas automáticas.
- Agregar límites y validaciones adicionales para los archivos cargados.
- Mejorar la relación entre imágenes y fragmentos de texto.
- Incorporar mecanismos de seguimiento y registro de errores más completos.

## 12. Conclusión

Con este proyecto aprendimos a integrar diferentes herramientas de Python para construir una aplicación que permite consultar información almacenada en documentos PDF.

Uno de los aprendizajes principales fue comprender que un sistema RAG no consiste solamente en enviar preguntas a una inteligencia artificial. También necesita preparar los documentos, almacenar información, buscar contenido relevante y presentar resultados de una manera comprensible.

El proyecto permitió practicar el desarrollo de API, la integración de servicios externos, el manejo de documentos, las búsquedas y las pruebas de software.
