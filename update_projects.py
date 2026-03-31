import requests
import pandas as pd
import os
from dotenv import load_dotenv

load_dotenv()

def ejecutar_sincronizacion():
    token = os.getenv('HUBSPOT_ACCESS_TOKEN') or os.getenv('HS_ACCESS_TOKEN')
    headers = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}
    
    # 1. Leer CSV
    df = pd.read_csv('clientes_hubspot.csv')
    df['CIF'] = df['CIF'].astype(str).str.strip()

    # 2. Consultar Negocios - Pedimos explícitamente cif y ciudad
    url = "https://api.hubapi.com/crm/v3/objects/deals"
    res = requests.get(url, headers=headers, params={'properties': 'cif,ciudad,dealname'})
    
    if res.status_code == 200:
        items = res.json().get('results', [])
        for item in items:
            props = item['properties']
            cif_hs = str(props.get('cif', '')).strip()
            
            # Buscar en el Excel
            match = df[df['CIF'] == cif_hs]
            
            if not match.empty:
                info = match.iloc[0]
                deal_id = item['id']
                nueva_ciudad = str(info['Ciudad'])
                nuevo_nombre = str(info['Empresa'])

                print(f"🔄 Intentando actualizar Negocio ID: {deal_id}")
                print(f"👉 Datos a enviar: Nombre='{nuevo_nombre}', Ciudad='{nueva_ciudad}'")

                payload = {
                    "properties": {
                        "dealname": nuevo_nombre,
                        "ciudad": nueva_ciudad
                    }
                }
                
                upd = requests.patch(f"{url}/{deal_id}", headers=headers, json=payload)
                
                if upd.status_code == 200:
                    print(f"✅ RESPUESTA HUBSPOT: OK (200). Los datos ya deberían estar allí.")
                else:
                    print(f"❌ RESPUESTA HUBSPOT ERROR: {upd.status_code} - {upd.text}")
    else:
        print(f"❌ Error de conexión inicial: {res.status_code}")

if __name__ == "__main__":
    ejecutar_sincronizacion()
