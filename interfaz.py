import os
import threading
import tkinter
from tkinter import ttk
from tkinter import filedialog
from tkinter import messagebox
from scriptMensajesWapp import (
    cargar_data,
    filtrar_visitas,
    generar_mensaje,
    abrir_whatsapp,
    enviar_mensaje
)
from agenda import (
    createTable, 
    insertContact, 
    getContacts, 
    updateContact, 
    deleteContact
)

# Función para enviar mensajes de WhatsApp
def enviar_mensajes():
    if os.path.exists(rutaArchivo):
        with open(rutaArchivo, 'r') as file:
            path = file.read().strip()

    else:
        path = str()
        
    if not path or not path.endswith(('.xlsx', '.xls')):
        messagebox.showerror("Error", "Por favor, seleccione un archivo de Excel válido.")
        return
    
    df_datos = cargar_data(path)  
    fechas_validas = filtrar_visitas(df_datos) 

    # Verifica si hay visitas agendadas dentro de las próximas 48 horas (o el rango definido)
    if fechas_validas.empty:
        # estado_visitas.config(text="No hay visitas agendadas dentro de las próximas 48 hs.")
        messagebox.showinfo("Aviso", "No hay visitas agendadas dentro de las próximas 48 hs.")
        return
    mensaje = generar_mensaje(fechas_validas)  

    # Obtiene los contactos de la agenda
    contactos = getContacts()
    if not contactos:
        messagebox.showerror("Error", "No hay contactos disponibles en la agenda.")
        return

    driver = abrir_whatsapp()  
    
    # Envía el mensaje a cada contacto
    enviar_mensaje(contactos, driver, mensaje) 

# Función para abrir la agenda de contactos
def abrir_agenda():
    ventana_agenda = tkinter.Toplevel(ventana)
    ventana_agenda.title("Agenda de Contactos")
    ventana_agenda.geometry("600x400")
    ventana_agenda.configure(bg="#d7d4d4")

    createTable()  
   
    tree = ttk.Treeview(ventana_agenda, columns=("Nombre", "Teléfono"), show="headings")
    tree.heading("Nombre", text="Nombre")
    tree.heading("Teléfono", text="Teléfono")
    tree.pack(fill=tkinter.BOTH, expand=True)

    # Funciones para eliminar y/o editar contactos
    def cargar_contactos():
        tree.delete(*tree.get_children())
        for nombre, telefono in getContacts():
            tree.insert("", "end", values=(nombre, telefono))

    def eliminar_contacto():
            seleccion = tree.selection()
            if not seleccion:
                messagebox.showwarning("Aviso", "Seleccione un contacto para eliminar.")
                return
            item = tree.item(seleccion[0])
            nombre = item["values"][0]
            confirmacion = messagebox.askyesno("Confirmar", f"¿Eliminar a {nombre}?")
            if confirmacion:
                deleteContact(nombre)
                cargar_contactos()

    def editar_contacto():
        selected_item = tree.selection()
        if not selected_item:
            messagebox.showwarning("Advertencia", "Seleccione un contacto para editar.")
            return
        item = tree.item(selected_item[0])
        nombre_actual = item["values"][0]
        telefono_actual = item["values"][1]
       
        ventana_modificar = tkinter.Toplevel(ventana_agenda)
        ventana_modificar.title(f"Modificar: {nombre_actual}")
        ventana_modificar.geometry("300x150")

        etiqueta_tel = tkinter.Label(ventana_modificar, text="Nuevo teléfono:")
        etiqueta_tel.pack(pady=(10, 0))
        entrada_tel = tkinter.Entry(ventana_modificar)
        entrada_tel.insert(0, telefono_actual)
        entrada_tel.pack(pady=5)

        def guardar_modificacion():
            nuevo_tel = entrada_tel.get().strip()
            if not nuevo_tel:
                messagebox.showerror("Error", "El teléfono no puede estar vacío.")
                return
            updateContact(nombre_actual, nuevo_tel)
            ventana_modificar.destroy()
            cargar_contactos()

        boton_guardar = tkinter.Button(ventana_modificar, text="Guardar", command=guardar_modificacion)
        boton_guardar.pack(pady=10)

    cargar_contactos()
    
    # Botones para editar y/o eliminar contactos
    boton_editar = tkinter.Button(
        ventana_agenda, 
        text="Editar Contacto", 
        command=editar_contacto, 
        bg="#d9d9d9", 
        fg="#000000", 
        font=("Helvetica", 12)
    )
    boton_editar.pack(pady=5)

    boton_eliminar = tkinter.Button(
        ventana_agenda, 
        text="Eliminar Contacto", 
        command=eliminar_contacto, 
        bg="#d9d9d9", 
        fg="#000000", 
        font=("Helvetica", 12)
    )
    boton_eliminar.pack(pady=5)

