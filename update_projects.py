import requests
import pandas as pd
import os
from dotenv import load_dotenv

load_dotenv()

def actualizar_proyectos_desde_csv():
    token = os.getenv('HUBSPOT_ACCESS_TOKEN') or os.getenv('HS_ACCESS_TOKEN')
    headers = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}
    
    archivo_datos = 'clientes_hubspot.csv'
    if not os.path.exists(archivo_datos):
        print(f"❌ No existe el archivo {archivo_datos}")
        return
        
    df = pd.read_csv(archivo_datos)
    columnas_cif = [c for c in df.columns if 'cif' in c.lower()]
    if not columnas_cif: return
    col_cif = columnas_cif[0]
    df[col_cif] = df[col_cif].astype(str).str.strip()

    # --- PROBAMOS CON EL ID NUMÉRICO DEL OBJETO PERSONALIZADO ---
    url_base = "https://api.hubapi.com/crm/v3/objects/0-970"
    
    prop_cif_hs = "cif_proyecto" 
    prop_nombre_hs = "nombre_empresa_proyecto"
    
    params = {'properties': f'{prop_cif_hs},{prop_nombre_hs}', 'limit': 100}
    
    print(f"🔎 Buscando proyectos en el objeto 0-970...")
    res = requests.get(url_base, headers=headers, params=params)
    
    # SI FALLA EL 403, INTENTAREMOS OTRA RUTA AUTOMÁTICAMENTE
    if res.status_code == 403:
        print("⚠️ El ID 0-970 falló. Probando ruta alternativa...")
        url_base = "https://api.hubapi.com/crm/v3/objects/p_proyectos" # Nombre interno común
        res = requests.get(url_base, headers=headers, params=params)

    if res.status_code != 200:
        print(f"❌ Error API ({res.status_code}): {res.text}")
        return

    proyectos = res.json().get('results', [])
    print(f"📦 Analizando {len(proyectos)} registros...")

    for proj in proyectos:
        id_hs = proj['id']
        cif_actual = str(proj['properties'].get(prop_cif_hs, '')).strip()

        if cif_actual and cif_actual not in ['None', '']:
            match = df[df[col_cif] == cif_actual]
            if not match.empty:
                info = match.iloc[0]
                print(f"✨ Match! CIF {cif_actual} -> ID {id_hs}")
                body = {
                    "properties": {
                        "nombre_empresa_proyecto": info.get('empresa_para_excel', info.get('nombre_empresa', '---')),
                        "email_proyecto": info.get('correo', info.get('email', '---')),
                        "pais_proyecto": info.get('country', info.get('pais', 'ESPAÑA'))
                    }
                }
                requests.patch(f"{url_base}/{id_hs}", headers=headers, json=body)

if __name__ == "__main__":
    actualizar_proyectos_desde_csv()
