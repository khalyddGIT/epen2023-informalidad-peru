import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.linear_model import LinearRegression
import os

# Configuración estética de gráficos
plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.size'] = 11

output_img_dir = r"d:\Escritorio\Data\graficos"
os.makedirs(output_img_dir, exist_ok=True)

print("=== CARGANDO TABLAS NORMALIZADAS Y DATOS DEL PROYECTO ===")
fact = pd.read_csv(r"d:\Escritorio\Data\processed_tables\fact_empleo.csv")
dim_dept = pd.read_csv(r"d:\Escritorio\Data\processed_tables\dim_departamento.csv")
dim_demog = pd.read_csv(r"d:\Escritorio\Data\processed_tables\dim_demografia.csv")
dim_cond = pd.read_csv(r"d:\Escritorio\Data\processed_tables\dim_condicion_laboral.csv")

# Merge para análisis completo
df = fact.merge(dim_dept, on='IdDepartamento')
df = df.merge(dim_demog, on='IdDemografia')
df = df.merge(dim_cond, on='IdCondicion')

print(f"Total registros para análisis: {len(df):,}")

# --- 1. TASA DE INFORMALIDAD POR DEPARTAMENTO ---
df_inf = df[df['DescInformalidad'].isin(['Informal', 'Formal'])].copy()
tasa_inf = df_inf.groupby('NombreDepartamento')['DescInformalidad'].apply(
    lambda x: (x == 'Informal').sum() / len(x) * 100
).reset_index(name='Tasa_Informalidad')
tasa_inf = tasa_inf.sort_values(by='Tasa_Informalidad', ascending=False)

plt.figure(figsize=(12, 6))
barplot = sns.barplot(data=tasa_inf, x='NombreDepartamento', y='Tasa_Informalidad', palette='Reds_r')
plt.xticks(rotation=60, ha='right', fontsize=10)
plt.title('Tasa de Informalidad Laboral por Departamento (EPEN 2023)', fontsize=14, fontweight='bold', pad=15)
plt.xlabel('Departamento', fontweight='bold')
plt.ylabel('Tasa de Informalidad (%)', fontweight='bold')
plt.ylim(0, 100)

for p in barplot.patches:
    barplot.annotate(f'{p.get_height():.1f}%', 
                     (p.get_x() + p.get_width() / 2., p.get_height()), 
                     ha='center', va='bottom', fontsize=8, rotation=45, xytext=(0, 3), 
                     textcoords='offset points')

plt.tight_layout()
path_inf = os.path.join(output_img_dir, 'tasa_informalidad_dpto.png')
plt.savefig(path_inf, dpi=300)
plt.close()
print(f"[GRÁFICO] Guardado: {path_inf}")

# --- 2. INGRESO PROMEDIO MENSUAL POR DEPARTAMENTO ---
df_ocup = df[(df['DescCondicion'] == 'Ocupado') & (df['IngresoTotal'] > 0)].copy()
ing_dept = df_ocup.groupby('NombreDepartamento')['IngresoTotal'].mean().reset_index(name='Ingreso_Promedio')
ing_dept = ing_dept.sort_values(by='Ingreso_Promedio', ascending=False)

plt.figure(figsize=(12, 6))
barplot = sns.barplot(data=ing_dept, x='NombreDepartamento', y='Ingreso_Promedio', palette='Blues_r')
plt.xticks(rotation=60, ha='right', fontsize=10)
plt.title('Ingreso Promedio Mensual (S/.) por Departamento (EPEN 2023)', fontsize=14, fontweight='bold', pad=15)
plt.xlabel('Departamento', fontweight='bold')
plt.ylabel('Ingreso Promedio (S/.)', fontweight='bold')

for p in barplot.patches:
    barplot.annotate(f'S/.{p.get_height():.0f}', 
                     (p.get_x() + p.get_width() / 2., p.get_height()), 
                     ha='center', va='bottom', fontsize=8, rotation=45, xytext=(0, 3), 
                     textcoords='offset points')

plt.tight_layout()
path_ing = os.path.join(output_img_dir, 'ingreso_promedio_dpto.png')
plt.savefig(path_ing, dpi=300)
plt.close()
print(f"[GRÁFICO] Guardado: {path_ing}")

# --- 3. BRECHA DE INGRESO POR GÉNERO Y GRUPO DE EDAD ---
brecha = df_ocup.groupby(['GrupoEdad', 'DescSexo'])['IngresoTotal'].mean().reset_index()

plt.figure(figsize=(10, 5))
sns.barplot(data=brecha, x='GrupoEdad', y='IngresoTotal', hue='DescSexo', palette='Set2')
plt.title('Ingreso Promedio Mensual por Género y Grupo de Edad', fontsize=13, fontweight='bold', pad=15)
plt.xlabel('Grupo de Edad', fontweight='bold')
plt.ylabel('Ingreso Promedio Mensual (S/.)', fontweight='bold')
plt.legend(title='Sexo')
plt.tight_layout()
path_brecha = os.path.join(output_img_dir, 'brecha_ingreso_genero.png')
plt.savefig(path_brecha, dpi=300)
plt.close()
print(f"[GRÁFICO] Guardado: {path_brecha}")

