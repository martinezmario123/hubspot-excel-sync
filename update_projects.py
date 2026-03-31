import requests
import pandas as pd
import os
from dotenv import load_dotenv

load_dotenv()

def ejecutar_sincronizacion():
    token = os.getenv('HUBSPOT_ACCESS_TOKEN') or os.getenv('HS_ACCESS_TOKEN')
    headers = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}
    
    # 1. LEER EL CSV (SOLO LECTURA)
    try:
        df = pd.read_csv('clientes_hubspot.csv')
        print(f"✅ Leídas {len(df)} empresas del archivo.")
    except Exception as e:
        print(f"❌ Error al leer el CSV: {e}")
        return

    df['CIF'] = df['CIF'].astype(str).str.strip()

    # 2. SECCIÓN DE NEGOCIOS
    url = "https://api.hubapi.com/crm/v3/objects/deals"
    res = requests.get(url, headers=headers, params={'properties': 'cif', 'limit': 100})
    
    if res.status_code == 200:
        items = res.json().get('results', [])
        for item in items:
            cif_hs = str(item['properties'].get('cif', '')).strip()
            match = df[df['CIF'] == cif_hs]
            
            if not match.empty:
                info = match.iloc[0]
                print(f"✨ ¡Match! Actualizando en HubSpot: {info['Empresa']}")

                # SOLO ENVIAMOS DATOS A HUBSPOT, NO GUARDAMOS NADA EN GITHUB
                payload = {
                    "properties": {
                        "dealname": info['Empresa'],
                        "ciudad": info['Ciudad'],
                        "direccion": str(info.get('Direccion', '')),
                        "cp": str(info.get('CP', ''))
                    }
                }
                requests.patch(f"{url}/{item['id']}", headers=headers, json=payload)
    else:
        print(f"❌ Error API HubSpot: {res.status_code}")

if __name__ == "__main__":
    ejecutar_sincronizacion()
