import requests
import pandas as pd
import os
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('HUBSPOT_ACCESS_TOKEN')
HEADERS = {'Authorization': f'Bearer {TOKEN}', 'Content-Type': 'application/json'}
OBJETO_PROYECTOS = "0-970"

def ejecutar_sincronizacion_total():
    if not os.path.exists('clientes_hubspot.csv'):
        print("❌ No se encuentra 'clientes_hubspot.csv'")
        return
    
    df = pd.read_csv('clientes_hubspot.csv')
    df.columns = df.columns.str.strip()
    
    # LIMPIEZA PROFUNDA: Quitamos espacios y aseguramos mayúsculas en ambos lados
    df['CIF'] = df['CIF'].astype(str).str.replace(r'\s+', '', regex=True).str.upper()

    url = f"https://api.hubapi.com/crm/v3/objects/{OBJETO_PROYECTOS}"
    propiedades_hs = ['cif', 'ciudad', 'direccion', 'cp', 'name']
    
    res = requests.get(url, headers=HEADERS, params={'properties': ','.join(propiedades_hs)})
    if res.status_code != 200: return

    proyectos_en_hubspot = res.json().get('results', [])
    print(f"🔄 Sincronizando {len(proyectos_en_hubspot)} proyectos...")

    for proy in proyectos_en_hubspot:
        proy_id = proy['id']
        nombre_hs = proy['properties'].get('name', 'Sin nombre')
        # Limpieza del CIF que viene de HubSpot
        cif_hubspot = str(proy['properties'].get('cif', '')).replace(" ", "").upper()
        
        fila_excel = df[df['CIF'] == cif_hubspot]
        
        if not fila_excel.empty:
            datos = fila_excel.iloc[0]
            print(f"🎯 MATCH: {nombre_hs} (CIF: {cif_hubspot})")
            
            payload = {
                "properties": {
                    "ciudad": str(datos['Ciudad']),
                    "direccion": str(datos['Direccion']),
                    "cp": str(datos['CP'])
                }
            }
            requests.patch(f"{url}/{proy_id}", headers=HEADERS, json=payload)
            print(f"✅ Actualizado: {datos['Ciudad']}")
        else:
            if cif_hubspot and cif_hubspot != 'NONE':
                print(f"ℹ️ El CIF '{cif_hubspot}' no coincide con nadie en el Excel.")

if __name__ == "__main__":
    ejecutar_sincronizacion_total()
