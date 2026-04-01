import requests
import pandas as pd
import os
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('HUBSPOT_ACCESS_TOKEN')
HEADERS = {'Authorization': f'Bearer {TOKEN}', 'Content-Type': 'application/json'}
OBJETO_PROYECTOS = "0-970"

def sincronizacion_final_limpia():
    df = pd.read_csv('clientes_hubspot.csv')
    df.columns = df.columns.str.strip()
    df['CIF'] = df['CIF'].astype(str).str.replace(r'\s+', '', regex=True).str.upper()

    url = f"https://api.hubapi.com/crm/v3/objects/{OBJETO_PROYECTOS}"
    res = requests.get(url, headers=HEADERS, params={'properties': 'cif,name'})
    
    if res.status_code != 200: return

    proyectos = res.json().get('results', [])
    print(f"🔄 Sincronizando datos reales desde el Excel...")

    for proy in proyectos:
        cif_hs = str(proy['properties'].get('cif', '')).replace(" ", "").upper()
        match = df[df['CIF'] == cif_hs]
        
        if not match.empty:
            datos = match.iloc[0]
            payload = {
                "properties": {
                    "ciudad": str(datos['Ciudad']),
                    "direccion": str(datos['Direccion']),
                    "cp": str(datos['CP'])
                }
            }
            requests.patch(f"{url}/{proy['id']}", headers=HEADERS, json=payload)
            print(f"✅ {datos['Empresa']} actualizado con Ciudad: {datos['Ciudad']}")

if __name__ == "__main__":
    sincronizacion_final_limpia()
