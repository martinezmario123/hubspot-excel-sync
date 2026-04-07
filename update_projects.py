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
    print("🌐 Conectando con Google Drive...")
    try:
        response_drive = requests.get(URL_DRIVE)
        response_drive.encoding = 'utf-8'
        
        if response_drive.status_code != 200:
            print("❌ Error: No se pudo acceder al Excel en Drive.")
            return

        df = pd.read_csv(StringIO(response_drive.text))
        # Limpiamos los nombres de las columnas por si tienen espacios invisibles
        df.columns = df.columns.str.strip()
        print("✅ Datos cargados correctamente.")
        
    except Exception as e:
        print(f"❌ Error durante la descarga: {e}")
        return

    # Limpieza de CIF para el cruce de datos
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
            
            # 3. Preparar actualización con los nombres de columna reales de tu Excel
            # Usamos .get('NombreColumnaExcel', '') para evitar errores si falta la columna
            payload = {
                "properties": {
                    "ciudad": str(fila.get('Ciudad', '')),
                    "direccion": str(fila.get('Direccion', '')),
                    "codigo_postal": str(fila.get('CP', '')),
                    "nombre_completo_contacto": str(fila.get('Contacto Principal', '')) # <-- Ajustado aquí
                }
            }
            
            response = requests.patch(f"{url_hs}/{proy_id}", headers=HEADERS, json=payload)
            
            if response.status_code in [200, 204]:
                print(f"✅ {fila.get('Empresa', 'Proyecto')} actualizado con éxito.")
            else:
                print(f"⚠️ Error al actualizar el proyecto ID {proy_id}")

if __name__ == "__main__":
    ejecutar_sincronizacion_perfecta()
