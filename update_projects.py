import requests
import pandas as pd
import os
from dotenv import load_dotenv

load_dotenv()

def descubrir_asociacion_real():
    token = os.getenv('HUBSPOT_ACCESS_TOKEN')
    headers = {'Authorization': f'Bearer {token}'}
    
    # 1. Buscamos los negocios pero sin filtrar por objeto, para ver qué devuelve
    url = "https://api.hubapi.com/crm/v3/objects/deals"
    # Pedimos ver que IDs de otros objetos tiene pegados
    params = {'limit': 5, 'properties': 'dealname,cif'}
    
    print("🔎 Investigando asociaciones reales en HubSpot...")
    res = requests.get(url, headers=headers, params=params)
    
    if res.status_code == 200:
        negocios = res.json().get('results', [])
        for deal in negocios:
            deal_id = deal['id']
            nombre = deal['properties'].get('dealname')
            print(f"\n🏢 Negocio: {nombre} (ID: {deal_id})")
            
            # 2. Consultamos específicamente las asociaciones de ESTE negocio
            url_asoc = f"https://api.hubapi.com/crm/v3/objects/deals/{deal_id}/associations/0-970"
            res_asoc = requests.get(url_asoc, headers=headers)
            
            if res_asoc.status_code == 200:
                asocs = res_asoc.json().get('results', [])
                if asocs:
                    for a in asocs:
                        print(f"   ✅ ¡ENCONTRADO! Está asociado al Proyecto ID: {a['id']}")
                        print(f"   💡 USA ESTE ID EN EL PRÓXIMO PASO.")
                else:
                    print(f"   ❌ No se detectan asociaciones con el objeto 0-970 por la vía estándar.")
            else:
                print(f"   ⚠️ Error al consultar asociaciones: {res_asoc.status_code}")
    else:
        print(f"❌ Error: {res.status_code}")

if __name__ == "__main__":
    descubrir_asociacion_real()
