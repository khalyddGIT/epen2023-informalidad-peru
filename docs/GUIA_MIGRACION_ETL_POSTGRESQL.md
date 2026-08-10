# GUÍA TÉCNICA DE MIGRACIÓN: EXCEL/CSV A POSTGRESQL (3FN)

**PROYECTO:** Análisis de Microdatos de Empleo e Ingresos (EPEN 2023 - INEI Perú)  
**ASIGNATURA:** Modelamiento de Base de Datos / Big Data con Datos Abiertos Reales  
**CARRERA:** Ingeniería de Sistemas de Información  
**DOCUMENTO:** Guía de Ejecución y Comandos de Migración ETL  

---

## 📌 1. Visión General del Proceso

Esta guía documenta el procedimiento paso a paso para la extracción, limpieza, normalización en **Tercera Forma Normal (3FN)** y carga de datos masivos desde el archivo primario en formato CSV (`EPEN 2023 BD_Publicación Dpto.csv`, 449,202 registros y 132 columnas) hacia la base de datos relacional **PostgreSQL** (`db_epen2023`).

```
┌───────────────────────────────┐
│ Dataset Primario CSV (INEI)   │ (449,202 filas x 132 cols)
└───────────────┬───────────────┘
                │
                ▼
┌───────────────────────────────┐
│ Pipeline ETL (Python/Pandas)  │ Filtro RESIDENT == 1
│ etl_epen2023.py               │ Normalización a 3FN
└───────────────┬───────────────┘
                │
                ▼
┌───────────────────────────────┐
│ Archivos Procesados 3FN (CSV) │ dim_departamento.csv
│ /processed_tables/            │ dim_demografia.csv
│                               │ dim_condicion_laboral.csv
│                               │ fact_empleo.csv (417,551 filas)
└───────────────┬───────────────┘
                │
                ▼
┌───────────────────────────────┐
│ Carga Masiva a PostgreSQL     │ COPY STDIN (psycopg2) / \copy CLI
│ setup_postgres_db.py          │ Tablas, Índices B-Tree, Vistas y SP
└───────────────────────────────┘
```

---

## 🚀 2. Fase 1: Extracción, Limpieza y Normalización a 3FN en Python

El script `etl_epen2023.py` realiza la carga eficiente por bloques, aplica el filtro de validez muestral del INEI y descompone el dataset plano en 3 Tablas de Dimensión y 1 Tabla de Hechos.

### 📜 Comando de Ejecución (Terminal / Powershell):
```bash
python d:\Escritorio\Data\etl\etl_epen2023.py
```

