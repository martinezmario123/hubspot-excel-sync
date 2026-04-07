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

# URL de tu Apps Script (Para marcar como PROCESADO)
URL_APPS_SCRIPT = "https://script.google.com/macros/s/AKfycbx9EZ0FbqF0JfQcPU5ShjHYQRqoGMAwfKTutKWiJaAVnEBl_RIo6xnlvDSwLHd_dQtVnA/exec"

# URL de tu Google Drive (Publicado como CSV)
URL_DRIVE = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSib6KDzwI4xKJpg_HHJD_jI2Or8ACdnGPS1DTpKSCoc35piMCZJDeXxmvn7AAxiGcXtF9oX3yyWoEK/pub?output=csv"

def marcar_como_procesado_en_google(cif):
    """Envía la señal al Excel para cambiar el estado a PROCESADO"""
    payload = {
        "accion": "marcar_procesado",
        "cif": str(cif).strip()
    }
    try:
        # allow_redirects=True es fundamental para que Google Scripts funcione
        response = requests.post(URL_APPS_SCRIPT, data=json.dumps(payload), allow_redirects=True)
        print(f"  ∟ 📝 Google Sheets: {response.text}")
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
        print(f"✅ Datos cargados: {len(df)} filas encontradas.")
        
    except Exception as e:
        print(f"❌ Error durante la descarga de Drive: {e}")
        return

    # Limpieza de CIF para evitar errores de formato
    df['CIF'] = df['CIF'].astype(str).str.replace(r'\s+', '', regex=True).str.upper()

    # 2. Obtener Proyectos actuales de HubSpot
    url_hs = f"https://api.hubapi.com/crm/v3/objects/{OBJETO_PROYECTOS}"
    res = requests.get(url_hs, headers=HEADERS, params={'properties': 'cif,name'})
    
    if res.status_code != 200:
        print("❌ Error de conexión con HubSpot. Revisa el TOKEN.")
        return

    proyectos = res.json().get('results', [])
    print(f"🔄 Sincronizando {len(proyectos)} proyectos desde HubSpot...")

    for proy in proyectos:
        proy_id = proy['id']
        # Limpiamos el CIF de HubSpot
        cif_hs = str(proy['properties'].get('cif', '')).replace(" ", "").upper()
        
        if not cif_hs:
            continue

        # Buscamos este CIF en nuestro DataFrame de Drive
        match = df[df['CIF'] == cif_hs]
        
        if not match.empty:
            fila = match.iloc[0]
            
            # Preparamos los datos para HubSpot
            payload = {
                "properties": {
                    "ciudad": str(fila.get('Ciudad', '')),
                    "direccion": str(fila.get('Direccion', '')),
                    "codigo_postal": str(fila.get('CP', '')),
                    "nombre_completo_contacto": str(fila.get('Contacto Principal', ''))
                }
            }
            
            # Enviamos la actualización a HubSpot
            response = requests.patch(f"{url_hs}/{proy_id}", headers=HEADERS, json=payload)
            
            if response.status_code in [200, 204]:
                print(f"✅ {fila.get('Empresa', 'Proyecto')} actualizado en HubSpot.")
                
                # --- AQUÍ AVISAMOS A GOOGLE SHEETS ---
                marcar_como_procesado_en_google(cif_hs)
            else:
                print(f"⚠️ Error al actualizar el proyecto ID {proy_id} en HubSpot.")

if __name__ == "__main__":
    ejecutar_sincronizacion_perfecta()
