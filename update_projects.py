import requests
import os
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('HUBSPOT_ACCESS_TOKEN')
HEADERS = {'Authorization': f'Bearer {TOKEN}', 'Content-Type': 'application/json'}

def diagnostico_iberdrola():
    # ID del proyecto de Iberdrola que el robot encontró antes
    # (Lo buscamos por el CIF para estar seguros)
    url = "https://api.hubapi.com/crm/v3/objects/0-970"
    res = requests.get(url, headers=HEADERS, params={'properties': 'cif,ciudad,name'})
    
    proyectos = res.json().get('results', [])
    for p in proyectos:
        if p['properties'].get('cif') == 'A48010615':
            proy_id = p['id']
            print(f"🔎 Analizando Iberdrola (ID: {proy_id})...")
            
            # 1. Intentamos escribir 'BILBAO_TEST'
            requests.patch(f"{url}/{proy_id}", headers=HEADERS, json={"properties": {"ciudad": "BILBAO_TEST"}})
            
            # 2. Leemos inmediatamente qué hay guardado
            import time
            time.sleep(2)
            revisar = requests.get(f"{url}/{proy_id}?properties=ciudad", headers=HEADERS).json()
            valor_real = revisar.get('properties', {}).get('ciudad')
            
            print(f"📊 VALOR EN LA BASE DE DATOS: '{valor_real}'")
            
            if valor_real == "BILBAO_TEST":
                print("✅ El dato SE GUARDA, pero no lo ves en tu pantalla. Estás mirando el campo equivocado.")
            else:
                print("❌ El dato SE BORRA solo. Tienes una automatización o sincronización que limpia el campo.")

if __name__ == "__main__":
    diagnostico_iberdrola()
