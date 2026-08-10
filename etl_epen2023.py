import pandas as pd
import numpy as np
import os

print("=== INICIANDO PROCESO ETL - EPEN 2023 INEI ===")

# 1. Extracción de los datos originales
csv_path = r"d:\Escritorio\Data\EPEN 2023 BD_Publicación Dpto.csv"
output_dir = r"d:\Escritorio\Data\processed_tables"
os.makedirs(output_dir, exist_ok=True)

df_raw = pd.read_csv(csv_path, encoding='latin1', low_memory=False)
print(f"[EXTRACCIÓN] Registros cargados: {len(df_raw):,}, Columnas: {len(df_raw.columns)}")

# 2. Limpieza y Transformación
# Filtrar residentes habituales (RESIDENT == 1)
df = df_raw[df_raw['RESIDENT'] == 1].copy()
print(f"[FILTRADO] Registros residentes habituales: {len(df):,}")

# Mapeo de Departamentos (INEI Ubigeo CCDD)
dept_map = {
    1: 'Amazonas', 2: 'Áncash', 3: 'Apurímac', 4: 'Arequipa', 5: 'Ayacucho',
    6: 'Cajamarca', 7: 'Callao', 8: 'Cusco', 9: 'Huancavelica', 10: 'Huánuco',
    11: 'Ica', 12: 'Junín', 13: 'La Libertad', 14: 'Lambayeque', 15: 'Lima',
    16: 'Loreto', 17: 'Madre de Dios', 18: 'Moquegua', 19: 'Pasco', 20: 'Piura',
    21: 'Puno', 22: 'San Martín', 23: 'Tacna', 24: 'Tumbes', 25: 'Ucayali'
}

# Mapeo de Educación (P301A / C301_NIVEL / C301A / C301_...)
# C300N o P208 o C301_MES etc. C300n / C301_DIA / etc.
# Usaremos C207 (Sexo), C208 (Edad), P301a / C301 si está, sino derivado
df['NomDepartamento'] = df['CCDD'].map(dept_map)

# 3. Normalización a Tercera Forma Normal (3FN)

# ENTIDAD 1: Dim_Departamento
dim_dept = pd.DataFrame({
    'IdDepartamento': list(dept_map.keys()),
    'NombreDepartamento': list(dept_map.values()),
    'RegionNatural': ['Sierra' if k in [3, 9, 10, 12, 19, 21] else ('Selva' if k in [1, 16, 17, 22, 25] else 'Costa') for k in dept_map.keys()]
})
dim_dept.to_csv(os.path.join(output_dir, 'dim_departamento.csv'), index=False, encoding='utf-8-sig')
print("[3FN] Creada dimensión Dim_Departamento")

# ENTIDAD 2: Dim_Demografia (Combinaciones únicas de Sexo y Grupos de Edad)
# Sexo: 1=Hombre, 2=Mujer
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
print("[3FN] Creada dimensión Dim_Demografia")

# Mapear IdDemografia a Fact
df = df.merge(dim_demog[['C207', 'GrupoEdad', 'IdDemografia']], on=['C207', 'GrupoEdad'], how='left')

# ENTIDAD 3: Dim_CondicionLaboral
# OCUP300: 1=Ocupado, 2=Desocupado abierto, 3=Desocupado oculto, 4=Inactivo
ocup_map = {1.0: 'Ocupado', 2.0: 'Desocupado', 3.0: 'Desocupado Oculto', 4.0: 'Inactivo'}
informal_map = {1.0: 'Informal', 2.0: 'Formal'}

df['DescCondicion'] = df['OCUP300'].map(ocup_map).fillna('Sin Información')
df['DescInformalidad'] = df['Informal_P'].map(informal_map).fillna('No Aplica')

dim_cond = df[['OCUP300', 'DescCondicion', 'Informal_P', 'DescInformalidad']].drop_duplicates().reset_index(drop=True)
dim_cond['IdCondicion'] = dim_cond.index + 1
dim_cond.to_csv(os.path.join(output_dir, 'dim_condicion_laboral.csv'), index=False, encoding='utf-8-sig')
print("[3FN] Creada dimensión Dim_CondicionLaboral")

df = df.merge(dim_cond[['OCUP300', 'Informal_P', 'IdCondicion']], on=['OCUP300', 'Informal_P'], how='left')

# ENTIDAD 4: Fact_Empleo (Tabla de Hechos)
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
print(f"[3FN] Creada tabla de hechos Fact_Empleo con {len(fact_empleo):,} filas.")

print("=== PROCESO ETL FINALIZADO CON ÉXITO ===")
