import requests
import pandas as pd
import os
from dotenv import load_dotenv

load_dotenv()

def ejecutar_sincronizacion():
    token = os.getenv('HUBSPOT_ACCESS_TOKEN') or os.getenv('HS_ACCESS_TOKEN')
    headers = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}
    
    # 1. LEER EL CSV
    df = pd.read_csv('clientes_hubspot.csv')
    
    # Buscamos las columnas en el Excel (sin importar mayúsculas)
    col_cif_csv = [c for c in df.columns if 'cif' in c.lower()][0]
    
    # Intentamos encontrar la columna de Nombre y Ciudad en el Excel
    def buscar_columna(lista_nombres, df):
        for nombre in lista_nombres:
            encontradas = [c for c in df.columns if nombre in c.lower()]
            if encontradas: return encontradas[0]
        return None

    col_nombre_excel = buscar_columna(['empresa', 'nombre', 'client'], df)
    col_ciudad_excel = buscar_columna(['ciudad', 'poblacion', 'city', 'town'], df)

    # Limpiamos el CIF del Excel
    df[col_cif_csv] = df[col_cif_csv].astype(str).str.strip()

    # 2. SECCIÓN DE NEGOCIOS (DEALS)
    url = "https://api.hubapi.com/crm/v3/objects/deals"
    res = requests.get(url, headers=headers, params={'properties': 'cif', 'limit': 100})
    
    if res.status_code == 200:
        items = res.json().get('results', [])
        for item in items:
            cif_hs = str(item['properties'].get('cif', '')).strip()
            match = df[df[col_cif_csv] == cif_hs]
            
            if not match.empty:
                info = match.iloc[0]
                
                # Sacamos los datos del Excel
                valor_nombre = info.get(col_nombre_excel, "Empresa Desconocida")
                valor_ciudad = info.get(col_ciudad_excel, "---")
                
                print(f"✨ ¡Match! CIF {cif_hs} -> {valor_nombre} ({valor_ciudad})")

                # ACTUALIZAMOS
                payload = {
                    "properties": {
                        "dealname": valor_nombre, # Cambia el título del negocio
                        "ciudad": valor_ciudad    # Rellena el campo ciudad que acabas de crear
                    }
                }
                requests.patch(f"{url}/{item['id']}", headers=headers, json=payload)
    else:
        print(f"❌ Error API: {res.status_code}")

if __name__ == "__main__":
    ejecutar_sincronizacion()
