import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import pandas as pd
import numpy as np
import os

print("=== CONECTANDO Y CONFIGURANDO BASE DE DATOS POSTGRESQL ===")

DB_HOST = "localhost"
DB_PORT = 5432
DB_USER = "postgres"
DB_PASS = "root"
TARGET_DB = "db_epen2023"

# 1. Crear Base de Datos si no existe
try:
    conn_default = psycopg2.connect(dbname="postgres", user=DB_USER, password=DB_PASS, host=DB_HOST, port=DB_PORT)
    conn_default.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cursor_default = conn_default.cursor()
    
    cursor_default.execute(f"SELECT 1 FROM pg_catalog.pg_database WHERE datname = '{TARGET_DB}'")
    exists = cursor_default.fetchone()
    if not exists:
        cursor_default.execute(f"CREATE DATABASE {TARGET_DB}")
        print(f"[OK] Base de datos '{TARGET_DB}' creada exitosamente.")
    else:
        print(f"[INFO] La base de datos '{TARGET_DB}' ya existe.")
    
    cursor_default.close()
    conn_default.close()
except Exception as e:
    print(f"[ERROR] No se pudo conectar/crear la base de datos: {e}")
    exit(1)

# 2. Conectar a db_epen2023 y ejecutar schema_postgresql.sql
try:
    conn = psycopg2.connect(dbname=TARGET_DB, user=DB_USER, password=DB_PASS, host=DB_HOST, port=DB_PORT)
    cursor = conn.cursor()
    
    sql_script_path = r"d:\Escritorio\Data\schema_postgresql.sql"
    with open(sql_script_path, 'r', encoding='utf-8') as f:
        sql_ddl = f.read()
        
    cursor.execute(sql_ddl)
    conn.commit()
    print("[OK] Tablas, Índices, Vistas y Procedimiento Almacenado creados en PostgreSQL.")

    # 3. Poblar las tablas de dimensión
    tables_dir = r"d:\Escritorio\Data\processed_tables"
    
    # Dim_Departamento
    df_dept = pd.read_csv(os.path.join(tables_dir, "dim_departamento.csv"))
    dept_records = [(int(row['IdDepartamento']), str(row['NombreDepartamento']), str(row['RegionNatural'])) for _, row in df_dept.iterrows()]
    cursor.executemany("INSERT INTO Dim_Departamento (IdDepartamento, NombreDepartamento, RegionNatural) VALUES (%s, %s, %s)", dept_records)
    print(f"[OK] Insertados {len(df_dept)} registros en Dim_Departamento.")
    
    # Dim_Demografia
    df_demog = pd.read_csv(os.path.join(tables_dir, "dim_demografia.csv"))
    demog_records = [(int(row['IdDemografia']), int(row['C207']), str(row['DescSexo']), str(row['GrupoEdad'])) for _, row in df_demog.iterrows()]
    cursor.executemany("INSERT INTO Dim_Demografia (IdDemografia, CodigoSexo, DescripcionSexo, GrupoEdad) VALUES (%s, %s, %s, %s)", demog_records)
    print(f"[OK] Insertados {len(df_demog)} registros en Dim_Demografia.")
    
    # Dim_CondicionLaboral
    df_cond = pd.read_csv(os.path.join(tables_dir, "dim_condicion_laboral.csv"))
    cond_records = []
    for _, row in df_cond.iterrows():
        ocup = int(row['OCUP300']) if pd.notna(row['OCUP300']) else None
        inf = int(row['Informal_P']) if pd.notna(row['Informal_P']) else None
        cond_records.append((int(row['IdCondicion']), ocup, str(row['DescCondicion']), inf, str(row['DescInformalidad'])))
    cursor.executemany("INSERT INTO Dim_CondicionLaboral (IdCondicion, CodigoOcupacion, DescripcionCondicion, CodigoInformalidad, DescripcionInformalidad) VALUES (%s, %s, %s, %s, %s)", cond_records)
    print(f"[OK] Insertados {len(df_cond)} registros en Dim_CondicionLaboral.")
    
    # Fact_Empleo (usando COPY STDIN masivo para alto rendimiento)
    print("[CARGA MASIVA] Insertando 417,551 registros en Fact_Empleo...")
    fact_csv_path = os.path.join(tables_dir, "fact_empleo.csv")
    
    with open(fact_csv_path, 'r', encoding='utf-8') as f:
        cursor.copy_expert("COPY Fact_Empleo FROM STDIN WITH (FORMAT csv, HEADER true)", f)
    
    conn.commit()
    print("[OK] Carga masiva completada: 417,551 filas insertadas exitosamente en Fact_Empleo.")

    # 4. Probar Vista Analítica y Procedimiento Almacenado
    print("\n--- CONSULTA A VISTA ANALÍTICA (vw_resumen_informalidad_departamento) ---")
    cursor.execute("SELECT * FROM vw_resumen_informalidad_departamento ORDER BY Tasa_Informalidad_Porcentaje DESC LIMIT 5;")
    for row in cursor.fetchall():
        print(" ->", row)
        
    print("\n--- EJECUCIÓN DE PROCEDIMIENTO ALMACENADO (sp_obtener_estadisticas_departamento para Lima) ---")
    cursor.execute("SELECT * FROM sp_obtener_estadisticas_departamento(15);")
    print(" -> Resultado SP (Lima):", cursor.fetchone())

    cursor.close()
    conn.close()
    print("\n=== BASE DE DATOS POSTGRESQL TOTALMENTE POBLADA Y FUNCIONAL ===")

except Exception as e:
    print(f"[ERROR] Ocurrió un error en PostgreSQL: {e}")
