import pandas as pd
import requests
import os

token = os.getenv('HUBSPOT_ACCESS_TOKEN')
headers = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}

def sincronizar_todo():
    file_path = 'datos.xlsx'
    if not os.path.exists(file_path): 
        print("❌ Archivo datos.xlsx no encontrado.")
        return
    
    # Leemos el Excel
    df = pd.read_excel(file_path)
    
    # TRUCO: Limpiamos los nombres de las columnas (quitamos espacios y pasamos a minúsculas)
    df.columns = [str(c).strip().lower() for c in df.columns]
    
    print(f"Columnas detectadas en el Excel: {list(df.columns)}")
    print(f"Filas a procesar: {len(df)}")

    for _, fila in df.iterrows():
        # Extraemos los datos usando siempre minúsculas para no fallar
        cif = str(fila.get('cif', '')).strip()
        nombre_empresa = str(fila.get('empresa', '')).strip()
        pais = str(fila.get('pais', '')).strip()
        email = str(fila.get('correo', '')).strip()
        nombre_persona = str(fila.get('nombre', '')).strip()
        apellido_persona = str(fila.get('apellido', '')).strip()
        moneda = str(fila.get('moneda', '')).strip()

        id_empresa = None
        id_contacto = None

        # --- 1. GESTIÓN DE EMPRESA ---
        if cif and cif not in ['nan', 'None', '']:
            props_emp = {'name': nombre_empresa, 'cif': cif, 'country': pais}
            url_emp = f"https://api.hubapi.com/crm/v3/objects/companies/{cif}?idProperty=cif"
            res_emp = requests.patch(url_emp, headers=headers, json={"properties": props_emp})
            
            if res_emp.status_code == 404:
                res_emp = requests.post("https://api.hubapi.com/crm/v3/objects/companies", headers=headers, json={"properties": props_emp})
            
            if res_emp.status_code in [200, 201]:
                id_empresa = res_emp.json().get('id')

        # --- 2. GESTIÓN DE CONTACTO ---
        if email and email not in ['nan', 'None', '']:
            props_con = {
                'email': email,
                'firstname': nombre_persona,
                'lastname': apellido_persona,
                'moneda_contacto': moneda
            }
            url_con = f"https://api.hubapi.com/crm/v3/objects/contacts/{email}?idProperty=email"
            res_con = requests.patch(url_con, headers=headers, json={"properties": props_con})
            
            if res_con.status_code == 404:
                res_con = requests.post("https://api.hubapi.com/crm/v3/objects/contacts", headers=headers, json={"properties": props_con})
            
            if res_con.status_code in [200, 201]:
                id_contacto = res_con.json().get('id')

        # --- 3. ASOCIACIÓN Y LOGS ---
        if id_empresa and id_contacto:
            url_assoc = f"https://api.hubapi.com/crm/v3/objects/contacts/{id_contacto}/associations/companies/{id_empresa}/contact_to_company"
            requests.put(url_assoc, headers=headers)
            print(f"✅ Sincronizado: {nombre_empresa} <-> {email}")
        elif id_empresa or id_contacto:
            print(f"⚠️ Sincronizado parcial (sin asociación): Empresa {id_empresa} | Contacto {id_contacto}")
        else:
            print(f"❌ Error: Fila vacía o datos no encontrados para CIF: {cif} / Email: {email}")

if __name__ == "__main__":
    sincronizar_todo()
