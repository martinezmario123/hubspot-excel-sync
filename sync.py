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
    
    df = pd.read_excel(file_path)
    print(f"Filas a procesar: {len(df)}")

    for _, fila in df.iterrows():
        # --- 1. GESTIÓN DE EMPRESA (Usando CIF) ---
        cif = str(fila.get('CIF', '')).strip()
        nombre_empresa = str(fila.get('Empresa', '')).strip()
        pais = str(fila.get('Pais', '')).strip()
        id_empresa = None

        if cif and cif not in ['nan', 'None', '']:
            props_emp = {'name': nombre_empresa, 'cif': cif, 'country': pais}
            url_emp = f"https://api.hubapi.com/crm/v3/objects/companies/{cif}?idProperty=cif"
            res_emp = requests.patch(url_emp, headers=headers, json={"properties": props_emp})
            
            if res_emp.status_code == 404:
                res_emp = requests.post("https://api.hubapi.com/crm/v3/objects/companies", headers=headers, json={"properties": props_emp})
            
            if res_emp.status_code in [200, 201]:
                id_empresa = res_emp.json().get('id')

        # --- 2. GESTIÓN DE CONTACTO (Usando Correo) ---
        email = str(fila.get('Correo', '')).strip()
        id_contacto = None

        if email and email not in ['nan', 'None', '']:
            props_con = {
                'email': email,
                'firstname': str(fila.get('Nombre', '')),
                'lastname': str(fila.get('Apellido', '')),
                'moneda_contacto': str(fila.get('Moneda', ''))
            }
            url_con = f"https://api.hubapi.com/crm/v3/objects/contacts/{email}?idProperty=email"
            res_con = requests.patch(url_con, headers=headers, json={"properties": props_con})
            
            if res_con.status_code == 404:
                res_con = requests.post("https://api.hubapi.com/crm/v3/objects/contacts", headers=headers, json={"properties": props_con})
            
            if res_con.status_code in [200, 201]:
                id_contacto = res_con.json().get('id')

        # --- 3. ASOCIACIÓN (Unir Persona con Empresa) ---
        if id_empresa and id_contacto:
            url_assoc = f"https://api.hubapi.com/crm/v3/objects/contacts/{id_contacto}/associations/companies/{id_empresa}/contact_to_company"
            requests.put(url_assoc, headers=headers)
            print(f"✅ Sincronizado: {nombre_empresa} <-> {email}")
        else:
            print(f"⚠️ Faltan datos críticos para {nombre_empresa} o {email}")

if __name__ == "__main__":
    sincronizar_todo()
