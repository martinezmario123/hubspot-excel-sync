import requests
import os
from dotenv import load_dotenv

load_dotenv()

def escaneo_total_objetos():
    token = os.getenv('HUBSPOT_ACCESS_TOKEN')
    headers = {'Authorization': f'Bearer {token}'}
    
    # 1. Probamos a listar todos los ESQUEMAS (la estructura de tu HubSpot)
    url = "https://api.hubapi.com/crm/v3/schemas"
    
    print("📡 Iniciando escaneo profundo de objetos...")
    res = requests.get(url, headers=headers)
    
    if res.status_code == 200:
        objetos = res.json().get('results', [])
        print(f"✅ ¡Conexión establecida! He encontrado {len(objetos)} tipos de objetos.\n")
        
        for obj in objetos:
            singular = obj['labels']['singular']
            nombre_api = obj['name']
            id_objeto = obj['objectTypeId']
            
            print(f"📌 OBJETO: {singular}")
            print(f"   - NOMBRE PARA EL CÓDIGO: {nombre_api}")
            print(f"   - ID: {id_objeto}")
            print("-" * 30)
            
    else:
        print(f"❌ Error {res.status_code}: {res.text}")
        print("\n💡 Si sale 403 aquí, es que falta el permiso 'crm.schemas.custom.read'.")

if __name__ == "__main__":
    escaneo_total_objetos()
