import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime

try:
    import Neo4jtest as neo4jcrud
    import crudbibliotest as bibliografias
    import crudusuariostest as usuarios
    import crudcursostest as cursos
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


class VentanaEnlaceBiblio:
    def __init__(self, master, titulo, enlace):
        self.enlace_window = tk.Toplevel(master)
        self.enlace_window.title(f"Enlace para: {titulo[:30]}...")
        self.enlace_window.geometry("450x150")
        self.enlace_window.resizable(False, False)
        
        self.enlace = enlace

        # Hacer la ventana modal
        self.enlace_window.transient(master)
        self.enlace_window.grab_set()

        main_frame = ttk.Frame(self.enlace_window, padding=15)
        main_frame.pack(expand=True, fill=tk.BOTH)

        ttk.Label(main_frame, text="Enlace de la Bibliografía:", font=('Helvetica', 10, 'bold')).pack(anchor="w")
        
        enlace_entry = ttk.Entry(main_frame, font=('Courier', 9))
        enlace_entry.insert(0, self.enlace)
        enlace_entry.config(state="readonly")
        enlace_entry.pack(fill=tk.X, pady=5)
        
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(10,0))
        
        ttk.Button(button_frame, text="Copiar enlace", command=self._copiar_al_portapapeles).pack(side=tk.LEFT)
        
        self.copiado_label = ttk.Label(button_frame, text="", font=('Helvetica', 9, 'italic'), foreground="green")
        self.copiado_label.pack(side=tk.LEFT, padx=10)

    def _copiar_al_portapapeles(self):
        """Copia el enlace al portapapeles del sistema."""
        try:
            self.enlace_window.clipboard_clear()
            self.enlace_window.clipboard_append(self.enlace)
            self.copiado_label.config(text="¡Copiado!")
            self.enlace_window.after(2000, lambda: self.copiado_label.config(text=""))
        except tk.TclError:
            self.copiado_label.config(text="Error al copiar.", foreground="red")
            print("No se pudo acceder al portapapeles.")


class VentanaCamino:
    def __init__(self, master, datos_usuario, neo4j_crud_instance):
        self.camino_window = tk.Toplevel(master)
        self.camino_window.title(f"Camino de Aprendizaje de {datos_usuario['username']}")
        self.camino_window.geometry("700x500")
        
        self.datos_usuario = datos_usuario
        self.neo4j_crud = neo4j_crud_instance
        
        canvas = tk.Canvas(self.camino_window)
        scrollbar = ttk.Scrollbar(self.camino_window, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas, padding=20)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(
                scrollregion=canvas.bbox("all")
            )
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        ttk.Label(scrollable_frame, text="Mi Camino de Aprendizaje", font=('Helvetica', 14, 'bold')).pack(pady=10)
        
        self.mostrar_info_camino(scrollable_frame)

    def mostrar_info_camino(self, parent_frame):
        cursos_completados = self.datos_usuario.get('progreso', [])
        
        if not cursos_completados:
            ttk.Label(parent_frame, text="Aún no has completado ningún curso. ¡Empieza tu camino desde la pestaña 'Cursos'!").pack(pady=20)
            return

        ttk.Label(parent_frame, text="Mi Progreso Actual:", font=('Helvetica', 11, 'bold')).pack(anchor="w", pady=(10, 0))
        for curso_nombre in cursos_completados:
            ttk.Label(parent_frame, text=f"  ✓ {curso_nombre} (Completado)").pack(anchor="w", padx=20)

        ttk.Label(parent_frame, text="\nRuta de Aprendizaje Requerida:", font=('Helvetica', 11, 'bold')).pack(anchor="w")
        predecesores = self.neo4j_crud.obtener_rama_predecesora_completa(cursos_completados)
        if predecesores:
            for nodo in predecesores:
                texto_nodo = f"  - {nodo['nombre']} ({nodo['tipo_nodo']})"
                if nodo.get('dificultad'):
                    texto_nodo += f" - Dificultad: {nodo['dificultad']}"
                ttk.Label(parent_frame, text=texto_nodo).pack(anchor="w", padx=20)
        else:
             ttk.Label(parent_frame, text="  No hay cursos predecesores definidos para tu progreso actual.").pack(anchor="w", padx=20)
        
        ttk.Label(parent_frame, text="\nPróximos Pasos Recomendados:", font=('Helvetica', 11, 'bold')).pack(anchor="w")
        siguientes = self.neo4j_crud.obtener_cursos_siguientes_de_lista(cursos_completados)
        if siguientes:
            for curso in siguientes:
                ttk.Label(parent_frame, text=f"  - {curso['nombre']} (Dificultad: {curso['dificultad']})").pack(anchor="w", padx=20)
        else:
            ttk.Label(parent_frame, text="  ¡Felicidades! Has completado todas las ramas disponibles.").pack(anchor="w", padx=20)


