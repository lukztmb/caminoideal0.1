import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from pymongo import MongoClient
import bcrypt 
from datetime import datetime 
import Neo4jtest as neo4jcrud
import crudbibliotest as bibliografias
import crudusuariostest as usuarios
import crudcursostest as cursos
import guipantallausuariotinker as pantallaprincipal

# --- Lógica de Backend ---

usuarios_crud = usuarios.UsuariosCRUD()  
bibliografias_crud = bibliografias.BiblioCRUD() 
cursos_crud = cursos.CursosCRUD() 
def verificar_login_usuario(username_ingresado, password_plano_ingresado):
    """Verifica las credenciales de inicio de sesión de un usuario."""
    if not username_ingresado or not password_plano_ingresado:
        return False, "El nombre de usuario y la contraseña no pueden estar vacíos.", None
    try:
        usuario_doc = usuarios_crud.leer_usuario(username_ingresado)
        if usuario_doc is None:
            return False, "Nombre de usuario no encontrado.", None
        hashed_pw_almacenado = usuario_doc.get("password")
        if hashed_pw_almacenado is None:
            return False, "Error: El usuario no tiene una contraseña almacenada correctamente.", None
        if bcrypt.checkpw(password_plano_ingresado.encode('utf-8'), hashed_pw_almacenado):
            datos_usuario_limpios = {k: v for k, v in usuario_doc.items() if k != "password"}
            return True, f"Inicio de sesión exitoso. ¡Bienvenido, {username_ingresado}!", datos_usuario_limpios
        else:
            return False, "Contraseña incorrecta.", None
    except Exception as e:
        print(f"Error durante la verificación de login: {e}")
        return False, f"Error inesperado durante el inicio de sesión: {e}", None

def obtener_bibliografias_por_titulos(lista_titulos_bibliografias):
    """
    Placeholder para buscar bibliografías en MongoDB por una lista de títulos.
    En una implementación real, buscarías en la colección 'bibliografias'.
    """
    if not lista_titulos_bibliografias:
        return []
        
    print(f"MongoBibliografiasPlaceholder: Buscando bibliografías con títulos: {lista_titulos_bibliografias}")
    
    biblios_encontradas = bibliografias_crud.leer_bibliografias_por_titulos(lista_titulos_bibliografias)
    
    if not biblios_encontradas:
        print("MongoBibliografiasPlaceholder: No se encontraron bibliografías directas, devolviendo ejemplos.")
        return [
            {"titulo": "Libro Ejemplo A", "autor": "Autor A", "descripcion": "Descripción del libro A.", "enlace": "#"},
            {"titulo": "Libro Ejemplo B", "autor": "Autor B", "descripcion": "Descripción del libro B.", "enlace": "#"}
        ]
    return biblios_encontradas


# --- Interfaz Gráfica de Login ---
class VentanaLogin:
    def __init__(self, master):
        self.master = master
        master.title("Inicio de Sesión")
        master.geometry("400x300")
        master.resizable(False, False)

        style = ttk.Style()
        style.theme_use('clam')
        style.configure("TLabel", padding=5, font=('Helvetica', 10))
        style.configure("TEntry", padding=5, font=('Helvetica', 10))
        style.configure("TButton", padding=10, font=('Helvetica', 10, 'bold'))

        main_frame = ttk.Frame(master, padding="30 30 30 30")
        main_frame.pack(expand=True, fill=tk.BOTH)
        
        titulo_label = ttk.Label(main_frame, text="Acceso de Usuario", font=('Helvetica', 16, 'bold'))
        titulo_label.pack(pady=(0, 20))

        username_frame = ttk.Frame(main_frame)
        username_frame.pack(fill=tk.X, pady=5)
        ttk.Label(username_frame, text="Usuario:").pack(side=tk.LEFT, padx=(0,10))
        self.username_entry = ttk.Entry(username_frame)
        self.username_entry.pack(side=tk.LEFT, expand=True, fill=tk.X)
        self.username_entry.focus_set()

        password_frame = ttk.Frame(main_frame)
        password_frame.pack(fill=tk.X, pady=5)
        ttk.Label(password_frame, text="Contraseña:").pack(side=tk.LEFT, padx=(0,10))
        self.password_entry = ttk.Entry(password_frame, show="*")
        self.password_entry.pack(side=tk.LEFT, expand=True, fill=tk.X)

        self.login_button = ttk.Button(main_frame, text="Iniciar Sesión", command=self.intentar_login)
        self.login_button.pack(pady=20, fill=tk.X)

        self.status_label_var = tk.StringVar()
        self.status_label = ttk.Label(main_frame, textvariable=self.status_label_var, foreground="red", anchor="center")
        self.status_label.pack(fill=tk.X)
        
        self.password_entry.bind("<Return>", self.intentar_login_event)
        self.username_entry.bind("<Return>", lambda event: self.password_entry.focus_set())

    def intentar_login_event(self, event=None):
        self.intentar_login()

    def intentar_login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()

        if usuarios_crud is None:
            messagebox.showerror("Error de Conexión", "No se pudo conectar a la base de datos. Verifique la consola.")
            self.status_label_var.set("Error: Sin conexión a la DB.")
            return

        exito, mensaje, datos_usuario = verificar_login_usuario(username, password)

        if exito:
            self.status_label_var.set("")
            messagebox.showinfo("Inicio de Sesión Exitoso", mensaje)
            print(f"Datos del usuario '{username}': {datos_usuario}")
            
            self.master.withdraw()
            ventana_app_principal_root = tk.Toplevel(self.master)
           
            app_principal = pantallaprincipal.VentanaPrincipalApp(ventana_app_principal_root, datos_usuario)
            
            app_principal.master.protocol("WM_DELETE_WINDOW", lambda: (app_principal.master.destroy(), self.master.destroy()))
        else:
            self.status_label_var.set(mensaje)
            messagebox.showerror("Error de Inicio de Sesión", mensaje)
            self.password_entry.delete(0, tk.END)

# --- Script Principal para Ejecutar la Aplicación ---
def main_gui_app():
    root = tk.Tk()
    app_login = VentanaLogin(root)
    root.mainloop()

if __name__ == "__main__":
    main_gui_app()
