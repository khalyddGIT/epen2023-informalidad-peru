# DOCUMENTACIÓN DE LA API REST (EPEN 2023 - INEI PERÚ)

**PROYECTO:** Big Data y Modelado Predictivo de Empleo e Ingresos (EPEN 2023)  
**FRAMEWORK:** FastAPI (Python 3.13)  
**BASE DE DATOS:** PostgreSQL 15 (`db_epen2023`) / Fallback en CSV Pandas  
**ARQUITECTURA:** RESTful / JSON Data Format  
**BASE URL LOCAL:** `http://localhost:8000`  
**SWAGGER UI INTERACTIVO:** `http://localhost:8000/docs`  
**REDOC INTERACTIVO:** `http://localhost:8000/redoc`  

---

## 1. Visión General de la API

La API REST proporciona una interfaz de consulta analítica y predicción econométrica sobre los microdatos de la Encuesta Permanente de Empleo Nacional (EPEN) 2023 del INEI. Está diseñada bajo una arquitectura híbrida resiliente que consulta directamente las vistas e índices B-Tree de la base de datos relacional PostgreSQL en 3FN, activando automáticamente un mecanismo de respaldo (*fallback*) sobre archivos CSV optimizados en memoria si la conexión a la base de datos se interrumpe.

---

## 2. Configuración de CORS y Protocolo

* **Origen Permitido (CORS):** Habilitado para todos los orígenes (`*`) facilitando la integración con dashboards de frontend React/Vite.
* **Métodos Permitidos:** `GET`, `POST`, `OPTIONS`.
* **Formato de Respuesta:** `application/json` con codificación `UTF-8`.

---

## 3. Catálogo de Endpoints

### 3.1. Estado de la API y Conexión
Verifica la disponibilidad del servicio API REST y el estado del motor de base de datos PostgreSQL.

* **URL:** `/`
* **Método:** `GET`
* **Parámetros:** Ninguno.
* **Respuesta Exitosa (200 OK):**
```json
{
  "message": "API REST EPEN 2023 activa",
  "database": "Conectado a PostgreSQL (db_epen2023)"
}
```

---

### 3.2. Indicadores Macro (KPIs)
Retorna las métricas cuantitativas consolidadas a nivel nacional.

* **URL:** `/api/kpis`
* **Método:** `GET`
* **Parámetros:** Ninguno.
* **Respuesta Exitosa (200 OK):**
```json
{
  "total_encuestados": 417551,
  "tasa_informalidad_porcentaje": 71.24,
  "ingreso_medio_soles": 1514.93,
  "poblacion_ocupada_estimada": 17245890.0,
  "fuente": "PostgreSQL Direct DB"
}
```

---

### 3.3. Resumen Territorial por Departamento
Entrega la desagregación de informalidad e ingreso medio para los 24 departamentos del Perú y la Provincia Constitucional del Callao, ordenados descendentemente por tasa de informalidad.

* **URL:** `/api/departamentos`
* **Método:** `GET`
* **Parámetros:** Ninguno.
* **Respuesta Exitosa (200 OK):**
```json
[
  {
    "id_departamento": 3,
    "nombre": "Ayacucho",
    "region": "Sierra",
    "tasa_informalidad": 79.58,
    "ingreso_medio": 1213.20,
    "total_encuestados": 14210
  },
  {
    "id_departamento": 21,
    "nombre": "Puno",
    "region": "Sierra",
    "tasa_informalidad": 78.77,
    "ingreso_medio": 1192.57,
    "total_encuestados": 18540
  },
  {
    "id_departamento": 15,
    "nombre": "Lima",
    "region": "Costa",
    "tasa_informalidad": 59.74,
    "ingreso_medio": 1823.04,
    "total_encuestados": 58920
  }
]
```

---

### 3.4. Brecha Salarial por Género y Edad
Proporciona la comparación de ingresos promedios entre hombres y mujeres desglosada por grupos etarios.

