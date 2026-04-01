import requests
import os
from dotenv import load_dotenv

load_dotenv()

def prueba_campo_alternativo():
    token = os.getenv('HUBSPOT_ACCESS_TOKEN')
    headers = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}
    proy_id = "1174184826056" 
    
    # Intentamos escribir en el campo DIRECCION
    url = f"https://api.hubapi.com/crm/v3/objects/0-970/{proy_id}"
    payload = {"properties": {"direccion": "CALLE PROBANDO 123"}}
    
    print(f"🚀 Intentando escribir en el campo DIRECCION...")
    res = requests.patch(url, headers=headers, json=payload)
    
    import time
    time.sleep(2) 
    
    check = requests.get(f"{url}?properties=direccion", headers=headers).json()
    valor = check.get('properties', {}).get('direccion', 'VACÍO')
    
    print(f"\n📊 RESULTADO EN DIRECCION: '{valor}'")
    
    if valor == "CALLE PROBANDO 123":
        print("✅ ¡La dirección SÍ se guarda! El problema es solo el campo Ciudad.")
    else:
        print("❌ Tampoco se guarda la dirección. El problema es de permisos generales.")

if __name__ == "__main__":
    prueba_campo_alternativo()
