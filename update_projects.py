import requests
import pandas as pd
import os
from dotenv import load_dotenv

load_dotenv()

def sincronizacion_final_explicativa():
    token = os.getenv('HUBSPOT_ACCESS_TOKEN')
    headers = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}
    
    df = pd.read_csv('clientes_hubspot.csv')
    df['CIF'] = df['CIF'].astype(str).str.strip()

    url = "https://api.hubapi.com/crm/v3/objects/deals"
    params = {'associations': '0-970', 'properties': 'cif,dealname', 'limit': 100}
    
    res = requests.get(url, headers=headers, params=params)
    if res.status_code == 200:
        results = res.json().get('results', [])
        print(f"🧐 Revisando {len(results)} negocios en HubSpot...")
        
        for deal in results:
            nombre = deal['properties'].get('dealname', 'Sin nombre')
            cif_hs = str(deal['properties'].get('cif', '')).strip()
            
            # 1. Comprobar CIF
            match = df[df['CIF'] == cif_hs]
            if match.empty:
                print(f"❌ '{nombre}': El CIF '{cif_hs}' no está en tu Excel.")
                continue

            # 2. Comprobar Asociación
            asoc_data = deal.get('associations', {})
            p_asoc = None
            for key in asoc_data.keys():
                if "0-970" in key or "proyectos" in key.lower():
                    p_asoc = asoc_data[key].get('results', [])

            if not p_asoc:
                print(f"⚠️ '{nombre}': CIF correcto, pero NO TIENE PROYECTO ENLAZADO en la derecha.")
                continue

            # 3. Actualizar
            info = match.iloc[0]
            for a in p_asoc:
                proy_id = a['id']
                print(f"✅ '{nombre}': ¡Enlace encontrado! Actualizando Proyecto {proy_id}...")
                
                url_p = f"https://api.hubapi.com/crm/v3/objects/0-970/{proy_id}"
                payload = {"properties": {"ciudad": str(info['Ciudad']), "direccion": str(info.get('Direccion', ''))}}
                requests.patch(url_p, headers=headers, json=payload)
                
        print("\n🏁 ¡Listo! Revisa tu pantalla de Proyectos.")
    else:
        print(f"❌ Error: {res.text}")

if __name__ == "__main__":
    sincronizacion_final_explicativa()
