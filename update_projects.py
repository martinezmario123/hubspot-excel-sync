import requests
import pandas as pd
import os
from dotenv import load_dotenv

load_dotenv()

def sincronizacion_ninja():
    token = os.getenv('HUBSPOT_ACCESS_TOKEN')
    headers = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}
    
    df = pd.read_csv('clientes_hubspot.csv')
    df['CIF'] = df['CIF'].astype(str).str.strip()

    # 1. Buscamos los Negocios (Deals) asociados
    url_deals = "https://api.hubapi.com/crm/v3/objects/deals"
    # Pedimos las asociaciones con el objeto 0-970 (Proyectos)
    params = {'associations': '0-970', 'properties': 'cif', 'limit': 100}
    
    print("📡 Buscando conexiones entre Negocios y Proyectos...")
    res = requests.get(url_deals, headers=headers, params=params)
    
    if res.status_code == 200:
        for deal in res.json().get('results', []):
            cif_hs = str(deal['properties'].get('cif', '')).strip()
            match = df[df['CIF'] == cif_hs]
            
            if not match.empty:
                info = match.iloc[0]
                # Miramos si este negocio tiene un Proyecto asociado
                asociaciones = deal.get('associations', {}).get('p147977807_proyectos', {}).get('results', [])
                # Nota: Si el nombre interno falla, probamos con '0-970'
                if not asociaciones:
                    asociaciones = deal.get('associations', {}).get('0-970', {}).get('results', [])

                for asoc in asociaciones:
                    proyecto_id = asoc['id']
                    print(f"🏗️ ¡Bingo! Proyecto {proyecto_id} encontrado para {info['Empresa']}. Actualizando...")
                    
                    url_proy = f"https://api.hubapi.com/crm/v3/objects/0-970/{proyecto_id}"
                    payload = {
                        "properties": {
                            "ciudad": str(info['Ciudad']),
                            "direccion": str(info.get('Direccion', '')),
                            "cp": str(info.get('CP', ''))
                        }
                    }
                    upd = requests.patch(url_proy, headers=headers, json=payload)
                    print(f"   📥 Resultado en Proyecto: {upd.status_code}")
        
        print("🚀 Sincronización Ninja finalizada.")
    else:
        print(f"❌ Error: {res.status_code}")

if __name__ == "__main__":
    sincronizacion_ninja()
