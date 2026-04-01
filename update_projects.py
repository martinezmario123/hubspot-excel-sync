import requests
import os
from dotenv import load_dotenv

load_dotenv()

def descubrir_nombre_objeto():
    token = os.getenv('HUBSPOT_ACCESS_TOKEN')
    headers = {'Authorization': f'Bearer {token}'}
    
    # Pedimos la lista de todos los esquemas de objetos personalizados
    url = "https://api.hubapi.com/crm/v3/schemas"
    
    print("🔍 Buscando el nombre técnico del objeto Proyectos...")
    res = requests.get(url, headers=headers)
    
    if res.status_code == 200:
        schemas = res.json().get('results', [])
        for s in schemas:
            print(f"📌 Encontrado: {s.get('labels', {}).get('singular')} -> Nombre técnico: '{s.get('name')}'")
    else:
        print(f"❌ Error: {res.text}")

if __name__ == "__main__":
    descubrir_nombre_objeto()
