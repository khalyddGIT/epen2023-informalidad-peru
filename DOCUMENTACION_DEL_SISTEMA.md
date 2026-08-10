# DOCUMENTACIÓN TÉCNICA DEL SISTEMA DE BIG DATA Y ANALÍTICA PREDICTIVA

**PROYECTO:** Sistema de Análisis, Normalización (3FN), Pipeline ETL, API REST y Tablero Predictivo de Empleo e Ingresos (EPEN 2023 - INEI Perú)  
**INSTITUCIÓN:** Escuela Superior La Pontificia  
**CARRERA:** Ingeniería de Sistemas de Información  
**ASIGNATURA:** Modelamiento de Base de Datos / Big Data  
**AUTOR:** Yoniver Cusi Huerta  
**DOCENTE:** Ing. Palomino Alanya, Erick  
**FECHA:** Agosto 2026  

---

## 1. Arquitectura General del Sistema

El sistema implementa una solución integral de **Big Data, Ingeniería de Datos y Aprendizaje Automático** estructurada en una arquitectura multicapa desacoplada:

```
[ Fuente de Datos ] ----> [ Pipeline ETL ] ----> [ Base de Datos ] ----> [ API REST Backend ] ----> [ Dashboard Frontend ]
  (INEI EPEN 2023)        (Python/Pandas)       (PostgreSQL 3FN)          (FastAPI ML)            (React + Vite)
```

### Componentes de la Arquitectura:
1. **Capa de Almacenamiento Primario (Dataset):** Microdatos de la Encuesta Permanente de Empleo Nacional (EPEN) 2023 del INEI (**449,202 registros, 132 variables**).
2. **Capa de Procesamiento ETL (Python):** Script ejecutable `etl_epen2023.py` para la extracción, filtrado muestral (`RESIDENT == 1`), imputación de nulos, casteo de tipos y generación de tablas normalizadas.
3. **Capa de Base de Datos Relacional (PostgreSQL / SQL Server):** Esquema dimensional en **Tercera Forma Normal (3FN)** con claves PK/FK, 4 índices B-Tree de alto rendimiento, 2 vistas analíticas y 1 procedimiento almacenado PL/pgSQL.
4. **Capa de Backend y Machine Learning (FastAPI):** Servidor API REST en Python que expone indicadores macro, consultas territoriales, brechas de género, tendencias y un modelo predictivo de **Regresión Lineal Múltiple OLS** en tiempo real.
5. **Capa de Presentación e Interfaz de Usuario (React + Vite):** Tablero interactivo SPA (*Single Page Application*) desarrollado con React 19, Chart.js, Recharts, Lucide Icons y CSS moderno.

---

## 2. Base de Datos Relacional y Normalización (3FN)

### 2.1 Modelo Entidad-Relación y Tablas
La base de datos original monolítica de 132 columnas se descompuso en un modelo relacional en estrella en **Tercera Forma Normal (3FN)** para garantizar la integridad referencial y acelerar las consultas analíticas:

* **`Fact_Empleo` (Tabla de Hechos Central):** Almacena 417,551 registros procesados con las métricas cuantitativas (`IngresoTotal`, `HorasTrabajadas`, `Edad`, `FactorPonderador`) y las claves foráneas hacia las dimensiones.
* **`Dim_Departamento` (Dimensión Geográfica):** Catálogo de los 24 departamentos del Perú y la Provincia Constitucional del Callao, con su clasificación macro-regional (Costa, Sierra, Selva).
* **`Dim_Demografia` (Dimensión Demográfica):** Catálogo de clasificaciones de sexo (Hombre, Mujer) y grupos etarios (Joven, Adulto Joven, Adulto, Adulto Mayor).
* **`Dim_CondicionLaboral` (Dimensión Ocupacional):** Catálogo de estado ocupacional (Ocupado, Desocupado, Inactivo) y condición de informalidad (Formal, Informal).

### 2.2 Objetos de Base de Datos Creados (Scripts DDL)
* **Índices de Rendimiento (B-Tree):**
  - `idx_fact_departamento`: Optimiza JOINs y agrupaciones territoriales.
  - `idx_fact_anio_mes`: Optimiza filtrados y tendencias temporales.
  - `idx_fact_condicion_ingreso`: Acelera agregaciones salariales por condición de informalidad.
  - `idx_fact_dept_condicion`: Optimiza filtros cruzados regionales.