* **URL:** `/api/brecha-genero`
* **Método:** `GET`
* **Parámetros:** Ninguno.
* **Respuesta Exitosa (200 OK):**
```json
[
  {
    "grupo_edad": "14-29 Joven",
    "Hombre": 1250.40,
    "Mujer": 980.10
  },
  {
    "grupo_edad": "30-49 Adulto Joven",
    "Hombre": 1920.50,
    "Mujer": 1410.20
  },
  {
    "grupo_edad": "50-64 Adulto",
    "Hombre": 1810.00,
    "Mujer": 1250.40
  },
  {
    "grupo_edad": "65+ Adulto Mayor",
    "Hombre": 1050.10,
    "Mujer": 680.50
  }
]
```

---

### 3.5. Tendencia Mensual de Población Ocupada
Proporciona la estimación ponderada mensual de la masa laboral ocupada (en millones de personas) para los 12 meses del año 2023.

* **URL:** `/api/tendencia-mensual`
* **Método:** `GET`
* **Parámetros:** Ninguno.
* **Respuesta Exitosa (200 OK):**
```json
[
  {"mes_num": 1, "mes_nombre": "Ene", "poblacion_ocupada_millones": 17.150},
  {"mes_num": 2, "mes_nombre": "Feb", "poblacion_ocupada_millones": 17.180},
  {"mes_num": 5, "mes_nombre": "May", "poblacion_ocupada_millones": 17.310},
  {"mes_num": 12, "mes_nombre": "Dic", "poblacion_ocupada_millones": 17.420}
]
```

---

### 3.6. Parámetros del Modelo ML y Proyección Quinquenal
Devuelve la ecuación matemática entrenada por Regresión Lineal OLS, el coeficiente de determinación ($R^2$), los pesos econométricos y la proyección proyectada del ingreso medio para el período 2024–2028.

* **URL:** `/api/proyeccion`
* **Método:** `GET`
* **Parámetros:** Ninguno.
* **Respuesta Exitosa (200 OK):**
```json
{
  "modelo_ecuacion": "Ingreso = 643.52 + (21.10 * Horas) + (1.63 * Edad)",
  "r2_score": 0.3842,
  "coeficientes": {
    "intercepto": 643.52,
    "horas_trabajadas": 21.10,
    "edad": 1.63
  },
  "proyeccion_5_anios": [
    {"anio": 2024, "ingreso_proyectado": 1751.91},
    {"anio": 2025, "ingreso_proyectado": 1849.62},
    {"anio": 2026, "ingreso_proyectado": 1947.32},
    {"anio": 2027, "ingreso_proyectado": 2045.02},
    {"anio": 2028, "ingreso_proyectado": 2142.73}
  ]
}
```

---

### 3.7. Endpoint de Predicción en Tiempo Real (Machine Learning)
Calcula la estimación puntual del ingreso mensual en Soles (S/.) en función de las horas semanales trabajadas y la edad ingresada por el usuario.

* **URL:** `/api/predict`
* **Método:** `POST`
* **Encabezados:** `Content-Type: application/json`
* **Cuerpo de la Solicitud (JSON Request Body):**
```json
{
  "horas_trabajadas": 45.0,
  "edad": 35.0
}
```
* **Respuesta Exitosa (200 OK):**
```json
{
  "horas_trabajadas": 45.0,
  "edad": 35.0,
  "ingreso_estimado_soles": 1650.07
}
```
* **Respuesta de Error de Validación (400 Bad Request):**
```json
{
  "detail": "Horas o edad inválidas"
}
```

---

## 4. Códigos de Estado HTTP

| Código | Descripción | Contexto |
| :--- | :--- | :--- |
| `200 OK` | Solicitud procesada correctamente | Respuestas estándar de lectura y predicción ML |
| `400 Bad Request` | Parámetros o payload de entrada fuera de rango | Horas trabajadas < 0 o Edad < 14 en `/api/predict` |
| `422 Unprocessable Entity` | Error de tipo de dato en payload JSON | Formato JSON incorrecto o tipos erróneos |
| `500 Internal Server Error` | Excepción no controlada en el servidor | Fallo de conexión o cálculo interno |

---

## 5. Instrucciones para la Ejecución del Servidor API

Para iniciar el servidor FastAPI localmente en modo desarrollo con recarga automática:

```bash
cd backend
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```
