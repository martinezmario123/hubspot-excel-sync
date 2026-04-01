import requests
import pandas as pd
import os
from dotenv import load_dotenv

load_dotenv()

def sincronizacion_final_confirmada():
    token = os.getenv('HUBSPOT_ACCESS_TOKEN')
    headers = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}
    
    # 1. Leer el Excel
    df = pd.read_csv('clientes_hubspot.csv')
    df['CIF'] = df['CIF'].astype(str).str.strip()

    # 2. Obtener los Negocios
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
                
                # 3. Buscar el Proyecto asociado a este Negocio específico
                url_asoc = f"https://api.hubapi.com/crm/v3/objects/deals/{deal_id}/associations/0-970"
                res_asoc = requests.get(url_asoc, headers=headers)
                
                if res_asoc.status_code == 200:
                    asociaciones = res_asoc.json().get('results', [])
                    for asoc in asociaciones:
                        proy_id = asoc['id']
                        print(f"🚀 Actualizando Proyecto {proy_id} con datos de {info['Empresa']}...")
                        
                        # 4. Inyectar datos en el Proyecto
                        url_proy = f"https://api.hubapi.com/crm/v3/objects/0-970/{proy_id}"
                        payload = {
                            "properties": {
                                "ciudad": str(info['Ciudad']),
                                "direccion": str(info.get('Direccion', ''))
                            }
                        }
                        requests.patch(url_proy, headers=headers, json=payload)
        print("\n🏁 ¡Sincronización terminada! Revisa tus Proyectos.")
    else:
        print(f"❌ Error: {res_deals.status_code}")

if __name__ == "__main__":
    sincronizacion_final_confirmada()
