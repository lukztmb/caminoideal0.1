from neo4j import GraphDatabase, exceptions

class Neo4jCRUD:
    def __init__(self):
        try:
            self._driver = GraphDatabase.driver(uri = "bolt://localhost:7687", auth=("neo4j", "12345678"))
            self._database = "vocacionescursos1"
            self._driver.verify_connectivity()
            print("Conexión a Neo4j establecida exitosamente.")
        except exceptions.AuthError as e:
            print(f"Error de autenticación con Neo4j: {e}")
            self._driver = None
        except exceptions.ServiceUnavailable as e:
            print(f"No se pudo conectar al servicio Neo4j en bolt: {e}")
            self._driver = None
        except Exception as e:
            print(f"Ocurrió un error inesperado al conectar con Neo4j: {e}")
            self._driver = None

    def close(self):
        """Cierra la conexión con la base de datos."""
        if self._driver is not None:
            self._driver.close()
            print("Conexión a Neo4j cerrada.")

    def _ejecutar_transaccion(self, tx_function, **kwargs):
        """
        Método auxiliar para ejecutar una transacción de escritura.
        """
        if self._driver is None:
            print("No hay conexión activa a Neo4j.")
            return None
        with self._driver.session(database=self._database) as session:
            try:
                return session.execute_write(tx_function, **kwargs)
            except exceptions.ConstraintError as e:
                print(f"Error de restricción (ConstraintError): {e}")
                return None
            except Exception as e:
                print(f"Error durante la transacción de escritura: {e}")
                return None
    
    def _ejecutar_lectura(self, tx_function, **kwargs):
        """
        Método auxiliar para ejecutar una transacción de lectura.
        """
        if self._driver is None:
            print("No hay conexión activa a Neo4j.")
            return []
        with self._driver.session(database=self._database) as session:
            try:
                return session.execute_read(tx_function, **kwargs)
            except Exception as e:
                print(f"Error durante la transacción de lectura: {e}")
                return []

    # --- CRUD Vocaciones ---
    @staticmethod
    def _crear_vocacion_tx(tx, nombre):
        query = "CREATE (v:Vocacion {nombre: $nombre}) RETURN id(v) AS id, v.nombre AS nombre"
        result = tx.run(query, nombre=nombre)
        record = result.single()
        if record:
            print(f"Vocación '{record['nombre']}' creada con ID interno: {record['id']}.")
            return {"id_interno_neo4j": record["id"], "nombre": record["nombre"]}
        return None

    def crear_vocacion(self, nombre):
        """Crea un nuevo nodo Vocacion."""
        return self._ejecutar_transaccion(self._crear_vocacion_tx, nombre=nombre)

    @staticmethod
    def _obtener_vocaciones_tx(tx):
        query = "MATCH (v:Vocacion) RETURN id(v) AS id, v.nombre AS nombre ORDER BY v.nombre"
        results = tx.run(query)
        return [{"id_interno_neo4j": record["id"], "nombre": record["nombre"]} for record in results]

    def obtener_vocaciones(self):
        """Obtiene todas las vocaciones."""
        return self._ejecutar_lectura(self._obtener_vocaciones_tx)

    @staticmethod
    def _actualizar_vocacion_tx(tx, nombre_actual, nuevo_nombre):
        query = (
            "MATCH (v:Vocacion {nombre: $nombre_actual}) "
            "SET v.nombre = $nuevo_nombre "
            "RETURN id(v) AS id, v.nombre AS nombre_actualizado"
        )
        result = tx.run(query, nombre_actual=nombre_actual, nuevo_nombre=nuevo_nombre)
        record = result.single()
        if record:
            print(f"Vocación '{nombre_actual}' actualizada a '{record['nombre_actualizado']}'.")
            return {"id_interno_neo4j": record["id"], "nombre": record["nombre_actualizado"]}
        else:
            print(f"No se encontró la vocación '{nombre_actual}' para actualizar.")
            return None
            
    def actualizar_vocacion(self, nombre_actual, nuevo_nombre):
        """Actualiza el nombre de una vocación existente."""
        return self._ejecutar_transaccion(self._actualizar_vocacion_tx, nombre_actual=nombre_actual, nuevo_nombre=nuevo_nombre)

    @staticmethod
    def _eliminar_vocacion_tx(tx, nombre):
        query = (
            "MATCH (v:Vocacion {nombre: $nombre}) "
            "DETACH DELETE v" 
        )
        summary = tx.run(query, nombre=nombre).consume()
        if summary.counters.nodes_deleted > 0:
            print(f"Vocación '{nombre}' y sus relaciones directas eliminadas.")
            return True
        else:
            print(f"No se encontró la vocación '{nombre}' para eliminar.")
            return False

    def eliminar_vocacion(self, nombre):
        """Elimina una vocación y sus relaciones TIENE_CURSO."""
        return self._ejecutar_transaccion(self._eliminar_vocacion_tx, nombre=nombre)
    
    @staticmethod
    def _crear_o_encontrar_vocacion_tx(tx, nombre):
        query = "MERGE (v:Vocacion {nombre: $nombre}) RETURN id(v) AS id, v.nombre AS nombre"
        result = tx.run(query, nombre=nombre).single()
        if result:
            return {"id_interno_neo4j": result["id"], "nombre": result["nombre"]}
        raise Exception(f"No se pudo crear o encontrar la vocación '{nombre}'.")

    # --- CRUD Cursos ---
    @staticmethod
    def _crear_curso_tx(tx, nombre, dificultad):
        query = "CREATE (c:Curso {nombre: $nombre, dificultad: $dificultad}) RETURN id(c) AS id, c.nombre AS nombre, c.dificultad AS dificultad"
        result = tx.run(query, nombre=nombre, dificultad=dificultad)
        record = result.single()
        if record:
            print(f"Curso '{record['nombre']}' (Dificultad: {record['dificultad']}) creado con ID interno: {record['id']}.")
            return {"id_interno_neo4j": record["id"], "nombre": record["nombre"], "dificultad": record["dificultad"]}
        return None

    def crear_curso(self, nombre, dificultad):
        """Crea un nuevo nodo Curso."""
        return self._ejecutar_transaccion(self._crear_curso_tx, nombre=nombre, dificultad=dificultad)

    @staticmethod
    def _obtener_cursos_tx(tx):
        query = "MATCH (c:Curso) RETURN id(c) AS id, c.nombre AS nombre, c.dificultad AS dificultad ORDER BY c.nombre"
        results = tx.run(query)
        return [{"id_interno_neo4j": record["id"], "nombre": record["nombre"], "dificultad": record["dificultad"]} for record in results]

    def obtener_cursos(self):
        """Obtiene todos los cursos."""
        return self._ejecutar_lectura(self._obtener_cursos_tx)

    @staticmethod
    def _actualizar_curso_tx(tx, nombre_actual, nuevo_nombre, nueva_dificultad):
        query_parts = []
        params = {"nombre_actual": nombre_actual}
        
        if nuevo_nombre is not None:
            query_parts.append("c.nombre = $nuevo_nombre")
            params["nuevo_nombre"] = nuevo_nombre
        if nueva_dificultad is not None:
            query_parts.append("c.dificultad = $nueva_dificultad")
            params["nueva_dificultad"] = nueva_dificultad
        
        if not query_parts:
            print("No se proporcionaron datos para actualizar el curso.")
            return None

        set_clause = "SET " + ", ".join(query_parts)
        query = (
            f"MATCH (c:Curso {{nombre: $nombre_actual}}) "
            f"{set_clause} "
            "RETURN id(c) AS id, c.nombre AS nombre_actualizado, c.dificultad AS dificultad_actualizada"
        )
        
        result = tx.run(query, **params)
        record = result.single()
        if record:
            print(f"Curso '{nombre_actual}' actualizado a '{record['nombre_actualizado']}' (Dificultad: {record['dificultad_actualizada']}).")
            return {"id_interno_neo4j": record["id"], "nombre": record["nombre_actualizado"], "dificultad": record["dificultad_actualizada"]}
        else:
            print(f"No se encontró el curso '{nombre_actual}' para actualizar.")
            return None

    def actualizar_curso(self, nombre_actual, nuevo_nombre=None, nueva_dificultad=None):
        """Actualiza propiedades de un curso existente."""
        if nuevo_nombre is None and nueva_dificultad is None:
            print("Debe proporcionar al menos un nuevo nombre o una nueva dificultad para actualizar.")
            return None
        return self._ejecutar_transaccion(self._actualizar_curso_tx, nombre_actual=nombre_actual, nuevo_nombre=nuevo_nombre, nueva_dificultad=nueva_dificultad)

    @staticmethod
    def _eliminar_curso_tx(tx, nombre):
        query = (
            "MATCH (c:Curso {nombre: $nombre}) "
            "DETACH DELETE c"
        )
        summary = tx.run(query, nombre=nombre).consume()
        if summary.counters.nodes_deleted > 0:
            print(f"Curso '{nombre}' y todas sus relaciones eliminadas.")
            return True
        else:
            print(f"No se encontró el curso '{nombre}' para eliminar.")
            return False

    def eliminar_curso(self, nombre):
        """Elimina un curso y todas sus relaciones."""
        return self._ejecutar_transaccion(self._eliminar_curso_tx, nombre=nombre)
    
    @staticmethod
    def _crear_o_encontrar_curso_tx(tx, nombre, dificultad):
        query = (
            "MERGE (c:Curso {nombre: $nombre}) "
            "ON CREATE SET c.dificultad = $dificultad "
            "ON MATCH SET c.dificultad = $dificultad " 
            "RETURN id(c) AS id, c.nombre AS nombre, c.dificultad AS dificultad"
        )
        result = tx.run(query, nombre=nombre, dificultad=dificultad).single()
        if result:
            return {"id_interno_neo4j": result["id"], "nombre": result["nombre"], "dificultad": result["dificultad"]}
        raise Exception(f"No se pudo crear o encontrar el curso '{nombre}'.")

    # --- Gestión de Relaciones ---
    @staticmethod
    def _vincular_vocacion_a_curso_tx(tx, nombre_vocacion, nombre_curso):
        query = (
            "MATCH (v:Vocacion {nombre: $nombre_vocacion}) "
            "MATCH (c:Curso {nombre: $nombre_curso}) "
            "MERGE (v)-[r:TIENE_CURSO]->(c) " 
            "RETURN type(r) AS tipo_relacion"
        )
        result = tx.run(query, nombre_vocacion=nombre_vocacion, nombre_curso=nombre_curso)
        record = result.single()
        if record:
            print(f"Vocación '{nombre_vocacion}' vinculada al curso '{nombre_curso}' con relación '{record['tipo_relacion']}'.")
            return True
        else:
            print(f"No se pudo vincular. Asegúrese que la vocación '{nombre_vocacion}' y el curso '{nombre_curso}' existen.")
            return False

    def vincular_vocacion_a_curso(self, nombre_vocacion, nombre_curso):
        """Crea una relación TIENE_CURSO de una Vocacion a un Curso (primer curso de una rama)."""
        return self._ejecutar_transaccion(self._vincular_vocacion_a_curso_tx, nombre_vocacion=nombre_vocacion, nombre_curso=nombre_curso)

    @staticmethod
    def _vincular_curso_a_curso_tx(tx, nombre_curso_origen, nombre_curso_destino):
        query = (
            "MATCH (c1:Curso {nombre: $nombre_curso_origen}) "
            "MATCH (c2:Curso {nombre: $nombre_curso_destino}) "
            "MERGE (c1)-[r:PRECEDE_A]->(c2) "
            "RETURN type(r) AS tipo_relacion"
        )
        result = tx.run(query, nombre_curso_origen=nombre_curso_origen, nombre_curso_destino=nombre_curso_destino)
        record = result.single()
        if record:
            print(f"Curso '{nombre_curso_origen}' vinculado para preceder al curso '{nombre_curso_destino}'.")
            return True
        else:
            print(f"No se pudo vincular. Asegúrese que ambos cursos ('{nombre_curso_origen}', '{nombre_curso_destino}') existen.")
            return False
            
    def vincular_curso_a_curso(self, nombre_curso_origen, nombre_curso_destino):
        """Crea una relación PRECEDE_A entre dos cursos."""
        return self._ejecutar_transaccion(self._vincular_curso_a_curso_tx, nombre_curso_origen=nombre_curso_origen, nombre_curso_destino=nombre_curso_destino)

    # --- Consultas Especializadas ---
    @staticmethod
    def _obtener_cursos_por_dificultad_tx(tx, dificultad):
        query = (
            "MATCH (c:Curso {dificultad: $dificultad}) "
            "RETURN id(c) AS id, c.nombre AS nombre, c.dificultad AS dificultad ORDER BY c.nombre"
        )
        results = tx.run(query, dificultad=dificultad)
        return [{"id_interno_neo4j": record["id"], "nombre": record["nombre"], "dificultad": record["dificultad"]} for record in results]

    def obtener_cursos_por_dificultad(self, dificultad):
        """Obtiene cursos filtrados por dificultad."""
        return self._ejecutar_lectura(self._obtener_cursos_por_dificultad_tx, dificultad=dificultad)

    @staticmethod
    def _obtener_cursos_siguientes_tx(tx, nombre_curso_actual):
        query = (
            "MATCH (c_actual:Curso {nombre: $nombre_curso_actual})-[:PRECEDE_A]->(c_siguiente:Curso) "
            "RETURN id(c_siguiente) AS id, c_siguiente.nombre AS nombre, c_siguiente.dificultad AS dificultad ORDER BY c_siguiente.nombre"
        )
        results = tx.run(query, nombre_curso_actual=nombre_curso_actual)
        return [{"id_interno_neo4j": record["id"], "nombre": record["nombre"], "dificultad": record["dificultad"]} for record in results]

    def obtener_cursos_siguientes(self, nombre_curso_actual):
        """Obtiene los cursos que son directamente siguientes (precedidos por) al curso actual."""
        return self._ejecutar_lectura(self._obtener_cursos_siguientes_tx, nombre_curso_actual=nombre_curso_actual)

    @staticmethod
    def _obtener_cursos_anteriores_tx(tx, nombre_curso_actual):
        query = (
            "MATCH (nodo_anterior)-[r:PRECEDE_A|TIENE_CURSO]->(c_actual:Curso {nombre: $nombre_curso_actual}) "
            "RETURN id(nodo_anterior) AS id, labels(nodo_anterior)[0] AS tipo_nodo, nodo_anterior.nombre AS nombre, "
            "CASE WHEN 'Curso' IN labels(nodo_anterior) THEN nodo_anterior.dificultad ELSE NULL END AS dificultad "
            "ORDER BY nodo_anterior.nombre"
        )
        results = tx.run(query, nombre_curso_actual=nombre_curso_actual)
        cursos_anteriores = []
        for record in results:
            data = {"id_interno_neo4j": record["id"], "tipo_nodo": record["tipo_nodo"], "nombre": record["nombre"]}
            if record["tipo_nodo"] == "Curso":
                data["dificultad"] = record["dificultad"]
            cursos_anteriores.append(data)
        return cursos_anteriores

    def obtener_cursos_anteriores(self, nombre_curso_actual):
        """
        Obtiene los nodos (Cursos o Vocaciones) que preceden directamente al curso actual.
        Más cercanos al inicio de la rama.
        """
        return self._ejecutar_lectura(self._obtener_cursos_anteriores_tx, nombre_curso_actual=nombre_curso_actual)
    
    def crear_vocacion_con_ramas_desde_dict(self, datos_vocacion_completa):

        if self._driver is None:
            print("Error: No hay conexión activa a Neo4j.")
            return None

        def _tx_crear_estructura_completa(tx, datos_voc):
            vocacion_nombre = datos_voc.get("vocacion_nombre")
            if not vocacion_nombre:
                raise ValueError("El diccionario debe contener 'vocacion_nombre'.")

            voc_result = Neo4jCRUD._crear_o_encontrar_vocacion_tx(tx, vocacion_nombre)
            print(f"Procesando Vocación: '{voc_result['nombre']}'")

            cursos_creados_info = []

            def _procesar_cursos_recursivo(tx_inner, nombre_nodo_padre_actual, tipo_nodo_padre, lista_cursos_hijos_data):
                for curso_data_actual in lista_cursos_hijos_data:
                    nombre_curso = curso_data_actual.get("nombre")
                    dificultad_curso = curso_data_actual.get("dificultad")

                    if not nombre_curso or not dificultad_curso:
                        print(f"  Advertencia: Datos incompletos para un curso bajo '{nombre_nodo_padre_actual}'. Omitiendo.")
                        continue

                    curso_result = Neo4jCRUD._crear_o_encontrar_curso_tx(tx_inner, nombre_curso, dificultad_curso)
                    print(f"  Procesando Curso: '{curso_result['nombre']}' (Dificultad: {dificultad_curso})")
                    cursos_creados_info.append(curso_result)

                    if tipo_nodo_padre == "Vocacion":
                        if Neo4jCRUD._vincular_vocacion_a_curso_tx(tx_inner, nombre_nodo_padre_actual, nombre_curso):
                            print(f"    Relación: Vocación '{nombre_nodo_padre_actual}' --TIENE_CURSO--> Curso '{nombre_curso}'")
                        else:
                            print(f"    Advertencia: No se pudo vincular Vocación '{nombre_nodo_padre_actual}' a Curso '{nombre_curso}'. ¿Nodos existen?")
                    elif tipo_nodo_padre == "Curso":
                        if Neo4jCRUD._vincular_curso_a_curso_tx(tx_inner, nombre_nodo_padre_actual, nombre_curso):
                            print(f"    Relación: Curso '{nombre_nodo_padre_actual}' --PRECEDE_A--> Curso '{nombre_curso}'")
                        else:
                            print(f"    Advertencia: No se pudo vincular Curso '{nombre_nodo_padre_actual}' a Curso '{nombre_curso}'. ¿Nodos existen?")
                    
                    cursos_siguientes_data = curso_data_actual.get("siguientes", [])
                    if cursos_siguientes_data:
                        _procesar_cursos_recursivo(tx_inner, nombre_curso, "Curso", cursos_siguientes_data)
            
            cursos_rama_data = datos_voc.get("cursos_rama", [])
            _procesar_cursos_recursivo(tx, vocacion_nombre, "Vocacion", cursos_rama_data)
            
            return {
                "vocacion_procesada": voc_result,
                "cursos_procesados_count": len(cursos_creados_info),
                "detalle_cursos": cursos_creados_info,
                "status": "Estructura de vocación y cursos procesada."
            }

        with self._driver.session(database=self._database) as session:
            try:
                resultado = session.execute_write(_tx_crear_estructura_completa, datos_voc=datos_vocacion_completa)
                print(f"Resultado final del procesamiento de '{datos_vocacion_completa.get('vocacion_nombre')}': {resultado['status']}")
                return resultado
            except ValueError as ve:
                print(f"Error de datos al procesar la estructura: {ve}")
                return None 
            except Exception as e: 
                print(f"Error crítico durante la transacción de creación de estructura: {e}")
                return None 

    @staticmethod
    def _obtener_rama_cursos_por_vocacion_tx(tx, nombre_vocacion):
        query = (
            "MATCH (v:Vocacion {nombre: $nombre_vocacion})-[r:TIENE_CURSO|PRECEDE_A*0..]->(c:Curso) "
            "WITH v, c, r as rels "
            "RETURN id(c) AS id, c.nombre AS nombre, c.dificultad AS dificultad, size(rels) AS nivel "
            "ORDER BY nivel, c.nombre" 
        )
        results = tx.run(query, nombre_vocacion=nombre_vocacion)
        return [{"id_interno_neo4j": record["id"], "nombre": record["nombre"], "dificultad": record["dificultad"], "nivel_en_rama": record["nivel"]} for record in results]

    def obtener_rama_cursos_por_vocacion(self, nombre_vocacion):
        return self._ejecutar_lectura(self._obtener_rama_cursos_por_vocacion_tx, nombre_vocacion=nombre_vocacion)
    
    @staticmethod
    def _obtener_cursos_directos_por_vocacion_tx(tx, nombre_vocacion):
        """Función transaccional para obtener cursos directamente relacionados con una vocación."""
        query = (
            "MATCH (v:Vocacion {nombre: $nombre_vocacion})-[:TIENE_CURSO]->(c:Curso) "
            "RETURN id(c) AS id, c.nombre AS nombre, c.dificultad AS dificultad "
            "ORDER BY c.nombre"
        )
        results = tx.run(query, nombre_vocacion=nombre_vocacion)
        return [
            {"id_interno_neo4j": record["id"], "nombre": record["nombre"], "dificultad": record["dificultad"]}
            for record in results
        ]

    def obtener_cursos_directos_por_vocacion(self, nombre_vocacion):
        """
        Retorna solo los cursos que están directamente relacionados a una vocación
        (los cursos iniciales de cada rama).
        """
        print(f"\nBuscando cursos directamente relacionados con la vocación: '{nombre_vocacion}'...")
        return self._ejecutar_lectura(self._obtener_cursos_directos_por_vocacion_tx, nombre_vocacion=nombre_vocacion)

    @staticmethod
    def _obtener_cursos_siguientes_de_lista_tx(tx, nombres_cursos_actuales):
        """Función transaccional para obtener el siguiente nivel de cursos desde una lista."""
        query = (
            "UNWIND $nombres_cursos AS nombre_curso_actual "
            "MATCH (:Curso {nombre: nombre_curso_actual})-[:PRECEDE_A]->(c_siguiente:Curso) "
            "WITH c_siguiente "
            "RETURN DISTINCT id(c_siguiente) AS id, c_siguiente.nombre AS nombre, c_siguiente.dificultad AS dificultad "
            "ORDER BY nombre"
        )
        results = tx.run(query, nombres_cursos=nombres_cursos_actuales)
        return [
            {"id_interno_neo4j": record["id"], "nombre": record["nombre"], "dificultad": record["dificultad"]}
            for record in results
        ]

    def obtener_cursos_siguientes_de_lista(self, nombres_cursos_actuales):
        """
        Retorna solo los cursos un nivel de rama por encima (siguientes) 
        de los cursos en la lista de nombres recibida. Sin duplicados.
        """
        print(f"\nBuscando cursos siguientes a: {nombres_cursos_actuales}...")
        return self._ejecutar_lectura(self._obtener_cursos_siguientes_de_lista_tx, nombres_cursos_actuales=nombres_cursos_actuales)

    @staticmethod
    def _obtener_rama_predecesora_completa_tx(tx, nombres_cursos_actuales):
        """
        Función transaccional para obtener todos los nodos predecesores
        de una lista de cursos.
        """
        query = (
            "UNWIND $nombres_cursos AS nombre_curso_actual "
            "MATCH (c_actual:Curso {nombre: nombre_curso_actual}) "
            "MATCH path = (predecesor)-[:TIENE_CURSO|PRECEDE_A*]->(c_actual) "
            "UNWIND nodes(path) AS nodo_en_rama "
            "WITH DISTINCT nodo_en_rama "
            "RETURN id(nodo_en_rama) AS id, labels(nodo_en_rama)[0] AS tipo_nodo, nodo_en_rama.nombre AS nombre, "
            "CASE WHEN 'Curso' IN labels(nodo_en_rama) THEN nodo_en_rama.dificultad ELSE NULL "
            "END AS dificultad "
            "ORDER BY tipo_nodo DESC, nombre "
        )
        results = tx.run(query, nombres_cursos=nombres_cursos_actuales)
        nodos_predecesores = []
        for record in results:
            data = {"id_interno_neo4j": record["id"], "tipo_nodo": record["tipo_nodo"], "nombre": record["nombre"]}
            if record["tipo_nodo"] == "Curso":
                data["dificultad"] = record["dificultad"]
            nodos_predecesores.append(data)
        return nodos_predecesores

    def obtener_rama_predecesora_completa(self, nombres_cursos_actuales):
        """
        Retorna toda la rama de cursos y vocaciones predecesores (más cercanos al inicio)
        de los cursos en la lista de nombres recibida. Sin duplicados.
        """
        print(f"\nBuscando la rama predecesora completa de: {nombres_cursos_actuales}...")
        return self._ejecutar_lectura(self._obtener_rama_predecesora_completa_tx, nombres_cursos_actuales=nombres_cursos_actuales)
        


