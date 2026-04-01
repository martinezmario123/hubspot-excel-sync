import requests
import pandas as pd
import os
from dotenv import load_dotenv

load_dotenv()

def sincronizar():
    token = os.getenv('HUBSPOT_ACCESS_TOKEN')
    headers = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}
    
    # 1. Leer Excel
    df = pd.read_csv('clientes_hubspot.csv')
    df['CIF'] = df['CIF'].astype(str).str.strip()

    # 2. Consultar Negocios (Donde ahora vive tu pipeline de Proyectos)
    url = "https://api.hubapi.com/crm/v3/objects/deals"
    params = {'properties': 'cif,dealname,ciudad,direccion,cp', 'limit': 100}
    
    res = requests.get(url, headers=headers, params=params)
    
    if res.status_code == 200:
        items = res.json().get('results', [])
        for item in items:
            cif_hs = str(item['properties'].get('cif', '')).strip()
            match = df[df['CIF'] == cif_hs]
            
            if not match.empty:
                info = match.iloc[0]
                print(f"🏗️ Sincronizando: {info['Empresa']}")
                payload = {
                    "properties": {
                        "dealname": str(info['Empresa']),
                        "ciudad": str(info['Ciudad']),
                        "direccion": str(info.get('Direccion', '')),
                        "cp": str(info.get('CP', ''))
                    }
                }
                requests.patch(f"{url}/{item['id']}", headers=headers, json=payload)
        print("✅ Proceso finalizado.")
    else:
        print(f"❌ Error: {res.status_code}")

if __name__ == "__main__":
    sincronizar()
