import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from pymongo import MongoClient
import bcrypt # Para verificar contraseñas hasheadas
from datetime import datetime # Asegurar que datetime esté importado
import Neo4jtest as neo4jcrud

# --- Configuración de la Base de Datos (MongoDB) ---
MONGO_URI = "mongodb://admin:admin123@localhost:27017/"
DATABASE_NAME_DATA = "datos"
COLLECTION_NAME_USUARIOS = "usuarios"
COLLECTION_NAME_BIBLIOGRAFIAS_MONGO = "bibliografias" # Para el CRUD de bibliografías


# --- Lógica de Backend (Login - MongoDB) ---
def conectar_db_mongo():
    """Establece conexión con la base de datos MongoDB."""
    try:
        client = MongoClient(MONGO_URI)
        client.admin.command('ping')
        db = client[DATABASE_NAME_DATA]
        print(f"Conexión a MongoDB exitosa.")
        return db
    except Exception as e:
        print(f"Error al conectar a MongoDB: {e}")
        return None

def verificar_login_usuario(db_mongo, username_ingresado, password_plano_ingresado):
    """Verifica las credenciales de inicio de sesión de un usuario."""
    if db_mongo is None:
        return False, "Error de conexión a la base de datos.", None
    if not username_ingresado or not password_plano_ingresado:
        return False, "El nombre de usuario y la contraseña no pueden estar vacíos.", None
    try:
        usuario_doc = db_mongo[COLLECTION_NAME_USUARIOS].find_one({"username": username_ingresado})
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

# --- Placeholder para el CRUD de Bibliografías (MongoDB) ---
def obtener_bibliografias_por_titulos(db_mongo, lista_titulos_bibliografias):
    """
    Placeholder para buscar bibliografías en MongoDB por una lista de títulos.
    En una implementación real, buscarías en la colección 'bibliografias'.
    """
    if db_mongo is None:
        print("MongoBibliografiasPlaceholder: No hay conexión a la DB.")
        return []
    if not lista_titulos_bibliografias:
        return []
        
    print(f"MongoBibliografiasPlaceholder: Buscando bibliografías con títulos: {lista_titulos_bibliografias}")
    
    # Simulación: buscar en la colección 'bibliografias' por el campo 'titulo'
    biblios_encontradas = list(db_mongo[COLLECTION_NAME_BIBLIOGRAFIAS_MONGO].find(
        {"titulo": {"$in": lista_titulos_bibliografias}}
    ))
    
    # Si no se encuentran, devolver algunas de ejemplo para la demo
    if not biblios_encontradas:
        print("MongoBibliografiasPlaceholder: No se encontraron bibliografías directas, devolviendo ejemplos.")
        return [
            {"titulo": "Libro Ejemplo A", "autor": "Autor A", "descripcion": "Descripción del libro A.", "enlace": "#"},
            {"titulo": "Libro Ejemplo B", "autor": "Autor B", "descripcion": "Descripción del libro B.", "enlace": "#"}
        ]
    return biblios_encontradas


