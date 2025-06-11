import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
from datetime import datetime

# Asumiendo que estos módulos existen y tienen las clases y métodos necesarios.
try:
    import crudvocactest as vocaciones
    import crudcursostest as cursos
    import Neo4jtest as neo4j
except ImportError as e:
    print(f"Error de importación: {e}. Asegúrate de que los archivos CRUD existan.")
    class PlaceholderCRUD:
        def __init__(self, *args, **kwargs): print(f"Placeholder CRUD inicializado para {self.__class__.__name__}")
        def __getattr__(self, name): return lambda *args, **kwargs: print(f"Llamada a método placeholder: {name}") or []
        def close(self): print(f"Cerrando placeholder CRUD {self.__class__.__name__}")
    
    vocaciones = type("vocaciones", (object,), {"VocacionesCRUD": PlaceholderCRUD})
    # Corregido: PlaceholderGUI no estaba definido, usando PlaceholderCRUD
    cursos = type("cursos", (object,), {"CursosCRUD": PlaceholderCRUD}) 
    neo4j = type("neo4j", (object,), {"Neo4jCRUD": PlaceholderCRUD})


class AuraLoaderApp:
    def __init__(self, master):
        self.master = master
        master.title("Diseñador de Ramas de Aprendizaje para Neo4j")
        master.geometry("1100x750") # Ajustado para más espacio

        # --- Instancias de CRUD ---
        self.cursos_crud = cursos.CursosCRUD()
        self.vocaciones_crud = vocaciones.VocacionesCRUD()
        self.neo4j_crud = None # Se instanciará al conectar
        self.todos_los_cursos_mongo = [] # Cache para los cursos de MongoDB

        # --- Estructura principal con Pestañas ---
        self.notebook = ttk.Notebook(master)
        self.notebook.pack(expand=True, fill=tk.BOTH, padx=5, pady=5)

        # --- Pestaña 1: Conexión ---
        self.tab_conexion = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(self.tab_conexion, text='Conexión')
        self._crear_widgets_conexion()

        # --- Pestaña 2: Diseñador de Ramas ---
        self.tab_disenador = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(self.tab_disenador, text='Diseñador de Ramas', state="disabled") # Deshabilitada al inicio
        self._crear_widgets_disenador() # Crear widgets pero la pestaña está deshabilitada

        # --- Pestaña 3: Log de Proceso ---
        self.tab_log = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(self.tab_log, text='Registro de Proceso')
        self._crear_widgets_log()

        # Cargar datos iniciales de MongoDB
        self.log("Iniciando aplicación. Por favor, conéctese a Neo4j en la pestaña 'Conexión'.")
        self.master.protocol("WM_DELETE_WINDOW", self.cerrar_aplicacion)

    # --- Creación de Widgets ---

    def _crear_widgets_conexion(self):
        self.conexion_frame_credenciales = ttk.LabelFrame(self.tab_conexion, text="Credenciales Neo4j AuraDB", padding=10)
        self.conexion_frame_credenciales.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(self.conexion_frame_credenciales, text="URI:").grid(row=0, column=0, sticky="w", padx=5, pady=2)
        self.uri_entry = ttk.Entry(self.conexion_frame_credenciales, width=50)
        self.uri_entry.insert(0, "neo4j+s://xxxxxxxx.databases.neo4j.io")
        self.uri_entry.grid(row=0, column=1, sticky="ew", padx=5, pady=2)

        ttk.Label(self.conexion_frame_credenciales, text="Usuario:").grid(row=1, column=0, sticky="w", padx=5, pady=2)
        self.user_entry = ttk.Entry(self.conexion_frame_credenciales)
        self.user_entry.insert(0, "neo4j")
        self.user_entry.grid(row=1, column=1, sticky="ew", padx=5, pady=2)
        
        ttk.Label(self.conexion_frame_credenciales, text="Contraseña:").grid(row=2, column=0, sticky="w", padx=5, pady=2)
        self.password_entry = ttk.Entry(self.conexion_frame_credenciales, show="*")
        self.password_entry.grid(row=2, column=1, sticky="ew", padx=5, pady=2)
        
        self.connect_button = ttk.Button(self.conexion_frame_credenciales, text="Conectar a Neo4j", command=self._conectar_a_neo4j)
        self.connect_button.grid(row=3, column=0, columnspan=2, pady=10)

        self.conexion_frame_credenciales.columnconfigure(1, weight=1)

        self.conexion_frame_estado = ttk.LabelFrame(self.tab_conexion, text="Estado de la Conexión", padding=10)
        self.conexion_frame_estado.pack(fill=tk.X, padx=5, pady=10)
        self.estado_label = ttk.Label(self.conexion_frame_estado, text="No conectado.", font=('Helvetica', 10, 'italic'), foreground="red")
        self.estado_label.pack()

    def _crear_widgets_disenador(self):
        # Frame principal del diseñador
        designer_main_frame = ttk.Frame(self.tab_disenador)
        designer_main_frame.pack(expand=True, fill=tk.BOTH)

        # Fila superior para selección de vocación
        top_frame = ttk.Frame(designer_main_frame)
        top_frame.pack(fill=tk.X, pady=(0, 10))
        ttk.Label(top_frame, text="Vocación a Cargar:", font=('Helvetica', 10, 'bold')).pack(side=tk.LEFT, padx=(0, 10))
        self.vocacion_combobox = ttk.Combobox(top_frame, state="readonly", width=40)
        self.vocacion_combobox.pack(side=tk.LEFT, fill=tk.X, expand=True)

        # PanedWindow para los dos paneles de cursos
        paned_window = tk.PanedWindow(designer_main_frame, orient=tk.HORIZONTAL)
        paned_window.pack(expand=True, fill=tk.BOTH)

        # Panel izquierdo: Cursos disponibles de MongoDB
        left_panel = ttk.LabelFrame(paned_window, text="Cursos Disponibles (MongoDB)", padding=5)
        # MODIFICADO: Cambiado 'show' a "tree headings" para que se vea el nombre del curso.
        self.cursos_disponibles_tree = ttk.Treeview(left_panel, columns=("dificultad"), show="tree headings")
        self.cursos_disponibles_tree.heading("#0", text="Nombre del Curso")
        self.cursos_disponibles_tree.heading("dificultad", text="Dificultad")
        # MODIFICADO: Ajustado el ancho de las columnas
        self.cursos_disponibles_tree.column("#0", width=350, stretch=tk.YES)
        self.cursos_disponibles_tree.column("dificultad", width=100, anchor="center", stretch=tk.NO)
        self.cursos_disponibles_tree.pack(expand=True, fill=tk.BOTH)
        # MODIFICADO: Aumentado el ancho inicial del panel
        paned_window.add(left_panel, width=550)

        # Panel central: Controles
        controls_panel = ttk.Frame(paned_window, padding=10)
        ttk.Button(controls_panel, text=">", command=self._anadir_a_rama, width=3).pack(pady=5)
        ttk.Button(controls_panel, text="<", command=self._quitar_de_rama, width=3).pack(pady=5)
        ttk.Button(controls_panel, text="Acoplar como Siguiente", command=self._acoplar_curso).pack(pady=15)
        paned_window.add(controls_panel)

        # Panel derecho: Estructura de la rama
        right_panel = ttk.LabelFrame(paned_window, text="Estructura de la Rama", padding=5)
        self.rama_builder_tree = ttk.Treeview(right_panel, columns=("dificultad"), show="tree headings")
        self.rama_builder_tree.heading("#0", text="Curso y Sub-ramas")
        self.rama_builder_tree.heading("dificultad", text="Dificultad")
        self.rama_builder_tree.column("#0", width=250, stretch=tk.YES)
        self.rama_builder_tree.column("dificultad", width=100, anchor="center", stretch=tk.NO)
        self.rama_builder_tree.pack(expand=True, fill=tk.BOTH)
        paned_window.add(right_panel, width=400)
        
        # Fila inferior para el botón de carga
        bottom_frame = ttk.Frame(designer_main_frame)
        bottom_frame.pack(fill=tk.X, pady=(10, 0))
        self.load_button = ttk.Button(bottom_frame, text="Cargar Vocación y Estructura a Neo4j", command=self.iniciar_carga)
        self.load_button.pack()
        
    def _crear_widgets_log(self):
        log_frame = ttk.Frame(self.tab_log)
        log_frame.pack(expand=True, fill=tk.BOTH)
        self.log_text = scrolledtext.ScrolledText(log_frame, wrap=tk.WORD, height=10)
        self.log_text.pack(fill=tk.BOTH, expand=True)

    # --- Lógica de la Aplicación ---

    def log(self, message):
        """Añade un mensaje al área de texto de registro."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_text.insert(tk.END, f"[{timestamp}] {message}\n")
        self.log_text.see(tk.END)
        self.master.update_idletasks()
        
    def _conectar_a_neo4j(self):
        uri = self.uri_entry.get()
        user = self.user_entry.get()
        password = self.password_entry.get()
        
        if not all([uri, user, password]) or "xxxxxxxx" in uri:
            messagebox.showerror("Credenciales Incompletas", "Por favor, ingrese URI, usuario y contraseña de Neo4j válidos.")
            return

        self.log(f"Intentando conectar a {uri}...")
        # Asume que el constructor de Neo4jCRUD se ha adaptado para tomar las credenciales
        self.neo4j_crud = neo4j.Neo4jCRUD() 
        if self.neo4j_crud and self.neo4j_crud._driver:
            self.estado_label.config(text=f"Conectado a {uri} (DB: {self.neo4j_crud._database})", foreground="green")
            self.log("Conexión a Neo4j exitosa.")
            self.connect_button.config(state="disabled")
            self.uri_entry.config(state="disabled")
            self.user_entry.config(state="disabled")
            self.password_entry.config(state="disabled")
            # Cargar datos y habilitar la pestaña del diseñador
            self._cargar_datos_disenador()
            self.notebook.tab(1, state="normal")
            self.notebook.select(self.tab_disenador)
        else:
            self.estado_label.config(text="Falló la conexión. Revise la consola.", foreground="red")
            self.log("Error en la conexión a Neo4j.")
            messagebox.showerror("Error de Conexión", "No se pudo conectar a Neo4j. Revise la consola y sus credenciales.")

    def _cargar_datos_disenador(self):
        # Cargar vocaciones en el Combobox
        self.log("Obteniendo vocaciones de MongoDB...")
        vocaciones_lista = self.vocaciones_crud.leer_vocaciones()
        if vocaciones_lista:
            nombres_voc = [v['nombre'] for v in vocaciones_lista]
            self.vocacion_combobox['values'] = nombres_voc
            if nombres_voc: self.vocacion_combobox.current(0)
            self.log(f"Se encontraron {len(nombres_voc)} vocaciones.")
        else:
            self.log("No se encontraron vocaciones en MongoDB.")

        # Cargar cursos en el Treeview de disponibles
        self.log("Obteniendo cursos de MongoDB...")
        self.todos_los_cursos_mongo = self.cursos_crud.leer_cursos()
        for item in self.cursos_disponibles_tree.get_children():
            self.cursos_disponibles_tree.delete(item)
            
        if self.todos_los_cursos_mongo:
            self.cursos_disponibles_data = {}
            for curso in self.todos_los_cursos_mongo:
                iid = self.cursos_disponibles_tree.insert("", "end", text=curso["nombre"], values=(curso["nivel"],))
                self.cursos_disponibles_data[iid] = curso
            self.log(f"Se encontraron {len(self.todos_los_cursos_mongo)} cursos.")
        else:
            self.log("No se encontraron cursos en MongoDB.")

    def _anadir_a_rama(self):
        seleccionados = self.cursos_disponibles_tree.selection()
        if not seleccionados:
            messagebox.showwarning("Sin Selección", "Seleccione al menos un curso del panel izquierdo para añadir.")
            return

        for iid in seleccionados:
            datos_curso = self.cursos_disponibles_data.get(iid)
            if datos_curso:
                if not self._curso_existe_en_rama(datos_curso["nombre"]):
                    self.rama_builder_tree.insert("", "end", text=datos_curso["nombre"], values=(datos_curso["nivel"],), open=True)
                else:
                    self.log(f"El curso '{datos_curso['nombre']}' ya está en la rama.")

    def _quitar_de_rama(self):
        seleccionado = self.rama_builder_tree.selection()
        if not seleccionado:
            messagebox.showwarning("Sin Selección", "Seleccione un curso del panel derecho para quitar.")
            return
        for iid in seleccionado:
            self.rama_builder_tree.delete(iid)
            
    def _acoplar_curso(self):
        padre_seleccionado = self.rama_builder_tree.selection()
        hijos_seleccionados = self.cursos_disponibles_tree.selection()

        if len(padre_seleccionado) != 1:
            messagebox.showwarning("Selección Inválida", "Seleccione exactamente un curso 'padre' en el panel derecho.")
            return
        if not hijos_seleccionados:
            messagebox.showwarning("Selección Inválida", "Seleccione al menos un curso 'hijo' del panel izquierdo.")
            return

        padre_iid = padre_seleccionado[0]
        for hijo_iid in hijos_seleccionados:
            datos_curso_hijo = self.cursos_disponibles_data.get(hijo_iid)
            if datos_curso_hijo:
                if not self._curso_existe_en_rama(datos_curso_hijo["nombre"]):
                    self.rama_builder_tree.insert(padre_iid, "end", text=datos_curso_hijo["nombre"], values=(datos_curso_hijo["nivel"],), open=True)
                else:
                    self.log(f"El curso '{datos_curso_hijo['nombre']}' ya está en la rama y no puede ser acoplado de nuevo.")
                    
    def _curso_existe_en_rama(self, nombre_curso):
        def buscar_recursivo(item_id):
            if self.rama_builder_tree.item(item_id, "text") == nombre_curso:
                return True
            for child_id in self.rama_builder_tree.get_children(item_id):
                if buscar_recursivo(child_id):
                    return True
            return False
            
        for root_item_id in self.rama_builder_tree.get_children():
            if buscar_recursivo(root_item_id):
                return True
        return False
        
    def _convertir_arbol_a_diccionario(self):
        def construir_recursivo(item_id):
            nombre = self.rama_builder_tree.item(item_id, "text")
            dificultad = self.rama_builder_tree.item(item_id, "values")[0]
            
            nodo = {"nombre": nombre, "dificultad": dificultad}
            
            hijos = self.rama_builder_tree.get_children(item_id)
            if hijos:
                nodo["siguientes"] = [construir_recursivo(hijo_id) for hijo_id in hijos]
            
            return nodo

        cursos_rama = [construir_recursivo(root_id) for root_id in self.rama_builder_tree.get_children()]
        return cursos_rama

    def iniciar_carga(self):
        if not self.neo4j_crud or not self.neo4j_crud._driver:
            messagebox.showerror("Sin Conexión", "No hay una conexión activa a Neo4j. Por favor, conéctese primero.")
            self.notebook.select(self.tab_conexion)
            return

        nombre_vocacion = self.vocacion_combobox.get()
        if not nombre_vocacion:
            messagebox.showerror("Sin Vocación", "Por favor, seleccione una vocación.")
            return

        cursos_rama = self._convertir_arbol_a_diccionario()
        if not cursos_rama:
            messagebox.showwarning("Rama Vacía", "La estructura de la rama está vacía. Añada al menos un curso.")
            return
            
        diccionario_final = {
            "vocacion_nombre": nombre_vocacion,
            "cursos_rama": cursos_rama
        }

        self.log(f"--- Iniciando Carga para: '{nombre_vocacion}' ---")
        self.log(f"Estructura a cargar: {diccionario_final}")
        
        if messagebox.askyesno("Confirmar Carga", f"Se cargará la estructura para la vocación '{nombre_vocacion}' con {len(cursos_rama)} rama(s) principal(es). ¿Desea continuar?"):
            try:
                # Asume que el CRUD de Neo4j está listo para ser usado
                resultado = self.neo4j_crud.crear_vocacion_con_ramas_desde_dict(diccionario_final)
                if resultado and resultado.get('status'):
                    self.log(f"Éxito: {resultado.get('status')}")
                    messagebox.showinfo("Carga Completa", "La vocación y su estructura de cursos han sido cargadas exitosamente en Neo4j.")
                else:
                    raise Exception("La operación en Neo4j no retornó un resultado exitoso o esperado.")
            except Exception as e:
                self.log(f"Error durante la carga a Neo4j: {e}")
                messagebox.showerror("Error de Carga", f"Ocurrió un error al cargar los datos. Revise el log.\n\n{e}")

    def cerrar_aplicacion(self):
        if messagebox.askokcancel("Salir", "¿Estás seguro de que quieres salir?"):
            if hasattr(self.vocaciones_crud, 'client') and self.vocaciones_crud.client: self.vocaciones_crud.client.close()
            if hasattr(self.cursos_crud, 'client') and self.cursos_crud.client: self.cursos_crud.client.close()
            if self.neo4j_crud: self.neo4j_crud.close()
            self.master.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = AuraLoaderApp(root)
    root.mainloop()

