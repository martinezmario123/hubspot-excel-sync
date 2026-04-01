import requests
import os
import pandas as pd
from dotenv import load_dotenv

load_dotenv()

def diagnostico_profundo():
    token = os.getenv('HUBSPOT_ACCESS_TOKEN')
    headers = {'Authorization': f'Bearer {token}'}
    
    # 1. Ver qué hay en el Excel
    df = pd.read_csv('clientes_hubspot.csv')
    print(f"📊 EXCEL: He leído {len(df)} filas. El primer CIF es: '{df['CIF'].iloc[0]}'")

    # 2. Ver qué negocios encuentra el robot
    url = "https://api.hubapi.com/crm/v3/objects/deals"
    params = {'properties': 'cif,dealname,ciudad', 'limit': 10}
    
    res = requests.get(url, headers=headers, params=params)
    
    if res.status_code == 200:
        negocios = res.json().get('results', [])
        print(f"📡 HUBSPOT: He encontrado {len(negocios)} negocios en total.")
        
        for n in negocios:
            id_hs = n['id']
            nombre = n['properties'].get('dealname')
            cif_hs = n['properties'].get('cif')
            
            print(f"\n🔎 Analizando Negocio ID {id_hs}:")
            print(f"   - Nombre en HS: '{nombre}'")
            print(f"   - CIF en HS: '{cif_hs}'")
            
            if cif_hs:
                match = df[df['CIF'].astype(str) == str(cif_hs)]
                if not match.empty:
                    print(f"   ✅ ¡HAY COINCIDENCIA! Debería actualizarse con {match.iloc[0]['Ciudad']}")
                    
                    # PROBAMOS ACTUALIZACIÓN REAL CON UN SOLO CAMBIO: EL NOMBRE
                    test_payload = {"properties": {"dealname": nombre + " (OK)"}}
                    test_res = requests.patch(f"{url}/{id_hs}", headers=headers, json=test_payload)
                    print(f"   ⚡ Intento de cambio de nombre: {test_res.status_code}")
                else:
                    print(f"   ❌ El CIF '{cif_hs}' no existe en tu Excel.")
            else:
                print(f"   ⚠️ Este negocio NO TIENE CIF puesto en HubSpot.")
    else:
        print(f"❌ Error de conexión: {res.status_code}")

if __name__ == "__main__":
    diagnostico_profundo()
