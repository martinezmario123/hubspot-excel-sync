import requests
import pandas as pd
import os
from dotenv import load_dotenv

load_dotenv()

def sincronizacion_final_proyectos():
    token = os.getenv('HUBSPOT_ACCESS_TOKEN')
    headers = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}
    
    df = pd.read_csv('clientes_hubspot.csv')
    df['CIF'] = df['CIF'].astype(str).str.strip()

    # Buscamos negocios y sus asociaciones con Proyectos (0-970)
    url = "https://api.hubapi.com/crm/v3/objects/deals"
    params = {'associations': '0-970', 'properties': 'cif,dealname', 'limit': 100}
    
    res = requests.get(url, headers=headers, params=params)
    if res.status_code == 200:
        results = res.json().get('results', [])
        for deal in results:
            cif_hs = str(deal['properties'].get('cif', '')).strip()
            match = df[df['CIF'] == cif_hs]
            
            if not match.empty:
                info = match.iloc[0]
                # Buscamos el ID del Proyecto asociado
                asociaciones = deal.get('associations', {})
                
                # Intentamos encontrar la clave de asociación (puede variar el nombre)
                p_asoc = None
                for key in asociaciones.keys():
                    if "0-970" in key or "proyectos" in key.lower():
                        p_asoc = asociaciones[key].get('results', [])

                if p_asoc:
                    for a in p_asoc:
                        proy_id = a['id']
                        print(f"🚀 ¡Conexión hallada! Pasando datos de {info['Empresa']} al Proyecto {proy_id}")
                        
                        # Actualizamos la pantalla de Proyectos (0-970)
                        url_p = f"https://api.hubapi.com/crm/v3/objects/0-970/{proy_id}"
                        payload = {
                            "properties": {
                                "ciudad": str(info['Ciudad']),
                                "direccion": str(info.get('Direccion', ''))
                            }
                        }
                        requests.patch(url_p, headers=headers, json=payload)
        print("🏁 Proceso completado.")
    else:
        print(f"❌ Error: {res.text}")

if __name__ == "__main__":
    sincronizacion_final_proyectos()
