import requests
import os
from dotenv import load_dotenv

load_dotenv()

def escaneo_simple():
    token = os.getenv('HUBSPOT_ACCESS_TOKEN')
    headers = {'Authorization': f'Bearer {token}'}
    proy_id = "1174184826056" 
    
    # Esta URL pide el objeto sin filtros, para que nos devuelva lo que tenga
    url = f"https://api.hubapi.com/crm/v3/objects/0-970/{proy_id}"
    
    print(f"🔎 Escaneando todas las propiedades visibles del Proyecto {proy_id}...")
    res = requests.get(url, headers=headers)
    
    if res.status_code == 200:
        properties = res.json().get('properties', {})
        print("\n📋 DATOS ENCONTRADOS:")
        print("-" * 50)
        for nombre, valor in properties.items():
            if valor:
                print(f"🔸 {nombre}: {valor}")
        print("-" * 50)
    else:
        print(f"❌ Error: {res.status_code} - {res.text}")

if __name__ == "__main__":
    escaneo_simple()