### 💻 Código Fuente del Pipeline ETL (`etl/etl_epen2023.py`):
```python
import pandas as pd
import numpy as np
import os

print("=== INICIANDO PROCESO ETL - EPEN 2023 INEI ===")

# 1. Rutas de entrada y salida
csv_path = r"d:\Escritorio\Data\EPEN 2023 BD_Publicación Dpto.csv"
output_dir = r"d:\Escritorio\Data\processed_tables"
os.makedirs(output_dir, exist_ok=True)

# 2. Extracción de los datos originales
df_raw = pd.read_csv(csv_path, encoding='latin1', low_memory=False)
print(f"[EXTRACCIÓN] Registros cargados: {len(df_raw):,}, Columnas: {len(df_raw.columns)}")

# 3. Filtrado de residentes habituales (RESIDENT == 1)
df = df_raw[df_raw['RESIDENT'] == 1].copy()
print(f"[FILTRADO] Universo muestral válido: {len(df):,} registros")

# 4. Mapeo de Departamentos (INEI Ubigeo CCDD)
dept_map = {
    1: 'Amazonas', 2: 'Áncash', 3: 'Apurímac', 4: 'Arequipa', 5: 'Ayacucho',
    6: 'Cajamarca', 7: 'Callao', 8: 'Cusco', 9: 'Huancavelica', 10: 'Huánuco',
    11: 'Ica', 12: 'Junín', 13: 'La Libertad', 14: 'Lambayeque', 15: 'Lima',
    16: 'Loreto', 17: 'Madre de Dios', 18: 'Moquegua', 19: 'Pasco', 20: 'Piura',
    21: 'Puno', 22: 'San Martín', 23: 'Tacna', 24: 'Tumbes', 25: 'Ucayali'
}
df['NomDepartamento'] = df['CCDD'].map(dept_map)

# --- NORMALIZACIÓN A TERCERA FORMA NORMAL (3FN) ---

# DIMENSIÓN 1: Dim_Departamento
dim_dept = pd.DataFrame({
    'IdDepartamento': list(dept_map.keys()),
    'NombreDepartamento': list(dept_map.values()),
    'RegionNatural': ['Sierra' if k in [3, 9, 10, 12, 19, 21] else ('Selva' if k in [1, 16, 17, 22, 25] else 'Costa') for k in dept_map.keys()]
})
dim_dept.to_csv(os.path.join(output_dir, 'dim_departamento.csv'), index=False, encoding='utf-8-sig')

# DIMENSIÓN 2: Dim_Demografia (Sexo y Grupo de Edad)
df['DescSexo'] = df['C207'].map({1.0: 'Hombre', 2.0: 'Mujer'}).fillna('No Especificado')

def calcular_grupo_edad(edad):
    if pd.isna(edad): return 'Desconocido'
    elif edad < 14: return 'Menor de Edad (0-13)'
    elif edad <= 29: return 'Jóvenes (14-29)'
    elif edad <= 49: return 'Adultos Jóvenes (30-49)'
    elif edad <= 64: return 'Adultos (50-64)'
    else: return 'Adultos Mayores (65+)'

df['GrupoEdad'] = df['C208'].apply(calcular_grupo_edad)

dim_demog = df[['C207', 'DescSexo', 'GrupoEdad']].drop_duplicates().reset_index(drop=True)
dim_demog['IdDemografia'] = dim_demog.index + 1
dim_demog.to_csv(os.path.join(output_dir, 'dim_demografia.csv'), index=False, encoding='utf-8-sig')

df = df.merge(dim_demog[['C207', 'GrupoEdad', 'IdDemografia']], on=['C207', 'GrupoEdad'], how='left')

# DIMENSIÓN 3: Dim_CondicionLaboral (Ocupación e Informalidad)
ocup_map = {1.0: 'Ocupado', 2.0: 'Desocupado', 3.0: 'Desocupado Oculto', 4.0: 'Inactivo'}
informal_map = {1.0: 'Informal', 2.0: 'Formal'}

df['DescCondicion'] = df['OCUP300'].map(ocup_map).fillna('Sin Información')
df['DescInformalidad'] = df['Informal_P'].map(informal_map).fillna('No Aplica')

dim_cond = df[['OCUP300', 'DescCondicion', 'Informal_P', 'DescInformalidad']].drop_duplicates().reset_index(drop=True)
dim_cond['IdCondicion'] = dim_cond.index + 1
dim_cond.to_csv(os.path.join(output_dir, 'dim_condicion_laboral.csv'), index=False, encoding='utf-8-sig')

df = df.merge(dim_cond[['OCUP300', 'Informal_P', 'IdCondicion']], on=['OCUP300', 'Informal_P'], how='left')

# TABLA DE HECHOS: Fact_Empleo
fact_empleo = pd.DataFrame({
    'IdFact': range(1, len(df) + 1),
    'IdDepartamento': df['CCDD'].astype(int),
    'IdDemografia': df['IdDemografia'].astype(int),
    'IdCondicion': df['IdCondicion'].astype(int),
    'Anio': df['ANIO'].astype(int),
    'Mes': df['MES'].astype(int),
    'Edad': df['C208'].fillna(-1).astype(int),
    'IngresoTotal': df['INGTOT'].fillna(0.0),
    'HorasTrabajadas': df['whoraT'].fillna(0.0),
    'FactorPonderador': df['FAC300_ANUAL'].fillna(1.0)
})

fact_empleo.to_csv(os.path.join(output_dir, 'fact_empleo.csv'), index=False, encoding='utf-8-sig')
print("=== ETL FINALIZADO CON ÉXITO ===")
```

