boton_agregar_contacto = tkinter.Button(
    ventana, 
    text="Agregar contacto", 
    bg="#d9d9d9", 
    fg="#000000", 
    font=("Helvetica", 12), 
    command=ingresar_contacto
)

boton_agregar_contacto.pack(padx=20, pady=10)

def ingresar_contacto():
    createTable()
    nombre = entrada_contacto.get().strip()
    telefono = entrada_telefono.get().strip()
    if not nombre or not telefono: 
        messagebox.showerror("Error", "Por favor, complete todos los campos.")
        return
    insertContact(nombre, telefono)
    messagebox.showinfo("Éxito", "Contacto agregado correctamente.")


entrada_contacto = tkinter.Entry(
    ventana, 
    font=("Helvetica", 12))
entrada_contacto.pack(padx=20, pady=10)

entrada_telefono = tkinter.Entry(
    ventana, 
    font=("Helvetica", 12))
entrada_telefono.pack(padx=20, pady=10)