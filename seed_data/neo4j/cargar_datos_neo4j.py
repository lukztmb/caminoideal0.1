from neo4j import GraphDatabase
import Neo4jtest
class Neo4jCourseLoader:
    def __init__(self, uri, user, password, database="vocacionescursos"):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))
        self.database = database
    
    def close(self):
        self.driver.close()
    
    def crear_vocacion_con_ramas_desde_dict(self, datos_vocacion_completa):

        if self._driver is None:
            print("Error: No hay conexión activa a Neo4j.")
            return None

        def _tx_crear_estructura_completa(tx, datos_voc):
            vocacion_nombre = datos_voc.get("vocacion_nombre")
            if not vocacion_nombre:
                raise ValueError("El diccionario debe contener 'vocacion_nombre'.")

            voc_result = Neo4jtest.Neo4jCRUD._crear_o_encontrar_vocacion_tx(tx, vocacion_nombre)
            print(f"Procesando Vocación: '{voc_result['nombre']}'")

            cursos_creados_info = []

            def _procesar_cursos_recursivo(tx_inner, nombre_nodo_padre_actual, tipo_nodo_padre, lista_cursos_hijos_data):
                for curso_data_actual in lista_cursos_hijos_data:
                    nombre_curso = curso_data_actual.get("nombre")
                    dificultad_curso = curso_data_actual.get("dificultad")

                    if not nombre_curso or not dificultad_curso:
                        print(f"  Advertencia: Datos incompletos para un curso bajo '{nombre_nodo_padre_actual}'. Omitiendo.")
                        continue

                    curso_result = Neo4jtest.Neo4jCRUD._crear_o_encontrar_curso_tx(tx_inner, nombre_curso, dificultad_curso)
                    print(f"  Procesando Curso: '{curso_result['nombre']}' (Dificultad: {dificultad_curso})")
                    cursos_creados_info.append(curso_result)

                    if tipo_nodo_padre == "Vocacion":
                        if Neo4jtest.Neo4jCRUD._vincular_vocacion_a_curso_tx(tx_inner, nombre_nodo_padre_actual, nombre_curso):
                            print(f"    Relación: Vocación '{nombre_nodo_padre_actual}' --TIENE_CURSO--> Curso '{nombre_curso}'")
                        else:
                            print(f"    Advertencia: No se pudo vincular Vocación '{nombre_nodo_padre_actual}' a Curso '{nombre_curso}'. ¿Nodos existen?")
                    elif tipo_nodo_padre == "Curso":
                        if Neo4jtest.Neo4jCRUD._vincular_curso_a_curso_tx(tx_inner, nombre_nodo_padre_actual, nombre_curso):
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
    def sample_structure():
        """Retorna un diccionario con la estructura de ejemplo"""
        return [
            {
                "vocacion_nombre": "Ingeniería de Software", 
                "cursos_rama": [
                    {
                        "nombre": "Introducción al Desarrollo Web: HTML, CSS y JavaScript", 
                        "dificultad": "Principiante", 
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
                "vocacion_nombre": "Especialista en Ciberseguridad",
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
                "vocacion_nombre": "Diseño Gráfico",
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
                        "nombre": "Ilustración Digital y Concept Art para Videojuegos y Cine", 
                        "dificultad": "Intermedio" 
                    }
                ]
            },
            {
                "vocacion_nombre": "Marketing Digital",
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
                                "nombre": "Fundamentos del Diseño de Experiencia de Usuario (UX)", 
                                "dificultad": "Principiante"
                            }
                        ]
                    }
                ]
            },
            {
                "vocacion_nombre": "Aprender programación desde cero",
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
                        "nombre": "Desarrollo de Videojuegos 2D con Unity", 
                        "dificultad": "Principiante"
                    }
                ]
            },
            {
                "vocacion_nombre": "Desarrollo de Videojuegos Indie",
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
                        "nombre": "Animación 2D y 3D para Cine y Publicidad", 
                        "dificultad": "Intermedio" 
                    }
                ]
            },
            {
                "vocacion_nombre": "Ciencia de Datos",
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
                "vocacion_nombre": "Desarrollar un emprendimiento digital",
                "cursos_rama": [
                    {
                        "nombre": "Introducción al Desarrollo Web: HTML, CSS y JavaScript",
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
                        "nombre": "Cloud Computing con AWS: Fundamentos y Servicios Clave",
                        "dificultad": "Principiante"
                    }
                ]
            },
            {
                "vocacion_nombre": "Obtener una certificación internacional (como AWS o TOEFL)",
                "cursos_rama": [
                    {
                        "nombre": "Cloud Computing con AWS: Fundamentos y Servicios Clave",
                        "dificultad": "Principiante",
                        "siguientes": [
                            {
                                "nombre": "Certificación AWS Certified Solutions Architect - Associate",
                                "dificultad": "Intermedio"
                            },
                            {
                                "nombre": "Certificación TOEFL: Preparación y Estrategias",
                                "dificultad": "Todos los niveles"
                            }
                        ]
                    }
                    
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
        """
        
        """
if __name__ == "__main__":
    URI = "bolt://localhost:7687"
    USER = "neo4j"
    PASSWORD = "12345678"
    
    loader = Neo4jCourseLoader(URI, USER, PASSWORD)
    datos_para_carga_masiva_neo4j = Neo4jCourseLoader.sample_structure()
    try:
        if loader.driver:
            try:
                with loader.driver.session() as s:
                    s.run("CREATE CONSTRAINT vocacion_nombre_unique IF NOT EXISTS FOR (v:Vocacion) REQUIRE v.nombre IS UNIQUE")
                    s.run("CREATE CONSTRAINT curso_nombre_unique IF NOT EXISTS FOR (c:Curso) REQUIRE c.nombre IS UNIQUE")
                    print("Constraints de unicidad para Vocacion.nombre y Curso.nombre aseguradas.")
            except Exception as e_constraint:
                print(f"Advertencia al crear constraints (pueden ya existir o error de permisos): {e_constraint}")

            for vocacion_data in datos_para_carga_masiva_neo4j:
                print(f"\n--- Cargando Vocación: {vocacion_data['vocacion_nombre']} ---")
                resultado = loader.crear_vocacion_con_ramas_desde_dict(vocacion_data)
                if resultado:
                    print(f"Carga para '{vocacion_data['vocacion_nombre']}' completada con estado: {resultado.get('status')}")
                else:
                    print(f"Error al cargar la vocación: {vocacion_data['vocacion_nombre']}")
                    loader.close()
        else:
            print("No se pudo conectar a Neo4j para la carga masiva.")
        
    except Exception as e:
        print(f"Error al cargar la estructura: {e}")
    finally:
        loader.close()