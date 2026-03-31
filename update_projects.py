import requests
import pandas as pd
import os
from dotenv import load_dotenv

load_dotenv()

def actualizar_sistema():
    token = os.getenv('HUBSPOT_ACCESS_TOKEN') or os.getenv('HS_ACCESS_TOKEN')
    headers = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}
    
    # 1. Intentamos localizar el objeto "Proyecto" mirando todos los esquemas
    print("🔎 Buscando la ruta correcta de tus Proyectos...")
    res_schemas = requests.get("https://api.hubapi.com/crm/v3/schemas", headers=headers)
    
    target_object = None
    if res_schemas.status_code == 200:
        for s in res_schemas.json().get('results', []):
            label = s.get('labels', {}).get('singular', '').lower()
            if 'proyect' in label:
                target_object = s['name']
                print(f"✅ ¡Ruta encontrada!: {target_object}")
                break
    
    # Si no lo encuentra por nombre, usamos el ID que vimos en tu URL de HubSpot
    if not target_object:
        target_object = "0-970"
        print(f"⚠️ No se detectó por nombre, usando ID por defecto: {target_object}")

    # 2. Cargar datos del Excel (CSV)
    if not os.path.exists('clientes_hubspot.csv'):
        print("❌ Error: No encuentro el archivo clientes_hubspot.csv")
        return
        
    df = pd.read_csv('clientes_hubspot.csv')
    col_cif_csv = [c for c in df.columns if 'cif' in c.lower()][0]
    df[col_cif_csv] = df[col_cif_csv].astype(str).str.strip()

    # 3. Descargar proyectos actuales de HubSpot
    url_base = f"https://api.hubapi.com/crm/v3/objects/{target_object}"
    # Usamos los nombres internos que confirmamos: cif, ciudad, nombre_de_la_empresa
    params = {'properties': 'cif,ciudad,nombre_de_la_empresa', 'limit': 100}
    
    res = requests.get(url_base, headers=headers, params=params)
    
    if res.status_code != 200:
        print(f"❌ Error API ({res.status_code}): {res.text}")
        return

    proyectos = res.json().get('results', [])
    print(f"📦 Procesando {len(proyectos)} registros en HubSpot...")

    for p in proyectos:
        id_hs = p['id']
        cif_hs = str(p['properties'].get('cif', '')).strip()

        if cif_hs and cif_hs != 'None':
            match = df[df[col_cif_csv] == cif_hs]
            if not match.empty:
                info = match.iloc[0]
                print(f"✨ Match CIF {cif_hs} -> Actualizando...")
                
                payload = {
                    "properties": {
                        "nombre_de_la_empresa": info.get('nombre_empresa', info.get('empresa_para_excel', '---')),
                        "ciudad": info.get('ciudad', '---')
                    }
                }
                requests.patch(f"{url_base}/{id_hs}", headers=headers, json=payload)

if __name__ == "__main__":
    actualizar_sistema()
