from neo4j import GraphDatabase


class GrafoCaminos:
    def __init__(self):
        self.driver = GraphDatabase.driver(uri = "bolt://localhost:7687", auth=("neo4j", "12345678"))
        self.database = "caminos1"

    def cerrar(self):
        self.driver.close()

    def buscarObjetivos(self):
        with self.driver.session(database=self.database) as session:
            resultados = session.run("MATCH (o:Objetivo) RETURN o.nombre AS nombre")
            objetivos = [resultado["nombre"] for resultado in resultados]
            return objetivos
        
    def obtener_cursos_por_dificultad(self, objetivo_nombre):
        with self.driver.session(database=self.database) as session:
            result = session.run("""
                MATCH path = (o:Objetivo {nombre: $objetivo})-[:CONLLEVA_A|SIGUIENTE_CURSO*]->(c:Curso)
                WITH nodes(path) AS nodos
                UNWIND nodos AS n
                WITH DISTINCT n
                WHERE n:Curso
                RETURN n.nombre AS nombre, n.dificultad AS dificultad
                ORDER BY CASE n.dificultad
                        WHEN 'principiante' THEN 1
                        WHEN 'avanzado' THEN 2
                        WHEN 'experto' THEN 3
                     END, nombre
            """, objetivo=objetivo_nombre)

            cursos_por_dificultad = {"principiante": [], "avanzado": [], "experto": []}
            for record in result:
                nombre = record["nombre"]
                dificultad = record["dificultad"]
                if dificultad in cursos_por_dificultad:
                    cursos_por_dificultad[dificultad].append(nombre)

            print(f"Cursos del objetivo '{objetivo_nombre}' agrupados por dificultad:")
            for nivel, cursos in cursos_por_dificultad.items():
                print(f"  {nivel.capitalize()}:")
                for curso in cursos:
                    print(f"    - {curso}")

            return cursos_por_dificultad

    def obtener_cursos_por_dificultad_especifica1(self, objetivo_nombre, dificultad_objetivo):
        with self.driver.session(database=self.database) as session:
            result = session.run("""
                MATCH (c:Curso {dificultad: $dificultad})-[:CONLLEVA_A|SIGUIENTE_CURSO*]->(:Objetivo {nombre: $objetivo})
                RETURN DISTINCT c.nombre AS nombre
                ORDER BY nombre
            """, objetivo=objetivo_nombre, dificultad=dificultad_objetivo)

            cursos = [record["nombre"] for record in result]

            print(f"Cursos con dificultad '{dificultad_objetivo}' para el objetivo '{objetivo_nombre}':")
            for curso in cursos:
                print(f"  - {curso}")

            return cursos

    def obtener_cursos_por_dificultad_especifica2(self, objetivo_nombre, dificultad_objetivo):

        with self.driver.session(database=self.database) as session:
            result = session.run("""
                MATCH path = (o:Objetivo {nombre: $objetivo})-[:CONLLEVA_A|SIGUIENTE_CURSO*]->(c:Curso)
                WITH nodes(path) AS nodos
                UNWIND nodos AS n
                WITH DISTINCT n
                WHERE n:Curso AND n.dificultad = $dificultad
                RETURN n.nombre AS nombre
                ORDER BY nombre
            """, objetivo=objetivo_nombre, dificultad=dificultad_objetivo)

            cursos = [record["nombre"] for record in result]

            print(f"Cursos con dificultad '{dificultad_objetivo}' para el objetivo '{objetivo_nombre}':")
            for curso in cursos:
                print(f"  - {curso}")

            return cursos
        
    def obtener_cursos_por_categoria_dificultad(self, objetivo, nombre_categoria, nivel_dificultad):
        with self.driver.session(database=self.database) as session:
            result = session.run("""
                MATCH (:Objetivo {nombre: $objetivo})-[:TIENE_CATEGORIA]->
                    (:Categoria {nombre: $categoria})-[:TIENE_DIFICULTAD]->
                    (:Dificultad {nivel: $dificultad})-[:TIENE_CURSO]->(c:Curso)
                RETURN c.nombre AS nombre, c.duracion AS duracion, c.descripcion AS descripcion
                ORDER BY nombre
            """, objetivo=objetivo, categoria=nombre_categoria, dificultad=nivel_dificultad)

            cursos = [{
                "nombre": record["nombre"],
                "duracion": record["duracion"],
                "descripcion": record["descripcion"]
            } for record in result]

            print(f"\nCursos de '{nombre_categoria}' con dificultad '{nivel_dificultad}':")
            for curso in cursos:
                print(f"  - {curso['nombre']} ({curso['duracion']} horas): {curso['descripcion']}")

            return cursos

        
    def modificarObjetivo(self, nombreActual, nuevoNombre):
        with self.driver.session(database=self.database) as session:
            session.run("""
                MATCH (o:Objetivo {nombre: $nombre_actual})
                SET o.nombre = $nuevo_nombre
            """, nombre_actual=nombreActual, nuevo_nombre=nuevoNombre)
            print(f"Objetivo '{nombreActual}' renombrado a '{nuevoNombre}'")

    def modificarNodo(self, nombreActual, nuevoNombre, dificultadNueva):
        with self.driver.session(database=self.database) as session:
            session.run("""
                MATCH (c:Curso {nombre: $nombreActual})
                SET c.nombre = $nuevoNombre
                SET c.dificultad = $dificultadNueva
            """, nombreActual=nombreActual, nuevoNombre=nuevoNombre, dificultadNueva=dificultadNueva)
            print(f"Curso '{nombreActual}' renombrado a '{nuevoNombre}'")

    def crearCursoHoja(self, nombre_origen, nombre_destino, tipo_relacion):
        with self.driver.session(database=self.database) as session:
            session.run(f"""
                MERGE (a:Curso {{nombre: $nombre_origen}})
                MERGE (b:Curso {{nombre: $nombre_destino}})
                MERGE (b)-[:{tipo_relacion}]->(a)
            """, nombre_origen=nombre_origen, nombre_destino=nombre_destino)
        print(f"Curso hoja '{nombre_destino}' creado desde '{nombre_origen}'.")

                        


if __name__ == "__main__":
    grafo = GrafoCaminos()
    #grafo.obtener_cursos_por_categoria_dificultad('Robótica Inteligente', 'Experto')
    grafo.cerrar()
    