---

## 🏛️ 3. Fase 2: Definición del Esquema DDL en PostgreSQL (`schema_postgresql.sql`)

El archivo DDL crea la estructura relacional con integridad referencial, índices de alto rendimiento (B-Tree), vistas analíticas y procedimientos almacenados en PL/pgSQL.

```sql
-- =============================================================================
-- PROYECTO BIG DATA: EPEN 2023 (INEI - PERÚ)
-- SCRIPT DDL COMPLETO EN 3FN (PostgreSQL)
-- =============================================================================

-- 1. ELIMINACIÓN PREVENTIVA DE OBJETOS
DROP FUNCTION IF EXISTS sp_obtener_estadisticas_departamento(INT);
DROP VIEW IF EXISTS vw_ingreso_promedio_genero_edad;
DROP VIEW IF EXISTS vw_resumen_informalidad_departamento;
DROP TABLE IF EXISTS Fact_Empleo CASCADE;
DROP TABLE IF EXISTS Dim_CondicionLaboral CASCADE;
DROP TABLE IF EXISTS Dim_Demografia CASCADE;
DROP TABLE IF EXISTS Dim_Departamento CASCADE;

-- 2. CREACIÓN DE TABLAS DE DIMENSIÓN (3FN)
CREATE TABLE Dim_Departamento (
    IdDepartamento INT PRIMARY KEY,
    NombreDepartamento VARCHAR(100) NOT NULL,
    RegionNatural VARCHAR(50) NOT NULL
);

CREATE TABLE Dim_Demografia (
    IdDemografia INT PRIMARY KEY,
    CodigoSexo INT NOT NULL,
    DescripcionSexo VARCHAR(20) NOT NULL,
    GrupoEdad VARCHAR(50) NOT NULL
);

CREATE TABLE Dim_CondicionLaboral (
    IdCondicion INT PRIMARY KEY,
    CodigoOcupacion INT,
    DescripcionCondicion VARCHAR(50) NOT NULL,
    CodigoInformalidad INT,
    DescripcionInformalidad VARCHAR(50) NOT NULL
);

-- 3. CREACIÓN DE TABLA DE HECHOS (Fact_Empleo)
CREATE TABLE Fact_Empleo (
    IdFact INT PRIMARY KEY,
    IdDepartamento INT NOT NULL,
    IdDemografia INT NOT NULL,
    IdCondicion INT NOT NULL,
    Anio INT NOT NULL,
    Mes INT NOT NULL,
    Edad INT NOT NULL,
    IngresoTotal NUMERIC(12, 2) DEFAULT 0.00,
    HorasTrabajadas NUMERIC(8, 2) DEFAULT 0.00,
    FactorPonderador NUMERIC(12, 4) DEFAULT 1.0000,
    CONSTRAINT FK_Fact_Departamento FOREIGN KEY (IdDepartamento) REFERENCES Dim_Departamento(IdDepartamento),
    CONSTRAINT FK_Fact_Demografia FOREIGN KEY (IdDemografia) REFERENCES Dim_Demografia(IdDemografia),
    CONSTRAINT FK_Fact_Condicion FOREIGN KEY (IdCondicion) REFERENCES Dim_CondicionLaboral(IdCondicion)
);

-- 4. ÍNDICES B-TREE
CREATE INDEX idx_fact_departamento ON Fact_Empleo (IdDepartamento);
CREATE INDEX idx_fact_anio_mes ON Fact_Empleo (Anio, Mes);
CREATE INDEX idx_fact_condicion_ingreso ON Fact_Empleo (IdCondicion, IngresoTotal);
CREATE INDEX idx_fact_dept_condicion ON Fact_Empleo (IdDepartamento, IdCondicion);

-- 5. VISTA ANALÍTICA DE INFORMALIDAD
CREATE VIEW vw_resumen_informalidad_departamento AS
SELECT 
    d.NombreDepartamento,
    d.RegionNatural,
    COUNT(f.IdFact) AS Total_Encuestados,
    SUM(CASE WHEN c.DescripcionInformalidad = 'Informal' THEN 1 ELSE 0 END) AS Total_Informales,
    SUM(CASE WHEN c.DescripcionInformalidad = 'Formal' THEN 1 ELSE 0 END) AS Total_Formales,
    ROUND(
        (SUM(CASE WHEN c.DescripcionInformalidad = 'Informal' THEN 1.0 ELSE 0.0 END) * 100.0) / 
        NULLIF(SUM(CASE WHEN c.DescripcionInformalidad IN ('Informal', 'Formal') THEN 1.0 ELSE 0.0 END), 0), 2
    ) AS Tasa_Informalidad_Porcentaje
FROM Fact_Empleo f
JOIN Dim_Departamento d ON f.IdDepartamento = d.IdDepartamento
JOIN Dim_CondicionLaboral c ON f.IdCondicion = c.IdCondicion
GROUP BY d.NombreDepartamento, d.RegionNatural;

-- 6. PROCEDIMIENTO ALMACENADO PL/pgSQL
CREATE OR REPLACE FUNCTION sp_obtener_estadisticas_departamento(p_id_departamento INT)
RETURNS TABLE (
    Departamento VARCHAR,
    TotalEncuestados BIGINT,
    IngresoMedio NUMERIC,
    InformalidadPct NUMERIC
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        d.NombreDepartamento::VARCHAR,
        COUNT(f.IdFact) AS TotalEncuestados,
        ROUND(AVG(f.IngresoTotal), 2) AS IngresoMedio,
        ROUND(
            (SUM(CASE WHEN c.DescripcionInformalidad = 'Informal' THEN 1.0 ELSE 0.0 END) * 100.0) / 
            NULLIF(SUM(CASE WHEN c.DescripcionInformalidad IN ('Informal', 'Formal') THEN 1.0 ELSE 0.0 END), 0), 2
        ) AS InformalidadPct
    FROM Fact_Empleo f
    JOIN Dim_Departamento d ON f.IdDepartamento = d.IdDepartamento
    JOIN Dim_CondicionLaboral c ON f.IdCondicion = c.IdCondicion
    WHERE f.IdDepartamento = p_id_departamento
    GROUP BY d.NombreDepartamento;
END;
$$ LANGUAGE plpgsql;
```