* **Vistas Analíticas:**
  - `vw_resumen_informalidad_departamento`: Calcula totales e índices porcentuales de informalidad por departamento.
  - `vw_ingreso_promedio_genero_edad`: Consolida promedios salariales y horas semanales por sexo y grupo etario.
* **Procedimiento Almacenado (PL/pgSQL):**
  - `sp_obtener_estadisticas_departamento(p_id_departamento)`: Retorna métricas cuantitativas e informalidad de un departamento específico.

---

## 3. Tubería ETL y Procesamiento de Datos

El script `etl_epen2023.py` automatiza las fases del pipeline:

1. **Extracción:** Carga optimizada por bloques (*chunking*) desde la fuente plana CSV en Latin1.
2. **Filtrado Muestral:** Criterio de inclusión del INEI seleccionando residentes habituales (`RESIDENT == 1`), depurando 31,651 registros no pertenecientes a la población objetivo y consolidando **417,551 observaciones válidas**.
3. **Saneamiento e Imputación:** Imputación de ingresos no declarados a `0.00` y estandarización categórica de nulos.
4. **Casteo de Tipos:** Conversión rigurosa de flotantes a enteros (`Anio`, `Mes`, `Edad`, `IdDepartamento`) y decimales de precisión fija (`NUMERIC(12,2)`).
5. **Carga:** Exportación de tablas normalizadas en `processed_tables/` e inserción relacional en PostgreSQL.

---

## 4. API REST Backend (FastAPI)

Servidor web asíncrono ejecutado con **Uvicorn** en el puerto `8000`.

### Catálogo de Endpoints REST:

| Método | Endpoint | Descripción | Formato Entrada | Formato Salida |
| :--- | :--- | :--- | :--- | :--- |
| `GET` | `/` | Estado de la API y verificación de conexión a PostgreSQL | N/A | JSON mensaje y estado DB |
| `GET` | `/api/kpis` | Indicadores macro (Total encuestados, Informalidad %, Ingreso medio, Población ocupada) | N/A | JSON objeto KPI |
| `GET` | `/api/departamentos` | Desglose regional de informalidad e ingreso medio ordenado por informalidad | N/A | JSON arreglo de departamentos |
| `GET` | `/api/brecha-genero` | Comparativa salarial mensual entre hombres y mujeres por grupo de edad | N/A | JSON arreglo etario |
| `GET` | `/api/tendencia-mensual` | Evolución ponderada mensual de la población ocupada (en millones) | N/A | JSON arreglo 12 meses |
| `GET` | `/api/proyeccion` | Parámetros del modelo ML (Ecuación, $R^2$, coeficientes) y proyección a 5 años (2024-2028) | N/A | JSON objeto con proyección |
| `POST` | `/api/predict` | Calculadora en tiempo real del ingreso estimado según horas y edad | JSON `{horas_trabajadas, edad}` | JSON `{ingreso_estimado_soles}` |

---

## 5. Modelo Predictivo y Aprendizaje Automático (Machine Learning)

Se entrenó un modelo supervisado de **Regresión Lineal Múltiple (OLS)** en Python (`scikit-learn` / `statsmodels`):

### 5.1 Ecuación Econométrica del Modelo:
$$\text{Ingreso (S/.)} = 643.52 + (21.10 \times \text{HorasTrabajadas}) + (1.63 \times \text{Edad})$$

* **Intercepto ($\beta_0 = 643.52$):** Ingreso base de partida teórico estimado.
* **Horas Trabajadas ($\beta_1 = +21.10$, $p < 0.001$):** Por cada hora adicional trabajada a la semana, el ingreso mensual se incrementa en **S/. 21.10**.
* **Edad ($\beta_2 = +1.63$, $p < 0.001$):** Por cada año de experiencia acumulada, el ingreso mensual se incrementa en **S/. 1.63**.

