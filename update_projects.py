import requests
import pandas as pd
import os
from dotenv import load_dotenv

load_dotenv()

def ejecutar_sincronizacion():
    token = os.getenv('HUBSPOT_ACCESS_TOKEN') or os.getenv('HS_ACCESS_TOKEN')
    headers = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}
    
    # 1. Leer el Excel de GitHub
    df = pd.read_csv('clientes_hubspot.csv')
    df['CIF'] = df['CIF'].astype(str).str.strip()

    # 2. Configurar el objeto PROYECTOS (ID: 0-970)
    objeto_proyectos = "0-970" 
    url = f"https://api.hubapi.com/crm/v3/objects/{objeto_proyectos}"
    
    # Pedimos los proyectos (importante que el nombre interno del CIF sea 'cif')
    params = {'properties': 'cif,name,ciudad,direccion,cp', 'limit': 100}
    res = requests.get(url, headers=headers, params=params)
    
    if res.status_code == 200:
        items = res.json().get('results', [])
        print(f"🔎 Buscando en {len(items)} proyectos de HubSpot...")
        
        for item in items:
            props = item['properties']
            cif_hs = str(props.get('cif', '')).strip()
            
            # Buscar coincidencia en el Excel
            match = df[df['CIF'] == cif_hs]
            
            if not match.empty:
                info = match.iloc[0]
                print(f"🏗️ ¡Match! Actualizando Proyecto: {info['Empresa']}")

                payload = {
                    "properties": {
                        # En objetos personalizados el nombre suele ser 'name'
                        "name": str(info['Empresa']), 
                        "ciudad": str(info['Ciudad']),
                        "direccion": str(info.get('Direccion', '')),
                        "cp": str(info.get('CP', ''))
                    }
                }
                
                upd = requests.patch(f"{url}/{item['id']}", headers=headers, json=payload)
                if upd.status_code == 200:
                    print(f"   ✅ Proyecto actualizado correctamente.")
                else:
                    print(f"   ⚠️ Error al guardar datos: {upd.text}")
    else:
        print(f"❌ Error al conectar con Proyectos (0-970): {res.status_code}")

if __name__ == "__main__":
    ejecutar_sincronizacion()
