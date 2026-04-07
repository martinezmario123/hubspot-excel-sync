import requests
import pandas as pd
import os
from io import StringIO
from dotenv import load_dotenv

load_dotenv()

# Configuración de HubSpot
TOKEN = os.getenv('HUBSPOT_ACCESS_TOKEN')
HEADERS = {'Authorization': f'Bearer {TOKEN}', 'Content-Type': 'application/json'}
OBJETO_PROYECTOS = "0-970"

# URL de tu Google Drive (Publicado como CSV)
URL_DRIVE = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSib6KDzwI4xKJpg_HHJD_jI2Or8ACdnGPS1DTpKSCoc35piMCZJDeXxmvn7AAxiGcXtF9oX3yyWoEK/pub?output=csv"

def ejecutar_sincronizacion_perfecta():
    # 1. Cargar datos desde Google Drive
    print("🌐 Conectando con Google Drive...")
    try:
        response_drive = requests.get(URL_DRIVE)
        response_drive.encoding = 'utf-8'
        
        if response_drive.status_code != 200:
            print("❌ Error: No se pudo acceder al Excel en Drive.")
            return

        df = pd.read_csv(StringIO(response_drive.text))
        print("✅ Datos cargados correctamente desde la nube.")
        
    except Exception as e:
        print(f"❌ Error durante la descarga: {e}")
        return

    # Limpieza de datos
    df.columns = df.columns.str.strip()
    df['CIF'] = df['CIF'].astype(str).str.replace(r'\s+', '', regex=True).str.upper()

    # 2. Obtener Proyectos de HubSpot
    url_hs = f"https://api.hubapi.com/crm/v3/objects/{OBJETO_PROYECTOS}"
    res = requests.get(url_hs, headers=HEADERS, params={'properties': 'cif,name'})
    
    if res.status_code != 200:
        print("❌ Error de conexión con HubSpot.")
        return

    proyectos = res.json().get('results', [])
    print(f"🔄 Sincronizando {len(proyectos)} proyectos...")

    for proy in proyectos:
        proy_id = proy['id']
        cif_hs = str(proy['properties'].get('cif', '')).replace(" ", "").upper()
        
        # Buscar en los datos de Drive
        match = df[df['CIF'] == cif_hs]
        
        if not match.empty:
            fila = match.iloc[0]
            
            # 3. Preparar actualización con el nombre interno correcto: codigo_postal
            payload = {
                "properties": {
                    "ciudad": str(fila['Ciudad']),
                    "city": str(fila['Ciudad']), 
                    "direccion": str(fila['Direccion']),
                    "address": str(fila['Direccion']),
                    "cp": str(fila['CP']),
                    "zip": str(fila['CP']),
                    "codigo_postal": str(fila['CP']) # <-- Ajustado aquí
                }
            }
            
            response = requests.patch(f"{url_hs}/{proy_id}", headers=HEADERS, json=payload)
            
            if response.status_code in [200, 204]:
                print(f"✅ {fila['Empresa']} actualizado con éxito (incluyendo CP).")
            else:
                # Intento de rescate si fallan campos como 'city' o 'zip', usamos los nombres que sabemos que funcionan
                payload_simple = {
                    "properties": {
                        "ciudad": str(fila['Ciudad']), 
                        "direccion": str(fila['Direccion']),
                        "codigo_postal": str(fila['CP']) # <-- También en el modo simple
                    }
                }
                requests.patch(f"{url_hs}/{proy_id}", headers=HEADERS, json=payload_simple)
                print(f"⚠️ {fila['Empresa']} actualizado (modo simple con CP).")

if __name__ == "__main__":
    ejecutar_sincronizacion_perfecta()
