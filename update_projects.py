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
        print(f"❌ Error: No encuentro el archivo {archivo_datos}")
        return
        
    print(f"📊 Leyendo datos desde {archivo_datos}...")
    df = pd.read_csv(archivo_datos)

    # --- ARREGLO PARA EL ERROR DE COLUMNA ---
    # Buscamos qué columna contiene la palabra 'cif' (sin importar mayúsculas)
    columnas_posibles = [c for c in df.columns if 'cif' in c.lower()]
    
    if not columnas_posibles:
        print(f"❌ Error: No encuentro ninguna columna que se llame 'cif' en el CSV.")
        print(f"Las columnas disponibles son: {list(df.columns)}")
        return
    
    columna_cif_csv = columnas_posibles[0]
    print(f"✅ Usando la columna '{columna_cif_csv}' como fuente de CIFs.")
    
    df[columna_cif_csv] = df[columna_cif_csv].astype(str).str.strip()
    # ----------------------------------------

    url_base = "https://api.hubapi.com/crm/v3/objects/0-970"
    prop_cif_proy = "cif_proyecto" 
    prop_nombre_proy = "nombre_empresa_proyecto"
    
    params = {'properties': f'{prop_cif_proy},{prop_nombre_proy}', 'limit': 100}
    
    print("🔎 Buscando proyectos en HubSpot...")
    res = requests.get(url_base, headers=headers, params=params)
    
    if res.status_code != 200:
        print(f"❌ Error API HubSpot ({res.status_code}): {res.text}")
        return

    proyectos = res.json().get('results', [])
    print(f"📦 Analizando {len(proyectos)} proyectos...")

    for proj in proyectos:
        id_hs = proj['id']
        cif_en_proyecto = str(proj['properties'].get(prop_cif_proy, '')).strip()

        if cif_en_proyecto and cif_en_proyecto not in ['None', '']:
            match = df[df[columna_cif_csv] == cif_en_proyecto]
            
            if not match.empty:
                info = match.iloc[0]
                print(f"✨ ¡Match! CIF {cif_en_proyecto} -> Actualizando Proyecto {id_hs}")

                # Ajustamos los nombres de las columnas para que coincidan con el CSV
                # Si fallan, el .get() pondrá '---' en lugar de romper el programa
                body = {
                    "properties": {
                        "nombre_empresa_proyecto": info.get('empresa_para_excel', info.get('nombre_empresa', '---')),
                        "email_proyecto": info.get('correo', info.get('email', '---')),
                        "pais_proyecto": info.get('country', info.get('pais', 'ESPAÑA')),
                        "moneda_proyecto": info.get('moneda_para_excel', 'EUR')
                    }
                }
                
                res_patch = requests.patch(f"{url_base}/{id_hs}", headers=headers, json=body)
                if res_patch.status_code == 200:
                    print(f"   ✅ OK.")
                else:
                    print(f"   ⚠️ Error API: {res_patch.text}")

if __name__ == "__main__":
    actualizar_proyectos_desde_csv()
