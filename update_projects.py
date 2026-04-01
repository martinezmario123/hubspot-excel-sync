import requests
import os
from dotenv import load_dotenv

load_dotenv()

def diagnostico_proyectos():
    token = os.getenv('HUBSPOT_ACCESS_TOKEN') or os.getenv('HS_ACCESS_TOKEN')
    headers = {'Authorization': f'Bearer {token}'}
    
    print("🔍 INVESTIGANDO OBJETOS PERSONALIZADOS...")
    
    # Intentamos leer el "Esquema" (la definición de tus objetos)
    url_schemas = "https://api.hubapi.com/crm/v3/schemas"
    res = requests.get(url_schemas, headers=headers)
    
    if res.status_code == 200:
        schemas = res.json().get('results', [])
        print(f"✅ ¡Conexión exitosa! Tienes acceso a {len(schemas)} objetos personalizados.")
        
        encontrado = False
        for s in schemas:
            label = s['labels']['singular']
            obj_id = s['objectTypeId']
            nombre_interno = s['name']
            print(f"📌 OBJETO ENCONTRADO: '{label}' | ID: {obj_id} | Nombre Interno: {nombre_interno}")
            
            if obj_id == "0-970" or label.lower() == "proyecto":
                encontrado = True
                print(f"⭐ ¡AQUÍ ESTÁ! Para actualizar 'Proyectos' debemos usar el nombre: {nombre_interno}")
        
        if not encontrado:
            print("⚠️ CUIDADO: El objeto 'Proyectos' (0-970) no aparece en la lista de permisos de este token.")
            
    elif res.status_code == 403:
        print("❌ ERROR 403: El token sigue sin tener permiso para leer 'Schemas'.")
        print("Revisa en HubSpot que el permiso 'crm.schemas.custom.read' esté marcado.")
    else:
        print(f"❌ Error inesperado {res.status_code}: {res.text}")

if __name__ == "__main__":
    diagnostico_proyectos()
