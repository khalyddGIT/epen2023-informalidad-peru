# 📊 Sistema de Análisis de Informalidad Laboral en el Perú - EPEN 2023 (INEI)

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100%2B-009688.svg)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-18-61DAFB.svg)](https://reactjs.org/)
[![Vite](https://img.shields.io/badge/Vite-5.0-646CFF.svg)](https://vitejs.dev/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15%2B-336791.svg)](https://www.postgresql.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

Sistema Web Interactivo e Inteligencia de Negocios para el análisis sociodemográfico y predictivo del empleo e informalidad laboral en el Perú a nivel departamental, basado en la **Encuesta Nacional de Empresas e Informalidad (EPEN 2023)** elaborada por el **INEI**.

---

## 🏛️ Información Académica

- **Institución:** Escuela Superior La Pontificia
- **Carrera:** Ingeniería de Sistemas de Información (Sección VIII - "A")
- **Curso:** Modelamiento de Base de Datos / Big Data
- **Docente:** Ing. Palomino Alanya, Erick
- **Estudiante:** Yoniver Cusi Huerta

---

## 📁 Estructura del Proyecto

El repositorio está organizado siguiendo las mejores prácticas de arquitectura de software y separación de responsabilidades:

```text
.
├── 📂 backend/               # Servidor REST FastAPI y Motor Predictivo Scikit-Learn
│   └── main.py              # Endpoints API REST (/api/kpi, /api/departamentos, /api/predict)
├── 📂 frontend/              # Aplicación Web SPA (React + Vite + Recharts + SVG Perú)
│   ├── src/
│   │   ├── App.jsx          # Dashboard interactivo con pestañas, mapas y simulador ML
│   │   ├── index.css        # Sistema de diseño UI anti-generico (Design System)
│   │   └── peru_map_paths.json # Vectores de alta definición para los 25 departamentos
│   ├── package.json
│   └── vite.config.js
├── 📂 database/              # Diseños de Base de Datos y Scripts de Despliegue
│   ├── schema_postgresql.sql# Modelo 3FN (Vistas, Procedimientos e Índices B-Tree)
│   ├── schema_sqlserver.sql # DDL optimizado para Microsoft SQL Server
│   ├── schema_ddl.sql       # Esquema genérico SQL de creación de tablas
│   └── setup_postgres_db.py # Script ejecutable de automatización de base de datos
├── 📂 docs/                  # Documentación Técnica e Informes del Sistema
│   ├── DOCUMENTACION_DEL_SISTEMA.md # Manual técnico integral del sistema
│   ├── API_DOCUMENTATION.md        # Especificación detallada de la API REST
│   └── INFORME_TECNICO_EPEN2023.md  # Informe metodológico y estadístico
├── 📂 etl/                   # Pipeline ETL y Procesamiento de Datos
│   ├── etl_epen2023.py      # Extracción, Limpieza y Normalización a 3FN
│   ├── analisis_y_modelo.py  # Modelado estadístico y Regresión Lineal OLS
│   └── processed_tables/    # Tablas CSV procesadas (Fact_Empleo, Dim_Demografia, etc.)
├── 📂 graficos/              # Gráficos generados para el informe técnico
├── 📂 scripts/               # Herramientas auxiliares y utilitarios de desarrollo
├── .gitignore               # Configuración de archivos ignorados en control de versiones
└── README.md                # Presentación general del proyecto
```

---

## 🚀 Guía de Inicio Rápido

### Prerrequisitos

- Python 3.10+
- Node.js 18+ y npm
- PostgreSQL 14+ (Opcional si se utiliza el motor en memoria)

---

### 1. Iniciar el Backend (FastAPI)

```bash
cd backend
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```
- **API REST:** `http://localhost:8000`
- **Documentación Interactive (Swagger UI):** `http://localhost:8000/docs`

---

### 2. Iniciar el Frontend (React + Vite)

```bash
cd frontend
npm install
npm run dev
```
- **Dashboard Web:** `http://localhost:5173`

---

### 3. Cargar la Base de Datos PostgreSQL (Opcional)

```bash
python database/setup_postgres_db.py
```

---

## ⚡ Características Principales del Dashboard

1. **🗺️ Mapa Interactivo del Perú (25 Departamentos):** Vectorial de alta definición con fichas sociodemográficas flotantes y filtrado al clic.
2. **🧮 Simulador ML "What-If" de Escenarios Laborales:** Regresión OLS para estimación de ingresos por horas y edad.
3. **📊 Comparador Multivariado (Gráfico de Radar):** Evaluación simultánea de hasta 5 departamentos.
4. **🔍 Filtros Multicriterio:** Por salario promedio, tasa máxima de informalidad y Macro-Región.
5. **📑 Exportación Automatizada de Reportes:** Informes ejecutivos imprimibles y descargables.

---

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Libre uso educativo y académico.
