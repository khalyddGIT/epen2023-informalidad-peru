# ARQUITECTURA Y TECNOLOGÍAS DEL SISTEMA (EPEN 2023 - INEI)

**INSTITUCIÓN:** Escuela de Educación Superior Tecnológica La Pontificia  
**CARRERA:** Ingeniería de Sistemas de Información  
**ASIGNATURA:** Modelamiento de Base de Datos / Big Data  
**DOCUMENTO:** Especificación Técnica de Arquitectura y Stack Tecnológico  

---

## 📌 1. Visión General de la Arquitectura

El sistema implementa una **Arquitectura de Ingeniería de Datos e Inteligencia de Negocios End-to-End** dividida en 4 capas secuenciales e independientes. Su propósito es la ingesta, limpieza, normalización en **Tercera Forma Normal (3FN)**, almacenamiento relacional, exposición mediante servicios REST y visualización web interactiva de los microdatos de la **Encuesta Permanente de Empleo Nacional (EPEN 2023 - INEI)**.

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                    CAPA 1: INGESTIÓN Y PIPELINE ETL (PYTHON)                    │
│  - Dataset Primario CSV (INEI: 449,202 filas x 132 columnas / 114.6 MB)         │
│  - Limpieza, Chunking y Filtro Muestral (RESIDENT == 1 -> 417,551 válidos)      │
│  - Desacoplamiento y Normalización a Tercera Forma Normal (3FN)                 │
└────────────────────────────────────────┬────────────────────────────────────────┘
                                         │ (Exportación a /processed_tables/)
                                         ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│               CAPA 2: ALMACENAMIENTO RELACIONAL 3FN (POSTGRESQL)                │
│  - Modelo Dimensional Estrella (1 Tabla de Hechos + 3 Tablas de Dimensión)      │
│  - Fact_Empleo (417,551 reg.), Dim_Departamento, Dim_Demografia, Dim_Condicion  │
│  - 4 Índices B-Tree, 2 Vistas Analíticas de Alta Agregación y 1 Stored Procedure │
└────────────────────────────────────────┬────────────────────────────────────────┘
                                         │ (Consultas SQL Híbridas / Fallback)
                                         ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│                    CAPA 3: SERVICIOS Y API REST (FASTAPI / ML)                  │
│  - Servidor REST asíncrono en FastAPI + Uvicorn (Puerto 8000)                   │
│  - Endpoints REST (/api/kpis, /api/departamentos, /api/predict)                 │
│  - Motor Econométrico de Machine Learning (Regresión Lineal OLS con Scikit-Learn)│
└────────────────────────────────────────┬────────────────────────────────────────┘
                                         │ (JSON API)
                                         ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│                CAPA 4: INTERFAZ WEB Y PRESENTACIÓN (REACT + VITE)               │
│  - Aplicación Web SPA en React 18 + Vite (Puerto 5173)                          │
│  - Dashboard General con Métricas Macro, Mapa Vectorial del Perú (SVG 25 Dptos) │
│  - Comparador Multivariado Radar, Simulador ML "What-If" y Exportador CSV/JSON  │
└─────────────────────────────────────────────────────────────────────────────────┘
```

---

## 🏛️ 2. Desglose de Capas de la Arquitectura

### 🔹 Capa 1: Ingestión y Pipeline ETL (`/etl/etl_epen2023.py`)
* **Extracción Eficiente:** Carga por bloques (*chunking*) del archivo primario CSV de 114.6 MB codificado en `ISO-8859-1`.
* **Filtro Muestral:** Filtrado estricto de residentes habituales (`RESIDENT == 1`), depurando 31,651 registros inválidos para obtener un universo final de **417,551 observaciones**.
* **Normalización 3FN:** Descomposición de la tabla monolítica de 132 columnas en 3 Dimensiones (`Dim_Departamento`, `Dim_Demografia`, `Dim_CondicionLaboral`) y 1 Tabla de Hechos (`Fact_Empleo`).

---

### 🔹 Capa 2: Base de Datos Relacional en 3FN (`/database/schema_postgresql.sql`)
* **Esquema Estrella Normalizado:** Reducción del 70% en redundancia de almacenamiento mediante claves primarias y foráneas atómicas.
* **Índices B-Tree:** 4 índices estratégicos (`idx_fact_departamento`, `idx_fact_anio_mes`, `idx_fact_condicion_ingreso`, `idx_fact_dept_condicion`) para acelerar la velocidad de JOINs y filtrados.
* **Vistas Analíticas:** `vw_resumen_informalidad_departamento` y `vw_ingreso_promedio_genero_edad`.
* **Procedimiento Almacenado:** `sp_obtener_estadisticas_departamento(p_id_departamento INT)` en PL/pgSQL.

---

### 🔹 Capa 3: Backend y API REST con Machine Learning (`/backend/main.py`)
* **Framework FastAPI:** Endpoints asíncronos y documentación interactiva Swagger en `/docs`.
* **Resiliencia Híbrida:** Intentos automáticos de consulta a PostgreSQL con mecanismo de *fallback* a tablas procesadas en memoria en caso de desconexión.
* **Motor Predictivo OLS:** Modelo econométrico ajustado por Mínimos Cuadrados Ordinarios para estimar ingresos laborales según horas trabajadas, edad y condición de formalidad.

---

### 🔹 Capa 4: Frontend y Dashboard Interactivo (`/frontend/src/App.jsx`)
* **Single Page Application (SPA):** Construida en React 18 y Vite 5.
* **Mapa Vectorial Interactivo:** Renderizado dinámico SVG de alta definición de los **25 departamentos del Perú**.
* **Comparador Radar:** Evaluación multivariada simultánea de hasta 5 departamentos.
* **Simulador ML "What-If":** Interfaz reactiva para proyectar salarios modificando horas y edad.

---

## 🛠️ 3. Stack Tecnológico Detallado

| Capa / Dominio | Tecnología / Herramienta | Versión | Función en el Sistema |
| :--- | :--- | :--- | :--- |
| **Lenguaje Base ETL** | Python | 3.10+ | Procesamiento de microdatos y lógica de transformación. |
| **Manipulación de Datos** | Pandas | 2.0+ | Limpieza de nulos, mapeo categórico y segmentación 3FN. |
| **Cálculo Matricia** | NumPy | 1.24+ | Operaciones vectoriales y agregaciones numéricas. |
| **Base de Datos** | PostgreSQL / SQL Server | 15+ / 2019 | Almacenamiento relacional en 3FN con vistas e índices B-Tree. |
| **Driver BD** | Psycopg2 | 2.9+ | Conector nativo de Python a PostgreSQL. |
| **Backend REST API** | FastAPI | 0.100+ | Exposición de servicios web JSON asíncronos. |
| **Servidor ASGI** | Uvicorn | 0.22+ | Servidor de alta velocidad para ejecutar el backend. |
| **Machine Learning** | Scikit-Learn | 1.3+ | Regresión Lineal OLS para predicción y simulaciones. |
| **Frontend Framework** | React | 18.2 | Desarrollo de componentes UI reactivos y estado global. |
| **Empaquetador Web** | Vite | 5.0+ | Compilación y servidor de desarrollo SPA ultrarrápido. |
| **Gráficos Interactivos** | Recharts | 2.7+ | Renderizado de gráficos de barras, líneas y araña/radar. |
| **Iconografía** | Lucide React | 0.260+ | Colección de íconos vectoriales modernos. |
| **Sistema de Diseño** | Vanilla CSS | CSS3 | HSL Tokens, diseño adaptable anti-genérico y animaciones. |
