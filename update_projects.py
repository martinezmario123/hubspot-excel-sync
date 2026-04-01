import requests
import pandas as pd
import os
from dotenv import load_dotenv

load_dotenv()

def sincronizacion_final_validada():
    token = os.getenv('HUBSPOT_ACCESS_TOKEN')
    headers = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}
    
    # 1. Leer el Excel de GitHub
    df = pd.read_csv('clientes_hubspot.csv')
    df['CIF'] = df['CIF'].astype(str).str.strip()

    # 2. Consultar Negocios para encontrar los Proyectos asociados
    url_deals = "https://api.hubapi.com/crm/v3/objects/deals"
    # Pedimos el CIF para saber quién es quién
    res_deals = requests.get(url_deals, headers=headers, params={'properties': 'cif,dealname'})
    
    if res_deals.status_code == 200:
        for deal in res_deals.json().get('results', []):
            deal_id = deal['id']
            cif_hs = str(deal['properties'].get('cif', '')).strip()
            
            # Buscamos el CIF en el Excel
            match = df[df['CIF'] == cif_hs]
            if not match.empty:
                info = match.iloc[0]
                
                # 3. Buscar el Proyecto (0-970) asociado a este Negocio
                url_asoc = f"https://api.hubapi.com/crm/v3/objects/deals/{deal_id}/associations/0-970"
                res_asoc = requests.get(url_asoc, headers=headers)
                
                if res_asoc.status_code == 200:
                    asociaciones = res_asoc.json().get('results', [])
                    for asoc in asociaciones:
                        proy_id = asoc['id']
                        print(f"🚀 Sincronizando {info['Empresa']} -> Proyecto {proy_id}")
                        
                        # 4. Actualizamos usando los NOMBRES INTERNOS de tu escaneo
                        url_upd = f"https://api.hubapi.com/crm/v3/objects/0-970/{proy_id}"
                        payload = {
                            "properties": {
                                "ciudad": str(info['Ciudad']),
                                "direccion": str(info.get('Direccion', '')),
                                "codigo_postal": str(info.get('CP', '')) # Usamos el nombre de tu escaneo
                            }
                        }
                        r = requests.patch(url_upd, headers=headers, json=payload)
                        print(f"   📥 Resultado: {r.status_code} (Datos enviados: {info['Ciudad']})")
        print("\n🏁 Proceso terminado.")
    else:
        print(f"❌ Error al leer negocios: {res_deals.text}")

if __name__ == "__main__":
    sincronizacion_final_validada()
