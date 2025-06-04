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
        if nombres_cursos_progreso and cursos_crud and usuarios_crud:
            cursos_progreso_docs = cursos_crud.leer_cursos_por_nombres(nombres_cursos_progreso)
            for curso_doc in cursos_progreso_docs:
                if curso_doc.get("enciclopedia_desbloqueada"):
                    titulos_biblios_a_buscar.add(curso_doc.get("enciclopedia_desbloqueada"))


        if titulos_biblios_a_buscar:
            bibliografias_data = bibliografias_crud.leer_bibliografias_por_titulos(list(titulos_biblios_a_buscar))
            if bibliografias_data:
                for biblio in bibliografias_data:
                    self.tree_biblios.insert("", tk.END, values=(biblio.get("titulo"), biblio.get("autor"), biblio.get("descripcion", "N/A")))
            else:
                self.tree_biblios.insert("", tk.END, values=("No se encontraron bibliografías para estos cursos.", "", ""))
        else:
            self.tree_biblios.insert("", tk.END, values=("No hay cursos con bibliografías asociadas o progreso.", "", ""))