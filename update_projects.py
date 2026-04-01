import requests
import pandas as pd
import os
from dotenv import load_dotenv

load_dotenv()

def ejecutar_sincronizacion():
    token = os.getenv('HUBSPOT_ACCESS_TOKEN') or os.getenv('HS_ACCESS_TOKEN')
    headers = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}
    
    # 1. Leer el Excel
    df = pd.read_csv('clientes_hubspot.csv')
    df['CIF'] = df['CIF'].astype(str).str.strip()

    # 2. PROBAR CON EL NOMBRE INTERNO (p2_proyectos o similar)
    # En muchos HubSpot, el objeto 0-970 se llama internamente "p_proyectos" o similar
    # Vamos a intentar llamar a la lista general de esquemas para ver cómo se llama
    
    url_esquema = "https://api.hubapi.com/crm/v3/schemas"
    res_schema = requests.get(url_esquema, headers=headers)
    
    if res_schema.status_code == 200:
        schemas = res_schema.json().get('results', [])
        nombre_tecnico = "0-970" # Por defecto
        for s in schemas:
            if s.get('objectTypeId') == "0-970":
                nombre_tecnico = s.get('name')
                print(f"🔍 Encontrado nombre técnico del objeto: {nombre_tecnico}")

        # AHORA SI, PROBAMOS LA CONEXIÓN CON EL NOMBRE REAL
        url = f"https://api.hubapi.com/crm/v3/objects/{nombre_tecnico}"
        params = {'properties': 'cif,name,ciudad,direccion,cp', 'limit': 100}
        res = requests.get(url, headers=headers, params=params)
        
        if res.status_code == 200:
            items = res.json().get('results', [])
            print(f"✅ Conectado con éxito a {nombre_tecnico}. Procesando...")
            
            for item in items:
                cif_hs = str(item['properties'].get('cif', '')).strip()
                match = df[df['CIF'] == cif_hs]
                
                if not match.empty:
                    info = match.iloc[0]
                    print(f"🏗️ Match: {info['Empresa']}")
                    payload = {
                        "properties": {
                            "name": str(info['Empresa']),
                            "ciudad": str(info['Ciudad']),
                            "direccion": str(info.get('Direccion', '')),
                            "cp": str(info.get('CP', ''))
                        }
                    }
                    requests.patch(f"{url}/{item['id']}", headers=headers, json=payload)
        else:
            print(f"❌ Error {res.status_code} al acceder a {nombre_tecnico}")
    else:
        print(f"❌ Error 403 persistente. El Token no tiene permisos de 'schemas'.")

if __name__ == "__main__":
    ejecutar_sincronizacion()
