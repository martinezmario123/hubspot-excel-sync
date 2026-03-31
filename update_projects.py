import requests
import pandas as pd
import os
from dotenv import load_dotenv

load_dotenv()

def actualizar_proyectos_desde_excel():
    token = os.getenv('HS_ACCESS_TOKEN')
    headers = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}
    
    # 1. LEER EXCEL (Asegúrate de que datos.xlsx esté en la raíz de tu repo)
    if not os.path.exists('datos.xlsx'):
        print("❌ No encuentro el archivo datos.xlsx")
        return
        
    df = pd.read_excel('datos.xlsx')
    # Convertimos a string y quitamos espacios
    df['cif_excel'] = df['cif_excel'].astype(str).str.strip()

    # 2. URL DE PROYECTOS (Usando el ID de tu captura)
    url_base = "https://api.hubapi.com/crm/v3/objects/0-970"
    
    # IMPORTANTE: Revisa que estos nombres internos existan en tu objeto Proyecto
    prop_cif = "cif_proyecto" 
    prop_nombre = "nombre_empresa_proyecto"
    
    params = {'properties': f'{prop_cif},{prop_nombre}', 'limit': 100}
    
    print("🔎 Buscando proyectos en HubSpot...")
    res = requests.get(url_base, headers=headers, params=params)
    
    if res.status_code != 200:
        print(f"❌ Error API ({res.status_code}): {res.text}")
        return

    proyectos = res.json().get('results', [])

    for proj in proyectos:
        id_hs = proj['id']
        cif_proy = str(proj['properties'].get(prop_cif, '')).strip()

        if cif_proy and cif_proy != 'None':
            # 3. BUSCAR EN EXCEL
            match = df[df['cif_excel'] == cif_proy]
            
            if not match.empty:
                info = match.iloc[0]
                print(f"✨ Match para CIF {cif_proy}. Actualizando ID {id_hs}...")

                # 4. ACTUALIZAR
                body = {
                    "properties": {
                        prop_nombre: info['empresa_para_excel'],
                        "email_proyecto": info['correo'],
                        "pais_proyecto": info['country']
                    }
                }
                
                res_patch = requests.patch(f"{url_base}/{id_hs}", headers=headers, json=body)
                if res_patch.status_code == 200:
                    print(f"✅ ¡Actualizado!")
                else:
                    print(f"⚠️ Error al actualizar: {res_patch.text}")

if __name__ == "__main__":
    actualizar_proyectos_desde_excel()
