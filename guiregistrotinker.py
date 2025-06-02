from pymongo import MongoClient
from datetime import datetime
from tkinter import ttk
from tkinter import messagebox
from tkcalendar import DateEntry
from datetime import datetime, date
import crudvocactest as vocaciones
import bcrypt
import tkinter as tk

def conectar_db():
    try:
        # Ajusta la URI de conexión si es necesario
        cli = MongoClient("mongodb://admin:admin123@localhost:27017/")
        cli.admin.command('ping') # Verificar conexión
        db = cli["datos"]
        return db
    except Exception as e:
        print(f"Error al conectar a MongoDB: {e}")
        return None


    
def calcular_edad(fecha_nacimiento_dt):
    hoy = datetime.today()
    edad = hoy.year - fecha_nacimiento_dt.year - ((hoy.month, hoy.day) < (fecha_nacimiento_dt.month, fecha_nacimiento_dt.day))
    return edad

def hashear_password(password_texto_plano):
    salt = bcrypt.gensalt()
    hashed_pw = bcrypt.hashpw(password_texto_plano.encode('utf-8'), salt)
    return hashed_pw # Guardar esto como binario en MongoDB o convertir a string si es necesario

def registrar_usuario_db(username, password_plano, fecha_nac_dt, vocacion_seleccionada):
    cliaux = MongoClient("mongodb://admin:admin123@localhost:27017/")
    dbusuarios = cliaux["datos"]
    if dbusuarios is None:
        return False, "Error de conexión a la base de datos."

    # Validaciones básicas (puedes expandirlas)
    if not all([username, password_plano, fecha_nac_dt, vocacion_seleccionada]):
        return False, "Todos los campos son requeridos."

    # Verificar si el usuario ya existe
    if dbusuarios["usuarios"].find_one({"username": username}):
        return False, f"El nombre de usuario '{username}' ya existe."

    try:
        hashed_pw = hashear_password(password_plano)
        edad = calcular_edad(fecha_nac_dt)

        usuario_doc = {
            "username": username,
            "password": hashed_pw, # Se guarda el hash binario
            "fecha_nacimiento": fecha_nac_dt,
            "edad": edad,
            "vocacion": vocacion_seleccionada,
            "progreso": [] # Inicialmente vacío
        }

        dbusuarios["usuarios"].insert_one(usuario_doc)
        return True, "Usuario registrado exitosamente."
    except Exception as e:
        return False, f"Error al registrar usuario: {e}"
    
