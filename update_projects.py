import requests
import pandas as pd
import os
from dotenv import load_dotenv

load_dotenv()

def ejecutar_sincronizacion():
    token = os.getenv('HUBSPOT_ACCESS_TOKEN') or os.getenv('HS_ACCESS_TOKEN')
    headers = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}
    
    # --- PASO 1: IDENTIFICAR EL OBJETO SIN USAR IDs PROHIBIDOS ---
    print("🔎 Buscando objetos accesibles...")
    res_schemas = requests.get("https://api.hubapi.com/crm/v3/schemas", headers=headers)
    
    rutas_a_probar = []
    if res_schemas.status_code == 200:
        for s in res_schemas.json().get('results', []):
            name = s['name']
            label = s.get('labels', {}).get('singular', '').lower()
            print(f"📌 Detectado objeto: {label} (Ruta: {name})")
            if 'proyect' in label or 'proyect' in name.lower():
                rutas_a_probar.append(name)
    
    # Si no detectamos nada, probamos con 'deals' que es lo más común
    if not rutas_a_probar:
        print("⚠️ No se detectaron objetos llamados 'Proyecto'. Probando con 'deals' (Negocios)...")
        rutas_a_probar = ["deals"]

    # --- PASO 2: INTENTAR ACTUALIZAR ---
    if not os.path.exists('clientes_hubspot.csv'): return
    df = pd.read_csv('clientes_hubspot.csv')
    col_cif_csv = [c for c in df.columns if 'cif' in c.lower()][0]

    for ruta in rutas_a_probar:
        print(f"🚀 Intentando sincronizar en la ruta: {ruta}...")
        url = f"https://api.hubapi.com/crm/v3/objects/{ruta}"
        # Intentamos leer (cif es el campo clave)
        res = requests.get(url, headers=headers, params={'properties': 'cif,ciudad,nombre_de_la_empresa'})
        
        if res.status_code == 200:
            items = res.json().get('results', [])
            print(f"✅ ¡Conectado con éxito a {ruta}! Procesando {len(items)} registros...")
            for item in items:
                cif_hs = str(item['properties'].get('cif', '')).strip()
                match = df[df[col_cif_csv].astype(str) == cif_hs]
                if not match.empty:
                    info = match.iloc[0]
                    payload = {"properties": {
                        "nombre_de_la_empresa": info.get('nombre_empresa', '---'),
                        "ciudad": info.get('ciudad', '---')
                    }}
                    requests.patch(f"{url}/{item['id']}", headers=headers, json=payload)
                    print(f"   ✨ Actualizado CIF: {cif_hs}")
            return # Si funciona una ruta, paramos
        else:
            print(f"❌ Ruta {ruta} rechazada (Error {res.status_code})")

if __name__ == "__main__":
    ejecutar_sincronizacion()
