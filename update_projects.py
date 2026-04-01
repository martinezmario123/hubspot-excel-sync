import requests
import pandas as pd
import os
import time
from dotenv import load_dotenv

load_dotenv()

def sincronizacion_final_total():
    token = os.getenv('HUBSPOT_ACCESS_TOKEN')
    headers = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}
    
    # 1. Leer el Excel
    df = pd.read_csv('clientes_hubspot.csv')
    df['CIF'] = df['CIF'].astype(str).str.strip()

    # 2. Obtener todos los Negocios para cruzar por CIF
    url_deals = "https://api.hubapi.com/crm/v3/objects/deals"
    res_deals = requests.get(url_deals, headers=headers, params={'properties': 'cif,dealname'})
    
    if res_deals.status_code == 200:
        for deal in res_deals.json().get('results', []):
            deal_id = deal['id']
            cif_hs = str(deal['properties'].get('cif', '')).strip()
            
            # Buscar coincidencia en el Excel
            match = df[df['CIF'] == cif_hs]
            if not match.empty:
                info = match.iloc[0]
                empresa = info['Empresa']
                
                # 3. Buscar Proyectos asociados a este Negocio (Objeto 0-970)
                url_asoc = f"https://api.hubapi.com/crm/v3/objects/deals/{deal_id}/associations/0-970"
                res_asoc = requests.get(url_asoc, headers=headers).json()
                
                for asoc in res_asoc.get('results', []):
                    proy_id = asoc['id']
                    
                    # 4. Actualizar Ciudad y Dirección
                    url_upd = f"https://api.hubapi.com/crm/v3/objects/0-970/{proy_id}"
                    payload = {
                        "properties": {
                            "ciudad": str(info['Ciudad']),
                            "direccion": str(info.get('Direccion', ''))
                        }
                    }
                    
                    r = requests.patch(url_upd, headers=headers, json=payload)
                    if r.status_code in [200, 204]:
                        print(f"✅ {empresa}: Actualizado con Ciudad '{info['Ciudad']}'")
                    else:
                        print(f"❌ Error en {empresa}: {r.text}")
        
        print("\n🏁 ¡PROCESO COMPLETADO! Ve a HubSpot y actualiza la página.")
    else:
        print(f"❌ Error de conexión inicial: {res_deals.status_code}")

if __name__ == "__main__":
    sincronizacion_final_total()
