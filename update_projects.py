import requests
import os
import pandas as pd
from dotenv import load_dotenv

load_dotenv()

def actualizar_proyectos_directo():
    token = os.getenv('HUBSPOT_ACCESS_TOKEN')
    headers = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}
    
    # 1. Leer el CSV (Asegúrate de que el CIF 4587965Y esté en el Excel)
    df = pd.read_csv('clientes_hubspot.csv')
    df['CIF'] = df['CIF'].astype(str).str.strip()

    # 2. PROBAMOS CON EL NOMBRE TÉCNICO ESTÁNDAR
    # Intentaremos con 'p_proyectos'. Si falla, probaremos con 'proyectos'
    nombre_objeto = "p_proyectos" 
    url = f"https://api.hubapi.com/crm/v3/objects/{nombre_objeto}"
    
    print(f"🚀 Intentando conexión directa a: {nombre_objeto}")
    params = {'properties': 'cif,name,ciudad', 'limit': 100}
    res = requests.get(url, headers=headers, params=params)
    
    # Si da error, probamos la segunda opción común
    if res.status_code != 200:
        nombre_objeto = "proyectos"
        url = f"https://api.hubapi.com/crm/v3/objects/{nombre_objeto}"
        print(f"🔄 Reintentando con: {nombre_objeto}")
        res = requests.get(url, headers=headers, params=params)

    if res.status_code == 200:
        items = res.json().get('results', [])
        print(f"✅ ¡CONECTADO! Encontrados {len(items)} proyectos.")
        
        for item in items:
            cif_hs = str(item['properties'].get('cif', '')).strip()
            match = df[df['CIF'] == cif_hs]
            
            if not match.empty:
                info = match.iloc[0]
                print(f"🏗️ Actualizando: {info['Empresa']}")
                payload = {
                    "properties": {
                        "name": str(info['Empresa']),
                        "ciudad": str(info['Ciudad'])
                    }
                }
                upd = requests.patch(f"{url}/{item['id']}", headers=headers, json=payload)
                print(f"   Resultado: {upd.status_code}")
    else:
        print(f"❌ Error final {res.status_code}: {res.text}")
        print("👉 Si sale 403, ve a la configuración del Objeto 'Proyecto' y busca el 'Nombre Interno'.")

if __name__ == "__main__":
    actualizar_proyectos_directo()