---

## ⚡ 4. Fase 3: Carga Masiva Automatizada desde Python (`setup_postgres_db.py`)

### 📜 Comando de Ejecución:
```bash
python d:\Escritorio\Data\database\setup_postgres_db.py
```

### 💻 Código Fuente del Cargador (`database/setup_postgres_db.py`):
```python
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import pandas as pd
import os

DB_HOST = "localhost"
DB_PORT = 5432
DB_USER = "postgres"
DB_PASS = "root"
TARGET_DB = "db_epen2023"

# 1. Crear Base de Datos si no existe
conn_default = psycopg2.connect(dbname="postgres", user=DB_USER, password=DB_PASS, host=DB_HOST, port=DB_PORT)
conn_default.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
cursor_default = conn_default.cursor()

cursor_default.execute(f"SELECT 1 FROM pg_catalog.pg_database WHERE datname = '{TARGET_DB}'")
if not cursor_default.fetchone():
    cursor_default.execute(f"CREATE DATABASE {TARGET_DB}")
    print(f"[OK] Base de datos '{TARGET_DB}' creada.")

cursor_default.close()
conn_default.close()

# 2. Conectar a db_epen2023 y ejecutar DDL
conn = psycopg2.connect(dbname=TARGET_DB, user=DB_USER, password=DB_PASS, host=DB_HOST, port=DB_PORT)
cursor = conn.cursor()

with open(r"d:\Escritorio\Data\database\schema_postgresql.sql", 'r', encoding='utf-8') as f:
    cursor.execute(f.read())
conn.commit()

tables_dir = r"d:\Escritorio\Data\processed_tables"

# 3. Poblar Tablas de Dimensión
df_dept = pd.read_csv(os.path.join(tables_dir, "dim_departamento.csv"))
cursor.executemany("INSERT INTO Dim_Departamento VALUES (%s, %s, %s)", 
                   [(int(r['IdDepartamento']), str(r['NombreDepartamento']), str(r['RegionNatural'])) for _, r in df_dept.iterrows()])

df_demog = pd.read_csv(os.path.join(tables_dir, "dim_demografia.csv"))
cursor.executemany("INSERT INTO Dim_Demografia VALUES (%s, %s, %s, %s)", 
                   [(int(r['IdDemografia']), int(r['C207']), str(r['DescSexo']), str(r['GrupoEdad'])) for _, r in df_demog.iterrows()])

df_cond = pd.read_csv(os.path.join(tables_dir, "dim_condicion_laboral.csv"))
cond_records = []
for _, row in df_cond.iterrows():
    ocup = int(row['OCUP300']) if pd.notna(row['OCUP300']) else None
    inf = int(row['Informal_P']) if pd.notna(row['Informal_P']) else None
    cond_records.append((int(row['IdCondicion']), ocup, str(row['DescCondicion']), inf, str(row['DescInformalidad'])))
cursor.executemany("INSERT INTO Dim_CondicionLaboral VALUES (%s, %s, %s, %s, %s)", cond_records)

# 4. Carga Masiva (COPY STDIN) de 417,551 filas en Fact_Empleo
with open(os.path.join(tables_dir, "fact_empleo.csv"), 'r', encoding='utf-8') as f:
    cursor.copy_expert("COPY Fact_Empleo FROM STDIN WITH (FORMAT csv, HEADER true)", f)

conn.commit()
print("=== BASE DE DATOS POSTGRESQL POBLADA Y FUNCIONAL ===")
```