# Función para abrir la ventana de agregar contacto
def abrir_ventana_contacto():
    ventana_contacto = tkinter.Toplevel(ventana)
    ventana_contacto.title("Agregar Contacto")
    ventana_contacto.geometry("300x200")
    ventana_contacto.configure(bg="#d7d4d4")

    etiqueta_nombre = tkinter.Label(ventana_contacto, text="Nombre:", bg="#d7d4d4", fg="#000000", font=("Helvetica", 12))
    etiqueta_nombre.pack(pady=5)

    entrada_nombre = tkinter.Entry(ventana_contacto, font=("Helvetica", 12))
    entrada_nombre.pack(pady=5)

    etiqueta_telefono = tkinter.Label(ventana_contacto, text="Teléfono:", bg="#d7d4d4", fg="#000000", font=("Helvetica", 12))
    etiqueta_telefono.pack(pady=5)

    entrada_telefono = tkinter.Entry(ventana_contacto, font=("Helvetica", 12))
    entrada_telefono.pack(pady=5)

    def agregar_contacto():
        nombre = entrada_nombre.get().strip()
        telefono = entrada_telefono.get().strip()
        if not nombre or not telefono:
            messagebox.showerror("Error", "Por favor, complete todos los campos.")
            return
        insertContact(nombre, telefono)
        messagebox.showinfo("Éxito", "Contacto agregado correctamente.")
        ventana_contacto.destroy()

    boton_agregar = tkinter.Button(
        ventana_contacto, 
        text="Agregar Contacto", 
        command=agregar_contacto, 
        bg="#d9d9d9", 
        fg="#000000", 
        font=("Helvetica", 12)
    )
    boton_agregar.pack(pady=10)

# Ejecuta el hilo para enviar mensajes - mejora la experiencia del usuario
def ejecutar_hilo():
    hilo = threading.Thread(target = enviar_mensajes)
    hilo.start() 

ventana = tkinter.Tk()
ventana.title("Asignación de visitas PampaFox")  
ventana.geometry("280x300")
ventana.configure(bg="#d7d4d4")
ventana.grid_rowconfigure(0, weight=1)
ventana.grid_columnconfigure(0, weight=1)

# Verifica si el archivo de Excel ya ha sido seleccionado
RUTA_ARCHIVO = "archivo_seleccionado.txt"
ruta_archivo = tkinter.StringVar()
if os.path.exists(RUTA_ARCHIVO):
    with open(RUTA_ARCHIVO, 'r') as file:
        path_excel = file.read().strip()
        if path_excel and os.path.exists(path_excel):
            ruta_archivo.set(os.path.basename(path_excel))
        else:
            ruta_archivo.set("Seleccione un archivo de Excel")
else:
    ruta_archivo.set("Seleccione un archivo de Excel")

etiqueta_archivo = tkinter.Label(
    textvariable=ruta_archivo, 
    bg="#d7d4d4", 
    fg="#000000", 
    font=("Helvetica", 12)
)
etiqueta_archivo.pack(padx=20, pady=10)

rutaArchivo = "archivo_seleccionado.txt"  
def seleccionar_archivo():
    path_excel = filedialog.askopenfilename(
        parent=ventana,
        title="Seleccionar archivo de Excel",
        filetypes=[("Archivos de Excel", "*.xlsx *.xls")]
    )
    if path_excel:
        with open(rutaArchivo, 'w') as file:
            file.write(path_excel)

        nombre_archivo = os.path.basename(path_excel)
        ruta_archivo.set(nombre_archivo)
       
# Botones de la interfaz
boton_seleccionar = tkinter.Button(
    text="Seleccionar archivo", 
    command=seleccionar_archivo, 
    bg="#d9d9d9", 
    fg="#000000", 
    font=("Helvetica", 12)
)   
boton_seleccionar.pack(padx=20, pady=10)

boton_agenda = tkinter.Button(
    ventana,
    text="Abrir agenda",
    bg="#d9d9d9",   
    fg="#000000",
    font=("Helvetica", 12),
    command = abrir_agenda
)
boton_agenda.pack(padx=20, pady=10)

boton_agregar_contacto = tkinter.Button(
    ventana, 
    text="Agregar contacto", 
    bg="#d9d9d9", 
    fg="#000000", 
    font=("Helvetica", 12), 
    command = abrir_ventana_contacto
)

boton_agregar_contacto.pack(padx=20, pady=10)

boton_mensaje = tkinter.Button(
    ventana, 
    text="Asignar visitas", 
    bg="#d9d9d9", 
    fg="#000000", 
    font=("Helvetica", 12), 
    command = ejecutar_hilo
    )
boton_mensaje.pack(padx=20, pady=10)

estado_visitas = tkinter.Label(ventana, text= str(), bg="#d7d4d4", fg="#000000", font=("Helvetica", 12))
estado_visitas.pack()

# Loop principal de la ventana
ventana.mainloop()