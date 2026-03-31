import requests
import pandas as pd
import os
from dotenv import load_dotenv

load_dotenv()

def actualizar_proyectos_desde_csv():
    token = os.getenv('HUBSPOT_ACCESS_TOKEN') or os.getenv('HS_ACCESS_TOKEN')
    headers = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}
    
    # --- PASO 1: ESCANEAR TODOS LOS OBJETOS DISPONIBLES ---
    print("🔍 Escaneando nombres de objetos permitidos...")
    res_schemas = requests.get("https://api.hubapi.com/crm/v3/schemas", headers=headers)
    
    nombre_real = None
    if res_schemas.status_code == 200:
        esquemas = res_schemas.json().get('results', [])
        for s in esquemas:
            label = s.get('labels', {}).get('singular', '').lower()
            internal_name = s.get('name')
            print(f"📌 Encontrado objeto: '{label}' con nombre interno: '{internal_name}'")
            
            if label in ['proyecto', 'proyectos']:
                nombre_real = internal_name
    
    if not nombre_real:
        print("❌ No hemos encontrado el nombre técnico de 'Proyectos'.")
        return

    print(f"🚀 ¡Bingo! Usando el nombre real: {nombre_real}")

    # --- PASO 2: PROCEDER CON LA ACTUALIZACIÓN ---
    url_base = f"https://api.hubapi.com/crm/v3/objects/{nombre_real}"
    
    # Leer CSV
    if not os.path.exists('clientes_hubspot.csv'): return
    df = pd.read_csv('clientes_hubspot.csv')
    col_cif = [c for c in df.columns if 'cif' in c.lower()][0]
    df[col_cif] = df[col_cif].astype(str).str.strip()

    # Usamos tus nombres internos confirmados
    params = {'properties': 'cif,ciudad,nombre_de_la_empresa', 'limit': 100}
    res = requests.get(url_base, headers=headers, params=params)

    if res.status_code == 200:
        proyectos = res.json().get('results', [])
        for proj in proyectos:
            cif_hs = str(proj['properties'].get('cif', '')).strip()
            match = df[df[col_cif] == cif_hs]
            if not match.empty:
                info = match.iloc[0]
                body = {
                    "properties": {
                        "nombre_de_la_empresa": info.get('nombre_empresa', info.get('empresa_para_excel', '---')),
                        "ciudad": info.get('ciudad', '---')
                    }
                }
                requests.patch(f"{url_base}/{proj['id']}", headers=headers, json=body)
                print(f"✅ Proyecto {cif_hs} actualizado.")
    else:
        print(f"❌ Error final: {res.text}")

if __name__ == "__main__":
    actualizar_proyectos_desde_csv()
