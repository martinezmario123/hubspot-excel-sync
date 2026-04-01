import requests
import pandas as pd
import os
from dotenv import load_dotenv

load_dotenv()

def ejecutar_sincronizacion():
    token = os.getenv('HUBSPOT_ACCESS_TOKEN')
    headers = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}
    
    # 1. Leer el CSV
    df = pd.read_csv('clientes_hubspot.csv')
    df['CIF'] = df['CIF'].astype(str).str.strip()

    # 2. Intentar con el nombre técnico que usa HubSpot para tu portal
    # Estructura: p[ID_PORTAL]_proyectos
    portal_id = "147977807"
    nombre_tecnico = f"p{portal_id}_proyectos"
    
    url = f"https://api.hubapi.com/crm/v3/objects/{nombre_tecnico}"
    
    print(f"📡 Intentando conectar a la puerta: {nombre_tecnico}...")
    
    params = {'properties': 'cif,name,ciudad,direccion,cp', 'limit': 100}
    res = requests.get(url, headers=headers, params=params)
    
    # Si falla por nombre técnico, intentamos por el ID 0-970 como última opción
    if res.status_code != 200:
        print(f"⚠️ Falló {nombre_tecnico}, probando con 0-970...")
        url = "https://api.hubapi.com/crm/v3/objects/0-970"
        res = requests.get(url, headers=headers, params=params)

    if res.status_code == 200:
        items = res.json().get('results', [])
        print(f"✅ ¡CONECTADO! Proyectos encontrados: {len(items)}")
        
        for item in items:
            props = item['properties']
            cif_hs = str(props.get('cif', '')).strip()
            
            match = df[df['CIF'] == cif_hs]
            if not match.empty:
                info = match.iloc[0]
                print(f"🏗️ Actualizando: {info['Empresa']} (ID: {item['id']})")

                payload = {
                    "properties": {
                        "name": str(info['Empresa']),
                        "ciudad": str(info['Ciudad']),
                        "direccion": str(info.get('Direccion', '')),
                        "cp": str(info.get('CP', ''))
                    }
                }
                
                upd = requests.patch(f"{url}/{item['id']}", headers=headers, json=payload)
                print(f"   Resultado: {upd.status_code}")
    else:
        print(f"❌ Error final {res.status_code}: {res.text}")
        print("👉 IMPORTANTE: Ve a HubSpot > Apps Privadas > Tu App > Scopes")
        print("Asegúrate de que 'crm.schemas.custom.read' y 'crm.objects.custom.read' estén marcados.")

if __name__ == "__main__":
    ejecutar_sincronizacion()
