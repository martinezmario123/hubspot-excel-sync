import pandas as pd
import requests
import os

# Configuración de acceso
token = os.getenv('HUBSPOT_ACCESS_TOKEN')
headers = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}

def sincronizar_todo():
    # 1. BUSCAR CUALQUIER ARCHIVO EXCEL EN EL REPOSITORIO
    archivos_excel = [f for f in os.listdir('.') if f.endswith('.xlsx')]
    
    if not archivos_excel:
        print("❌ ERROR: No se ha encontrado ningún archivo Excel (.xlsx) en el repositorio.")
        return
    
    # Cogemos el primero que encuentre (por si hay varios)
    file_path = archivos_excel[0]
    print(f"📂 Procesando el archivo encontrado: {file_path}")

    # 2. LEER EXCEL Y LIMPIAR COLUMNAS
    try:
        df = pd.read_excel(file_path)
        # Limpiamos los encabezados: minúsculas, sin espacios y sin saltos de línea
        df.columns = [str(c).strip().lower() for c in df.columns]
        print(f"DEBUG - Columnas detectadas: {list(df.columns)}")
    except Exception as e:
        print(f"❌ Error al leer el Excel: {e}")
        return

    print(f"Filas detectadas: {len(df)}")

    # 3. PROCESAR CADA FILA
    for _, fila in df.iterrows():
        # Extraemos datos (usando minúsculas según nuestra limpieza anterior)
        cif = str(fila.get('cif', '')).strip()
        nombre_empresa = str(fila.get('empresa', '')).strip()
        email = str(fila.get('correo', '')).strip()
        nombre_persona = str(fila.get('nombre', '')).strip()
        apellido_persona = str(fila.get('apellido', '')).strip()
        moneda = str(fila.get('moneda', '')).strip()
        pais = str(fila.get('pais', '')).strip()

        id_empresa = None
        id_contacto = None

        # --- A. GESTIÓN DE EMPRESA (Identificador: CIF) ---
        if cif and cif not in ['nan', 'None', '']:
            props_emp = {'name': nombre_empresa, 'cif': cif, 'country': pais}
            url_emp = f"https://api.hubapi.com/crm/v3/objects/companies/{cif}?idProperty=cif"
            res_emp = requests.patch(url_emp, headers=headers, json={"properties": props_emp})
            
            if res_emp.status_code == 404:
                res_emp = requests.post("https://api.hubapi.com/crm/v3/objects/companies", headers=headers, json={"properties": props_emp})
            
            if res_emp.status_code in [200, 201]:
                id_empresa = res_emp.json().get('id')
            else:
                print(f"❌ Error Empresa {cif}: {res_emp.text}")

        # --- B. GESTIÓN DE CONTACTO (Identificador: EMAIL) ---
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
            else:
                print(f"❌ Error Contacto {email}: {res_con.text}")

        # --- C. ASOCIACIÓN (Vincular Persona con su Empresa) ---
        if id_empresa and id_contacto:
            url_assoc = f"https://api.hubapi.com/crm/v3/objects/contacts/{id_contacto}/associations/companies/{id_empresa}/contact_to_company"
            requests.put(url_assoc, headers=headers)
            print(f"✅ ÉXITO: {nombre_empresa} conectado con {email}")
        elif id_empresa or id_contacto:
            print(f"⚠️ Sincronización parcial para {nombre_empresa} / {email} (Falta un ID para asociar)")

if __name__ == "__main__":
    sincronizar_todo()