class VentanaCurso:
    def __init__(self, master, nombre_curso, datos_usuario, usuarios_crud_instance, on_close_callback):
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
        if messagebox.askyesno("Confirmar Finalización", f"¿Estás seguro de que deseas marcar '{self.nombre_curso}' como completado?"):
            progreso_actual = self.datos_usuario.get('progreso', [])
            if self.nombre_curso not in progreso_actual:
                nuevo_progreso = progreso_actual + [self.nombre_curso]
                datos_a_actualizar = {"progreso": nuevo_progreso}
                id_usuario_mongo = self.datos_usuario.get('_id')
                
                exito = self.usuarios_crud.actualizar_usuario(id_usuario_mongo, datos_a_actualizar)
                
                if exito:
                    messagebox.showinfo("¡Felicidades!", f"Has completado el curso: {self.nombre_curso}.")
                    self.on_close_callback()
                    self.curso_window.destroy()
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
        VentanaCamino(self.master, self.datos_usuario, self.neo4j_crud)
            
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
        self.tree_cursos.bind("<Double-1>", self._al_hacer_doble_clic_curso)

    def _cargar_cursos_vocacion(self):
        for i in self.tree_cursos.get_children():
            self.tree_cursos.delete(i)

        cursos_a_mostrar = []
        nombres_reales_para_biblios = []
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
                nombres_reales_para_biblios = [c.get("nombre") for c in cursos_a_mostrar]
        else:
            self.notebook.tab(self.tab_cursos, text='Mis Próximos Pasos')
            self.cursos_titulo_label.config(text="Tus Próximos Pasos Recomendados")
            cursos_siguientes = self.neo4j_crud.obtener_cursos_siguientes_de_lista(cursos_completados)
            for nombre_curso in cursos_completados:
                cursos_a_mostrar.append({"nombre": f"✓ {nombre_curso}", "dificultad": "Completado"})
            cursos_a_mostrar.extend(cursos_siguientes)
            nombres_reales_para_biblios = cursos_completados + [c.get("nombre") for c in cursos_siguientes]
            
        if cursos_a_mostrar:
            for curso in cursos_a_mostrar:
                self.tree_cursos.insert("", tk.END, values=(curso.get("nombre"), curso.get("dificultad")))
            self._cargar_bibliografias_por_nombres_de_curso(nombres_reales_para_biblios)
        else:
            self.tree_cursos.insert("", tk.END, values=("No hay cursos recomendados por ahora.", ""))
            self._cargar_bibliografias_por_nombres_de_curso([])

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
        self.tree_biblios.bind("<Double-1>", self._al_hacer_doble_clic_bibliografia)

    def _cargar_bibliografias_por_nombres_de_curso(self, nombres_cursos):
        for i in self.tree_biblios.get_children():
            self.tree_biblios.delete(i)
        
        if not nombres_cursos:
            self.tree_biblios.insert("", tk.END, values=("No hay cursos para buscar bibliografías.", "", ""))
            return
            
        titulos_biblios_a_buscar = set()
        if self.cursos_crud:
            cursos_docs_mongo = self.cursos_crud.leer_cursos_por_nombres(nombres_cursos)
            for curso_doc in cursos_docs_mongo:
                biblio_desbloqueada = curso_doc.get("enciclopedia_desbloqueada")
                if biblio_desbloqueada:
                    titulos_biblios_a_buscar.add(biblio_desbloqueada)

        if titulos_biblios_a_buscar and self.bibliografias_crud:
            bibliografias_data = self.bibliografias_crud.leer_bibliografias_por_titulos(list(titulos_biblios_a_buscar))
            if bibliografias_data:
                self.biblios_data_cache = {b.get("titulo"): b for b in bibliografias_data}
                for biblio in bibliografias_data:
                    self.tree_biblios.insert("", tk.END, iid=biblio.get("titulo"), values=(biblio.get("titulo"), biblio.get("autor"), biblio.get("descripcion", "N/A")))
            else:
                self.tree_biblios.insert("", tk.END, values=("No se encontraron bibliografías para estos cursos.", "", ""))
        elif not titulos_biblios_a_buscar:
            self.tree_biblios.insert("", tk.END, values=("Los cursos visibles no tienen bibliografías asociadas.", "", ""))

    def _al_hacer_doble_clic_bibliografia(self, event=None):
        selected_item_id = self.tree_biblios.focus()
        if not selected_item_id: return
        
        biblio_data_completa = getattr(self, 'biblios_data_cache', {}).get(selected_item_id)
        
        if biblio_data_completa and biblio_data_completa.get("enlace"):
            VentanaEnlaceBiblio(self.master, biblio_data_completa["titulo"], biblio_data_completa["enlace"])
        elif biblio_data_completa:
             messagebox.showinfo("Sin Enlace", f"La bibliografía '{biblio_data_completa['titulo']}' no tiene un enlace asociado.")
        else:
            titulo_seleccionado = self.tree_biblios.item(selected_item_id, "values")[0]
            messagebox.showinfo("Información", f"Buscando enlace para: {titulo_seleccionado} (implementación fallback).")


    def _al_cerrar_ventana_principal(self):
        if messagebox.askokcancel("Salir", "¿Estás seguro de que quieres cerrar la aplicación?"):
            if self.neo4j_crud:
                self.neo4j_crud.close()
            if self.usuarios_crud and getattr(self.usuarios_crud, 'client', None):
                self.usuarios_crud.client.close()
                print("Conexión a MongoDB cerrada.")
            self.master.destroy()
