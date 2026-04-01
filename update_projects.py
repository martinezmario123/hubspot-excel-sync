import requests
import os
from dotenv import load_dotenv

load_dotenv()

def prueba_nombre_alternativo():
    token = os.getenv('HUBSPOT_ACCESS_TOKEN')
    headers = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}
    proy_id = "1174184826056" 
    
    # Probamos con 'p_proyectos' que es el nombre por defecto en muchas cuentas
    # Si falla, probaremos con 'proyectos'
    nombres_a_probar = ["p_proyectos", "proyectos", "project"]
    
    for nombre in nombres_a_probar:
        print(f"🧪 Probando con el nombre técnico: '{nombre}'...")
        url = f"https://api.hubapi.com/crm/v3/objects/{nombre}/{proy_id}"
        payload = {"properties": {"ciudad": "Alicante"}}
        
        res = requests.patch(url, headers=headers, json=payload)
        
        if res.status_code in [200, 204]:
            print(f"✅ ¡BINGO! El nombre real era '{nombre}'.")
            return
        else:
            print(f"❌ '{nombre}' no es el correcto (Error {res.status_code})")

if __name__ == "__main__":
    prueba_nombre_alternativo()
