import requests
import pandas as pd
import os
from dotenv import load_dotenv

# Configuración inicial
load_dotenv()
TOKEN = os.getenv('HUBSPOT_ACCESS_TOKEN')
HEADERS = {'Authorization': f'Bearer {TOKEN}', 'Content-Type': 'application/json'}
OBJETO_PROYECTOS = "0-970"

def ejecutar_sincronizacion_total():
    # 1. Leer el Excel (CSV)
    if not os.path.exists('clientes_hubspot.csv'):
        print("❌ Error: No se encuentra el archivo 'clientes_hubspot.csv'")
        return
    
    # Leemos el CSV y limpiamos nombres de columnas por si acaso
    df = pd.read_csv('clientes_hubspot.csv')
    df.columns = df.columns.str.strip()
    
    # Limpieza correcta del CIF (usando .str antes de .upper())
    df['CIF'] = df['CIF'].astype(str).str.strip().get(0).upper() if df['CIF'].dtype == object else df['CIF']
    # Versión robusta para Pandas:
    df['CIF'] = df['CIF'].astype(str).str.strip().str.upper()

    # 2. Traer los proyectos de HubSpot
    propiedades_hs = ['cif', 'ciudad', 'direccion', 'cp']
    url = f"https://api.hubapi.com/crm/v3/objects/{OBJETO_PROYECTOS}"
    
    try:
        res = requests.get(url, headers=HEADERS, params={'properties': ','.join(propiedades_hs)})
        res.raise_for_status()
    except Exception as e:
        print(f"❌ Error al conectar con HubSpot: {e}")
        return

    proyectos_en_hubspot = res.json().get('results', [])
    print(f"🔄 Analizando {len(proyectos_en_hubspot)} proyectos en HubSpot...")

    for proy in proyectos_en_hubspot:
        proy_id = proy['id']
        props_hs = proy['properties']
        cif_hubspot = str(props_hs.get('cif', '')).strip().upper()
        
        # 3. Buscar este proyecto en nuestro Excel
        fila_excel = df[df['CIF'] == cif_hubspot]
        
        if not fila_excel.empty:
            datos = fila_excel.iloc[0]
            print(f"🎯 MATCH: Actualizando '{datos['Empresa']}' (ID: {proy_id})...")
            
            # 4. Mapeo de campos
            payload = {
                "properties": {
                    "ciudad": str(datos['Ciudad']),
                    "direccion": str(datos['Direccion']),
                    "cp": str(datos['CP'])
                }
            }
            
            # Enviamos la actualización
            requests.patch(f"{url}/{proy_id}", headers=HEADERS, json=payload)
            print(f"✅ Ok: {datos['Ciudad']}, {datos['Direccion']}")
        else:
            if cif_hubspot and cif_hubspot != 'NONE':
                print(f"ℹ️ El CIF '{cif_hubspot}' no está en el Excel.")

if __name__ == "__main__":
    ejecutar_sincronizacion_total()
