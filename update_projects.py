import requests
import os
from dotenv import load_dotenv

load_dotenv()

def actualizar_negocio_madre():
    token = os.getenv('HUBSPOT_ACCESS_TOKEN')
    headers = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}
    
    # ID del NEGOCIO de Mercadona (el Deal, no el Proyecto)
    deal_id = "1174184826056" 
    
    print(f"🎯 Intentando actualizar el NEGOCIO madre ({deal_id})...")
    
    url = f"https://api.hubapi.com/crm/v3/objects/deals/{deal_id}"
    payload = {
        "properties": {
            "ciudad": "Alicante",
            "direccion": "Calle de la Sincro 1"
        }
    }
    
    res = requests.patch(url, headers=headers, json=payload)
    
    if res.status_code in [200, 204]:
        print("✅ ¡ÉXITO! El Negocio se ha actualizado.")
        print("💡 Ahora ve a HubSpot y mira si el Proyecto de Mercadona ha cogido la ciudad 'Alicante' automáticamente.")
    else:
        print(f"❌ Error al actualizar Negocio: {res.text}")

if __name__ == "__main__":
    actualizar_negocio_madre()
