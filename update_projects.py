import requests
import pandas as pd
import os
from dotenv import load_dotenv

load_dotenv()

def ejecutar_sincronizacion():
    token = os.getenv('HUBSPOT_ACCESS_TOKEN') or os.getenv('HS_ACCESS_TOKEN')
    headers = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}
    
    # 1. LEER EL CSV
    if not os.path.exists('clientes_hubspot.csv'):
        print("❌ No encuentro el archivo CSV")
        return
    df = pd.read_csv('clientes_hubspot.csv')
    col_cif_csv = [c for c in df.columns if 'cif' in c.lower()][0]
    df[col_cif_csv] = df[col_cif_csv].astype(str).str.strip()

    # 2. PROBAR RUTAS ESTÁNDAR QUE SUELEN SER "PROYECTOS"
    # Probamos tickets primero porque es lo más probable para el ID 0-970
    rutas = ["tickets", "deals"] 
    
    for ruta in rutas:
        print(f"🚀 Probando en la sección de: {ruta}...")
        url = f"https://api.hubapi.com/crm/v3/objects/{ruta}"
        
        # Intentamos traer los registros
        res = requests.get(url, headers=headers, params={'properties': 'cif,ciudad,nombre_de_la_empresa', 'limit': 100})
        
        if res.status_code == 200:
            items = res.json().get('results', [])
            if len(items) == 0:
                print(f"ℹ️ Conectado a {ruta}, pero está vacío (0 registros).")
                continue
            
            print(f"✅ ¡Bingo! Encontrados {len(items)} registros en {ruta}. Sincronizando...")
            for item in items:
                cif_hs = str(item['properties'].get('cif', '')).strip()
                match = df[df[col_cif_csv] == cif_hs]
                
                if not match.empty:
                    info = match.iloc[0]
                    print(f"   ✨ Match CIF {cif_hs}. Actualizando...")
                    payload = {"properties": {
                        "nombre_de_la_empresa": info.get('nombre_empresa', '---'),
                        "ciudad": info.get('ciudad', '---')
                    }}
                    requests.patch(f"{url}/{item['id']}", headers=headers, json=payload)
            return 
        else:
            print(f"❌ Error en {ruta}: {res.status_code}")

if __name__ == "__main__":
    ejecutar_sincronizacion()
