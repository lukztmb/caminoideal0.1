from neo4j import GraphDatabase

class Neo4jCourseLoader:
    def __init__(self, uri, user, password, database="caminos"):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))
        self.database = database
    
    def close(self):
        self.driver.close()
    
    def load_structure(self, structure_data):
        with self.driver.session(database=self.database) as session:
            # Crear nodo objetivo
            session.run("""
                MERGE (o:Objetivo {nombre: $nombre})
                SET o.descripcion = $descripcion
            """, **structure_data['objetivo'])
            
            # Crear categorías y sus relaciones
            for categoria in structure_data['categorias']:
                session.run("""
                    MATCH (o:Objetivo {nombre: $objetivo_nombre})
                    MERGE (o)-[:TIENE_CATEGORIA]->(c:Categoria {nombre: $nombre})
                    SET c.descripcion = $descripcion
                """, objetivo_nombre=structure_data['objetivo']['nombre'], **categoria)
                
                # Crear dificultades y sus relaciones
                for dificultad in categoria['dificultades']:
                    session.run("""
                        MATCH (c:Categoria {nombre: $categoria_nombre})
                        MERGE (c)-[:TIENE_DIFICULTAD]->(d:Dificultad {nivel: $nivel})
                        SET d.descripcion = $descripcion
                    """, categoria_nombre=categoria['nombre'], **dificultad)
                    
                    # Crear cursos y sus relaciones
                    for curso in dificultad['cursos']:
                        session.run("""
                            MATCH (d:Dificultad {nivel: $dificultad_nivel})<-[:TIENE_DIFICULTAD]-(:Categoria {nombre: $categoria_nombre})
                            MERGE (d)-[:TIENE_CURSO]->(curso:Curso {nombre: $nombre})
                            SET curso.duracion = $duracion,
                                curso.descripcion = $descripcion
                        """, dificultad_nivel=dificultad['nivel'], 
                                   categoria_nombre=categoria['nombre'], 
                                   **curso)

    @staticmethod
    def sample_structure():
        """Retorna un diccionario con la estructura de ejemplo"""
        return {
            'objetivo': {
                'nombre': 'Inteligencia Artificial',
                'descripcion': 'Dominio de técnicas avanzadas de IA'
            },
            'categorias': [
                {
                    'nombre': 'Aprendizaje Automático',
                    'descripcion': 'Técnicas para que las máquinas aprendan de datos',
                    'dificultades': [
                        {
                            'nivel': 'Principiante',
                            'descripcion': 'Conceptos básicos',
                            'cursos': [
                                {
                                    'nombre': 'Introducción a ML',
                                    'duracion': 20,
                                    'descripcion': 'Conceptos básicos de aprendizaje supervisado y no supervisado'
                                },
                                {
                                    'nombre': 'Regresión Lineal',
                                    'duracion': 15,
                                    'descripcion': 'Fundamentos de modelos lineales'
                                }
                            ]
                        },
                        {
                            'nivel': 'Avanzado',
                            'descripcion': 'Temas intermedios con implementaciones',
                            'cursos': [
                                {
                                    'nombre': 'Redes Neuronales',
                                    'duracion': 30,
                                    'descripcion': 'Arquitecturas básicas de redes neuronales'
                                }
                            ]
                        }
                    ]
                },
                {
                    'nombre': 'Visión por Computadora',
                    'descripcion': 'Técnicas para que las máquinas interpreten imágenes',
                    'dificultades': [
                        {
                            'nivel': 'Principiante',
                            'descripcion': 'Conceptos básicos',
                            'cursos': [
                                {
                                    'nombre': 'Introducción a OpenCV',
                                    'duracion': 15,
                                    'descripcion': 'Fundamentos de procesamiento de imágenes'
                                }
                            ]
                        }
                    ]
                }
            ]
        }

# Ejemplo de uso
if __name__ == "__main__":
    # Configuración de conexión (modificar con tus credenciales)
    URI = "bolt://localhost:7687"
    USER = "neo4j"
    PASSWORD = "12345678"
    
    # Crear instancia del cargador
    loader = Neo4jCourseLoader(URI, USER, PASSWORD)
    
    try:
        # Cargar estructura de ejemplo
        sample_data = Neo4jCourseLoader.sample_structure()
        loader.load_structure(sample_data)
        print("Estructura cargada exitosamente!")
        
        # Aquí puedes cargar tu propia estructura personalizada
        # personal_data = {...}  # Tu diccionario con la estructura
        # loader.load_structure(personal_data)
        
    except Exception as e:
        print(f"Error al cargar la estructura: {e}")
    finally:
        loader.close()