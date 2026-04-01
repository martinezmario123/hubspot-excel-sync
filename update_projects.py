import requests
import pandas as pd
import os
from dotenv import load_dotenv

load_dotenv()

def actualizar_proyectos_directo():
    token = os.getenv('HUBSPOT_ACCESS_TOKEN')
    headers = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}
    
    df = pd.read_csv('clientes_hubspot.csv')
    df['CIF'] = df['CIF'].astype(str).str.strip()

    # Intentamos con el ID interno 0-970 (el de tu captura)
    # Si falla, HubSpot confirma que bloquea el acceso API a este objeto
    url = "https://api.hubapi.com/crm/v3/objects/0-970"
    params = {'properties': 'cif,name,ciudad,direccion', 'limit': 100}
    
    print(f"🚀 Intentando acceso directo a la pantalla de Proyectos...")
    res = requests.get(url, headers=headers, params=params)
    
    if res.status_code == 200:
        items = res.json().get('results', [])
        for item in items:
            cif_hs = str(item['properties'].get('cif', '')).strip()
            match = df[df['CIF'] == cif_hs]
            
            if not match.empty:
                info = match.iloc[0]
                print(f"✅ Coincidencia encontrada para {info['Empresa']}. Actualizando...")
                
                payload = {
                    "properties": {
                        "ciudad": str(info['Ciudad']),
                        "direccion": str(info.get('Direccion', '')),
                        "cp": str(info.get('CP', ''))
                    }
                }
                upd = requests.patch(f"{url}/{item['id']}", headers=headers, json=payload)
                print(f"   Resultado: {upd.status_code}")
    else:
        print(f"❌ Error {res.status_code}: HubSpot no permite que las Apps Privadas editen 'Proyectos' directamente.")
        print("👉 SOLUCIÓN: Usa el 'Plan Puente' (Sincronizar Negocios con Proyectos) dentro de HubSpot.")

if __name__ == "__main__":
    actualizar_proyectos_directo()
