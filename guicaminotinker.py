import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime

try:
    import Neo4jtest as neo4jcrud
    import crudbibliotest as bibliografias
    import crudusuariostest as usuarios
    import crudcursostest as cursos
except ImportError as e:
    print(f"Error de importación: {e}. Usando clases de reemplazo (placeholders).")
    class PlaceholderCRUD:
        def __init__(self, *args, **kwargs):
            print(f"Placeholder CRUD inicializado para {self.__class__.__name__}")
        
        def __getattr__(self, name):
            def placeholder_method(*args, **kwargs):
                print(f"Llamada a método placeholder: {name}")

                if name == 'obtener_rama_predecesora_completa':
                    return [{'nombre': f'Curso Predecesor {i}', 'tipo_nodo': 'Curso', 'dificultad': 'Básica'} for i in range(15)]
                if name == 'obtener_cursos_siguientes_de_lista':
                    return [{'nombre': f'Curso Siguiente {i}', 'dificultad': 'Avanzada'} for i in range(15)]
                return []
            return placeholder_method

        def close(self):
            print(f"Cerrando placeholder CRUD {self.__class__.__name__}")
    
    class Neo4jCRUD(PlaceholderCRUD): pass
    neo4jcrud = type("neo4jcrud", (object,), {"Neo4jCRUD": Neo4jCRUD})

class VentanaCamino:
    def __init__(self, master, datos_usuario, neo4j_crud_instance):
        """
        Inicializa la ventana que mostrará el camino de aprendizaje del usuario,
        ahora con una barra de scroll.
        """
        self.camino_window = tk.Toplevel(master)
        self.camino_window.title(f"Camino de Aprendizaje de {datos_usuario['username']}")
        self.camino_window.geometry("700x500")
        
        self.datos_usuario = datos_usuario
        self.neo4j_crud = neo4j_crud_instance
        
        container = ttk.Frame(self.camino_window)
        container.pack(expand=True, fill=tk.BOTH)

        self.canvas = tk.Canvas(container)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scrollbar = ttk.Scrollbar(container, orient=tk.VERTICAL, command=self.canvas.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.canvas.configure(yscrollcommand=scrollbar.set)

        self.scrollable_frame = ttk.Frame(self.canvas, padding=20)

        self.frame_id = self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        
        self.scrollable_frame.bind("<Configure>", self.on_frame_configure)
        self.canvas.bind("<Configure>", self.on_canvas_configure)

        self.camino_window.bind_all("<MouseWheel>", self._on_mousewheel) 
        self.camino_window.bind_all("<Button-4>", self._on_mousewheel)  
        self.camino_window.bind_all("<Button-5>", self._on_mousewheel) 

        self.mostrar_info_camino(self.scrollable_frame)

    def on_frame_configure(self, event=None):
        """Se activa cuando el tamaño del frame interior cambia, para ajustar el área de scroll."""
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def on_canvas_configure(self, event=None):
        """Se activa cuando el tamaño del canvas cambia, para ajustar el ancho del frame."""
        self.canvas.itemconfig(self.frame_id, width=event.width)

    def _on_mousewheel(self, event):
        """Maneja el evento de la rueda del ratón para hacer scroll."""
        if event.num == 4:  
            delta = -1
        elif event.num == 5: 
            delta = 1
        else: 
            delta = -int(event.delta / 120)
        
        self.canvas.yview_scroll(delta, "units")

    def mostrar_info_camino(self, parent_frame):
        """
        Puebla el frame con la información del camino de aprendizaje.
        El 'parent_frame' es ahora el 'scrollable_frame'.
        """
        cursos_completados = self.datos_usuario.get('progreso', [])
        
        ttk.Label(parent_frame, text="Mi Camino de Aprendizaje", font=('Helvetica', 14, 'bold')).pack(pady=10, anchor="w")

        if not cursos_completados:
            ttk.Label(parent_frame, text="Aún no has completado ningún curso. ¡Empieza tu camino desde la pestaña 'Cursos'!").pack(pady=20, anchor="w")
            return

        ttk.Label(parent_frame, text="Mi Progreso Actual:", font=('Helvetica', 11, 'bold')).pack(anchor="w", pady=(10, 0))
        for curso_nombre in cursos_completados:
            ttk.Label(parent_frame, text=f"- ✓ {curso_nombre} (Completado)").pack(anchor="w", padx=20)

        ttk.Label(parent_frame, text="\nRuta de Aprendizaje Completada:", font=('Helvetica', 11, 'bold')).pack(anchor="w")
        predecesores = self.neo4j_crud.obtener_rama_predecesora_completa(cursos_completados)
        if predecesores:
            for nodo in predecesores:
                texto_nodo = f"- {nodo.get('nombre', 'N/A')} ({nodo.get('tipo_nodo', 'N/A')})"
                if nodo.get('dificultad'):
                    texto_nodo += f" - Dificultad: {nodo['dificultad']}"
                ttk.Label(parent_frame, text=texto_nodo).pack(anchor="w", padx=20)
        
        ttk.Label(parent_frame, text="\nPróximos Pasos Recomendados:", font=('Helvetica', 11, 'bold')).pack(anchor="w")
        siguientes = self.neo4j_crud.obtener_cursos_siguientes_de_lista(cursos_completados)
        if siguientes:
            for curso in siguientes:
                ttk.Label(parent_frame, text=f"- {curso.get('nombre', 'N/A')} (Dificultad: {curso.get('dificultad', 'N/A')})").pack(anchor="w", padx=20)
        else:
            ttk.Label(parent_frame, text="¡Felicidades! Has completado todas las ramas disponibles.").pack(anchor="w", padx=20)

