import pandas as pd
import requests
import os

token = os.getenv('HUBSPOT_ACCESS_TOKEN')
headers = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}

def procesar_y_enviar():
    # Estas dos líneas nos dirán la verdad sobre el Portal ID
    info_test = requests.get("https://api.hubapi.com/account-info/v1/details", headers=headers).json()
    print(f"--- INFO DE CONEXIÓN ---")
    print(f"ESTOY ENVIANDO DATOS AL PORTAL ID: {info_test.get('portalId')}")
    print(f"-------------------------")

    file_path = 'datos.xlsx'
    if not os.path.exists(file_path): 
        print("Archivo no encontrado")
        return

    df = pd.read_excel(file_path)
    if 'CIF' not in df.columns: return

    indice_cif = df.columns.get_loc('CIF')
    df_recortado = df.iloc[:, indice_cif:]

    mapeo = {
        'CIF': 'cif',
        'NOMBRE': 'name',
        'EMPRESA': 'name',
        'SECTOR': 'industry'
    }

    for _, fila in df_recortado.iterrows():
        cif_valor = str(fila['CIF']).strip()
        if pd.isna(fila['CIF']) or cif_valor in ["", "nan"]: continue

        propiedades = {}
        for columna in df_recortado.columns:
            nombre_excel = columna.upper()
            if nombre_excel in mapeo and pd.notna(fila[columna]):
                nombre_hubspot = mapeo[nombre_excel]
                propiedades[nombre_hubspot] = str(fila[columna])

        url = f"https://api.hubapi.com/crm/v3/objects/companies/{cif_valor}?idProperty=cif"
        response = requests.patch(url, headers=headers, json={"properties": propiedades})

        if response.status_code == 404:
            url_crear = "https://api.hubapi.com/crm/v3/objects/companies"
            requests.post(url_crear, headers=headers, json={"properties": propiedades})
            print(f"Creado: {cif_valor}")
        else:
            print(f"Actualizado: {cif_valor}")

if __name__ == "__main__":
    procesar_y_enviar()
