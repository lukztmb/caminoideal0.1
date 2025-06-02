from neo4j import GraphDatabase

class GrafoTest:
    def __init__(self):
        self.driver = GraphDatabase.driver(uri = "bolt://localhost:7687", auth=("neo4j", "12345678"))
        self.database = "test"

    def cerrar(self):
        self.driver.close()
    
    #def crear_datos_iniciales(self):
    #    with self.driver.session() as session:
    #        session.run("""
    #            MERGE (u:Usuario {nombre: 'Juan'})
    #            MERGE (o:Objetivo {nombre: 'Ser desarrollador Fullstack'})
    #            MERGE (r:Recurso {nombre: 'Curso de JavaScript', tipo: 'video', dificultad: 'media'})
    #            MERGE (u)-[:QUIERE_LOGRAR]->(o)
    #            MERGE (o)-[:SE_PUEDE_ALCANZAR_CON]->(r)
    #        """)
        
    def buscar_usuarios(self):
        with self.driver.session(database=self.database) as session:
            result = session.run("MATCH (u:Usuario) RETURN u.nombre AS nombre")
            for record in result:
                print("Usuario encontrado:", record["nombre"])

    def modificar_usuario(self, nombre_actual, nuevo_nombre):
        with self.driver.session(database=self.database) as session:
            session.run("""
                MATCH (u:Usuario {nombre: $nombre_actual})
                SET u.nombre = $nuevo_nombre
            """, nombre_actual=nombre_actual, nuevo_nombre=nuevo_nombre)
            print(f"Usuario '{nombre_actual}' renombrado a '{nuevo_nombre}'")

    def eliminar_usuario(self, nombre):
        with self.driver.session(database=self.database) as session:
            session.run("""
                MATCH (u:Usuario {nombre: $nombre})
                DETACH DELETE u
            """, nombre=nombre)
            print(f"Usuario '{nombre}' eliminado")

    def eliminar_recurso(self, nombre):
        with self.driver.session(database=self.database) as session:
            session.run("""
                MATCH (r:Recurso {nombre: $nombre})
                DETACH DELETE r
            """, nombre=nombre)
            print(f"Recurso '{nombre}' eliminado")

    def mostrar_relaciones(self):
        with self.driver.session(database=self.database) as session:
            result = session.run("""
                MATCH (u:Usuario)-[r:QUIERE_LOGRAR]->(o:Objetivo)
                RETURN u.nombre AS usuario, o.nombre AS objetivo
            """)
            for record in result:
                print(f"{record['usuario']} → quiere lograr → {record['objetivo']}")
    
if __name__ == "__main__":
    grafo = GrafoTest()
    # grafo.buscar_usuarios()
    # grafo.modificar_usuario("Juan", "Juan Carlos")
    # grafo.eliminar_usuario("Juan Carlos")
    # grafo.eliminar_recurso("Curso de JavaScript")
    # grafo.mostrar_relaciones()

    grafo.cerrar()