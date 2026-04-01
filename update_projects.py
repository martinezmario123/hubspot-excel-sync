import requests
import os
from dotenv import load_dotenv

load_dotenv()

def prueba_definitiva_permisos():
    token = os.getenv('HUBSPOT_ACCESS_TOKEN')
    headers = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}
    proy_id = "1174184826056" 
    
    url = f"https://api.hubapi.com/crm/v3/objects/0-970/{proy_id}"
    payload = {"properties": {"ciudad": "Alicante_Test", "direccion": "Calle_Test"}}
    
    print("🔑 Probando llave maestra de escritura...")
    res = requests.patch(url, headers=headers, json=payload)
    
    # Si el error es de permisos, aquí HubSpot nos dirá la verdad
    if res.status_code != 204 and res.status_code != 200:
        print(f"❌ ERROR DE PERMISOS: {res.text}")
    else:
        import time
        time.sleep(2)
        check = requests.get(f"{url}?properties=ciudad,direccion", headers=headers).json()
        print(f"📊 Resultado en Servidor: {check.get('properties')}")

if __name__ == "__main__":
    prueba_definitiva_permisos()
