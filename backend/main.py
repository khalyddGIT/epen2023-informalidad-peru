from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import pandas as pd
import numpy as np
import psycopg2
from sklearn.linear_model import LinearRegression
import os

app = FastAPI(
    title="API REST EPEN 2023 - INEI Perú (PostgreSQL Direct)",
    description="API conectada a PostgreSQL local (db_epen2023) para servir indicadores, informalidad y modelo ML.",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Conexión a PostgreSQL
DB_HOST = "localhost"
DB_PORT = 5432
DB_USER = "postgres"
DB_PASS = "root"
DB_NAME = "db_epen2023"

def get_db_connection():
    try:
        return psycopg2.connect(dbname=DB_NAME, user=DB_USER, password=DB_PASS, host=DB_HOST, port=DB_PORT)
    except Exception as e:
        print("Error al conectar a PostgreSQL:", e)
        return None

# Cargar datos para el modelo ML en memoria
BASE_DIR = r"d:\Escritorio\Data\processed_tables"
fact = pd.read_csv(os.path.join(BASE_DIR, "fact_empleo.csv"))
dim_dept = pd.read_csv(os.path.join(BASE_DIR, "dim_departamento.csv"))
dim_demog = pd.read_csv(os.path.join(BASE_DIR, "dim_demografia.csv"))
dim_cond = pd.read_csv(os.path.join(BASE_DIR, "dim_condicion_laboral.csv"))

df = fact.merge(dim_dept, on='IdDepartamento')
df = df.merge(dim_demog, on='IdDemografia')
df = df.merge(dim_cond, on='IdCondicion')

df_ocup = df[(df['DescCondicion'] == 'Ocupado') & (df['IngresoTotal'] > 0) & (df['IngresoTotal'] < 15000)].copy()
X_ml = df_ocup[['HorasTrabajadas', 'Edad']]
y_ml = df_ocup['IngresoTotal']
ml_model = LinearRegression()
ml_model.fit(X_ml, y_ml)

ing_mes_mean = df_ocup.groupby('Mes')['IngresoTotal'].mean().reset_index()
X_time = ing_mes_mean[['Mes']].values
y_time = ing_mes_mean['IngresoTotal'].values
time_model = LinearRegression()
time_model.fit(X_time, y_time)

class PredictRequest(BaseModel):
    horas_trabajadas: float
    edad: float

@app.get("/")
def read_root():
    conn = get_db_connection()
    db_status = "Conectado a PostgreSQL (db_epen2023)" if conn else "Fallback a archivos CSV"
    if conn: conn.close()
    return {"message": "API REST EPEN 2023 activa", "database": db_status}

@app.get("/api/kpis")
def get_kpis():
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM Fact_Empleo;")
            total_encuestados = cursor.fetchone()[0]
            
            cursor.execute("""
                SELECT 
                    ROUND((SUM(CASE WHEN c.DescripcionInformalidad = 'Informal' THEN 1.0 ELSE 0.0 END) * 100.0) / 
                    NULLIF(SUM(CASE WHEN c.DescripcionInformalidad IN ('Informal', 'Formal') THEN 1.0 ELSE 0.0 END), 0), 2)
                FROM Fact_Empleo f
                JOIN Dim_CondicionLaboral c ON f.IdCondicion = c.IdCondicion;
            """)
            tasa_informalidad = float(cursor.fetchone()[0])
            
            cursor.execute("SELECT ROUND(AVG(IngresoTotal), 2) FROM Fact_Empleo WHERE IngresoTotal > 0;")
            ingreso_medio = float(cursor.fetchone()[0])
            
            cursor.execute("SELECT ROUND(SUM(FactorPonderador), 0) FROM Fact_Empleo WHERE IngresoTotal > 0;")
            poblacion_ocupada_estimada = float(cursor.fetchone()[0])
            
            cursor.close()
            conn.close()
            return {
                "total_encuestados": total_encuestados,
                "tasa_informalidad_porcentaje": tasa_informalidad,
                "ingreso_medio_soles": ingreso_medio,
                "poblacion_ocupada_estimada": poblacion_ocupada_estimada,
                "fuente": "PostgreSQL Direct DB"
            }
        except Exception as e:
            print("Fallback CSV en /api/kpis:", e)

    df_inf = df[df['DescInformalidad'].isin(['Informal', 'Formal'])]
    return {
        "total_encuestados": len(df),
        "tasa_informalidad_porcentaje": round((df_inf['DescInformalidad'] == 'Informal').sum() / len(df_inf) * 100, 2),
        "ingreso_medio_soles": round(float(df_ocup['IngresoTotal'].mean()), 2),
        "poblacion_ocupada_estimada": round(float(df_ocup['FactorPonderador'].sum()), 0),
        "fuente": "CSV Fallback"
    }

@app.get("/api/departamentos")
def get_departamentos():
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT IdDepartamento, NombreDepartamento, RegionNatural, Total_Encuestados, Total_Informales, Total_Formales, Tasa_Informalidad_Porcentaje FROM vw_resumen_informalidad_departamento;")
            rows = cursor.fetchall()
            
            resumen = []
            for row in rows:
                dept_id = row[0]
                nombre = row[1]
                region = row[2]
                tasa_inf = float(row[6]) if row[6] is not None else 0.0
                
                # Obtener ingreso medio
                cursor.execute(f"SELECT ROUND(AVG(IngresoTotal), 2) FROM Fact_Empleo WHERE IdDepartamento = {dept_id} AND IngresoTotal > 0;")
                ing_row = cursor.fetchone()
                ingreso_medio = float(ing_row[0]) if ing_row and ing_row[0] is not None else 0.0
                
                resumen.append({
                    "id_departamento": dept_id,
                    "nombre": nombre,
                    "region": region,
                    "tasa_informalidad": tasa_inf,
                    "ingreso_medio": ingreso_medio,
                    "total_encuestados": row[3]
                })
            cursor.close()
            conn.close()
            return sorted(resumen, key=lambda x: x['tasa_informalidad'], reverse=True)
        except Exception as e:
            print("Fallback CSV en /api/departamentos:", e)

    resumen = []
    df_inf = df[df['DescInformalidad'].isin(['Informal', 'Formal'])]
    for dept_id, group in df.groupby('IdDepartamento'):
        nombre = group['NombreDepartamento'].iloc[0]
        region = group['RegionNatural'].iloc[0]
        sub_inf = df_inf[df_inf['IdDepartamento'] == dept_id]
        tasa_inf = round((sub_inf['DescInformalidad'] == 'Informal').sum() / len(sub_inf) * 100, 2) if len(sub_inf) > 0 else 0
        sub_ocup = group[(group['DescCondicion'] == 'Ocupado') & (group['IngresoTotal'] > 0)]
        ingreso_medio = round(float(sub_ocup['IngresoTotal'].mean()), 2) if len(sub_ocup) > 0 else 0
        
        resumen.append({
            "id_departamento": int(dept_id),
            "nombre": nombre,
            "region": region,
            "tasa_informalidad": tasa_inf,
            "ingreso_medio": ingreso_medio,
            "total_encuestados": len(group)
        })
    return sorted(resumen, key=lambda x: x['tasa_informalidad'], reverse=True)

@app.get("/api/brecha-genero")
def get_brecha_genero():
    brecha_df = df_ocup.groupby(['GrupoEdad', 'DescSexo'])['IngresoTotal'].mean().reset_index()
    resultado = []
    for grupo, g_df in brecha_df.groupby('GrupoEdad'):
        item = {"grupo_edad": grupo, "Hombre": 0, "Mujer": 0}
        for _, row in g_df.iterrows():
            if row['DescSexo'] in ['Hombre', 'Mujer']:
                item[row['DescSexo']] = round(float(row['IngresoTotal']), 2)
        resultado.append(item)
    return resultado

@app.get("/api/tendencia-mensual")
def get_tendencia_mensual():
    meses_nombre = ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun', 'Jul', 'Ago', 'Set', 'Oct', 'Nov', 'Dic']
    tend_mes = df_ocup.groupby('Mes')['FactorPonderador'].sum().reset_index()
    resultado = []
    for idx, row in tend_mes.iterrows():
        mes_num = int(row['Mes'])
        resultado.append({
            "mes_num": mes_num,
            "mes_nombre": meses_nombre[mes_num - 1],
            "poblacion_ocupada_millones": round(float(row['FactorPonderador']) / 1e6, 3)
        })
    return resultado

@app.get("/api/proyeccion")
def get_proyeccion():
    proyecciones = []
    for anio in range(2024, 2029):
        mes_inicio = (anio - 2023) * 12 + 1
        mes_fin = mes_inicio + 11
        m_range = np.arange(mes_inicio, mes_fin + 1).reshape(-1, 1)
        prom_anio = float(time_model.predict(m_range).mean())
        proyecciones.append({
            "anio": anio,
            "ingreso_proyectado": round(prom_anio, 2)
        })
    return {
        "modelo_ecuacion": f"Ingreso = {ml_model.intercept_:.2f} + ({ml_model.coef_[0]:.2f} * Horas) + ({ml_model.coef_[1]:.2f} * Edad)",
        "r2_score": round(float(ml_model.score(X_ml, y_ml)), 4),
        "coeficientes": {
            "intercepto": round(float(ml_model.intercept_), 2),
            "horas_trabajadas": round(float(ml_model.coef_[0]), 2),
            "edad": round(float(ml_model.coef_[1]), 2)
        },
        "proyeccion_5_anios": proyecciones
    }

@app.post("/api/predict")
def predict_ingreso(data: PredictRequest):
    if data.horas_trabajadas < 0 or data.edad < 14:
        raise HTTPException(status_code=400, detail="Horas o edad inválidas")
    
    pred = float(ml_model.predict([[data.horas_trabajadas, data.edad]])[0])
    return {
        "horas_trabajadas": data.horas_trabajadas,
        "edad": data.edad,
        "ingreso_estimado_soles": round(max(0, pred), 2)
    }
