import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime

try:
    import Neo4jtest as neo4jcrud
    import crudbibliotest as bibliografias
    import crudusuariostest as usuarios
    import crudcursostest as cursos
    import guicaminotinker as pantallacamino
except ImportError as e:
    print(f"Error de importación: {e}. Asegúrate de que los archivos CRUD existan.")
    class PlaceholderCRUD:
        def __init__(self, *args, **kwargs): print(f"Placeholder CRUD inicializado para {self.__class__.__name__}")
        def __getattr__(self, name): return lambda *args, **kwargs: print(f"Llamada a método placeholder: {name}") or []
        def close(self): print(f"Cerrando placeholder CRUD {self.__class__.__name__}")
    
    neo4jcrud = type("neo4jcrud", (object,), {"Neo4jCRUD": PlaceholderCRUD})
    bibliografias = type("bibliografias", (object,), {"BiblioCRUD": PlaceholderCRUD})
    usuarios = type("usuarios", (object,), {"UsuariosCRUD": PlaceholderCRUD})
    cursos = type("cursos", (object,), {"CursosCRUD": PlaceholderCRUD})
    camino = type("camino", (object,), {"VentanaCamino": PlaceholderCRUD})

class VentanaCurso:
    def __init__(self, master, nombre_curso, datos_usuario, usuarios_crud_instance, on_close_callback):
        """
        Inicializa la ventana para un curso activo.
        :param master: El widget padre.
        :param nombre_curso: El nombre del curso a iniciar.
        :param datos_usuario: El diccionario del usuario actual.
        :param usuarios_crud_instance: La instancia del CRUD de usuarios para actualizar el progreso.
        :param on_close_callback: Función a llamar cuando el curso se complete exitosamente.
        """
        self.curso_window = tk.Toplevel(master)
        self.curso_window.title(f"En Curso: {nombre_curso}")
        self.curso_window.geometry("500x200")
        self.curso_window.resizable(False, False)
        
        self.nombre_curso = nombre_curso
        self.datos_usuario = datos_usuario
        self.usuarios_crud = usuarios_crud_instance
        self.on_close_callback = on_close_callback

        self.curso_window.transient(master)
        self.curso_window.grab_set()

        main_frame = ttk.Frame(self.curso_window, padding=20)
        main_frame.pack(expand=True, fill=tk.BOTH)

        ttk.Label(main_frame, text=f"Estás cursando:", font=('Helvetica', 12)).pack()
        ttk.Label(main_frame, text=self.nombre_curso, font=('Helvetica', 14, 'bold')).pack(pady=10)

        
        ttk.Button(main_frame, text="Finalizar Curso", command=self._finalizar_curso).pack(pady=20, ipadx=10)

    def _finalizar_curso(self):
        """
        Maneja la lógica de finalización del curso.
        """
        if messagebox.askyesno("Confirmar Finalización", f"¿Estás seguro de que deseas marcar '{self.nombre_curso}' como completado?"):
            # Obtener la lista de progreso actual y añadir el nuevo curso
            progreso_actual = self.datos_usuario.get('progreso', [])
            if self.nombre_curso not in progreso_actual:
                nuevo_progreso = progreso_actual + [self.nombre_curso]

                # Crear el diccionario de datos para actualizar
                datos_a_actualizar = {"progreso": nuevo_progreso}
                id_usuario_mongo = self.datos_usuario.get('_id')

                # Llamar al método de actualización del CRUD de usuarios
                exito = self.usuarios_crud.actualizar_usuario(id_usuario_mongo, datos_a_actualizar)
                
                if exito:
                    messagebox.showinfo("¡Felicidades!", f"Has completado el curso: {self.nombre_curso}.")
                    # Llamar al callback para notificar a la ventana principal que debe refrescarse
                    self.on_close_callback()
                    self.curso_window.destroy() # Cerrar la ventana del curso
                else:
                    messagebox.showerror("Error", "No se pudo actualizar tu progreso. Inténtalo de nuevo.")
            else:
                 messagebox.showinfo("Información", "Este curso ya estaba en tu progreso.")
                 self.curso_window.destroy()


