import os
import shutil

root_dir = r"d:\Escritorio\Data"

# Target directories
dirs_to_create = ["database", "docs", "etl", "scripts"]
for d in dirs_to_create:
    os.makedirs(os.path.join(root_dir, d), exist_ok=True)

# 1. Database files
db_files = ["schema_ddl.sql", "schema_postgresql.sql", "schema_sqlserver.sql", "setup_postgres_db.py"]
for f in db_files:
    src = os.path.join(root_dir, f)
    if os.path.exists(src):
        shutil.move(src, os.path.join(root_dir, "database", f))

# 2. Docs files
doc_files = ["DOCUMENTACION_DEL_SISTEMA.md", "API_DOCUMENTATION.md", "INFORME_TECNICO_EPEN2023.md", "ACTIVIDAD SEMANA 06.pdf", "BASE DE DATOS- ANALISIS-PREDICCION (1).docx"]
for f in doc_files:
    src = os.path.join(root_dir, f)
    if os.path.exists(src):
        shutil.move(src, os.path.join(root_dir, "docs", f))

# 3. ETL files
etl_files = ["etl_epen2023.py", "analisis_y_modelo.py", "generate_report_docx.py"]
for f in etl_files:
    src = os.path.join(root_dir, f)
    if os.path.exists(src):
        shutil.move(src, os.path.join(root_dir, "etl", f))

# Move processed_tables folder into etl/ if it exists in root
proc_tables_src = os.path.join(root_dir, "processed_tables")
proc_tables_dst = os.path.join(root_dir, "etl", "processed_tables")
if os.path.exists(proc_tables_src) and not os.path.exists(proc_tables_dst):
    shutil.move(proc_tables_src, proc_tables_dst)

# 4. Move all temporary python scripts and json files to scripts/
for item in os.listdir(root_dir):
    item_path = os.path.join(root_dir, item)
    if os.path.isfile(item_path):
        if item.endswith(".py") and item != "organize_project.py":
            shutil.move(item_path, os.path.join(root_dir, "scripts", item))
        elif item.endswith(".json"):
            shutil.move(item_path, os.path.join(root_dir, "scripts", item))
        elif item.endswith(".js"):
            shutil.move(item_path, os.path.join(root_dir, "scripts", item))

print("Organization complete!")
