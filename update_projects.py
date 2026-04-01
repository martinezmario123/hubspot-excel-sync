import requests
import pandas as pd
import os
from dotenv import load_dotenv

load_dotenv()

def sincronizacion_con_chivato():
    token = os.getenv('HUBSPOT_ACCESS_TOKEN')
    headers = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}
    
    df = pd.read_csv('clientes_hubspot.csv')
    df['CIF'] = df['CIF'].astype(str).str.strip()

    url_deals = "https://api.hubapi.com/crm/v3/objects/deals"
    res_deals = requests.get(url_deals, headers=headers, params={'properties': 'cif,dealname'})
    
    if res_deals.status_code == 200:
        for deal in res_deals.json().get('results', []):
            deal_id = deal['id']
            cif_hs = str(deal['properties'].get('cif', '')).strip()
            nombre_n = deal['properties'].get('dealname')
            
            match = df[df['CIF'] == cif_hs]
            if not match.empty:
                info = match.iloc[0]
                nueva_ciudad = str(info['Ciudad'])
                
                # Buscar el Proyecto
                url_asoc = f"https://api.hubapi.com/crm/v3/objects/deals/{deal_id}/associations/0-970"
                res_asoc = requests.get(url_asoc, headers=headers)
                
                if res_asoc.status_code == 200:
                    for asoc in res_asoc.json().get('results', []):
                        proy_id = asoc['id']
                        
                        # --- EL CHIVATO ---
                        # Antes de actualizar, preguntamos qué tiene el proyecto ahora mismo
                        url_get = f"https://api.hubapi.com/crm/v3/objects/0-970/{proy_id}?properties=ciudad,direccion"
                        get_proy = requests.get(url_get, headers=headers).json()
                        ciudad_actual = get_proy.get('properties', {}).get('ciudad', 'VACÍO')
                        
                        print(f"🔎 PROYECTO {proy_id} ({nombre_n}):")
                        print(f"   Valor actual en HubSpot: '{ciudad_actual}'")
                        print(f"   Valor en el Excel: '{nueva_ciudad}'")
                        
                        # Intentar actualizar
                        payload = {"properties": {"ciudad": nueva_ciudad}}
                        r = requests.patch(f"https://api.hubapi.com/crm/v3/objects/0-970/{proy_id}", headers=headers, json=payload)
                        
                        if r.status_code in [200, 204]:
                            print(f"   ✅ ¡Actualizado con éxito a {nueva_ciudad}!")
                        else:
                            print(f"   ❌ Error al actualizar: {r.text}")
        print("\n🏁 Revisión terminada.")

if __name__ == "__main__":
    sincronizacion_con_chivato()
