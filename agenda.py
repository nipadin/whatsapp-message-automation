import sqlite3 as sql

# CREA LA TABLA CONTACTOS
def createTable():
    conn = sql.connect('agenda.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS contactos (
            nombre TEXT NOT NULL,
            telefono TEXT NOT NULL 
        )
    ''')
    conn.commit()
    conn.close()
    
# INSERTA UN NUEVO CONTACTO
def insertContact(nombre, telefono):
    conn = sql.connect('agenda.db')
    cursor = conn.cursor()
    intruccion = f"INSERT INTO contactos (nombre, telefono) VALUES ('{nombre}', '{telefono}')"
    cursor.execute(intruccion)
    conn.commit()   
    conn.close()

# OBTIENE TODOS LOS CONTACTOS
def getContacts():
    conn = sql.connect('agenda.db')
    cursor = conn.cursor()
    instrucción = f"SELECT nombre, telefono FROM contactos"
    cursor.execute(instrucción)
    contacts = cursor.fetchall()
    conn.close()
    return contacts
    # print(contacts)

# Busca contactos por nombre - no está siendo usado en el código actual
def search(nombre):
    conn = sql.connect('agenda.db')
    cursor = conn.cursor()
    instrucción = f"SELECT * FROM contactos WHERE nombre LIKE '%{nombre}%'"
    cursor.execute(instrucción)
    contacts = cursor.fetchall()
    conn.close()
    # return contacts

# Actualiza el número de teléfono de un contacto
def updateContact(nombre, telefono):
    conn = sql.connect('agenda.db')
    cursor = conn.cursor()
    instrucción = f"UPDATE contactos SET telefono = '{telefono}' WHERE nombre = '{nombre}'"
    cursor.execute(instrucción)
    conn.commit()
    conn.close()

# Elimina un contacto por nombre
def deleteContact(nombre):
    conn = sql.connect('agenda.db')
    cursor = conn.cursor()
    instrucción = f"DELETE FROM contactos WHERE nombre = '{nombre}'"
    cursor.execute(instrucción)
    conn.commit()
    conn.close()
