from pymongo import MongoClient
from datetime import datetime
from tkinter import ttk
from tkinter import messagebox
from tkcalendar import DateEntry
from datetime import datetime, date
import bcrypt
import tkinter as tk

def conectar_db():
    try:
        cli = MongoClient("mongodb://admin:admin123@localhost:27017/")
        cli.admin.command('ping')
        db = cli["datos"]
        return db
    except Exception as e:
        print(f"Error al conectar a MongoDB: {e}")
        return None
    
def crear_colecciones(db):
    colecciones = ["usuarios", "vocaciones", "cursos", "bibliografias"]
    for coleccion in colecciones:
        if coleccion not in db.list_collection_names():
            db.create_collection(coleccion)
            print(f"Colección '{coleccion}' creada.")
        else:
            print(f"La colección '{coleccion}' ya existe.")
    
    print("Vocaciones insertadas correctamente.")

def main():
    db = conectar_db()
    if db:
        crear_colecciones(db)
        print("Base de datos y colecciones creadas correctamente.")
    else:
        print("No se pudo conectar a la base de datos.")

if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()  # Ocultar la ventana principal
    main()
    messagebox.showinfo("Éxito", "Base de datos y colecciones creadas correctamente.")
    root.destroy()  # Cerrar la ventana oculta