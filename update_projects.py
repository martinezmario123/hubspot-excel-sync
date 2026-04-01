import requests
import os
import pandas as pd
from dotenv import load_dotenv

load_dotenv()

def forzar_actualizacion():
    token = os.getenv('HUBSPOT_ACCESS_TOKEN')
    headers = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}
    
    # 1. Tu nombre técnico calculado por el ID de portal
    # Si este no es, probaremos con 'proyectos' a secas
    nombres_a_probar = ["p147977807_proyectos", "proyectos", "proyecto"]
    
    df = pd.read_csv('clientes_hubspot.csv')
    df['CIF'] = df['CIF'].astype(str).str.strip()

    for nombre in nombres_a_probar:
        print(f"🧪 Probando con el nombre: {nombre}...")
        url = f"https://api.hubapi.com/crm/v3/objects/{nombre}"
        res = requests.get(url, headers=headers, params={'properties': 'cif,name'})
        
        if res.status_code == 200:
            items = res.json().get('results', [])
            print(f"✅ ¡LO ENCONTRAMOS! El nombre correcto es: {nombre}")
            
            for item in items:
                cif_hs = str(item['properties'].get('cif', '')).strip()
                match = df[df['CIF'] == cif_hs]
                
                if not match.empty:
                    info = match.iloc[0]
                    print(f"🏗️ Actualizando: {info['Empresa']}")
                    payload = {"properties": {"name": str(info['Empresa']), "ciudad": str(info['Ciudad'])}}
                    requests.patch(f"{url}/{item['id']}", headers=headers, json=payload)
            return # Salimos del bucle si funciona
        else:
            print(f"❌ No es '{nombre}' (Error {res.status_code})")

if __name__ == "__main__":
    forzar_actualizacion()
