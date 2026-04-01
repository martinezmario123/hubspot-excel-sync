import requests
import os
from dotenv import load_dotenv

load_dotenv()

def prueba_escritura_v2():
    token = os.getenv('HUBSPOT_ACCESS_TOKEN')
    headers = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}
    
    # ID de Mercadona
    proy_id = "1174184826056" 
    
    print(f"🚀 Intentando actualizar Ciudad a 'Alicante' con el nuevo Token...")
    
    url = f"https://api.hubapi.com/crm/v3/objects/0-970/{proy_id}"
    payload = {"properties": {"ciudad": "Alicante"}}
    
    # Enviamos el cambio
    requests.patch(url, headers=headers, json=payload)
    
    # Comprobamos el resultado inmediatamente
    import time
    time.sleep(1) # Esperamos un segundo para que HubSpot asimile el cambio
    
    check = requests.get(f"{url}?properties=ciudad", headers=headers).json()
    valor_final = check.get('properties', {}).get('ciudad', 'VACÍO')
    
    print(f"\n📊 RESULTADO FINAL EN HUBSPOT: '{valor_final}'")
    
    if valor_final == "Alicante":
        print("✅ ¡CONSEGUIDO! El nuevo token funciona. Ya podemos sincronizar todo.")
    else:
        print("❌ Sigue saliendo VACÍO. El problema es una automatización interna de HubSpot.")

if __name__ == "__main__":
    prueba_escritura_v2()
