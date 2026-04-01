import requests
import pandas as pd
import os
from dotenv import load_dotenv

load_dotenv()

def sincronizacion_forzada():
    token = os.getenv('HUBSPOT_ACCESS_TOKEN')
    headers = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}
    
    df = pd.read_csv('clientes_hubspot.csv')
    df['CIF'] = df['CIF'].astype(str).str.strip()

    # Buscamos el Negocio de Mercadona directamente para esta prueba
    url_deals = "https://api.hubapi.com/crm/v3/objects/deals"
    res_deals = requests.get(url_deals, headers=headers, params={'properties': 'cif,dealname'})
    
    for deal in res_deals.json().get('results', []):
        if "Mercadona" in deal['properties'].get('dealname', ''):
            deal_id = deal['id']
            # Buscamos el proyecto asociado
            url_asoc = f"https://api.hubapi.com/crm/v3/objects/deals/{deal_id}/associations/0-970"
            res_asoc = requests.get(url_asoc, headers=headers).json()
            
            for asoc in res_asoc.get('results', []):
                proy_id = asoc['id']
                print(f"🛠️ Forzando actualización en Proyecto ID: {proy_id}")
                
                # ACTUALIZAMOS
                url_upd = f"https://api.hubapi.com/crm/v3/objects/0-970/{proy_id}"
                payload = {"properties": {"ciudad": "ALICANTE_TEST", "direccion": "DIRECCION_TEST"}}
                requests.patch(url_upd, headers=headers, json=payload)
                
                # COMPROBAMOS INMEDIATAMENTE
                res_check = requests.get(f"{url_upd}?properties=ciudad", headers=headers).json()
                valor_final = res_check.get('properties', {}).get('ciudad')
                
                print(f"📢 Verificación post-vuelo: En la base de datos de HubSpot ahora pone: '{valor_final}'")

if __name__ == "__main__":
    sincronizacion_forzada()
