import requests
import os
from dotenv import load_dotenv

load_dotenv()

def forzar_actualizacion_directa():
    token = os.getenv('HUBSPOT_ACCESS_TOKEN')
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    
    # ID de Mercadona
    proy_id = "1174184826056" 
    
    # Intentamos escribir en Ciudad y un campo de Texto llamado 'name' (que siempre es editable)
    url = f"https://api.hubapi.com/crm/v3/objects/0-970/{proy_id}"
    payload = {
        "properties": {
            "ciudad": "Alicante",
            "direccion": "Calle de la Sincro 1"
        }
    }
    
    print(f"📡 Enviando comando de escritura al Proyecto {proy_id}...")
    
    # Usamos PATCH para actualizar
    res = requests.patch(url, headers=headers, json=payload)
    
    if res.status_code in [200, 204]:
        print("✅ Servidor de HubSpot: Petición aceptada.")
        
        # Pedimos el dato de vuelta inmediatamente
        verificacion = requests.get(f"{url}?properties=ciudad,direccion", headers=headers).json()
        props = verificacion.get('properties', {})
        
        print("\n📊 ESTADO REAL EN EL SERVIDOR:")
        print(f"📍 Ciudad: '{props.get('ciudad')}'")
        print(f"🏠 Dirección: '{props.get('direccion')}'")
        
        if props.get('ciudad') == "Alicante":
            print("\n🎉 ¡CONSEGUIDO! El dato ya está en la base de datos.")
        else:
            print("\n⚠️ El servidor aceptó el cambio pero el campo sigue vacío. Esto ocurre si el campo 'Ciudad' está vinculado a otro objeto.")
    else:
        print(f"❌ Error de API: {res.status_code} - {res.text}")

if __name__ == "__main__":
    forzar_actualizacion_directa()
