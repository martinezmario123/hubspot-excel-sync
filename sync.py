import pandas as pd
import requests
import os
import json

# Configuración de acceso
token = os.getenv('HUBSPOT_ACCESS_TOKEN')
headers = {
    'Authorization': f'Bearer {token}', 
    'Content-Type': 'application/json'
}

def procesar_y_enviar():
    # 1. Diagnóstico de conexión
    try:
        info_test = requests.get("https://api.hubapi.com/account-info/v1/details", headers=headers).json()
        print(f"--- INFO DE CONEXIÓN ---")
        print(f"PORTAL ID CONECTADO: {info_test.get('portalId')}")
        print(f"-------------------------")
    except Exception as e:
        print(f"Error de conexión: {e}")
        return

    # 2. Carga de archivo
    file_path = 'datos.xlsx'
    if not os.path.exists(file_path): 
        print(f"❌ Error: El archivo {file_path} no existe en el repositorio.")
        return

    df = pd.read_excel(file_path)
    if 'CIF' not in df.columns:
        print("❌ Error: No se encontró la columna 'CIF' en el Excel.")
        return

    # 3. Lógica de recorte (CIF y derecha)
    indice_cif = df.columns.get_loc('CIF')
    df_recortado = df.iloc[:, indice_cif:]
    print(f"Filas detectadas: {len(df_recortado)}")

    # 4. Mapeo de campos (Asegúrate de que 'cif' exista en HubSpot)
    mapeo = {
        'CIF': 'cif',
        'NOMBRE': 'name',
        'EMPRESA': 'name',
        'SECTOR': 'industry'
    }

    for _, fila in df_recortado.iterrows():
        cif_valor = str(fila['CIF']).strip()
        
        # Saltamos filas vacías
        if pd.isna(fila['CIF']) or cif_valor in ["", "nan", "None"]:
            continue

        # Construimos el objeto de propiedades
        propiedades = {}
        for columna in df_recortado.columns:
            nombre_excel = columna.upper()
            if nombre_excel in mapeo and pd.notna(fila[columna]):
                nombre_hubspot = mapeo[nombre_excel]
                propiedades[nombre_hubspot] = str(fila[columna])

        # 5. Intentar UPSERT (Actualizar o Crear)
        url_patch = f"https://api.hubapi.com/crm/v3/objects/companies/{cif_valor}?idProperty=cif"
        response = requests.patch(url_patch, headers=headers, json={"properties": propiedades})

        if response.status_code == 200:
            print(f"✅ ACTUALIZADO: {cif_valor}")
        
        elif response.status_code == 404:
            # Si no existe, intentamos CREAR
            url_post = "https://api.hubapi.com/crm/v3/objects/companies"
            res_crear = requests.post(url_post, headers=headers, json={"properties": propiedades})
            
            if res_crear.status_code == 201:
                print(f"✅ CREADO: {cif_valor}")
            else:
                # AQUÍ VEREMOS EL ERROR REAL SI FALLA
                print(f"❌ ERROR AL CREAR {cif_valor}: {res_crear.status_code}")
                print(f"Detalle del error: {res_crear.text}")
        
        else:
            print(f"❌ ERRORinesperado con {cif_valor}: {response.status_code}")
            print(f"Detalle: {response.text}")

if __name__ == "__main__":
    procesar_y_enviar()