if __name__ == "__main__":

    gestor_neo4j = Neo4jCRUD()

    if gestor_neo4j._driver is None:
        print("No se pudo conectar a Neo4j. Saliendo del ejemplo.")
    else:
        print("\n--- Iniciando Demo CRUD Neo4j ---")

        # try:
        #     gestor_neo4j._ejecutar_transaccion(lambda tx: tx.run("CREATE CONSTRAINT vocacion_nombre_unique IF NOT EXISTS FOR (v:Vocacion) REQUIRE v.nombre IS UNIQUE"))
        #     gestor_neo4j._ejecutar_transaccion(lambda tx: tx.run("CREATE CONSTRAINT curso_nombre_unique IF NOT EXISTS FOR (c:Curso) REQUIRE c.nombre IS UNIQUE"))
        #     print("Constraints de unicidad para nombre de Vocacion y Curso aseguradas (o ya existían).")
        # except Exception as e:
        #     print(f"Advertencia al crear constraints (pueden ya existir): {e}")


        datos_para_carga_masiva_neo4j = [
            {
                "vocacion_nombre": "Ingeniería de Software", # De datos.vocaciones.json
                "cursos_rama": [
                    {
                        "nombre": "Introducción al Desarrollo Web: HTML, CSS y JavaScript", # De datos.cursos.json
                        "dificultad": "Principiante", # De datos.cursos.json (nivel)
                        "siguientes": [
                            {
                                "nombre": "Desarrollo de Interfaces con React.js",
                                "dificultad": "Intermedio",
                                "siguientes": [
                                    { "nombre": "Backend con Node.js, Express y MongoDB", "dificultad": "Intermedio" },
                                    { "nombre": "Introducción a DevOps: Cultura, Prácticas y Herramientas", "dificultad": "Intermedio" }
                                ]
                            },
                            {
                                "nombre": "Python Esencial para Inteligencia Artificial",
                                "dificultad": "Principiante",
                                "siguientes": [
                                     { "nombre": "Machine Learning: De Cero a Práctico", "dificultad": "Principiante" },
                                     { "nombre": "SQL para Análisis de Datos: De Básico a Avanzado", "dificultad": "Intermedio"}
                                ]
                            }
                        ]
                    },
                    {
                        "nombre": "Gestión Ágil de Proyectos con Scrum y Kanban",
                        "dificultad": "Todos los niveles"
                    },
                    {
                        "nombre": "Cloud Computing con AWS: Fundamentos y Servicios Clave",
                        "dificultad": "Principiante"
                    }
                ]
            },
            {
                "vocacion_nombre": "Especialista en Ciberseguridad", # De datos.vocaciones.json
                "cursos_rama": [
                    {
                        "nombre": "Introducción a la Ciberseguridad",
                        "dificultad": "Principiante",
                        "siguientes": [
                            {
                                "nombre": "Ethical Hacking y Pruebas de Penetración",
                                "dificultad": "Avanzado"
                            },
                            {
                                "nombre": "Cloud Computing con AWS: Fundamentos y Servicios Clave",
                                "dificultad": "Principiante",
                                "siguientes": [
                                    # Podría ir un curso de "Seguridad Avanzada en AWS"
                                ]
                            }
                        ]
                    },
                    {
                        "nombre": "Blockchain y Criptomonedas: Fundamentos y Aplicaciones",
                        "dificultad": "Intermedio"
                    }
                ]
            },
            {
                "vocacion_nombre": "Diseño Gráfico", # De datos.vocaciones.json
                "cursos_rama": [
                    {
                        "nombre": "Fundamentos del Diseño de Experiencia de Usuario (UX)",
                        "dificultad": "Principiante",
                        "siguientes": [
                            {
                                "nombre": "Diseño de Interfaces (UI) con Figma",
                                "dificultad": "Intermedio",
                                "siguientes": [
                                    {"nombre": "Fotografía Digital Profesional", "dificultad": "Todos los niveles"}
                                ]
                            }
                        ]
                    },
                    {
                        "nombre": "Marketing Digital Integral: SEO, SEM y Redes Sociales",
                        "dificultad": "Principiante"
                    },
                    {
                        "nombre": "Ilustración Digital y Concept Art para Videojuegos y Cine", # Vocación relacionada
                        "dificultad": "Intermedio" # Asumiendo que existe un curso con este nombre
                    }
                ]
            },
            {
                "vocacion_nombre": "Marketing Digital", # De datos.vocaciones.json
                "cursos_rama": [
                    {
                        "nombre": "Marketing Digital Integral: SEO, SEM y Redes Sociales",
                        "dificultad": "Principiante",
                        "siguientes": [
                            {
                                "nombre": "SQL para Análisis de Datos: De Básico a Avanzado",
                                "dificultad": "Intermedio"
                            },
                            {
                                "nombre": "Fundamentos del Diseño de Experiencia de Usuario (UX)", # Para entender al cliente
                                "dificultad": "Principiante"
                            }
                        ]
                    }
                ]
            },
            {
                "vocacion_nombre": "Aprender programación desde cero", # De datos.vocaciones.json
                "cursos_rama": [
                    {
                        "nombre": "Introducción al Desarrollo Web: HTML, CSS y JavaScript",
                        "dificultad": "Principiante",
                        "siguientes": [
                            {
                                "nombre": "Python Esencial para Inteligencia Artificial",
                                "dificultad": "Principiante",
                                "siguientes": [
                                    { "nombre": "Machine Learning: De Cero a Práctico", "dificultad": "Principiante" }
                                ]
                            }
                        ]
                    },
                    {
                        "nombre": "SQL para Análisis de Datos: De Básico a Avanzado",
                        "dificultad": "Intermedio"
                    },
                    {
                        "nombre": "Desarrollo de Videojuegos 2D con Unity", # Otra opción para aprender programación
                        "dificultad": "Principiante"
                    }
                ]
            },
            {
                "vocacion_nombre": "Desarrollo de Videojuegos Indie", # De datos.vocaciones.json
                "cursos_rama": [
                    {
                        "nombre": "Desarrollo de Videojuegos 2D con Unity",
                        "dificultad": "Principiante",
                        "siguientes": [
                            {
                                "nombre": "Desarrollo de Videojuegos 3D con Unreal Engine",
                                "dificultad": "Intermedio",
                                "siguientes": [
                                     {"nombre": "Ilustración Digital y Concept Art para Videojuegos y Cine", "dificultad": "Intermedio"},
                                     {"nombre": "Producción Musical y Diseño de Sonido", "dificultad": "Intermedio"}
                                ]
                            }
                        ]
                    },
                    {
                        "nombre": "Animación 2D y 3D para Cine y Publicidad", # Habilidad complementaria
                        "dificultad": "Intermedio" # Asumiendo que existe un curso con este nombre
                    }
                ]
            },
            {
                "vocacion_nombre": "Ciencia de Datos", # De datos.vocaciones.json (o creado en script)
                "cursos_rama": [
                    {
                        "nombre": "Python para Ciencia de Datos: NumPy, Pandas y Matplotlib",
                        "dificultad": "Principiante",
                        "siguientes": [
                            {
                                "nombre": "Machine Learning Práctico con Scikit-learn",
                                "dificultad": "Intermedio",
                                "siguientes": [
                                    {
                                        "nombre": "Deep Learning con TensorFlow y Keras",
                                        "dificultad": "Avanzado",
                                        "siguientes": [
                                            {"nombre": "Inteligencia Artificial Generativa", "dificultad": "Avanzado"},
                                            {"nombre": "Visión por Computadora: Detección y Segmentación", "dificultad": "Avanzado"},
                                            {"nombre": "Procesamiento del Lenguaje Natural (PLN) con Python", "dificultad": "Intermedio"}
                                        ]
                                    },
                                    {
                                        "nombre": "Análisis y Predicción de Series Temporales",
                                        "dificultad": "Intermedio"
                                    },
                                    {
                                        "nombre": "Big Data e Inteligencia Artificial con Spark",
                                        "dificultad": "Avanzado"
                                    }
                                ]
                            },
                            {
                                "nombre": "SQL para Análisis de Datos: De Básico a Avanzado",
                                "dificultad": "Intermedio"
                            }
                        ]
                    },
                    {
                        "nombre": "Ética y Responsabilidad en Inteligencia Artificial",
                        "dificultad": "Todos los niveles"
                    },
                    {
                        "nombre": "Inteligencia Artificial Explicable (XAI)",
                        "dificultad": "Avanzado"
                    }
                ]
            },
            {
                "vocacion_nombre": "Desarrollar un emprendimiento digital", # De datos.vocaciones.json
                "cursos_rama": [
                    {
                        "nombre": "Introducción al Desarrollo Web: HTML, CSS y JavaScript", # Base para muchos emprendimientos
                        "dificultad": "Principiante",
                        "siguientes": [
                            {"nombre": "Backend con Node.js, Express y MongoDB", "dificultad": "Intermedio"}
                        ]
                    },
                    {
                        "nombre": "Marketing Digital Integral: SEO, SEM y Redes Sociales",
                        "dificultad": "Principiante"
                    },
                    {
                        "nombre": "Gestión Ágil de Proyectos con Scrum y Kanban",
                        "dificultad": "Todos los niveles"
                    },
                    {
                        "nombre": "Cloud Computing con AWS: Fundamentos y Servicios Clave", # Para desplegar
                        "dificultad": "Principiante"
                    }
                ]
            },
            {
                "vocacion_nombre": "Obtener una certificación internacional (como AWS o TOEFL)", # De datos.vocaciones.json
                "cursos_rama": [
                    {
                        "nombre": "Cloud Computing con AWS: Fundamentos y Servicios Clave",
                        "dificultad": "Principiante",
                        "siguientes": [
                            # Aquí irían cursos más avanzados de AWS si existieran en datos.cursos.json
                            # Por ejemplo: "AWS Certified Solutions Architect - Associate"
                        ]
                    }
                    # Para TOEFL, se necesitarían cursos de preparación de inglés específicos
                ]
            },
            {
                "vocacion_nombre": "Dominar el diseño gráfico",
                "cursos_rama": [
                    {
                        "nombre": "Fundamentos del Diseño de Experiencia de Usuario (UX)",
                        "dificultad": "Principiante"
                    },
                    {
                        "nombre": "Diseño de Interfaces (UI) con Figma",
                        "dificultad": "Intermedio"
                    },
                    {
                        "nombre": "Fotografía Digital Profesional",
                        "dificultad": "Todos los niveles"
                    },
                    {
                        "nombre": "Ilustración Digital y Concept Art para Videojuegos y Cine",
                        "dificultad": "Intermedio" 
                    }
                ]
            }
        ]

        #Carga masiva de datos
        """
        if gestor_neo4j._driver:
            try:
                with gestor_neo4j._driver.session() as s:
                    s.run("CREATE CONSTRAINT vocacion_nombre_unique IF NOT EXISTS FOR (v:Vocacion) REQUIRE v.nombre IS UNIQUE")
                    s.run("CREATE CONSTRAINT curso_nombre_unique IF NOT EXISTS FOR (c:Curso) REQUIRE c.nombre IS UNIQUE")
                    print("Constraints de unicidad para Vocacion.nombre y Curso.nombre aseguradas.")
            except Exception as e_constraint:
                print(f"Advertencia al crear constraints (pueden ya existir o error de permisos): {e_constraint}")

            for vocacion_data in datos_para_carga_masiva_neo4j:
                print(f"\n--- Cargando Vocación: {vocacion_data['vocacion_nombre']} ---")
                resultado = gestor_neo4j.crear_vocacion_con_ramas_desde_dict(vocacion_data)
                if resultado:
                    print(f"Carga para '{vocacion_data['vocacion_nombre']}' completada con estado: {resultado.get('status')}")
                else:
                    print(f"Error al cargar la vocación: {vocacion_data['vocacion_nombre']}")
                    gestor_neo4j.close()
        else:
            print("No se pudo conectar a Neo4j para la carga masiva.")

       
        print(f"\nIntentando crear la vocación y ramas para: '{datos_vocacion_ia['vocacion_nombre']}'")
        resultado_creacion = gestor_neo4j.crear_vocacion_con_ramas_desde_dict(datos_vocacion_ia)

        if resultado_creacion:
            print(f"\nResultado del procesamiento para '{resultado_creacion['vocacion_procesada']['nombre']}':")
            print(f"  Estado: {resultado_creacion['status']}")
            print(f"  Cursos procesados: {resultado_creacion['cursos_procesados_count']}")
            # for curso_info in resultado_creacion['detalle_cursos']:
            #     print(f"    - {curso_info['nombre']} ({curso_info['dificultad']})")
        else:
            print(f"Hubo un error al procesar la vocación '{datos_vocacion_ia['vocacion_nombre']}'.")

        # Verificar la rama creada
        print(f"\n--- Verificando Rama de Cursos para '{datos_vocacion_ia['vocacion_nombre']}' ---")
        rama_ia = gestor_neo4j.obtener_rama_cursos_por_vocacion(datos_vocacion_ia['vocacion_nombre'])
        if rama_ia:
            for curso_en_rama in rama_ia:
                print(f"  Nivel {curso_en_rama['nivel_en_rama']}: {curso_en_rama['nombre']} ({curso_en_rama['dificultad']})")
        else:
            print(f"No se encontraron cursos para la vocación '{datos_vocacion_ia['vocacion_nombre']}'.")
            
        # Ejemplo de creación de otra vocación más simple
        datos_vocacion_web_simple = {
            "vocacion_nombre": "Desarrollo Web Básico",
            "cursos_rama": [
                {"nombre": "HTML Esencial", "dificultad": "Fácil"},
                {"nombre": "CSS Fundamental", "dificultad": "Fácil"}
            ]
        }
        gestor_neo4j.crear_vocacion_con_ramas_desde_dict(datos_vocacion_web_simple)
        
        if gestor_neo4j._driver:
            for vocacion_data in datos_para_carga_masiva:
                print(f"\n--- Cargando Vocación: {vocacion_data['vocacion_nombre']} ---")
                resultado = gestor_neo4j.crear_vocacion_con_ramas_desde_dict(vocacion_data)
                if resultado:
                    print(f"Carga para '{vocacion_data['vocacion_nombre']}' completada con estado: {resultado.get('status')}")
                else:
                    print(f"Error al cargar la vocación: {vocacion_data['vocacion_nombre']}")
            gestor_neo4j.close()
        else:
            print("No se pudo conectar a Neo4j para la carga masiva.")

        # 1. Crear Vocaciones
        print("\n1. Creando Vocaciones...")
        voc1 = gestor_neo4j.crear_vocacion("Desarrollo Web Full-Stack")
        voc2 = gestor_neo4j.crear_vocacion("Ciencia de Datos")
        voc3 = gestor_neo4j.crear_vocacion("Diseño UX/UI")
        gestor_neo4j.crear_vocacion("Desarrollo Web Full-Stack") # Intentar duplicado

        # 2. Crear Cursos
        print("\n2. Creando Cursos...")
        curso_html = gestor_neo4j.crear_curso("HTML y CSS Básico", "Fácil")
        curso_js = gestor_neo4j.crear_curso("JavaScript Fundamental", "Fácil")
        curso_react = gestor_neo4j.crear_curso("React.js Avanzado", "Intermedio")
        curso_node = gestor_neo4j.crear_curso("Node.js y Express", "Intermedio")
        curso_db = gestor_neo4j.crear_curso("Bases de Datos SQL y NoSQL", "Intermedio")
        curso_python_ds = gestor_neo4j.crear_curso("Python para Ciencia de Datos", "Fácil")
        curso_stats = gestor_neo4j.crear_curso("Estadística Aplicada", "Intermedio")
        curso_ml = gestor_neo4j.crear_curso("Machine Learning con Scikit-learn", "Avanzado")
        curso_figma = gestor_neo4j.crear_curso("Diseño de Interfaces con Figma", "Fácil")
        curso_invest_ux = gestor_neo4j.crear_curso("Investigación de Usuarios", "Intermedio")

        # 3. Vincular Vocaciones a Cursos (primeros cursos de la rama)
        print("\n3. Vinculando Vocaciones a Cursos iniciales...")
        if voc1 and curso_html: gestor_neo4j.vincular_vocacion_a_curso(voc1["nombre"], curso_html["nombre"])
        if voc2 and curso_python_ds: gestor_neo4j.vincular_vocacion_a_curso(voc2["nombre"], curso_python_ds["nombre"])
        if voc3 and curso_figma: gestor_neo4j.vincular_vocacion_a_curso(voc3["nombre"], curso_figma["nombre"])

        # 4. Vincular Cursos entre sí (secuencia de dificultad)
        print("\n4. Vinculando Cursos en secuencia...")
        # Rama Desarrollo Web
        if curso_html and curso_js: gestor_neo4j.vincular_curso_a_curso(curso_html["nombre"], curso_js["nombre"])
        if curso_js and curso_react: gestor_neo4j.vincular_curso_a_curso(curso_js["nombre"], curso_react["nombre"])
        if curso_js and curso_node: gestor_neo4j.vincular_curso_a_curso(curso_js["nombre"], curso_node["nombre"]) # JS puede llevar a Backend o Frontend
        if curso_react and curso_db : gestor_neo4j.vincular_curso_a_curso(curso_react["nombre"], curso_db["nombre"]) # Ejemplo, podría ser paralelo
        if curso_node and curso_db : gestor_neo4j.vincular_curso_a_curso(curso_node["nombre"], curso_db["nombre"])
        
        # Rama Ciencia de Datos
        if curso_python_ds and curso_stats: gestor_neo4j.vincular_curso_a_curso(curso_python_ds["nombre"], curso_stats["nombre"])
        if curso_stats and curso_ml: gestor_neo4j.vincular_curso_a_curso(curso_stats["nombre"], curso_ml["nombre"])

        # Rama Diseño UX/UI
        if curso_figma and curso_invest_ux: gestor_neo4j.vincular_curso_a_curso(curso_figma["nombre"], curso_invest_ux["nombre"])

        # 5. Obtener y Mostrar Datos
        print("\n5. Consultando datos...")
        print("\n--- Todas las Vocaciones ---")
        for v in gestor_neo4j.obtener_vocaciones(): print(v)
        
        print("\n--- Todos los Cursos ---")
        for c in gestor_neo4j.obtener_cursos(): print(c)

        print("\n--- Cursos de Dificultad 'Fácil' ---")
        for c in gestor_neo4j.obtener_cursos_por_dificultad("Fácil"): print(c)

        if curso_js:
            print(f"\n--- Cursos Siguientes a '{curso_js['nombre']}' ---")
            for c in gestor_neo4j.obtener_cursos_siguientes(curso_js['nombre']): print(c)

        if curso_react:
            print(f"\n--- Nodos Anteriores a '{curso_react['nombre']}' ---")
            for n_ant in gestor_neo4j.obtener_cursos_anteriores(curso_react['nombre']): print(n_ant)
        
        if voc1:
            print(f"\n--- Rama de Cursos para Vocación '{voc1['nombre']}' ---")
            for c_rama in gestor_neo4j.obtener_rama_cursos_por_vocacion(voc1['nombre']): print(c_rama)
        """
        for v in gestor_neo4j.obtener_vocaciones():
            print(f"\n--- Rama de Cursos para Vocación '{v['nombre']}' ---")
            for c_rama in gestor_neo4j.obtener_rama_cursos_por_vocacion(v['nombre']):
                print(f"  {c_rama['nivel_en_rama']}: {c_rama['nombre']} ({c_rama['dificultad']})")
        """

        # 6. Actualizar Datos
        print("\n6. Actualizando datos...")
        if voc3: gestor_neo4j.actualizar_vocacion(voc3["nombre"], "Diseño de Experiencia de Usuario (UX)")
        if curso_ml: gestor_neo4j.actualizar_curso(curso_ml["nombre"], nueva_dificultad="Muy Avanzado")
        
        print("\n--- Vocaciones después de actualizar 'Diseño UX/UI' ---")
        for v in gestor_neo4j.obtener_vocaciones(): 
            if v["nombre"] == "Diseño de Experiencia de Usuario (UX)": print(v)
        
        print("\n--- Cursos después de actualizar dificultad de ML ---")
        for c in gestor_neo4j.obtener_cursos():
            if c["nombre"] == "Machine Learning con Scikit-learn": print(c)
        """

        #for c in gestor_neo4j.obtener_rama_cursos_por_vocacion("Ciencia de Datos"):
        #    print(f"  {c['nivel_en_rama']}: {c['nombre']} ({c['dificultad']})")
        # 7. Eliminar Datos (descomentar para probar)
        # print("\n7. Eliminando datos...")
        # if curso_db: gestor_neo4j.eliminar_curso(curso_db["nombre"])
        # if voc2: gestor_neo4j.eliminar_vocacion(voc2["nombre"]) # Elimina la vocación y su :TIENE_CURSO
        
        # print("\n--- Todos los Cursos después de eliminar 'Bases de Datos SQL y NoSQL' ---")
        # for c in gestor_neo4j.obtener_cursos(): print(c)
        
        # print("\n--- Todas las Vocaciones después de eliminar 'Ciencia de Datos' ---")
        # for v in gestor_neo4j.obtener_vocaciones(): print(v)

        # Cerrar la conexión
        gestor_neo4j.close()
        #print("\n--- Demo Finalizada ---")
