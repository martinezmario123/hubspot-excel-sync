import requests
import os
from dotenv import load_dotenv

load_dotenv()

def inspeccion_tecnica_propiedad():
    token = os.getenv('HUBSPOT_ACCESS_TOKEN')
    headers = {'Authorization': f'Bearer {token}'}
    
    # Consultamos la definición específica de la propiedad 'ciudad'
    url = "https://api.hubapi.com/crm/v3/properties/0-970/ciudad"
    
    print("🔬 Analizando la propiedad 'ciudad' en HubSpot...")
    res = requests.get(url, headers=headers)
    
    if res.status_code == 200:
        data = res.json()
        tipo = data.get('fieldType')
        opciones = data.get('options', [])
        
        print(f"\n📊 RESULTADOS:")
        print(f"🔹 Tipo de campo: {tipo}")
        
        if opciones:
            print(f"⚠️ ¡OJO! Es un desplegable. Las opciones permitidas son:")
            for opt in opciones:
                print(f"   - {opt['label']} (valor: {opt['value']})")
        else:
            print("✅ Es un campo de texto normal.")
            
    else:
        print(f"❌ Error al inspeccionar: {res.text}")

if __name__ == "__main__":
    inspeccion_tecnica_propiedad()
