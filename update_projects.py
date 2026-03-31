import requests
import pandas as pd
import os
from dotenv import load_dotenv

load_dotenv()

def actualizar_proyectos_desde_csv():
    token = os.getenv('HUBSPOT_ACCESS_TOKEN') or os.getenv('HS_ACCESS_TOKEN')
    headers = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}
    
    print("🔍 Listando todos los esquemas disponibles en esta cuenta...")
    res_schemas = requests.get("https://api.hubapi.com/crm/v3/schemas", headers=headers)
    
    nombre_tecnico_encontrado = None
    
    if res_schemas.status_code == 200:
        esquemas = res_schemas.json().get('results', [])
        print(f"📋 Se han encontrado {len(esquemas)} objetos.")
        
        for s in esquemas:
            singular = s.get('labels', {}).get('singular', 'S/N')
            plural = s.get('labels', {}).get('plural', 'S/N')
            interno = s.get('name')
            print(f"📌 Objeto: {singular} / {plural} -> Nombre interno: {interno}")
            
            # Si se llama Proyecto o algo parecido, lo guardamos
            if 'proyect' in singular.lower() or 'proyect' in plural.lower():
                nombre_tecnico_encontrado = interno
    else:
        print(f"❌ Error al consultar esquemas: {res_schemas.text}")
        return

    if not nombre_tecnico_encontrado:
        print("❌ No se detectó ningún objeto con la palabra 'Proyecto'.")
        print("💡 REVISA EL LOG ARRIBA: Mira la lista de 'Nombre interno' y dime cuál crees que es.")
        return

    print(f"🚀 ¡Objeto localizado! Usando: {nombre_tecnico_encontrado}")

    # --- PARTE DE ACTUALIZACIÓN ---
    archivo = 'clientes_hubspot.csv'
    if not os.path.exists(archivo): return
    df = pd.read_csv(archivo)
    col_cif = [c for c in df.columns if 'cif' in c.lower()][0]
    df[col_cif] = df[col_cif].astype(str).str.strip()

    url_base = f"https://api.hubapi.com/crm/v3/objects/{nombre_tecnico_encontrado}"
    params = {'properties': 'cif,ciudad,nombre_de_la_empresa', 'limit': 100}
    res = requests.get(url_base, headers=headers, params=params)

    if res.status_code == 200:
        proyectos = res.json().get('results', [])
        for proj in proyectos:
            cif_hs = str(proj['properties'].get('cif', '')).strip()
            match = df[df[col_cif] == cif_hs]
            if not match.empty:
                info = match.iloc[0]
                body = {"properties": {
                    "nombre_de_la_empresa": info.get('nombre_empresa', info.get('empresa_para_excel', '---')),
                    "ciudad": info.get('ciudad', '---')
                }}
                requests.patch(f"{url_base}/{proj['id']}", headers=headers, json=body)
                print(f"✅ Proyecto {cif_hs} actualizado.")
    else:
        print(f"❌ Error al leer objetos: {res.text}")

if __name__ == "__main__":
    actualizar_proyectos_desde_csv()
