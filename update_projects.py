import requests
import os
from dotenv import load_dotenv

load_dotenv()

def inspeccionar_nombres_reales():
    token = os.getenv('HUBSPOT_ACCESS_TOKEN')
    headers = {'Authorization': f'Bearer {token}'}
    
    # El ID del proyecto de Mercadona que sacamos antes
    proy_id = "1174184826056" 
    
    # Pedimos TODAS las propiedades que tengan algún valor
    url = f"https://api.hubapi.com/crm/v3/objects/0-970/{proy_id}"
    
    res = requests.get(url, headers=headers)
    
    if res.status_code == 200:
        props = res.json().get('properties', {})
        print(f"\n🔍 LISTA DE PROPIEDADES REALES (PROYECTO {proy_id}):")
        print("-" * 60)
        for nombre_interno, valor in props.items():
            # Buscamos la que tenga "Elche" o cualquier dato que reconozcas
            if valor and valor != "null":
                print(f"📌 Nombre Interno: {nombre_interno} | Valor Actual: {valor}")
        print("-" * 60)
        print("💡 Busca el que tenga valor 'Elche'. Ese nombre raro de la izquierda es el que pondremos en el código.")
    else:
        print(f"❌ Error al leer: {res.text}")

if __name__ == "__main__":
    inspeccionar_nombres_reales()