# --- Interfaz Gráfica Principal de la Aplicación ---
class VentanaPrincipalApp:
    def __init__(self, master, datos_usuario, db_mongo_conn):
        self.master = master
        self.datos_usuario = datos_usuario
        self.db_mongo = db_mongo_conn # Conexión a MongoDB
        self.neo4j_crud = neo4jcrud.Neo4jCRUD()

        master.title(f"Plataforma de Aprendizaje - Usuario: {datos_usuario['username']}")
        master.geometry("800x600")
        master.protocol("WM_DELETE_WINDOW", self._al_cerrar_ventana_principal)


        # Estilo
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("TNotebook.Tab", padding=[10, 5], font=('Helvetica', 10, 'bold'))
        style.configure("Treeview.Heading", font=('Helvetica', 10, 'bold'))

        # Notebook para pestañas
        self.notebook = ttk.Notebook(master)
        
        # Pestaña: Perfil de Usuario
        self.tab_perfil = ttk.Frame(self.notebook, padding=20)
        self.notebook.add(self.tab_perfil, text='Mi Perfil')
        self._crear_widgets_perfil()

        # Pestaña: Cursos Recomendados
        self.tab_cursos = ttk.Frame(self.notebook, padding=20)
        self.notebook.add(self.tab_cursos, text='Cursos de mi Vocación')
        self._crear_widgets_cursos()

        # Pestaña: Enciclopedia (Bibliografías)
        self.tab_bibliografias = ttk.Frame(self.notebook, padding=20)
        self.notebook.add(self.tab_bibliografias, text='Mi Enciclopedia')
        self._crear_widgets_bibliografias()

        self.notebook.pack(expand=True, fill='both')

        # Cargar cursos iniciales para la vocación del usuario
        self._cargar_cursos_vocacion()

    def _crear_widgets_perfil(self):
        ttk.Label(self.tab_perfil, text="Información del Usuario", font=('Helvetica', 16, 'bold')).pack(pady=(0,15))
        
        info_frame = ttk.Frame(self.tab_perfil)
        info_frame.pack(fill=tk.X)

        ttk.Label(info_frame, text="Nombre de Usuario:", font=('Helvetica', 11, 'bold')).grid(row=0, column=0, sticky="w", padx=5, pady=5)
        ttk.Label(info_frame, text=self.datos_usuario.get('username', 'N/A'), font=('Helvetica', 11)).grid(row=0, column=1, sticky="w", padx=5, pady=5)
        
        ttk.Label(info_frame, text="Vocación:", font=('Helvetica', 11, 'bold')).grid(row=1, column=0, sticky="w", padx=5, pady=5)
        ttk.Label(info_frame, text=self.datos_usuario.get('vocacion', 'N/A'), font=('Helvetica', 11)).grid(row=1, column=1, sticky="w", padx=5, pady=5)
        
        edad = self.datos_usuario.get('edad', 'N/A')
        ttk.Label(info_frame, text="Edad:", font=('Helvetica', 11, 'bold')).grid(row=2, column=0, sticky="w", padx=5, pady=5)
        ttk.Label(info_frame, text=str(edad), font=('Helvetica', 11)).grid(row=2, column=1, sticky="w", padx=5, pady=5)

        fecha_nac_dt = self.datos_usuario.get('fecha_nacimiento')
        fecha_nac_str = fecha_nac_dt.strftime('%d/%m/%Y') if isinstance(fecha_nac_dt, datetime) else 'N/A'
        ttk.Label(info_frame, text="Fecha de Nacimiento:", font=('Helvetica', 11, 'bold')).grid(row=3, column=0, sticky="w", padx=5, pady=5)
        ttk.Label(info_frame, text=fecha_nac_str, font=('Helvetica', 11)).grid(row=3, column=1, sticky="w", padx=5, pady=5)

        ttk.Label(self.tab_perfil, text="Progreso (Cursos Completados):", font=('Helvetica', 12, 'bold')).pack(pady=(20,5), anchor="w")
        progreso_frame = ttk.Frame(self.tab_perfil)
        progreso_frame.pack(fill=tk.BOTH, expand=True)
        
        self.progreso_listbox = tk.Listbox(progreso_frame, font=('Helvetica', 10), height=5)
        self.progreso_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, pady=5)
        scrollbar_progreso = ttk.Scrollbar(progreso_frame, orient="vertical", command=self.progreso_listbox.yview)
        scrollbar_progreso.pack(side=tk.RIGHT, fill="y")
        self.progreso_listbox.configure(yscrollcommand=scrollbar_progreso.set)

        for curso_completado in self.datos_usuario.get('progreso', []):
            self.progreso_listbox.insert(tk.END, curso_completado)
        if not self.datos_usuario.get('progreso'):
            self.progreso_listbox.insert(tk.END, "Aún no has completado cursos.")

    def _crear_widgets_cursos(self):
        ttk.Label(self.tab_cursos, text=f"Cursos Recomendados para: {self.datos_usuario.get('vocacion', 'N/A')}", font=('Helvetica', 14, 'bold')).pack(pady=(0,10))

        # Treeview para mostrar cursos
        cols_cursos = ("nombre_curso", "dificultad_curso", "nivel_rama")
        self.tree_cursos = ttk.Treeview(self.tab_cursos, columns=cols_cursos, show="headings", height=10)
        self.tree_cursos.heading("nombre_curso", text="Nombre del Curso")
        self.tree_cursos.heading("dificultad_curso", text="Dificultad")
        self.tree_cursos.heading("nivel_rama", text="Nivel en Rama")
        self.tree_cursos.column("nombre_curso", width=350)
        self.tree_cursos.column("dificultad_curso", width=100, anchor="center")
        self.tree_cursos.column("nivel_rama", width=100, anchor="center")
        self.tree_cursos.pack(fill=tk.BOTH, expand=True, pady=10)
        
        self.tree_cursos.bind("<<TreeviewSelect>>", self._al_seleccionar_curso)

        # Botón para cargar/refrescar cursos (aunque se cargan al inicio)
        # ttk.Button(self.tab_cursos, text="Refrescar Cursos", command=self._cargar_cursos_vocacion).pack(pady=10)


    def _cargar_cursos_vocacion(self):
        # Limpiar Treeview anterior
        for i in self.tree_cursos.get_children():
            self.tree_cursos.delete(i)

        nombre_vocacion = self.datos_usuario.get('vocacion')
        if nombre_vocacion and self.neo4j_crud:
            cursos_data = self.neo4j_crud.obtener_rama_cursos_por_vocacion(nombre_vocacion)
            if cursos_data:
                for curso in cursos_data:
                    self.tree_cursos.insert("", tk.END, values=(curso.get("nombre"), curso.get("dificultad"), curso.get("nivel_en_rama", "N/A")))
                # Después de cargar los cursos, cargar bibliografías relacionadas
                self._cargar_bibliografias_cursos_vocacion(cursos_data)
            else:
                self.tree_cursos.insert("", tk.END, values=("No hay cursos recomendados para esta vocación.", "", ""))
        else:
            self.tree_cursos.insert("", tk.END, values=("No se pudo obtener la vocación o conectar a Neo4j.", "", ""))
            
    def _al_seleccionar_curso(self, event=None):
        # Esta función podría usarse para mostrar más detalles del curso seleccionado
        # o para filtrar bibliografías si se desea.
        selected_item = self.tree_cursos.focus() # Obtener el item seleccionado
        if selected_item:
            item_values = self.tree_cursos.item(selected_item, "values")
            if item_values:
                nombre_curso_seleccionado = item_values[0]
                print(f"Curso seleccionado: {nombre_curso_seleccionado}")
                # Aquí podrías, por ejemplo, buscar bibliografías específicas para este curso
                # self._cargar_bibliografias_cursos_vocacion([{"nombre": nombre_curso_seleccionado, "enciclopedia_desbloqueada": "TITULO_LIBRO_ASOCIADO"}])


    def _crear_widgets_bibliografias(self):
        ttk.Label(self.tab_bibliografias, text="Bibliografías Desbloqueadas y Recomendadas", font=('Helvetica', 14, 'bold')).pack(pady=(0,10))

        # Treeview para mostrar bibliografías
        cols_biblios = ("titulo_biblio", "autor_biblio", "descripcion_biblio")
        self.tree_biblios = ttk.Treeview(self.tab_bibliografias, columns=cols_biblios, show="headings", height=10)
        self.tree_biblios.heading("titulo_biblio", text="Título")
        self.tree_biblios.heading("autor_biblio", text="Autor")
        self.tree_biblios.heading("descripcion_biblio", text="Descripción")
        self.tree_biblios.column("titulo_biblio", width=250)
        self.tree_biblios.column("autor_biblio", width=150)
        self.tree_biblios.column("descripcion_biblio", width=350)
        self.tree_biblios.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Podríamos añadir un botón para ver el enlace si se selecciona una bibliografía
        # self.tree_biblios.bind("<<TreeviewSelect>>", self._al_seleccionar_bibliografia)

    def _cargar_bibliografias_cursos_vocacion(self, cursos_de_vocacion):
        # Limpiar Treeview anterior
        for i in self.tree_biblios.get_children():
            self.tree_biblios.delete(i)

        # Recopilar todos los títulos de bibliografías de los cursos de la vocación
        # y del progreso del usuario.
        titulos_biblios_a_buscar = set()
        
        # De los cursos de la vocación (Neo4j)
        for curso_neo4j in cursos_de_vocacion:
            biblio_desbloqueada = curso_neo4j.get("enciclopedia_desbloqueada") # Asumiendo que este campo existe en los datos de Neo4j
            if biblio_desbloqueada:
                titulos_biblios_a_buscar.add(biblio_desbloqueada)
        
        # Del progreso del usuario (MongoDB)
        # Necesitamos obtener los cursos del progreso y sus 'enciclopedia_desbloqueada'
        # Esto requeriría otra consulta a la colección de cursos de MongoDB si 'progreso' solo tiene nombres de cursos.
        # Para este ejemplo, asumiremos que 'enciclopedia_desbloqueada' de los cursos de progreso ya se conoce
        # o que los cursos en 'progreso' son nombres de bibliografías directamente (según el último cambio).
        
        # Si el campo 'progreso' del usuario contiene nombres de cursos, necesitaríamos
        # una función para obtener la 'enciclopedia_desbloqueada' de esos cursos desde MongoDB.
        # Por simplicidad, si 'progreso' ya contiene los títulos de las bibliografías, los usamos.
        # O, si 'progreso' son nombres de cursos, y tenemos el campo 'enciclopedia_desbloqueada' en los datos de Neo4j,
        # podríamos cruzarlo.
        
        # Asumiendo que el campo 'enciclopedia_desbloqueada' en los datos de los cursos (ya sea de Neo4j o MongoDB)
        # es el TÍTULO de la bibliografía.
        
        # Ejemplo: Si el usuario tiene cursos completados y esos cursos tienen un campo 'enciclopedia_desbloqueada'
        # que es el título de un libro:
        # cursos_completados_info = self.db_mongo[COLLECTION_NAME_CURSOS_MONGO].find({"nombre": {"$in": self.datos_usuario.get('progreso', [])}})
        # for curso_comp in cursos_completados_info:
        #     if curso_comp.get("enciclopedia_desbloqueada"):
        #         titulos_biblios_a_buscar.add(curso_comp.get("enciclopedia_desbloqueada"))

        # Dado que el último cambio fue que 'enciclopedia_desbloqueada' en datos.cursos.json
        # AHORA CONTIENE el título de la bibliografía, podemos usarlo.
        # Vamos a asumir que los cursos en 'progreso' son nombres de cursos, y necesitamos
        # obtener sus 'enciclopedia_desbloqueada' (títulos de libros) de la colección de cursos de MongoDB.
        
        nombres_cursos_progreso = self.datos_usuario.get('progreso', [])
        if nombres_cursos_progreso and self.db_mongo:
            # Necesitaríamos la colección de cursos de MongoDB para esto.
            # Asumamos que se llama 'cursos' como en tus archivos JSON.
            cursos_progreso_docs = list(self.db_mongo["cursos"].find( # Usar el nombre de la colección de cursos de MongoDB
                {"nombre": {"$in": nombres_cursos_progreso}},
                {"enciclopedia_desbloqueada": 1} # Solo necesitamos este campo
            ))
            for curso_doc in cursos_progreso_docs:
                if curso_doc.get("enciclopedia_desbloqueada"):
                    titulos_biblios_a_buscar.add(curso_doc.get("enciclopedia_desbloqueada"))


        if titulos_biblios_a_buscar:
            bibliografias_data = obtener_bibliografias_por_titulos(self.db_mongo, list(titulos_biblios_a_buscar))
            if bibliografias_data:
                for biblio in bibliografias_data:
                    self.tree_biblios.insert("", tk.END, values=(biblio.get("titulo"), biblio.get("autor"), biblio.get("descripcion", "N/A")))
            else:
                self.tree_biblios.insert("", tk.END, values=("No se encontraron bibliografías para estos cursos.", "", ""))
        else:
            self.tree_biblios.insert("", tk.END, values=("No hay cursos con bibliografías asociadas o progreso.", "", ""))


    def _al_cerrar_ventana_principal(self):
        if messagebox.askokcancel("Salir", "¿Estás seguro de que quieres cerrar la aplicación?"):
            if self.neo4j_crud:
                self.neo4j_crud.close()
            if self.db_mongo is not None and self.db_mongo.client is not None: # MongoDB cierra la conexión del cliente
                 self.db_mongo.client.close()
                 print("Conexión a MongoDB cerrada desde VentanaPrincipalApp.")
            self.master.destroy()


