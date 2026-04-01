import requests
import pandas as pd
import os
from dotenv import load_dotenv

load_dotenv()

def sincronizacion_definitiva():
    token = os.getenv('HUBSPOT_ACCESS_TOKEN')
    headers = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}
    
    # 1. Leer el Excel
    df = pd.read_csv('clientes_hubspot.csv')
    df['CIF'] = df['CIF'].astype(str).str.strip()

    # 2. Consultar Negocios pidiendo asociación con 0-970
    url_deals = "https://api.hubapi.com/crm/v3/objects/deals"
    params = {
        'associations': '0-970', 
        'properties': 'cif,dealname', 
        'limit': 100
    }
    
    res = requests.get(url_deals, headers=headers, params=params)
    
    if res.status_code == 200:
        negocios = res.json().get('results', [])
        print(f"🧐 Analizando {len(negocios)} negocios...")

        for deal in negocios:
            nombre = deal['properties'].get('dealname', 'Sin nombre')
            cif_hs = str(deal['properties'].get('cif', '')).strip()
            
            # Ver si el CIF coincide con el Excel
            match = df[df['CIF'] == cif_hs]
            if not match.empty:
                info = match.iloc[0]
                
                # Buscamos la asociación con el objeto 0-970
                asoc_data = deal.get('associations', {})
                # Buscamos en todas las claves por si HubSpot le cambia el nombre
                proyectos = []
                for key in asoc_data.keys():
                    if "0-970" in key:
                        proyectos = asoc_data[key].get('results', [])

                if proyectos:
                    for p in proyectos:
                        proy_id = p['id']
                        print(f"🏗️ ¡CONEXIÓN! '{nombre}' -> Actualizando Proyecto {proy_id}")
                        
                        # Actualización del Proyecto (Tu pantalla 0-970)
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
                    # Si no hay asociación, te avisamos para que sepas a cuál le falta el "click"
                    print(f"   ⚠️ '{nombre}' (CIF {cif_hs}): No tiene el proyecto asociado en el panel derecho.")
    else:
        print(f"❌ Error API: {res.text}")

if __name__ == "__main__":
    sincronizacion_definitiva()
