import requests
import os
from dotenv import load_dotenv

load_dotenv()

def buscar_nombres_tecnicos():
    token = os.getenv('HUBSPOT_ACCESS_TOKEN') or os.getenv('HS_ACCESS_TOKEN')
    headers = {'Authorization': f'Bearer {token}'}
    
    print("🔎 BUSCANDO NOMBRES TÉCNICOS DE OBJETOS...")
    
    # Esta es la URL mágica que nos dice cómo se llaman tus objetos por dentro
    url_schemas = "https://api.hubapi.com/crm/v3/schemas"
    res = requests.get(url_schemas, headers=headers)
    
    if res.status_code == 200:
        schemas = res.json().get('results', [])
        print(f"✅ ¡Conectado! Tienes acceso a {len(schemas)} objetos.")
        
        for s in schemas:
            label = s['labels']['singular']
            obj_id = s['objectTypeId']
            nombre_real = s['name'] # ESTE ES EL QUE NECESITAMOS
            
            print(f"📌 Objeto: {label} | ID: {obj_id} | USAR ESTE NOMBRE: {nombre_real}")
    else:
        print(f"❌ Error {res.status_code}: {res.text}")
        print("👉 Si sale 403, revisa que el permiso 'crm.schemas.custom.read' esté marcado en HubSpot.")

if __name__ == "__main__":
    buscar_nombres_tecnicos()