class VentanaPrincipalApp:
    def __init__(self, master, datos_usuario):
        self.master = master
        self.datos_usuario = datos_usuario
        self.neo4j_crud = neo4jcrud.Neo4jCRUD()
        self.bibliografias_crud = bibliografias.BiblioCRUD()
        self.cursos_crud = cursos.CursosCRUD() 
        self.usuarios_crud = usuarios.UsuariosCRUD() 

        master.title(f"Plataforma de Aprendizaje - Usuario: {datos_usuario['username']}")
        master.geometry("800x600")
        master.protocol("WM_DELETE_WINDOW", self._al_cerrar_ventana_principal)

        style = ttk.Style()
        style.theme_use('clam')
        style.configure("TNotebook.Tab", padding=[10, 5], font=('Helvetica', 10, 'bold'))
        style.configure("Treeview.Heading", font=('Helvetica', 10, 'bold'))
        style.configure("Completed.Treeview", background="#e0ffe0") 

        self.notebook = ttk.Notebook(master)
        
        self.tab_perfil = ttk.Frame(self.notebook, padding=20)
        self.notebook.add(self.tab_perfil, text='Mi Perfil')
        self._crear_widgets_perfil()

        self.tab_cursos = ttk.Frame(self.notebook, padding=20)
        self.notebook.add(self.tab_cursos, text='Cursos') 
        self._crear_widgets_cursos()

        self.tab_bibliografias = ttk.Frame(self.notebook, padding=20)
        self.notebook.add(self.tab_bibliografias, text='Mi Enciclopedia')
        self._crear_widgets_bibliografias()

        self.notebook.pack(expand=True, fill='both')

        self.refrescar_toda_la_interfaz()

    def refrescar_toda_la_interfaz(self):
        """
        Función central para actualizar todos los datos de la GUI.
        """

        usuario_actualizado_doc = self.usuarios_crud.leer_usuario_por_id(self.datos_usuario.get('_id'))
        if usuario_actualizado_doc:
            self.datos_usuario = usuario_actualizado_doc
        
        self.progreso_listbox.delete(0, tk.END)
        cursos_completados = self.datos_usuario.get('progreso', [])
        if cursos_completados:
            for curso in cursos_completados:
                self.progreso_listbox.insert(tk.END, curso)
        else:
            self.progreso_listbox.insert(tk.END, "Aún no has completado cursos.")

        self._cargar_cursos_vocacion()

    def _crear_widgets_perfil(self):
        ttk.Label(self.tab_perfil, text="Información del Usuario", font=('Helvetica', 16, 'bold')).pack(pady=(0,15))
        info_frame = ttk.Frame(self.tab_perfil)
        info_frame.pack(fill=tk.X)
        ttk.Label(info_frame, text="Nombre de Usuario:", font=('Helvetica', 11, 'bold')).grid(row=0, column=0, sticky="w", padx=5, pady=5)
        ttk.Label(info_frame, text=self.datos_usuario.get('username', 'N/A'), font=('Helvetica', 11)).grid(row=0, column=1, sticky="w", padx=5, pady=5)
        ttk.Label(info_frame, text="Vocación:", font=('Helvetica', 11, 'bold')).grid(row=1, column=0, sticky="w", padx=5, pady=5)
        ttk.Label(info_frame, text=self.datos_usuario.get('vocacion', 'N/A'), font=('Helvetica', 11)).grid(row=1, column=1, sticky="w", padx=5, pady=5)
        ttk.Button(info_frame, text="Ver mi Camino de Aprendizaje", command=self._abrir_ventana_camino).grid(row=2, column=0, columnspan=2, pady=15)
        ttk.Label(self.tab_perfil, text="Progreso (Cursos Completados):", font=('Helvetica', 12, 'bold')).pack(pady=(10,5), anchor="w")
        progreso_frame = ttk.Frame(self.tab_perfil)
        progreso_frame.pack(fill=tk.BOTH, expand=True)
        self.progreso_listbox = tk.Listbox(progreso_frame, font=('Helvetica', 10), height=5)
        self.progreso_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, pady=5)
        scrollbar_progreso = ttk.Scrollbar(progreso_frame, orient="vertical", command=self.progreso_listbox.yview)
        scrollbar_progreso.pack(side=tk.RIGHT, fill="y")
        self.progreso_listbox.configure(yscrollcommand=scrollbar_progreso.set)

    def _abrir_ventana_camino(self):
        pantallacamino.VentanaCamino(self.master, self.datos_usuario, self.neo4j_crud)
            
    def _crear_widgets_cursos(self):
        self.cursos_titulo_label = ttk.Label(self.tab_cursos, text="Cursos", font=('Helvetica', 14, 'bold'))
        self.cursos_titulo_label.pack(pady=(0,10))
        cols_cursos = ("nombre_curso", "dificultad_curso")
        self.tree_cursos = ttk.Treeview(self.tab_cursos, columns=cols_cursos, show="headings", height=10)
        self.tree_cursos.heading("nombre_curso", text="Nombre del Curso")
        self.tree_cursos.heading("dificultad_curso", text="Dificultad / Estado")
        self.tree_cursos.column("nombre_curso", width=500)
        self.tree_cursos.column("dificultad_curso", width=150, anchor="center")
        self.tree_cursos.pack(fill=tk.BOTH, expand=True, pady=10)
        # Cambiado a doble clic
        self.tree_cursos.bind("<Double-1>", self._al_hacer_doble_clic_curso)

    def _cargar_cursos_vocacion(self):
        for i in self.tree_cursos.get_children():
            self.tree_cursos.delete(i)

        cursos_a_mostrar = []
        cursos_para_bibliografia = []
        nombre_vocacion = self.datos_usuario.get('vocacion')
        cursos_completados = self.datos_usuario.get('progreso', [])

        if not self.neo4j_crud:
            self.tree_cursos.insert("", tk.END, values=("Error: Servicio Neo4j no disponible.", ""))
            return

        if not cursos_completados:
            self.notebook.tab(self.tab_cursos, text='Cursos de mi Vocación')
            self.cursos_titulo_label.config(text=f"Cursos Recomendados para: {nombre_vocacion}")
            if nombre_vocacion:
                cursos_a_mostrar = self.neo4j_crud.obtener_cursos_directos_por_vocacion(nombre_vocacion)
                cursos_para_bibliografia = cursos_a_mostrar
        else:
            self.notebook.tab(self.tab_cursos, text='Mis Próximos Pasos')
            self.cursos_titulo_label.config(text="Tus Próximos Pasos Recomendados")
            cursos_siguientes = self.neo4j_crud.obtener_cursos_siguientes_de_lista(cursos_completados)
            for nombre_curso in cursos_completados:
                cursos_a_mostrar.append({"nombre": f"✓ {nombre_curso}", "dificultad": "Completado"})
            cursos_a_mostrar.extend(cursos_siguientes)
            nombres_reales_visibles = cursos_completados + [c.get("nombre") for c in cursos_siguientes]
            cursos_para_bibliografia = self.cursos_crud.leer_cursos_por_nombres(nombres_reales_visibles) or []
            
        if cursos_a_mostrar:
            for curso in cursos_a_mostrar:
                self.tree_cursos.insert("", tk.END, values=(curso.get("nombre"), curso.get("dificultad")))
            self._cargar_bibliografias_cursos_visibles(cursos_para_bibliografia)
        else:
            self.tree_cursos.insert("", tk.END, values=("No hay cursos recomendados por ahora.", ""))
            self._cargar_bibliografias_cursos_visibles([])

    def _al_hacer_doble_clic_curso(self, event=None):
        selected_item = self.tree_cursos.focus()
        if not selected_item: return

        item_values = self.tree_cursos.item(selected_item, "values")
        if not item_values: return
        
        nombre_curso_display = item_values[0]
        estado_curso = item_values[1]

        if estado_curso == "Completado":
            messagebox.showinfo("Curso Completado", f"Ya has completado el curso:\n'{nombre_curso_display.replace('✓ ', '')}'")
            return

        nombre_curso_real = nombre_curso_display
        if messagebox.askyesno("Iniciar Curso", f"¿Deseas iniciar el curso '{nombre_curso_real}'?"):
            VentanaCurso(self.master, nombre_curso_real, self.datos_usuario, self.usuarios_crud, self.refrescar_toda_la_interfaz)

    def _crear_widgets_bibliografias(self):
        ttk.Label(self.tab_bibliografias, text="Bibliografías Desbloqueadas y Recomendadas", font=('Helvetica', 14, 'bold')).pack(pady=(0,10))
        cols_biblios = ("titulo_biblio", "autor_biblio", "descripcion_biblio")
        self.tree_biblios = ttk.Treeview(self.tab_bibliografias, columns=cols_biblios, show="headings", height=10)
        self.tree_biblios.heading("titulo_biblio", text="Título")
        self.tree_biblios.heading("autor_biblio", text="Autor")
        self.tree_biblios.heading("descripcion_biblio", text="Descripción")
        self.tree_biblios.column("titulo_biblio", width=250)
        self.tree_biblios.column("autor_biblio", width=150)
        self.tree_biblios.column("descripcion_biblio", width=350)
        self.tree_biblios.pack(fill=tk.BOTH, expand=True, pady=10)

    def _cargar_bibliografias_cursos_visibles(self, cursos_visibles_docs):
        for i in self.tree_biblios.get_children():
            self.tree_biblios.delete(i)
        
        titulos_biblios_a_buscar = set()
        if cursos_visibles_docs and self.cursos_crud:
            for curso_doc in cursos_visibles_docs:
                biblio_desbloqueada = curso_doc.get("enciclopedia_desbloqueada")
                if biblio_desbloqueada:
                    titulos_biblios_a_buscar.add(biblio_desbloqueada)

        if titulos_biblios_a_buscar and self.bibliografias_crud:
            bibliografias_data = self.bibliografias_crud.leer_bibliografias_por_titulos(list(titulos_biblios_a_buscar))
            if bibliografias_data:
                for biblio in bibliografias_data:
                    self.tree_biblios.insert("", tk.END, values=(biblio.get("titulo"), biblio.get("autor"), biblio.get("descripcion", "N/A")))
            else:
                self.tree_biblios.insert("", tk.END, values=("No se encontraron bibliografías para los cursos relevantes.", "", ""))
        elif not titulos_biblios_a_buscar:
            self.tree_biblios.insert("", tk.END, values=("Los cursos visibles no tienen bibliografías asociadas.", "", ""))

    def _al_cerrar_ventana_principal(self):
        if messagebox.askokcancel("Salir", "¿Estás seguro de que quieres cerrar la aplicación?"):
            if self.neo4j_crud:
                self.neo4j_crud.close()
            if self.usuarios_crud and getattr(self.usuarios_crud, 'client', None):
                self.usuarios_crud.client.close()
                print("Conexión a MongoDB cerrada.")
            self.master.destroy()

