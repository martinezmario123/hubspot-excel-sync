import requests
import os
from dotenv import load_dotenv

load_dotenv()

def mapeo_real_propiedades():
    token = os.getenv('HUBSPOT_ACCESS_TOKEN')
    headers = {'Authorization': f'Bearer {token}'}
    proy_id = "1174184826056" 
    
    # Esta URL nos devuelve TODAS las propiedades que tienen valor
    url = f"https://api.hubapi.com/crm/v3/objects/0-970/{proy_id}?propertiesWithHistory=true"
    
    print("🔍 Escaneando nombres internos reales...")
    res = requests.get(url, headers=headers)
    
    if res.status_code == 200:
        properties = res.json().get('properties', {})
        print("\n📋 LISTA DE PROPIEDADES ENCONTRADAS:")
        print("-" * 50)
        for nombre, valor in properties.items():
            if valor:
                print(f"🔹 Nombre Interno: {nombre} | Valor: {valor}")
        print("-" * 50)
    else:
        print(f"❌ Error al escanear: {res.text}")

if __name__ == "__main__":
    mapeo_real_propiedades()
