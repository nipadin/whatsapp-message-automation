import os
import time
import pandas as pd
from datetime import datetime
from operator import itemgetter
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

# Carga de datos desde planillas excel -> posteriormente base de datos modificable (agenda y datos)
def cargar_data(path_datos_excel):
    df_datos = pd.read_excel(path_datos_excel)
    df_datos['Fecha Desde'] = pd.to_datetime(df_datos['Fecha Desde'], errors = 'coerce')
    df_datos['Fecha Hasta'] = pd.to_datetime(df_datos['Fecha Hasta'], errors ='coerce')
    return df_datos

# Filtrado de visitas agendadas dentro de las próximas 48 hs
def filtrar_visitas(df_datos):
    hoy = datetime.today() 
    fechas_validas = df_datos[
        (pd.notna(df_datos['Contrato'])) &
        (pd.notna(df_datos['Nro.Estab.'])) &
        (pd.notna(df_datos['Tareas'])) &
        (pd.notna(df_datos['Domicilio'])) &
        (pd.notna(df_datos['Localidad'])) &
        (pd.notna(df_datos['Fecha Desde'])) &
        ((df_datos['Fecha Hasta'] - hoy).dt.days >= 0) &
        ((df_datos['Fecha Hasta'] - hoy).dt.days <= 2)] # Puede elegirse el rango de días, en este caso 2 días
    return fechas_validas

# Generación del mensaje a enviar por WhatsApp
def generar_mensaje(fechas_validas):
    mensaje = str()
    fechas_ordenadas = fechas_validas.sort_values(by="Fecha Hasta", ascending=True)
    grupos = fechas_ordenadas.groupby(['Empresa', 'Contrato', 'Fecha Hasta'])
    claves_ordenadas = sorted(grupos.groups.keys(), key=itemgetter(2))

    for clave in claves_ordenadas:
        empresa, contrato, fecha_hasta = clave
        grupo = grupos.get_group(clave)
        mensaje += f"\n*Empresa*: {empresa}\n"
        mensaje += f"*Contrato*: {contrato}\n"
        mensaje += f"*Fecha Hasta*: {fecha_hasta.strftime('%d/%m/%y')}\n"
        mensaje += "*Establecimientos:*\n"
        for _, fila in grupo.iterrows():
            mensaje += (
                f"Estab: {fila['Nro.Estab.']}\n"
                f"Tareas: {fila['Tareas']}\n"
                f"Desde: {fila['Fecha Desde'].strftime('%d/%m/%y')}\n"
                f"Domicilio: {fila['Domicilio']} ({fila['Localidad']})\n\n"
            )
    return mensaje

# Abre WhatsApp Web en el navegador Chrome con un perfil específico
def abrir_whatsapp():
    carpeta_perfil = os.path.join(os.getcwd(), 'chromeWapp')
    if not os.path.exists(carpeta_perfil):
        os.makedirs(carpeta_perfil)
    options = webdriver.ChromeOptions()
    options = Options()
    options.add_argument(f"user-data-dir={carpeta_perfil}")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--no-sandbox")
    options.add_argument("--remote-debugging-port=9222")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    driver.get(f"https://web.whatsapp.com")
    try:
        WebDriverWait(driver, 60).until(EC.presence_of_all_elements_located((By.ID, "pane-side")))
    except  TimeoutException:
        print("No se escaneó correctamente el código QR")
    return driver

# Envía el mensaje a cada contacto en la lista de contactos
def enviar_mensaje(db_contactos, driver, mensaje):
    for nombre, telefono in db_contactos:
        try:
            buscar_contacto = WebDriverWait(driver, 20).until(EC.presence_of_element_located(
                (By.XPATH, '//div[@contenteditable="true" and @role="textbox"]')
                )
            )
            buscar_contacto.send_keys(telefono)
            buscar_contacto.send_keys(Keys.ENTER)
            buscar_contacto.clear()
            time.sleep(1) # Posiblemente después se cambie por un sleep más corto o un WebDriverWait

            caja_mensaje = WebDriverWait(driver,20).until(EC.presence_of_element_located(
                (By.XPATH, '//footer//div[@contenteditable="true" and @role="textbox"]') 
                    )
                    )
            
            for linea in mensaje.split('\n'):
                caja_mensaje.send_keys(linea)
                caja_mensaje.send_keys(Keys.SHIFT, Keys.ENTER)
            time.sleep(2)
            caja_mensaje.send_keys(Keys.ENTER)
            caja_mensaje.clear()
            time.sleep(1)                 
        except Exception as e: 
            print("Ocurrió un error: ", e)