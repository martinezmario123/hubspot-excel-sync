import requests
import os
import pandas as pd
from dotenv import load_dotenv

load_dotenv()

def sincronizacion_total_agresiva():
    token = os.getenv('HUBSPOT_ACCESS_TOKEN')
    headers = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}
    
    # Datos de prueba para Mercadona
    proy_id = "1174184826056"
    nueva_ciudad = "Alicante_Final"

    # 1. Primero pedimos TODAS las propiedades que existen en ese proyecto
    # para ver si hay otra 'ciudad' con nombre raro
    url_get = f"https://api.hubapi.com/crm/v3/objects/0-970/{proy_id}?properties=ciudad,direccion,nombre_fiscal_de_la_empresa"
    res_get = requests.get(url_get, headers=headers).json()
    
    print(f"📊 Antes de actualizar: {res_get.get('properties')}")

    # 2. Intentamos actualizar usando nombres alternativos por si acaso
    payload = {
        "properties": {
            "ciudad": nueva_ciudad,
            "direccion": "Calle Nueva 123",
            "nombre_fiscal_de_la_empresa": "Mercadona S.A."
        }
    }
    
    print(f"🚀 Enviando datos a Proyecto {proy_id}...")
    r = requests.patch(f"https://api.hubapi.com/crm/v3/objects/0-970/{proy_id}", headers=headers, json=payload)
    
    if r.status_code in [200, 204]:
        # 3. VERIFICACIÓN CRÍTICA
        # Esperamos 2 segundos para que HubSpot procese
        import time
        time.sleep(2)
        
        check = requests.get(url_get, headers=headers).json()
        final_props = check.get('properties', {})
        
        print("\n🏁 RESULTADO EN EL SERVIDOR:")
        print(f"🔹 Ciudad: '{final_props.get('ciudad')}'")
        print(f"🔹 Dirección: '{final_props.get('direccion')}'")
        print(f"🔹 Nombre Fiscal: '{final_props.get('nombre_fiscal_de_la_empresa')}'")
        
        if final_props.get('ciudad') == nueva_ciudad:
            print("\n✅ ¡SÍ! El dato se ha guardado correctamente. Si no lo ves, es el navegador.")
        else:
            print("\n❌ El servidor sigue borrando el dato. Hay un Workflow activo en tu HubSpot.")
    else:
        print(f"❌ Error API: {r.text}")

if __name__ == "__main__":
    sincronizacion_total_agresiva()
