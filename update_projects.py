import requests
import os
from dotenv import load_dotenv

load_dotenv()

def sincronizacion_directa_v3():
    token = os.getenv('HUBSPOT_ACCESS_TOKEN')
    headers = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}
    
    # El ID de tu proyecto de Mercadona (lo sacamos de tus logs anteriores)
    proy_id = "1174184826056" 
    
    print(f"⚡ Intentando inyectar 'ALICANTE' en Proyecto {proy_id}...")
    
    url = f"https://api.hubapi.com/crm/v3/objects/0-970/{proy_id}"
    payload = {
        "properties": {
            "ciudad": "Alicante",
            "direccion": "Nueva Direccion Mercadona"
        }
    }
    
    # Hacemos el envío
    res = requests.patch(url, headers=headers, json=payload)
    
    if res.status_code in [200, 204]:
        print("✅ ¡ÉXITO! HubSpot ha aceptado el cambio.")
        
        # Comprobamos si el dato se ha quedado guardado o si HubSpot lo borra
        print("🔎 Comprobando valor real en el servidor...")
        check = requests.get(f"{url}?properties=ciudad", headers=headers).json()
        valor = check.get('properties', {}).get('ciudad', 'ERROR/VACÍO')
        print(f"📊 Valor guardado en HubSpot: '{valor}'")
    else:
        print(f"❌ Error crítico: {res.text}")

if __name__ == "__main__":
    sincronizacion_directa_v3()