---

## 🖥️ 5. Alternativa: Comandos Directos en Terminal `psql` (CLI)

Si deseas realizar la carga de manera interactiva sin ejecutar scripts en Python:

```sql
-- 1. Iniciar sesión y crear la base de datos
psql -U postgres
CREATE DATABASE db_epen2023;
\c db_epen2023;

-- 2. Ejecutar el script DDL de creación de estructuras
\i 'd:/Escritorio/Data/database/schema_postgresql.sql'

-- 3. Cargar dimensiones
\copy Dim_Departamento FROM 'd:/Escritorio/Data/processed_tables/dim_departamento.csv' WITH (FORMAT csv, HEADER true);
\copy Dim_Demografia FROM 'd:/Escritorio/Data/processed_tables/dim_demografia.csv' WITH (FORMAT csv, HEADER true);
\copy Dim_CondicionLaboral FROM 'd:/Escritorio/Data/processed_tables/dim_condicion_laboral.csv' WITH (FORMAT csv, HEADER true);

-- 4. Carga masiva de la Tabla de Hechos (417,551 filas)
\copy Fact_Empleo FROM 'd:/Escritorio/Data/processed_tables/fact_empleo.csv' WITH (FORMAT csv, HEADER true);
```

---

## ✅ 6. Comandos de Verificación y Validación

Para validar la integridad de los datos cargados en PostgreSQL:

```sql
-- Validar número total de registros insertados en la Tabla de Hechos
SELECT COUNT(*) FROM Fact_Empleo; 
-- Resultado esperado: 417,551

-- Probar la vista analítica de informalidad por departamento
SELECT * FROM vw_resumen_informalidad_departamento ORDER BY Tasa_Informalidad_Porcentaje DESC LIMIT 5;

-- Probar el procedimiento almacenado PL/pgSQL para Lima (ID 15)
SELECT * FROM sp_obtener_estadisticas_departamento(15);
```
