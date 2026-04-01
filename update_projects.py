import requests
import pandas as pd
import os
from dotenv import load_dotenv

load_dotenv()

def ejecutar_sincronizacion():
    token = os.getenv('HUBSPOT_ACCESS_TOKEN')
    headers = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}
    
    # 1. Leer el CSV
    df = pd.read_csv('clientes_hubspot.csv')
    df['CIF'] = df['CIF'].astype(str).str.strip()

    # 2. Intentar acceso a Proyectos (0-970)
    url = "https://api.hubapi.com/crm/v3/objects/0-970"
    params = {'properties': 'cif,name,ciudad,direccion,cp', 'limit': 100}
    
    print(f"📡 Conectando con Proyectos usando Token nuevo...")
    res = requests.get(url, headers=headers, params=params)
    
    if res.status_code == 200:
        items = res.json().get('results', [])
        print(f"✅ ¡CONECTADO! Encontrados {len(items)} proyectos.")
        
        for item in items:
            cif_hs = str(item['properties'].get('cif', '')).strip()
            match = df[df['CIF'] == cif_hs]
            
            if not match.empty:
                info = match.iloc[0]
                print(f"🏗️ Actualizando: {info['Empresa']} (CIF: {cif_hs})")
                payload = {"properties": {"name": str(info['Empresa']), "ciudad": str(info['Ciudad'])}}
                upd = requests.patch(f"{url}/{item['id']}", headers=headers, json=payload)
                print(f"   Resultado: {upd.status_code}")
    else:
        print(f"❌ Error {res.status_code}: {res.text}")

if __name__ == "__main__":
    ejecutar_sincronizacion()
