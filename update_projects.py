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
    
    df = pd.read_csv('clientes_hubspot.csv')
    # Limpiamos los CIFs para que coincidan aunque tengan espacios o minúsculas
    df['CIF'] = df['CIF'].astype(str).str.strip().upper()

    # 2. Traer los proyectos de HubSpot
    # Aquí pedimos todas las propiedades que queremos sincronizar
    propiedades_hs = ['cif', 'ciudad', 'direccion', 'cp', 'email_proyecto', 'gestor_proyecto']
    url = f"https://api.hubapi.com/crm/v3/objects/{OBJETO_PROYECTOS}"
    
    res = requests.get(url, headers=HEADERS, params={'properties': ','.join(propiedades_hs)})
    
    if res.status_code != 200:
        print(f"❌ Error al conectar con HubSpot: {res.text}")
        return

    proyectos_en_hubspot = res.json().get('results', [])
    print(f"🔄 Sincronizando {len(proyectos_en_hubspot)} proyectos...")

    for proy in proyectos_en_hubspot:
        proy_id = proy['id']
        # Sacamos el CIF que tiene puesto el proyecto en HubSpot
        cif_hubspot = str(proy['properties'].get('cif', '')).strip().upper()
        
        # 3. Buscar este proyecto en nuestro Excel
        fila_excel = df[df['CIF'] == cif_hubspot]
        
        if not fila_excel.empty:
            datos = fila_excel.iloc[0]
            print(f"✅ Coincidencia: Actualizando {datos['Empresa']}...")
            
            # 4. Mapeo de campos: Excel -> HubSpot
            # (Aquí he puesto los nombres que suelen ser estándar)
            payload = {
                "properties": {
                    "ciudad": str(datos['Ciudad']),
                    "direccion": str(datos['Direccion']),
                    "cp": str(datos['CP']),
                    "email_proyecto": str(datos.get('Email Proyecto', '')),
                    "gestor_proyecto": str(datos.get('Gestor Proyecto', ''))
                }
            }
            
            # Enviamos la actualización
            requests.patch(f"{url}/{proy_id}", headers=HEADERS, json=payload)
        else:
            print(f"ℹ️ Saltando proyecto con CIF {cif_hubspot} (no está en el Excel)")

if __name__ == "__main__":
    ejecutar_sincronizacion_total()
