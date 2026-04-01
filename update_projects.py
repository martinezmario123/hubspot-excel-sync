import requests
import os
from dotenv import load_dotenv

load_dotenv()

def autopsia_token():
    token = os.getenv('HUBSPOT_ACCESS_TOKEN')
    headers = {'Authorization': f'Bearer {token}'}
    
    # 1. Preguntamos a HubSpot: "¿Quién soy y qué permisos tengo?"
    url_access = "https://api.hubapi.com/oauth/v1/access-tokens/" + token
    
    print("🕵️ Analizando Token en HubSpot...")
    res = requests.get(url_access)
    
    if res.status_code == 200:
        info = res.json()
        scopes = info.get('scopes', [])
        print(f"✅ Token válido para el portal: {info.get('hub_id')}")
        print("🔑 Permisos activos en este Token:")
        for s in scopes:
            print(f" - {s}")
        
        # Verificamos si 'crm.objects.custom.read' está en la lista
        if 'crm.objects.custom.read' not in scopes:
            print("\n❌ ¡CUIDADO! El permiso 'crm.objects.custom.read' NO está en este token.")
            print("👉 Esto significa que GitHub está usando un Token VIEJO. Tienes que actualizar el Secret.")
    else:
        print(f"❌ Error al validar token: {res.status_code}")

if __name__ == "__main__":
    autopsia_token()
