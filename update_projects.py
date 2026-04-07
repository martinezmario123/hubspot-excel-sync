import requests
import pandas as pd
import os
import json
from io import StringIO
from dotenv import load_dotenv

load_dotenv()

# --- CONFIGURACIÓN ---
TOKEN = os.getenv('HUBSPOT_ACCESS_TOKEN')
HEADERS = {'Authorization': f'Bearer {TOKEN}', 'Content-Type': 'application/json'}
OBJETO_PROYECTOS = "0-970"

# URL de tu Apps Script (La que me pasaste antes)
URL_APPS_SCRIPT = "https://script.google.com/macros/s/AKfycbx9EZ0FbqF0JfQcPU5ShjHYQRqoGMAwfKTutKWiJaAVnEBl_RIo6xnlvDSwLHd_dQtVnA/exec"

# URL de tu Google Drive (Publicado como CSV)
URL_DRIVE = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSib6KDzwI4xKJpg_HHJD_jI2Or8ACdnGPS1DTpKSCoc35piMCZJDeXxmvn7AAxiGcXtF9oX3yyWoEK/pub?output=csv"

def marcar_como_procesado_en_google(cif):
    """Función para avisar al Excel que el CIF ya se subió a HubSpot"""
    payload = {
        "accion": "marcar_procesado",
        "cif": str(cif).strip()
    }
    try:
        # allow_redirects=True es obligatorio para Google Apps Script
        response = requests.post(URL_APPS_SCRIPT, data=json.dumps(payload), allow_redirects=True)
        print(f"  ∟ 📝 Google Sheets dice: {response.text}")
    except Exception as e:
        print(f"  ∟ ❌ Error avisando a Google Sheets: {e}")

def ejecutar_sincronizacion_perfecta():
    print("🌐 Conectando con Google Drive...")
    try:
        response_drive = requests.get(URL_DRIVE)
        response_drive.encoding = 'utf-8'
        
        if response_drive.status_code != 200:
            print("❌ Error: No se pudo acceder al Excel en Drive.")
            return

        df = pd.read_csv(StringIO(response_drive.text))
        df.columns = df.columns.str.strip()
        print("✅ Datos de Drive cargados.")
        
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
            
            payload = {
                "properties": {
                    "ciudad": str(fila.get('Ciudad', '')),
                    "direccion": str(fila.get('Direccion', '')),
                    "codigo_postal": str(fila.get('CP', '')),
                    "nombre_completo_contacto": str(fila.get('Contacto Principal', ''))
                }
            }
            
            response = requests.patch(f"{url_hs}/{proy_id}", headers=HEADERS, json=payload)
            
            if response.status_code in [200, 204]:
                nombre_empresa = fila.get('Empresa', 'Proyecto')
                print(f"✅ {nombre_empresa} actualizado en HubSpot.")
                
                # --- AQUÍ LA MAGIA: Avisamos al Excel ---
                marcar_como_procesado_en_google(cif_hs)
            else:
                print(f"⚠️ Error al actualizar el proyecto ID {proy_id} en HubSpot.")

if __name__ == "__main__":
    ejecutar_sincronizacion_perfecta()
