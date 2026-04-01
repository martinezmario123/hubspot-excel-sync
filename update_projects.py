import requests
import os
from dotenv import load_dotenv

load_dotenv()

def inspeccionar_campos_reales():
    token = os.getenv('HUBSPOT_ACCESS_TOKEN')
    headers = {'Authorization': f'Bearer {token}'}
    
    # Esta URL pide la definición de los campos del objeto 0-970
    url = "https://api.hubapi.com/crm/v3/properties/0-970"
    
    print("🕵️ Investigando cómo se llaman los campos 'Ciudad' y 'Dirección' de verdad...")
    res = requests.get(url, headers=headers)
    
    if res.status_code == 200:
        propiedades = res.json().get('results', [])
        # Buscamos cualquier cosa que se parezca a ciudad o dirección
        for p in propiedades:
            n = p.get('name', '').lower()
            l = p.get('label', '').lower()
            if 'ciudad' in n or 'ciudad' in l or 'direc' in n or 'direc' in l:
                print(f"📌 ENCONTRADO -> Etiqueta: '{p.get('label')}' | NOMBRE INTERNO: '{p.get('name')}'")
    else:
        print(f"❌ Error al inspeccionar: {res.text}")

if __name__ == "__main__":
    inspeccionar_campos_reales()
