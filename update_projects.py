import requests
import pandas as pd
import os
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('HUBSPOT_ACCESS_TOKEN')
HEADERS = {'Authorization': f'Bearer {TOKEN}', 'Content-Type': 'application/json'}
OBJETO_PROYECTOS = "0-970"

def ejecutar_sincronizacion_total():
    # 1. Cargar la "Base de Datos" (tu Excel)
    if not os.path.exists('clientes_hubspot.csv'):
        print("❌ Error: No se encuentra el archivo 'clientes_hubspot.csv'")
        return
    
    df = pd.read_csv('clientes_hubspot.csv')
    df.columns = df.columns.str.strip()
    
    # Limpiamos el CIF del Excel (quitamos espacios y ponemos mayúsculas)
    df['CIF'] = df['CIF'].astype(str).str.replace(r'\s+', '', regex=True).str.upper()

    # 2. Pedir a HubSpot todos los proyectos que tiene creados
    # Traemos el CIF, Ciudad, Dirección y CP para comparar
    url = f"https://api.hubapi.com/crm/v3/objects/{OBJETO_PROYECTOS}"
    params = {'properties': 'cif,ciudad,direccion,cp,name'}
    
    res = requests.get(url, headers=HEADERS, params=params)
    if res.status_code != 200:
        print(f"❌ Error de conexión: {res.text}")
        return

    proyectos_hubspot = res.json().get('results', [])
    print(f"🔄 Escaneando {len(proyectos_hubspot)} proyectos en HubSpot...")

    # 3. El Bucle de Match (Cruzar datos)
    for proy in proyectos_hubspot:
        proy_id = proy['id']
        # Limpiamos el CIF que viene de HubSpot
        cif_hs = str(proy['properties'].get('cif', '')).replace(" ", "").upper()
        
        # Buscamos si este CIF de HubSpot existe en alguna fila del Excel
        match = df[df['CIF'] == cif_hs]
        
        if not match.empty:
            # Si hay MATCH, sacamos la info del Excel
            datos_nuevos = match.iloc[0]
            empresa = datos_nuevos['Empresa']
            
            print(f"🎯 Match encontrado: {empresa} (CIF: {cif_hs})")
            
            # 4. Actualizar HubSpot con lo que diga el Excel
            payload = {
                "properties": {
                    "ciudad": str(datos_nuevos['Ciudad']),
                    "direccion": str(datos_nuevos['Direccion']),
                    "cp": str(datos_nuevos['CP'])
                }
            }
            
            # Enviamos la actualización solo si hay cambios
            requests.patch(f"{url}/{proy_id}", headers=HEADERS, json=payload)
            print(f"✅ Campos actualizados para {empresa}.")
        else:
            # Si el CIF no está en el Excel, no hacemos nada
            if cif_hs and cif_hs != 'NONE':
                print(f"ℹ️ El CIF '{cif_hs}' no está en el Excel. Se ignora.")

if __name__ == "__main__":
    ejecutar_sincronizacion_total()
