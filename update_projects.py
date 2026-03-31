import requests
import pandas as pd
import os
from dotenv import load_dotenv

load_dotenv()

def actualizar_proyectos_desde_csv():
    token = os.getenv('HUBSPOT_ACCESS_TOKEN') or os.getenv('HS_ACCESS_TOKEN')
    headers = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}
    
    # 1. DETECTAR EL NOMBRE INTERNO DEL OBJETO (Evita el error 403/400)
    print("🔍 Consultando esquemas de objetos en HubSpot...")
    res_schemas = requests.get("https://api.hubapi.com/crm/v3/schemas", headers=headers)
    
    nombre_objeto = None
    if res_schemas.status_code == 200:
        schemas = res_schemas.json().get('results', [])
        for s in schemas:
            label_singular = s.get('labels', {}).get('singular', '').lower()
            if label_singular in ['proyecto', 'proyectos']:
                nombre_objeto = s['name']
                break
    
    if not nombre_objeto:
        # Si no lo encuentra por esquema, probamos el ID que vimos en tu captura
        nombre_objeto = "0-970"
    
    print(f"✅ Usando objeto: {nombre_objeto}")

    # 2. LEER DATOS DEL CSV
    archivo_datos = 'clientes_hubspot.csv'
    if not os.path.exists(archivo_datos):
        print(f"❌ No existe el archivo {archivo_datos}")
        return
        
    df = pd.read_csv(archivo_datos)
    
    # Buscamos la columna CIF en el CSV (puede llamarse 'cif_excel' o 'cif')
    cols_cif_csv = [c for c in df.columns if 'cif' in c.lower()]
    if not cols_cif_csv:
        print("❌ No encuentro columna CIF en el CSV")
        return
    col_cif_csv = cols_cif_csv[0]
    df[col_cif_csv] = df[col_cif_csv].astype(str).str.strip()

    # 3. BUSCAR PROYECTOS EN HUBSPOT
    url_base = f"https://api.hubapi.com/crm/v3/objects/{nombre_objeto}"
    
    # IMPORTANTE: Usamos los nombres internos que me has dado
    prop_cif_hs = "cif" 
    prop_ciudad_hs = "ciudad"
    prop_nombre_hs = "nombre_de_la_empresa"
    
    params = {'properties': f'{prop_cif_hs},{prop_ciudad_hs},{prop_nombre_hs}', 'limit': 100}
    res = requests.get(url_base, headers=headers, params=params)

    if res.status_code != 200:
        print(f"❌ Error al leer proyectos ({res.status_code}): {res.text}")
        return

    proyectos = res.json().get('results', [])
    print(f"📦 Analizando {len(proyectos)} proyectos en HubSpot...")

    for proj in proyectos:
        id_hs = proj['id']
        cif_hs = str(proj['properties'].get(prop_cif_hs, '')).strip()

        if cif_hs and cif_hs not in ['None', '']:
            # 4. BUSCAR EN EL CSV
            match = df[df[col_cif_csv] == cif_hs]
            
            if not match.empty:
                info = match.iloc[0]
                print(f"✨ ¡Match! CIF {cif_hs} -> Actualizando Proyecto {id_hs}")

                # 5. ACTUALIZAR CON LOS NOMBRES INTERNOS CORRECTOS
                body = {
                    "properties": {
                        prop_nombre_hs: info.get('nombre_empresa', info.get('empresa_para_excel', '---')),
                        prop_ciudad_hs: info.get('ciudad', info.get('city', '---')),
                        "email_proyecto": info.get('correo', info.get('email', '---')) # Ajusta si este tiene otro nombre
                    }
                }
                
                res_patch = requests.patch(f"{url_base}/{id_hs}", headers=headers, json=body)
                if res_patch.status_code == 200:
                    print(f"   ✅ Proyecto actualizado.")
                else:
                    print(f"   ⚠️ Error al actualizar: {res_patch.text}")

if __name__ == "__main__":
    actualizar_proyectos_desde_csv()
