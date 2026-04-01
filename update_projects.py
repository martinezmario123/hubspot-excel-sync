import requests
import pandas as pd
import os
from dotenv import load_dotenv

load_dotenv()

def buscar_y_actualizar():
    token = os.getenv('HUBSPOT_ACCESS_TOKEN')
    headers = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}
    
    # 1. Leer el CSV
    df = pd.read_csv('clientes_hubspot.csv')
    df['CIF'] = df['CIF'].astype(str).str.strip()

    # 2. Usar el Endpoint de BÚSQUEDA (Search)
    # Este endpoint suele saltarse las restricciones de nombre técnico
    url_search = "https://api.hubapi.com/crm/v3/objects/0-970/search"
    
    print("🔎 Intentando localizar proyectos vía API de Búsqueda...")

    # Vamos a buscar TODOS los proyectos (máximo 100)
    payload_search = {
        "properties": ["cif", "name", "ciudad", "direccion", "cp"],
        "limit": 100
    }

    res = requests.post(url_search, headers=headers, json=payload_search)
    
    if res.status_code == 200:
        items = res.json().get('results', [])
        print(f"✅ ¡ÉXITO! La búsqueda funcionó. Encontrados {len(items)} proyectos.")
        
        for item in items:
            props = item['properties']
            cif_hs = str(props.get('cif', '')).strip()
            
            match = df[df['CIF'] == cif_hs]
            if not match.empty:
                info = match.iloc[0]
                print(f"🏗️ Match encontrado para CIF {cif_hs}. Actualizando...")

                url_update = f"https://api.hubapi.com/crm/v3/objects/0-970/{item['id']}"
                payload_upd = {
                    "properties": {
                        "name": str(info['Empresa']),
                        "ciudad": str(info['Ciudad'])
                    }
                }
                upd = requests.patch(url_update, headers=headers, json=payload_upd)
                print(f"   📥 Resultado actualización: {upd.status_code}")
    else:
        print(f"❌ La búsqueda también falló (Error {res.status_code})")
        print(f"Mensaje: {res.text}")

if __name__ == "__main__":
    buscar_y_actualizar()
