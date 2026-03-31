import requests
import pandas as pd
import os
from dotenv import load_dotenv

load_dotenv()

def actualizar_proyectos_desde_csv():
    # Detectamos el token de las variables de entorno de GitHub
    token = os.getenv('HUBSPOT_ACCESS_TOKEN') or os.getenv('HS_ACCESS_TOKEN')
    headers = {
        'Authorization': f'Bearer {token}', 
        'Content-Type': 'application/json'
    }
    
    archivo_datos = 'clientes_hubspot.csv'
    
    if not os.path.exists(archivo_datos):
        print(f"❌ Error: No encuentro el archivo {archivo_datos}")
        return
        
    print(f"📊 Leyendo datos desde {archivo_datos}...")
    df = pd.read_csv(archivo_datos)

    # Buscamos la columna que contenga 'CIF' (ignora mayúsculas/minúsculas)
    columnas_cif = [c for c in df.columns if 'cif' in c.lower()]
    if not columnas_cif:
        print(f"❌ No hay columna CIF en el CSV. Columnas: {list(df.columns)}")
        return
    
    col_cif = columnas_cif[0]
    df[col_cif] = df[col_cif].astype(str).str.strip()
    print(f"✅ Usando columna '{col_cif}' del CSV.")

    # --- CAMBIO CLAVE: Usamos 'tickets' en lugar de '0-970' para evitar el Error 403 ---
    url_base = "https://api.hubapi.com/crm/v3/objects/tickets"
    
    # Propiedades que queremos leer de HubSpot
    prop_cif_hs = "cif_proyecto" 
    prop_nombre_hs = "nombre_empresa_proyecto"
    
    params = {'properties': f'{prop_cif_hs},{prop_nombre_hs}', 'limit': 100}
    
    print(f"🔎 Buscando proyectos (tickets) en HubSpot...")
    res = requests.get(url_base, headers=headers, params=params)
    
    if res.status_code != 200:
        print(f"❌ Error API HubSpot ({res.status_code}): {res.text}")
        print("💡 CONSEJO: Asegúrate de que tu App Privada tenga el permiso 'crm.objects.tickets.read'")
        return

    proyectos = res.json().get('results', [])
    print(f"📦 Analizando {len(proyectos)} registros encontrados...")

    for proj in proyectos:
        id_hs = proj['id']
        cif_actual = str(proj['properties'].get(prop_cif_hs, '')).strip()

        if cif_actual and cif_actual not in ['None', '']:
            # Buscar el CIF del ticket en nuestro CSV
            match = df[df[col_cif] == cif_actual]
            
            if not match.empty:
                info = match.iloc[0]
                print(f"✨ ¡Match! CIF {cif_actual} -> Actualizando ID {id_hs}...")

                # Mapeo de datos (CSV -> HubSpot)
                # .get('columna', 'valor_por_defecto') evita que el código rompa
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
                    print(f"   ✅ Campos actualizados con éxito.")
                else:
                    print(f"   ⚠️ Error al actualizar: {res_patch.text}")
            else:
                print(f"   ℹ️ CIF {cif_actual} no encontrado en el archivo de datos.")

if __name__ == "__main__":
    actualizar_proyectos_desde_csv()
