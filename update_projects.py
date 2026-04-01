import requests
import pandas as pd
import os
from dotenv import load_dotenv

load_dotenv()

def sincronizacion_final():
    token = os.getenv('HUBSPOT_ACCESS_TOKEN')
    headers = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}
    
    df = pd.read_csv('clientes_hubspot.csv')
    df['CIF'] = df['CIF'].astype(str).str.strip()

    url = "https://api.hubapi.com/crm/v3/objects/deals"
    params = {'properties': 'cif,dealname,ciudad', 'limit': 100}
    
    res = requests.get(url, headers=headers, params=params)
    if res.status_code == 200:
        for item in res.json().get('results', []):
            cif_hs = str(item['properties'].get('cif', '')).strip()
            match = df[df['CIF'] == cif_hs]
            
            if not match.empty:
                info = match.iloc[0]
                # Limpiamos el dato para que no lleve espacios raros
                ciudad_valor = str(info['Ciudad']).strip()
                
                print(f"🚀 Intentando enviar '{ciudad_valor}' a la propiedad 'ciudad' de {info['Empresa']}...")
                
                payload = {
                    "properties": {
                        "dealname": str(info['Empresa']),
                        "ciudad": ciudad_valor
                    }
                }
                
                upd = requests.patch(f"{url}/{item['id']}", headers=headers, json=payload)
                
                # REVISIÓN DE RESULTADO
                if upd.status_code == 200:
                    datos_confirmados = upd.json().get('properties', {})
                    print(f"   ✅ API dice OK. Valor actual en HubSpot: '{datos_confirmados.get('ciudad')}'")
                else:
                    print(f"   ❌ ERROR API: {upd.text}")
        
        print("\n🏁 Proceso terminado.")
    else:
        print(f"❌ Error de conexión: {res.status_code}")

if __name__ == "__main__":
    sincronizacion_final()
