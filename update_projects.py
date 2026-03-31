import requests
import pandas as pd
import os
from dotenv import load_dotenv

load_dotenv()

def actualizar_proyectos_desde_csv():
    # Usamos el token de las variables de entorno de GitHub
    token = os.getenv('HUBSPOT_ACCESS_TOKEN') or os.getenv('HS_ACCESS_TOKEN')
    headers = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}
    
    # 1. LEER EL ARCHIVO CSV QUE GENERA EL PASO 1
    archivo_datos = 'clientes_hubspot.csv'
    
    if not os.path.exists(archivo_datos):
        print(f"❌ Error: No encuentro el archivo {archivo_datos}")
        return
        
    print(f"📊 Leyendo datos desde {archivo_datos}...")
    # Leemos el CSV
    df = pd.read_csv(archivo_datos)
    
    # Limpieza de la columna CIF en el CSV (ajusta el nombre si en tu CSV se llama distinto)
    columna_cif_csv = 'cif_excel' 
    df[columna_cif_csv] = df[columna_cif_csv].astype(str).str.strip()

    # 2. CONFIGURACIÓN DEL OBJETO PROYECTOS (ID 0-970 según tu captura)
    url_base = "https://api.hubapi.com/crm/v3/objects/0-970"
    
    # Propiedades que vamos a pedir a los proyectos en HubSpot
    # IMPORTANTE: 'cif_proyecto' debe ser el nombre interno del campo CIF en el Proyecto
    prop_cif_proy = "cif_proyecto" 
    prop_nombre_proy = "nombre_empresa_proyecto"
    
    params = {'properties': f'{prop_cif_proy},{prop_nombre_proy}', 'limit': 100}
    
    print("🔎 Buscando proyectos en HubSpot...")
    res = requests.get(url_base, headers=headers, params=params)
    
    if res.status_code != 200:
        print(f"❌ Error API HubSpot ({res.status_code}): {res.text}")
        return

    proyectos = res.json().get('results', [])
    print(f"📦 Se han encontrado {len(proyectos)} proyectos para analizar.")

    for proj in proyectos:
        id_hs = proj['id']
        # Sacamos el CIF que tiene el proyecto actualmente
        cif_en_proyecto = str(proj['properties'].get(prop_cif_proy, '')).strip()

        if cif_en_proyecto and cif_en_proyecto != 'None' and cif_en_proyecto != '':
            # 3. BUSCAR COINCIDENCIA EN EL CSV
            match = df[df[columna_cif_csv] == cif_en_proyecto]
            
            if not match.empty:
                info = match.iloc[0]
                print(f"✨ Match encontrado! CIF {cif_en_proyecto} -> Actualizando Proyecto {id_hs}")

                # 4. ACTUALIZAR LOS CAMPOS DEL PROYECTO CON INFO DEL CSV
                # Usa aquí los nombres internos de las propiedades del objeto PROYECTO
                body = {
                    "properties": {
                        "nombre_empresa_proyecto": info.get('empresa_para_excel', '---'),
                        "email_proyecto": info.get('correo', '---'),
                        "pais_proyecto": info.get('country', 'ESPAÑA'),
                        "moneda_proyecto": info.get('moneda_para_excel', 'EUR')
                    }
                }
                
                res_patch = requests.patch(f"{url_base}/{id_hs}", headers=headers, json=body)
                if res_patch.status_code == 200:
                    print(f"   ✅ Proyecto actualizado correctamente.")
                else:
                    print(f"   ⚠️ Error al actualizar: {res_patch.text}")
            else:
                print(f"   ℹ️ El CIF {cif_en_proyecto} no existe en el CSV de clientes.")

if __name__ == "__main__":
    actualizar_proyectos_desde_csv()
