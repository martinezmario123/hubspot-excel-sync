import pandas as pd
import requests
import os

token = os.getenv('HUBSPOT_ACCESS_TOKEN')
headers = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}

def exportar_clientes():
    print("🔍 Consultando HubSpot para exportar clientes a CSV...")
    url = "https://api.hubapi.com/crm/v3/objects/companies/search"
    
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
        print(f"❌ Error HubSpot: {res.text}")
        return

    empresas = res.json().get('results', [])
    if not empresas:
        print("ℹ️ No hay clientes para exportar.")
        return

    datos_limpios = [e.get('properties', {}) for e in empresas]
    df = pd.DataFrame(datos_limpios)

    # Mapeo de nombres técnicos a nombres bonitos
    columnas_finales = {
        'name': 'Empresa',
        'nombre_fiscal_de_la_empresa': 'Nombre Fiscal',
        'cif': 'CIF',
        'nombre_completo_contacto': 'Contacto Principal',
        'nombre_responsablede_facturacion_de_la_empresa': 'Responsable Facturacion',
        'email_responsable_de_facturacion_de_la_empresa': 'Email Facturacion',
        'nombre_responsable_degestion_del_proyecto': 'Gestor Proyecto',
        'email_responsable_de_gestion_del_proyecto': 'Email Proyecto',
        'nombre_de_dominio_de_la_empresa': 'Dominio/Web',
        'address': 'Direccion',
        'city': 'Ciudad',
        'zip': 'CP'
    }

    # Aseguramos que solo usamos las columnas que existen en el resultado
    cols_existentes = [c for c in columnas_finales.keys() if c in df.columns]
    df = df[cols_existentes]
    
    # Renombramos
    df.rename(columns=columnas_finales, inplace=True)

    # --- EL CAMBIO CLAVE ---
    # Guardamos como CSV (formato estándar para Google Sheets)
    df.to_csv('clientes_hubspot.csv', index=False, encoding='utf-8')
    print(f"✅ ¡ÉXITO! Archivo 'clientes_hubspot.csv' actualizado con {len(df)} filas.")

if __name__ == "__main__":
    exportar_clientes()
