import pandas as pd
import requests
import os

token = os.getenv('HUBSPOT_ACCESS_TOKEN')
headers = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}

def exportar_clientes():
    print("🔍 Consultando HubSpot para obtener empresas en etapa 'Cliente'...")
    url = "https://api.hubapi.com/crm/v3/objects/companies/search"
    
    # Filtro para traer solo los que son "Customer"
    query = {
        "filterGroups": [{"filters": [{"propertyName": "lifecyclestage", "operator": "EQ", "value": "customer"}]}],
        "properties": [
            "name", "nombre_fiscal_de_la_empresa", "cif", 
            "nombre_completo_contacto", "nombre_responsablede_facturacion_de_la_empresa",
            "email_responsable_de_facturacion_de_la_empresa", "nombre_responsable_degestion_del_proyecto",
            "email_responsable_de_gestion_del_proyecto", "nombre_de_dominio_de_la_empresa",
            "address", "city", "zip"
        ],
        "limit": 100
    }

    res = requests.post(url, headers=headers, json=query)
    if res.status_code != 200:
        print(f"❌ Error: {res.text}")
        return

    empresas = res.json().get('results', [])
    if not empresas:
        print("ℹ️ No hay ninguna empresa marcada como 'Cliente' ahora mismo.")
        return

    # Extraer los datos limpios
    datos = [e.get('properties', {}) for e in empresas]
    df = pd.DataFrame(datos)

    # Ordenar y limpiar nombres de columnas para el Excel
    columnas = {
        'name': 'Empresa',
        'nombre_fiscal_de_la_empresa': 'Nombre Fiscal',
        'cif': 'CIF',
        'nombre_completo_contacto': 'Contacto Principal',
        'nombre_responsablede_facturacion_de_la_empresa': 'Resp. Facturación',
        'email_responsable_de_facturacion_de_la_empresa': 'Email Facturación',
        'address': 'Dirección',
        'city': 'Ciudad',
        'zip': 'CP'
    }
    df.rename(columns=columnas, inplace=True)

    # Guardar el archivo
    df.to_excel('clientes_hubspot.xlsx', index=False)
    print(f"✅ ¡Hecho! Se han guardado {len(df)} clientes en 'clientes_hubspot.xlsx'")

if __name__ == "__main__":
    exportar_clientes()