# --- Interfaz Gráfica de Login ---
class VentanaLogin:
    def __init__(self, master):
        self.master = master
        master.title("Inicio de Sesión")
        master.geometry("400x300")
        master.resizable(False, False)

        self.db_mongo_login = conectar_db_mongo() # Conexión específica para login

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

        if self.db_mongo_login is None:
            messagebox.showerror("Error de Conexión", "No se pudo conectar a la base de datos. Verifique la consola.")
            self.status_label_var.set("Error: Sin conexión a la DB.")
            return

        exito, mensaje, datos_usuario = verificar_login_usuario(self.db_mongo_login, username, password)

        if exito:
            self.status_label_var.set("")
            messagebox.showinfo("Inicio de Sesión Exitoso", mensaje)
            print(f"Datos del usuario '{username}': {datos_usuario}")
            
            self.master.withdraw() # Ocultar ventana de login
            # Crear y mostrar la ventana principal de la aplicación
            ventana_app_principal_root = tk.Toplevel(self.master)
            
            # Crear instancias de los CRUDs (o placeholders) para la ventana principal
            # La conexión de MongoDB para la app principal puede ser la misma o una nueva
            db_mongo_app = self.db_mongo_login # Reutilizar la conexión para la app
            
            #app_principal = VentanaPrincipalApp(ventana_app_principal_root, datos_usuario, db_mongo_app, neo4j_crud_app)
            app_principal = VentanaPrincipalApp(ventana_app_principal_root, datos_usuario, db_mongo_app)
            # Asegurarse de que al cerrar la ventana principal, la aplicación termine o la de login se cierre.
            # Esto es importante si la ventana de login no es la raíz principal de Tkinter.
            # Si la ventana de login ES la raíz (root = tk.Tk()), entonces al hacer root.destroy() se cierra todo.
            # Si la ventana de login es un Toplevel, entonces solo se cierra ella.
            # En este caso, VentanaLogin usa 'master' que es el root.
            # Cuando VentanaPrincipalApp se cierra, llama a self.master.destroy() que cierra el root.
        else:
            self.status_label_var.set(mensaje)
            messagebox.showerror("Error de Inicio de Sesión", mensaje)
            self.password_entry.delete(0, tk.END)

# --- Script Principal para Ejecutar la Aplicación ---
def main_gui_app():
    root = tk.Tk()
    app_login = VentanaLogin(root)
    root.mainloop()
    root.destroy()

if __name__ == "__main__":
    main_gui_app()
