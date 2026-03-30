import pandas as pd
import requests
import os
import sys

# 1. Configuración de Acceso
# El token se toma automáticamente del "Secret" que guardamos en GitHub
token = os.getenv('HUBSPOT_ACCESS_TOKEN')
headers = {
    'Authorization': f'Bearer {token}',
    'Content-Type': 'application/json'
}

def procesar_y_enviar():
    # 2. Cargar el archivo Excel
    # El archivo debe llamarse 'datos.xlsx' y estar en la raíz del repo
    file_path = 'datos.xlsx'
    
    if not os.path.exists(file_path):
        print(f"Error: No se encontró el archivo {file_path}")
        return

    try:
        df = pd.read_excel(file_path)
    except Exception as e:
        print(f"Error al abrir el Excel: {e}")
        return

    # 3. Lógica de "Recorte": Buscar CIF y lo que hay a su derecha
    if 'CIF' not in df.columns:
        print("Error: La columna 'CIF' no existe en el Excel.")
        return

    # Encontramos la posición de la columna CIF
    indice_cif = df.columns.get_loc('CIF')
    
    # Recortamos el DataFrame: todas las filas, desde indice_cif hasta el final
    df_recortado = df.iloc[:, indice_cif:]

    print(f"Detectadas {len(df_recortado)} filas para procesar.")

    # 4. Enviar a HubSpot (Bucle fila por fila)
    for _, fila in df_recortado.iterrows():
        # Limpiamos el valor del CIF (quitar espacios o vacíos)
        cif_valor = str(fila['CIF']).strip()
        
        if pd.isna(fila['CIF']) or cif_valor == "" or cif_valor == "nan":
            continue

        # Construimos el paquete de datos (Propiedades)
        # Convertimos cada columna en una propiedad de HubSpot
        propiedades = {}
        for columna in df_recortado.columns:
            if pd.notna(fila[columna]):
                # HubSpot usa nombres internos en minúsculas usualmente
                nombre_propiedad = columna.lower().replace(" ", "_")
                propiedades[nombre_propiedad] = str(fila[columna])

        # Intentamos actualizar (Upsert usando el CIF como ID único)
        url = f"https://api.hubapi.com/crm/v3/objects/companies/{cif_valor}?idProperty=cif"
        
        # Primero intentamos PATCH (Actualizar)
        response = requests.patch(url, headers=headers, json={"properties": propiedades})

        if response.status_code == 200:
            print(f"EXITO: Empresa con CIF {cif_valor} actualizada.")
        elif response.status_code == 404:
            # Si no existe (404), la creamos (POST)
            url_crear = "https://api.hubapi.com/crm/v3/objects/companies"
            response_crear = requests.post(url_crear, headers=headers, json={"properties": propiedades})
            if response_crear.status_code == 201:
                print(f"EXITO: Empresa con CIF {cif_valor} creada de cero.")
            else:
                print(f"ERROR al crear {cif_valor}: {response_crear.text}")
        else:
            print(f"ERROR con CIF {cif_valor}: {response.status_code} - {response.text}")

if __name__ == "__main__":
    procesar_y_enviar()
