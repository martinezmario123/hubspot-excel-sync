import requests
import pandas as pd
import os
from dotenv import load_dotenv

load_dotenv()

def sincronizar_por_cif_directo():
    token = os.getenv('HUBSPOT_ACCESS_TOKEN')
    headers = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}
    
    # 1. Cargar el Excel (CSV)
    df = pd.read_csv('clientes_hubspot.csv')
    df['CIF'] = df['CIF'].astype(str).str.strip().upper()

    # 2. Obtener los proyectos de HubSpot (ID, Nombre y CIF)
    url_get = "https://api.hubapi.com/crm/v3/objects/0-970"
    # Pedimos el nombre del proyecto también para que el log sea más claro
    params = {'properties': 'cif,ciudad,direccion,cp,name'} 
    res = requests.get(url_get, headers=headers, params=params)
    
    if res.status_code != 200:
        print(f"❌ Error al conectar: {res.text}")
        return

    proyectos_hs = res.json().get('results', [])
    print(f"🔎 Analizando {len(proyectos_hs)} proyectos en tu HubSpot...")

    for proy in proyectos_hs:
        props = proy['properties']
        proy_id = proy['id']
        nombre_hs = props.get('name', 'Sin nombre')
        cif_hs = str(props.get('cif', '')).strip().upper()
        
        # 3. Intentar emparejar por CIF
        match = df[df['CIF'] == cif_hs]
        
        if not match.empty:
            datos_excel = match.iloc[0]
            print(f"🎯 ¡MATCH! Proyecto: '{nombre_hs}' <--> Excel: '{datos_excel['Empresa']}' (CIF: {cif_hs})")
            
            # 4. Actualizar
            url_patch = f"https://api.hubapi.com/crm/v3/objects/0-970/{proy_id}"
            payload = {
                "properties": {
                    "ciudad": str(datos_excel['Ciudad']),
                    "direccion": str(datos_excel['Direccion']),
                    "cp": str(datos_excel['CP'])
                }
            }
            
            r = requests.patch(url_patch, headers=headers, json=payload)
            if r.status_code in [200, 204]:
                print(f"✅ Datos de '{datos_excel['Ciudad']}' subidos correctamente.")
            else:
                print(f"⚠️ Fallo al subir datos: {r.text}")
        else:
            print(f"⚪ Proyecto '{nombre_hs}' (CIF: {cif_hs}) no tiene datos nuevos en el Excel.")

if __name__ == "__main__":
    sincronizar_por_cif_directo()
