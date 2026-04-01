import requests
import pandas as pd
import os
from dotenv import load_dotenv

load_dotenv()

def escaneo_y_sincronizacion_final():
    token = os.getenv('HUBSPOT_ACCESS_TOKEN')
    headers = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}
    
    df = pd.read_csv('clientes_hubspot.csv')
    df['CIF'] = df['CIF'].astype(str).str.strip()

    # Buscamos negocios pidiendo TODAS las asociaciones posibles de forma genérica
    url_deals = "https://api.hubapi.com/crm/v3/objects/deals"
    params = {'associations': 'p147977807_proyectos,0-970', 'properties': 'cif,dealname', 'limit': 100}
    
    res = requests.get(url_deals, headers=headers, params=params)
    
    if res.status_code == 200:
        negocios = res.json().get('results', [])
        print(f"🧐 Analizando {len(negocios)} negocios...")

        for deal in negocios:
            nombre = deal['properties'].get('dealname', 'Sin nombre')
            cif_hs = str(deal['properties'].get('cif', '')).strip()
            
            match = df[df['CIF'] == cif_hs]
            if not match.empty:
                info = match.iloc[0]
                
                # BUSQUEDA AGRESIVA DE ASOCIACIONES
                asoc_data = deal.get('associations', {})
                proy_id = None
                
                # Miramos en todas las carpetas de asociaciones que nos devuelva HubSpot
                for key, value in asoc_data.items():
                    results = value.get('results', [])
                    if results:
                        proy_id = results[0]['id']
                        print(f"🏗️ ¡ENCONTRADO! Enlace mediante '{key}' para {nombre}")
                        break

                if proy_id:
                    print(f"🚀 Actualizando Proyecto {proy_id} con {info['Ciudad']}...")
                    url_p = f"https://api.hubapi.com/crm/v3/objects/0-970/{proy_id}"
                    payload = {
                        "properties": {
                            "ciudad": str(info['Ciudad']),
                            "direccion": str(info.get('Direccion', ''))
                        }
                    }
                    r = requests.patch(url_p, headers=headers, json=payload)
                    print(f"   📥 Resultado: {r.status_code}")
                else:
                    print(f"   ⚠️ '{nombre}' tiene el CIF OK, pero HubSpot no nos 'chiva' el ID del proyecto. Las claves que veo son: {list(asoc_data.keys())}")
    else:
        print(f"❌ Error API: {res.text}")

if __name__ == "__main__":
    escaneo_y_sincronizacion_final()
