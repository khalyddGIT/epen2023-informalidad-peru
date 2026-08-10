import urllib.request
import json

url = "http://127.0.0.1:8000/api/departamentos"
try:
    with urllib.request.urlopen(url) as response:
        data = json.loads(response.read().decode())
        print("Backend Departamentos:")
        for d in data:
            print(f"id: {d.get('id_departamento')}, name: {d.get('nombre_departamento')}, tasa: {d.get('tasa_informalidad')}")
except Exception as e:
    print("Error querying API:", e)
