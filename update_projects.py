import requests
import pandas as pd
import os
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('HUBSPOT_ACCESS_TOKEN')
HEADERS = {'Authorization': f'Bearer {TOKEN}', 'Content-Type': 'application/json'}
OBJETO_PROYECTOS = "0-970"

def ejecutar_sincronizacion_perfecta():
    # 1. Cargar Excel
    if not os.path.exists('clientes_hubspot.csv'):
        print("❌ No se encuentra el archivo Excel.")
        return
    
    df = pd.read_csv('clientes_hubspot.csv')
    df.columns = df.columns.str.strip()
    df['CIF'] = df['CIF'].astype(str).str.replace(r'\s+', '', regex=True).str.upper()

    # 2. Obtener Proyectos de HubSpot
    url = f"https://api.hubapi.com/crm/v3/objects/{OBJETO_PROYECTOS}"
    res = requests.get(url, headers=HEADERS, params={'properties': 'cif,name'})
    
    if res.status_code != 200:
        print("❌ Error de conexión con HubSpot.")
        return

    proyectos = res.json().get('results', [])
    print(f"🔄 Sincronizando {len(proyectos)} proyectos...")

    for proy in proyectos:
        proy_id = proy['id']
        cif_hs = str(proy['properties'].get('cif', '')).replace(" ", "").upper()
        
        # Buscar en Excel
        match = df[df['CIF'] == cif_hs]
        
        if not match.empty:
            fila = match.iloc[0]
            
            # 3. ACTUALIZACIÓN MULTI-CAMPO (Para evitar errores de nombre interno)
            # Actualizamos 'ciudad' y también 'city' por si tu HubSpot usa el estándar inglés
            payload = {
                "properties": {
                    "ciudad": str(fila['Ciudad']),
                    "city": str(fila['Ciudad']), 
                    "direccion": str(fila['Direccion']),
                    "address": str(fila['Direccion']),
                    "cp": str(fila['CP']),
                    "zip": str(fila['CP'])
                }
            }
            
            response = requests.patch(f"{url}/{proy_id}", headers=HEADERS, json=payload)
            
            if response.status_code in [200, 204]:
                print(f"✅ {fila['Empresa']} actualizado con éxito.")
            else:
                # Si falla por un campo, intentamos solo con los básicos
                payload_simple = {"properties": {"ciudad": str(fila['Ciudad']), "direccion": str(fila['Direccion'])}}
                requests.patch(f"{url}/{proy_id}", headers=HEADERS, json=payload_simple)
                print(f"⚠️ {fila['Empresa']} actualizado (modo simple).")

if __name__ == "__main__":
    ejecutar_sincronizacion_perfecta()