# --- 4. TENDENCIA MENSUAL DE EMPLEADOS EN EL AÑO 2023 ---
tend_mes = df_ocup.groupby('Mes')['FactorPonderador'].sum().reset_index(name='Poblacion_Ocupada_Estimada')

plt.figure(figsize=(9, 4.5))
plt.plot(tend_mes['Mes'], tend_mes['Poblacion_Ocupada_Estimada'] / 1e6, marker='o', color='#2b5c8f', linewidth=2.5)
plt.title('Evolución Mensual de la Población Ocupada Estimada - 2023', fontsize=13, fontweight='bold', pad=15)
plt.xlabel('Mes del Año 2023', fontweight='bold')
plt.ylabel('Población Ocupada (Millones)', fontweight='bold')
plt.xticks(range(1, 13), ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun', 'Jul', 'Ago', 'Set', 'Oct', 'Nov', 'Dic'])
plt.grid(True, linestyle='--', alpha=0.6)
plt.tight_layout()
path_tend = os.path.join(output_img_dir, 'tendencia_empleo_mensual.png')
plt.savefig(path_tend, dpi=300)
plt.close()
print(f"[GRÁFICO] Guardado: {path_tend}")

# --- 5. MODELO PREDICTIVO Y PROYECCIÓN FUTURA (REGRESIÓN LINEAL) ---
# Modelo 1: Regresión Lineal de Ingreso Total (Y) vs Horas Trabajadas (X1) y Edad (X2)
df_reg = df_ocup[(df_ocup['HorasTrabajadas'] > 0) & (df_ocup['IngresoTotal'] > 0) & (df_ocup['IngresoTotal'] < 15000)].copy()

X = df_reg[['HorasTrabajadas', 'Edad']]
Y = df_reg['IngresoTotal']

model = LinearRegression()
model.fit(X, Y)

intercept = model.intercept_
coef_horas = model.coef_[0]
coef_edad = model.coef_[1]
r2 = model.score(X, Y)

print("\n=== RESULTADOS DEL MODELO PREDICTIVO (REGRESIÓN LINEAL) ===")
print(f"Ecuación: Ingreso = {intercept:.2f} + ({coef_horas:.2f} * HorasTrabajadas) + ({coef_edad:.2f} * Edad)")
print(f"Coeficiente R²: {r2:.4f}")

# Proyección a nivel macro: Tendencia Temporal del Ingreso Promedio Mensual proyectado a 5 Años (2023 - 2028)
# Agrupamos por mes ordinal (1 a 12 de 2023) y proyectamos los próximos años
ing_mes_mean = df_ocup.groupby('Mes')['IngresoTotal'].mean().reset_index()
X_time = ing_mes_mean[['Mes']].values
Y_time = ing_mes_mean['IngresoTotal'].values

model_time = LinearRegression()
model_time.fit(X_time, Y_time)

# Proyectar meses futuros (2024=13..24, 2025=25..36, 2026=37..48, 2027=49..60, 2028=61..72)
future_months = np.arange(1, 73).reshape(-1, 1)
pred_future = model_time.predict(future_months)

plt.figure(figsize=(10, 5))
plt.scatter(X_time, Y_time, color='darkblue', label='Datos Históricos 2023 (Meses 1-12)', s=60)
plt.plot(future_months, pred_future, color='red', linestyle='--', label=f'Línea de Regresión y Proyección 2024-2028 (R²={model_time.score(X_time, Y_time):.2f})', linewidth=2)

plt.axvline(x=12.5, color='gray', linestyle=':', label='Límite Datos Reales 2023')
plt.title('Modelo Predictivo de Ingreso Promedio Mensual y Proyección Futura (2023 - 2028)', fontsize=13, fontweight='bold', pad=15)
plt.xlabel('Periodo Mensual (Mes 1 = Ene 2023, Mes 72 = Dic 2028)', fontweight='bold')
plt.ylabel('Ingreso Promedio Mensual Estimado (S/.)', fontweight='bold')
plt.legend()
plt.tight_layout()
path_pred = os.path.join(output_img_dir, 'modelo_prediccion_regresion.png')
plt.savefig(path_pred, dpi=300)
plt.close()
print(f"[GRÁFICO] Guardado: {path_pred}")

# Guardar proyecciones anuales estimadas
proyecciones = []
for anio in range(2024, 2029):
    mes_inicio = (anio - 2023) * 12 + 1
    mes_fin = mes_inicio + 11
    m_range = np.arange(mes_inicio, mes_fin + 1).reshape(-1, 1)
    prom_anio = model_time.predict(m_range).mean()
    proyecciones.append({'Año': anio, 'Ingreso_Promedio_Proyectado_Soles': round(prom_anio, 2)})

df_proy = pd.DataFrame(proyecciones)
print("\n--- PROYECCIÓN FUTURA PARA LOS PRÓXIMOS 5 AÑOS ---")
print(df_proy.to_string(index=False))

print("\n=== ANÁLISIS Y GENERACIÓN DE MODELO FINALIZADO CON ÉXITO ===")