class VentanaRegistro:
    def __init__(self, master):
        self.master = master
        master.title("Registro de Nuevo Usuario")
        master.geometry("450x450") # Ajusta el tamaño

        self.db = conectar_db() # Conectar a la DB al iniciar

        # Configurar estilo ttk widgets
        style = ttk.Style()
        style.theme_use('clam')
        #style.theme_use('alt')
        #style.theme_use('default')
        #style.theme_use('classic')

        # Frame principal
        main_frame = ttk.Frame(master, padding="20 20 20 20")
        main_frame.pack(expand=True, fill=tk.BOTH)

        # --- Widgets ---
        ttk.Label(main_frame, text="Nombre de Usuario:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.username_entry = ttk.Entry(main_frame, width=30)
        self.username_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        self.username_entry.focus_set() # Poner el foco inicial aquí

        ttk.Label(main_frame, text="Contraseña:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.password_entry = ttk.Entry(main_frame, show="*", width=30)
        self.password_entry.grid(row=1, column=1, padx=5, pady=5, sticky="ew")

        ttk.Label(main_frame, text="Fecha de Nacimiento:").grid(row=2, column=0, padx=5, pady=5, sticky="w")
        self.fecha_nac_entry = DateEntry(main_frame, width=27, background='darkblue',
                                         foreground='white', borderwidth=2, date_pattern='dd/mm/yyyy',
                                         maxdate=datetime.today()) # Evitar fechas futuras
        self.fecha_nac_entry.grid(row=2, column=1, padx=5, pady=5, sticky="ew")
        # Limpiar el campo de fecha inicialmente para que el usuario deba seleccionar una.
        self.fecha_nac_entry.delete(0, tk.END) 
        self.fecha_nac_entry.bind("<<DateEntrySelected>>", self.actualizar_edad_display)


        ttk.Label(main_frame, text="Edad:").grid(row=3, column=0, padx=5, pady=5, sticky="w")
        self.edad_label_var = tk.StringVar(value="N/A")
        self.edad_display_label = ttk.Label(main_frame, textvariable=self.edad_label_var)
        self.edad_display_label.grid(row=3, column=1, padx=5, pady=5, sticky="w")

        ttk.Label(main_frame, text="Vocación:").grid(row=4, column=0, padx=5, pady=5, sticky="w")
        self.vocacion_var = tk.StringVar()
        self.vocacion_combobox = ttk.Combobox(main_frame, textvariable=self.vocacion_var, width=28, state="readonly")
        self.vocacion_combobox.grid(row=4, column=1, padx=5, pady=5, sticky="ew")
        
        self.status_label_var = tk.StringVar()
        self.status_label = ttk.Label(main_frame, textvariable=self.status_label_var, foreground="blue")
        self.status_label.grid(row=6, column=0, columnspan=2, padx=5, pady=5)

        self.cargar_opciones_vocacion() 

        self.registrar_button = ttk.Button(main_frame, text="Registrar Usuario", command=self.intentar_registro)
        self.registrar_button.grid(row=5, column=0, columnspan=2, padx=5, pady=20)

        main_frame.columnconfigure(1, weight=1)


    def cargar_opciones_vocacion(self):
        if self.db is not None: 
            lista_voc = vocaciones.obtener_vocaciones_para_dropdown()
            if lista_voc: 
                self.vocacion_combobox['values'] = lista_voc
                if lista_voc: 
                    self.vocacion_combobox.current(0)
            else:
                self.vocacion_combobox['values'] = ["(No hay vocaciones)"]
                self.vocacion_combobox.current(0)
                self.status_label_var.set("Advertencia: No se cargaron vocaciones.")
        else:
            self.vocacion_combobox['values'] = ["(Error DB)"]
            self.vocacion_combobox.current(0)
            self.status_label_var.set("Error: No se pudo conectar a la DB para vocaciones.")

    def actualizar_edad_display(self, event=None): 
        try:
            fecha_seleccionada_obj_date = self.fecha_nac_entry.get_date() 
            if isinstance(fecha_seleccionada_obj_date, date):
                 # Aquí fecha_seleccionada_obj_date es un objeto datetime.date
                 edad = calcular_edad(fecha_seleccionada_obj_date) 
                 self.edad_label_var.set(str(edad))
            else: 
                 self.edad_label_var.set("N/A")
        except Exception as e:
            # print(f"Error al actualizar edad: {e}") 
            self.edad_label_var.set("N/A") 

    def intentar_registro(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        vocacion = self.vocacion_var.get()
        fecha_nac_str = self.fecha_nac_entry.get() # Obtener el string para verificar si está vacío

        if not fecha_nac_str: # Verificar si el campo de fecha está vacío
            messagebox.showerror("Error de Fecha", "Por favor, seleccione una fecha de nacimiento.")
            self.status_label_var.set("Error: Fecha de nacimiento no seleccionada.")
            return
            
        try:
            fecha_nac_obj_date = self.fecha_nac_entry.get_date() # Intenta obtener el objeto date
            if not isinstance(fecha_nac_obj_date, date): 
                messagebox.showerror("Error de Fecha", "Por favor, seleccione una fecha de nacimiento válida desde el calendario.")
                self.status_label_var.set("Error: Fecha de nacimiento inválida.")
                return
            fecha_nac_dt_completa = datetime.combine(fecha_nac_obj_date, datetime.min.time())
        except Exception as e: 
            messagebox.showerror("Error de Fecha", f"La fecha de nacimiento no es válida: {e}")
            self.status_label_var.set("Error: Fecha de nacimiento inválida.")
            return

        if self.db is None: 
            messagebox.showerror("Error de Base de Datos", "No hay conexión a la base de datos.")
            self.status_label_var.set("Error: Sin conexión a la DB.")
            return

        if not username.strip() or not password: 
             messagebox.showerror("Campos Vacíos", "El nombre de usuario y la contraseña no pueden estar vacíos.")
             self.status_label_var.set("Error: Usuario/Contraseña vacíos.")
             return
        if vocacion == "(No hay vocaciones)" or vocacion == "(Error DB)" or not vocacion:
             messagebox.showerror("Vocación Inválida", "Por favor, seleccione una vocación válida.")
             self.status_label_var.set("Error: Vocación no seleccionada.")
             return

        exito, mensaje = registrar_usuario_db(username, password, fecha_nac_dt_completa, vocacion)

        if exito:
            messagebox.showinfo("Registro Exitoso", mensaje)
            self.status_label_var.set(mensaje)
            self.username_entry.delete(0, tk.END)
            self.password_entry.delete(0, tk.END)
            self.fecha_nac_entry.delete(0, tk.END) # Limpiar DateEntry
            self.edad_label_var.set("N/A")
            if self.vocacion_combobox['values'] and self.vocacion_combobox['values'][0] not in ["(No hay vocaciones)", "(Error DB)"]:
                 self.vocacion_combobox.current(0)
        else:
            messagebox.showerror("Error de Registro", mensaje)
            self.status_label_var.set(f"Error: {mensaje}")

# Paso 5: Script Principal para Ejecutar la Aplicación
def main_gui():
    root = tk.Tk()
    app = VentanaRegistro(root)
    root.mainloop()

if __name__ == "__main__":
    temp_db_conn = conectar_db() 
    if temp_db_conn is not None: 
        if temp_db_conn["vocaciones"].count_documents({}) == 0:
            print("Poblando vocaciones de ejemplo...")
            vocaciones_ejemplo = [
                {"nombre_vocacion": "Desarrollo Web"},
                {"nombre_vocacion": "Ciencia de Datos"},
                {"nombre_vocacion": "Diseño Gráfico"},
                {"nombre_vocacion": "Marketing Digital"}
            ]
            try:
                temp_db_conn["vocaciones"].insert_many(vocaciones_ejemplo)
                print("Vocaciones de ejemplo añadidas.")
            except Exception as e:
                print(f"Error al poblar vocaciones: {e}")
    else:
        print("No se pudo conectar a la DB para verificar/poblar vocaciones.")
    main_gui()