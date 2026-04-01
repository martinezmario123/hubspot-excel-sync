import requests
import os
from dotenv import load_dotenv

load_dotenv()

def escanear_nombres_internos():
    token = os.getenv('HUBSPOT_ACCESS_TOKEN')
    headers = {'Authorization': f'Bearer {token}'}
    
    # Consultamos la definición del objeto 0-970
    url = "https://api.hubapi.com/crm/v3/schemas/0-970"
    
    print("🧬 Escaneando el ADN del objeto Proyectos...")
    res = requests.get(url, headers=headers)
    
    if res.status_code == 200:
        data = res.json()
        properties = data.get('properties', [])
        
        print(f"\n📋 CAMPOS ENCONTRADOS EN 'PROYECTOS':")
        print("-" * 60)
        for prop in properties:
            label = prop.get('label')  # El nombre que tú ves
            name = prop.get('name')    # EL NOMBRE QUE NECESITA EL ROBOT
            
            # Filtramos para no ver la basura del sistema
            if not name.startswith('hs_'):
                print(f"📍 Etiqueta: {label: <20} | NOMBRE INTERNO: {name}")
        print("-" * 60)
        print("\n💡 Busca el que ponga 'Ciudad'. El NOMBRE INTERNO será algo raro.")
    else:
        print(f"❌ Error al escanear: {res.text}")

if __name__ == "__main__":
    escanear_nombres_internos()
