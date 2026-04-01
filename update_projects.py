import requests
import os
from dotenv import load_dotenv

load_dotenv()

def verificar_acceso_proyectos():
    token = os.getenv('HUBSPOT_ACCESS_TOKEN')
    headers = {'Authorization': f'Bearer {token}'}
    
    # Probamos a leer el objeto Proyectos directamente
    url = "https://api.hubapi.com/crm/v3/objects/0-970"
    
    print("📡 Probando acceso a Proyectos (0-970)...")
    res = requests.get(url, headers=headers)
    
    if res.status_code == 200:
        print("✅ ¡POR FIN! El robot ya tiene permiso para entrar en Proyectos.")
        print(f"He encontrado {len(res.json().get('results', []))} proyectos.")
    else:
        print(f"❌ Seguimos con error {res.status_code}")
        print(f"Mensaje de HubSpot: {res.json().get('message')}")

if __name__ == "__main__":
    verificar_acceso_proyectos()
