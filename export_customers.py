import pandas as pd
import requests
import os

token = os.getenv('HUBSPOT_ACCESS_TOKEN')
headers = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}

def exportar_clientes():
    print("🔍 Extrayendo datos actualizados de Mercadona y otros clientes...")
    url = "https://api.hubapi.com/crm/v3/objects/companies/search"
    
    query = {
        "filterGroups": [{"filters": [{"propertyName": "lifecyclestage", "operator": "EQ", "value": "customer"}]}],
        "properties": [
            "name", 
            "nombre_fiscal_de_la_empresa", 
            "cif", 
            "nombre_completo_contacto", 
            "nombre_responsablede_facturacion_de_la_empresa",
            "email_responsable_de_facturacion_de_la_empresa", 
            "nombre_responsable_degestion_del_proyecto",
            "email_responsable_de_gestion_del_proyecto", 
            "nombre_de_dominio_de_la_empresa",
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
        print("ℹ️ No hay clientes para exportar.")
        return

    # Extraemos solo las propiedades, ignorando IDs internos de HubSpot
    datos_limpios = [e.get('properties', {}) for e in empresas]
    df = pd.DataFrame(datos_limpios)

    # DEFINIMOS EL ORDEN Y LOS NOMBRES BONITOS
    # Esto elimina las columnas como 'hs_object_id' que no queremos ver
    columnas_finales = {
        'name': 'Empresa',
        'nombre_fiscal_de_la_empresa': 'Nombre Fiscal',
        'cif': 'CIF',
        'nombre_completo_contacto': 'Contacto Principal',
        'nombre_responsablede_facturacion_de_la_empresa': 'Responsable Facturación',
        'email_responsable_de_facturacion_de_la_empresa': 'Email Facturación',
        'nombre_responsable_degestion_del_proyecto': 'Gestor Proyecto',
        'email_responsable_de_gestion_del_proyecto': 'Email Proyecto',
        'nombre_de_dominio_de_la_empresa': 'Dominio/Web',
        'address': 'Dirección',
        'city': 'Ciudad',
        'zip': 'CP'
    }

    # Seleccionamos solo las columnas que hemos definido arriba
    df = df[list(columnas_finales.keys())]
    # Les cambiamos el nombre técnico por el nombre "humano"
    df.rename(columns=columnas_finales, inplace=True)

    # Guardar el archivo
    df.to_excel('clientes_hubspot.xlsx', index=False)
    print(f"✅ ¡ÉXITO! Excel actualizado con {len(df)} filas y datos completos.")

if __name__ == "__main__":
    exportar_clientes()
