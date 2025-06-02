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
                'descripcion': 'Dominio de técnicas avanzadas para crear sistemas que exhiben comportamiento inteligente'
            },
            'categorias': [
                {
                    'nombre': 'Aprendizaje Automático',
                    'descripcion': 'Algoritmos que permiten a las máquinas aprender de datos',
                    'dificultades': [
                        {
                            'nivel': 'Principiante',
                            'descripcion': 'Fundamentos teóricos y aplicaciones básicas',
                            'cursos': [
                                {
                                    'nombre': 'Introducción al Machine Learning',
                                    'duracion': 20,
                                    'descripcion': 'Conceptos básicos de aprendizaje supervisado y no supervisado'
                                },
                                {
                                    'nombre': 'Regresión Lineal',
                                    'duracion': 15,
                                    'descripcion': 'Modelos lineales para predicción numérica'
                                }
                            ]
                        },
                        {
                            'nivel': 'Avanzado',
                            'descripcion': 'Implementación de modelos complejos',
                            'cursos': [
                                {
                                    'nombre': 'Redes Neuronales Artificiales',
                                    'duracion': 30,
                                    'descripcion': 'Arquitecturas básicas y funcionamiento interno'
                                },   
                                {
                                    'nombre': 'Sistemas de Recomendación',
                                    'duracion': 25,
                                    'descripcion': 'Filtrado colaborativo y basado en contenido'
                                }
                            ]
                        },
                        {
                            'nivel': 'Experto',
                            'descripcion': 'Técnicas de vanguardia e investigación',
                            'cursos': [
                                {
                                    'nombre': 'Deep Learning Avanzado',
                                    'duracion': 40,
                                    'descripcion': 'Arquitecturas Transformer y modelos generativos'
                                },
                                {
                                    'nombre': 'Aprendizaje por Refuerzo Profundo',
                                    'duracion': 35,
                                    'descripcion': 'Algoritmos DQN y Policy Gradients'
                                }
                            ]
                        }
                    ]
                },
                {
                    'nombre': 'Procesamiento de Lenguaje Natural',
                    'descripcion': 'Técnicas para que las máquinas entiendan y generen lenguaje humano',
                    'dificultades': [
                        {
                            'nivel': 'Principiante',
                            'descripcion': 'Procesamiento básico de texto',
                            'cursos': [
                                {
                                    'nombre': 'NLP Fundamental',
                                    'duracion': 18,
                                    'descripcion': 'Tokenización, stemming y bag-of-words'
                                }   
                            ]
                        },
                        {
                            'nivel': 'Avanzado',
                            'descripcion': 'Modelos de lenguaje estadísticos',
                            'cursos': [
                                {
                                    'nombre': 'Modelos de Secuencias',
                                    'duracion': 28,
                                    'descripcion': 'Cadenas de Markov y modelos ocultos'
                                }
                            ]
                        },
                        {
                            'nivel': 'Experto',
                            'descripcion': 'Modelos de lenguaje neuronal',
                            'cursos': [
                                {
                                    'nombre': 'Transformers en NLP',
                                    'duracion': 45,
                                    'descripcion': 'BERT, GPT y arquitecturas modernas'
                                }
                            ]
                        }
                    ]
                },
                {
                    'nombre': 'Visión por Computadora',
                    'descripcion': 'Técnicas para interpretar y analizar imágenes digitales',
                    'dificultades': [
                        {
                            'nivel': 'Principiante',
                            'descripcion': 'Procesamiento básico de imágenes',
                            'cursos': [
                                {
                                    'nombre': 'OpenCV Básico',
                                    'duracion': 15,
                                    'descripcion': 'Manipulación de imágenes con Python'
                                }
                            ]
                        },
                        {
                            'nivel': 'Avanzado',
                            'descripcion': 'Redes neuronales convolucionales',
                            'cursos': [
                                {
                                    'nombre': 'CNN para Clasificación',
                                    'duracion': 30,
                                    'descripcion': 'Arquitecturas ResNet y VGG'
                                }
                            ]
                        },
                        {
                            'nivel': 'Experto',
                            'descripcion': 'Aplicaciones avanzadas',
                            'cursos': [
                                {
                                    'nombre': 'Generación de Imágenes con GANs',
                                    'duracion': 40,
                                    'descripcion': 'Generative Adversarial Networks aplicadas'
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