### 5.2 Proyección Salarial Quinquenal (2024 – 2028):
* **2023 (Base Real):** S/. 1,514.93
* **2024 (Proyectado):** S/. 1,751.91 (+15.6%)
* **2025 (Proyectado):** S/. 1,849.62 (+5.6%)
* **2026 (Proyectado):** S/. 1,947.32 (+5.3%)
* **2027 (Proyectado):** S/. 2,045.02 (+5.0%)
* **2028 (Proyectado):** S/. 2,142.73 (+4.8%)

---

## 6. Frontend Interactivo (React + Vite Dashboard - 5 Nuevas Funcionalidades)

Aplicación web moderna desarrollada con **React 19** y **Vite 8** en el puerto `5173`.

### Características Interactivas Avanzadas Implementadas:
1. **🗺️ Mapa Interactivo del Perú (Vectorial SVG):** Mapa cartográfico con código de colores según nivel de informalidad (Rojo $>78\%$, Naranja $70\%-78\%$, Ámbar $62\%-70\%$, Verde $<62\%$). Ficha técnica en hover y filtrado al hacer clic.
2. **🧮 Simulador ML Avanzado de Escenarios "What-If":** Simulación comparativa en tiempo real calculando el diferencial entre el sector formal e informal, con badge de incremento neta en Soles ($+S/. X$) y porcentaje ($+Y\%$).
3. **📊 Comparador Multivariado de Departamentos (Gráfico de Araña / Radar):** Selector multivariado para comparar de 2 a 5 departamentos simultáneamente evaluando formalidad, ingresos medios y representación poblacional.
4. **🔍 Filtros Dinámicos Multicriterio:** Sliders de rango de ingresos ($S/. 1,000$ a $S/. 2,000$), informalidad máxima ($50\%$ a $85\%$), selector de Macro-Región (Costa, Sierra, Selva) y botón de restablecimiento.
5. **💡 Glosario Metodológico Explicativo (Íconos Info `(i)`):** Modales informativos contextuales que explican la Tercera Forma Normal (3FN), Regresión OLS, $R^2$, Ponderador `FAC300_ANUAL` y definición de informalidad INEI.

---

## 7. Guía de Despliegue y Ejecución Local

### Paso 1: Configurar y Cargar la Base de Datos PostgreSQL (Opcional)
```bash
python setup_postgres_db.py
```

### Paso 2: Iniciar el Servidor Backend (FastAPI)
```bash
cd backend
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```
* API REST: `http://localhost:8000` | Swagger UI: `http://localhost:8000/docs`

### Paso 3: Iniciar la Aplicación Frontend (React + Vite)
```bash
cd frontend
npm run dev
```
* Dashboard Web: `http://localhost:5173`

---

## 8. Estructura de Directorios del Proyecto

```
d:\Escritorio\Data\
├── BASE DE DATOS- ANALISIS-PREDICCION (1).docx  # Informe oficial en Word completado
├── INFORME_TECNICO_EPEN2023.md                 # Informe técnico extenso en Markdown
├── API_DOCUMENTATION.md                        # Documentación exclusiva de la API REST
├── DOCUMENTACION_DEL_SISTEMA.md                # Documentación completa del sistema
├── schema_postgresql.sql                       # Script DDL/DML nativo de PostgreSQL
├── schema_sqlserver.sql                        # Script DDL para SQL Server
├── etl_epen2023.py                             # Script ejecutable del proceso ETL
├── analisis_y_modelo.py                        # Script de análisis estadístico y ML OLS
├── setup_postgres_db.py                        # Script de carga automática a PostgreSQL
├── generate_report_docx.py                     # Generador del documento Word
├── backend/                                    # Código fuente del Servidor FastAPI
│   └── main.py                                 # Endpoints REST y modelos ML
├── frontend/                                   # Aplicación React + Vite
│   ├── src/
│   │   ├── App.jsx                             # Dashboard con Mapa, Radar, What-If y Glosario
│   │   └── index.css                           # Sistema de diseño CSS
│   ├── package.json                            # Dependencias de Node.js
│   └── vite.config.js                          # Configuración del bundler Vite
├── graficos/                                   # Imágenes PNG de alta resolución (5 figuras)
└── processed_tables/                           # Archivos CSV normalizados en 3FN
```
