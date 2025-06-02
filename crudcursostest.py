from pymongo import MongoClient
from bson.objectid import ObjectId

# Conexión a MongoDB local
try:
    cli = MongoClient("mongodb://admin:admin123@localhost:27017/")
    cli.admin.command('ping')
    print("Conexión a MongoDB exitosa.")
except Exception as e:
    print(f"No se pudo conectar a MongoDB: {e}")
    exit()

db = cli["datos"]
coleccion_cursos = db["cursos"]

def crear_curso(id_neo4j, nombre, descripcion, nivel, temas, prerrequisitos, enciclopedia_desbloqueada):
    """Crea un nuevo curso en la base de datos."""
    # Validación básica de campos
    if not all([id_neo4j, nombre, descripcion, nivel, enciclopedia_desbloqueada]):
        print("Error: Los campos 'id_neo4j', 'nombre', 'descripcion', 'nivel' y 'enciclopedia_desbloqueada' son requeridos.")
        return None
    if not isinstance(temas, list):
        print("Error: 'temas' debe ser una lista.")
        return None
    if not isinstance(prerrequisitos, list):
        print("Error: 'prerrequisitos' debe ser una lista.")
        return None

    curso = {
        "id_neo4j": id_neo4j,
        "nombre": nombre,
        "descripcion": descripcion,
        "nivel": nivel,
        "temas": temas,  # Debe ser una lista de strings
        "prerrequisitos": prerrequisitos,  # Debe ser una lista de strings
        "enciclopedia_desbloqueada": enciclopedia_desbloqueada
    }
    try:
        resultado = coleccion_cursos.insert_one(curso)
        print(f"Curso '{nombre}' creado con ID MongoDB: {resultado.inserted_id}")
        return resultado.inserted_id
    except Exception as e:
        print(f"Error al crear curso '{nombre}': {e}")
        return None

def leer_cursos():
    """Lee y muestra todos los cursos de la base de datos."""
    print("\n--- Lista de Cursos ---")
    if coleccion_cursos.count_documents({}) == 0:
        print("No hay cursos para mostrar.")
        return
    for curso in coleccion_cursos.find():
        print(f"  ID MongoDB: {curso['_id']}")
        print(f"  ID Neo4j: {curso['id_neo4j']}")
        print(f"  Nombre: {curso['nombre']}")
        print(f"  Descripción: {curso['descripcion']}")
        print(f"  Nivel: {curso['nivel']}")
        print(f"  Temas: {', '.join(curso['temas']) if curso['temas'] else 'Ninguno'}")
        print(f"  Prerrequisitos: {', '.join(curso['prerrequisitos']) if curso['prerrequisitos'] else 'Ninguno'}")
        print(f"  Enciclopedia Desbloqueada: {curso['enciclopedia_desbloqueada']}")
        print("-" * 20)

def actualizar_curso(id_curso_mongo, datos_para_actualizar):

    if not ObjectId.is_valid(id_curso_mongo):
        print(f"Error: El ID de curso '{id_curso_mongo}' no es válido.")
        return False
    
    if not datos_para_actualizar:
        print("Error: No se proporcionaron datos para actualizar.")
        return False

    try:
        resultado = coleccion_cursos.update_one(
            {"_id": ObjectId(id_curso_mongo)},
            {"$set": datos_para_actualizar}
        )
        if resultado.matched_count == 0:
            print(f"No se encontró ningún curso con ID: {id_curso_mongo}")
            return False
        if resultado.modified_count > 0:
            print(f"Curso con ID {id_curso_mongo} actualizado exitosamente.")
            return True
        else:
            print(f"Curso con ID {id_curso_mongo} encontrado, pero no se realizaron modificaciones (los datos podrían ser los mismos).")
            return True # Consideramos éxito si se encontró aunque no haya cambios.
    except Exception as e:
        print(f"Error al actualizar curso con ID {id_curso_mongo}: {e}")
        return False

def eliminar_curso(id_curso_mongo):
   
    if not ObjectId.is_valid(id_curso_mongo):
        print(f"Error: El ID de curso '{id_curso_mongo}' no es válido.")
        return False
    try:
        resultado = coleccion_cursos.delete_one({"_id": ObjectId(id_curso_mongo)})
        if resultado.deleted_count > 0:
            print(f"Curso con ID {id_curso_mongo} eliminado exitosamente.")
            return True
        else:
            print(f"No se encontró ningún curso con ID {id_curso_mongo} para eliminar.")
            return False
    except Exception as e:
        print(f"Error al eliminar curso con ID {id_curso_mongo}: {e}")
        return False

@staticmethod
def obtenerDiccionarioCursos():
    """Retorna un diccionario con datos de ejemplo para cursos."""
    return {
        "cursos_ia_machine_learning": [
            {
                "id_neo4j": "PYAI001",
                "nombre": "Python Esencial para Inteligencia Artificial",
                "descripcion": "Domina Python y sus librerías clave (NumPy, Pandas, Matplotlib, Scikit-learn) para construir proyectos de IA y Ciencia de Datos.",
                "nivel": "Principiante",
                "temas": ["Sintaxis Avanzada de Python", "Programación Orientada a Objetos en Python", "Manipulación de Datos con Pandas", "Visualización con Matplotlib y Seaborn", "Introducción a Scikit-learn para ML"],
                "prerrequisitos": [],
                "enciclopedia_desbloqueada": "Python_IA_Avanzado"
            },
            {
                "id_neo4j": "MLBASICO002",
                "nombre": "Machine Learning: De Cero a Práctico",
                "descripcion": "Una introducción completa a los conceptos fundamentales del Machine Learning, algoritmos supervisados y no supervisados, y evaluación de modelos con ejemplos prácticos.",
                "nivel": "Principiante",
                "temas": ["Aprendizaje Supervisado (Regresión Lineal, Logística, Árboles de Decisión, SVM)", "Aprendizaje No Supervisado (K-Means, Agrupamiento Jerárquico, PCA)", "Ingeniería de Características", "Validación Cruzada", "Métricas de Desempeño de Modelos"],
                "prerrequisitos": ["PYAI001"],
                "enciclopedia_desbloqueada": "MachineLearning_Modelos_Fundamentales"
            },
            {
                "id_neo4j": "DLINTER003",
                "nombre": "Deep Learning Aplicado con TensorFlow y Keras",
                "descripcion": "Construye y entrena redes neuronales profundas para tareas complejas. Aprende sobre arquitecturas como CNNs y RNNs.",
                "nivel": "Intermedio",
                "temas": ["Redes Neuronales Densas", "Optimización y Regularización", "TensorFlow y Keras API a Fondo", "Redes Neuronales Convolucionales (CNN) para Visión", "Redes Neuronales Recurrentes (RNN) para Secuencias", "Transfer Learning"],
                "prerrequisitos": ["MLBASICO002", "Conocimientos de Álgebra Lineal y Cálculo"],
                "enciclopedia_desbloqueada": "DeepLearning_Arquitecturas_Modernas"
            },
            {
                "id_neo4j": "NLPINTRO004",
                "nombre": "Procesamiento del Lenguaje Natural (PLN) con Python",
                "descripcion": "Aprende a procesar, analizar y entender el lenguaje humano con Python, NLTK y spaCy. Crea aplicaciones como análisis de sentimientos y chatbots básicos.",
                "nivel": "Intermedio",
                "temas": ["Preprocesamiento de Texto (Tokenización, Lematización, Stemming)", "Análisis de Sentimientos", "Modelos de Bolsa de Palabras (BoW)", "TF-IDF", "Word Embeddings (Word2Vec, GloVe)", "Clasificación de Texto", "Introducción a Transformers (BERT básico)"],
                "prerrequisitos": ["MLBASICO002", "PYAI001"],
                "enciclopedia_desbloqueada": "PLN_Modelado_Texto"
            },
            {
                "id_neo4j": "CVANZADO005",
                "nombre": "Visión por Computadora: Detección y Segmentación",
                "descripcion": "Explora técnicas avanzadas en Visión por Computadora, incluyendo detección de objetos en tiempo real y segmentación de imágenes con modelos pre-entrenados.",
                "nivel": "Avanzado",
                "temas": ["Fundamentos de Procesamiento de Imágenes", "Detección de Objetos (YOLO, SSD, Faster R-CNN)", "Segmentación Semántica e Instanciada (U-Net, Mask R-CNN)", "Generación de Imágenes con GANs", "Aplicaciones de Visión por Computadora en la Industria"],
                "prerrequisitos": ["DLINTER003"],
                "enciclopedia_desbloqueada": "VisionComputadora_Deteccion_Objetos"
            },
            {
                "id_neo4j": "RLINTRO006",
                "nombre": "Introducción al Aprendizaje por Refuerzo (RL)",
                "descripcion": "Descubre los principios del Aprendizaje por Refuerzo y cómo los agentes aprenden a tomar decisiones óptimas en entornos complejos.",
                "nivel": "Intermedio",
                "temas": ["Procesos de Decisión de Markov (MDP)", "Funciones de Valor y Políticas", "Q-Learning", "SARSA", "Deep Q-Networks (DQN) básico", "Entornos de RL (Gymnasium)"],
                "prerrequisitos": ["MLBASICO002", "Buenas bases de probabilidad"],
                "enciclopedia_desbloqueada": "Aprendizaje_Refuerzo_Principios"
            },
            {
                "id_neo4j": "TIMESERIES007",
                "nombre": "Análisis y Predicción de Series Temporales",
                "descripcion": "Aprende a analizar datos secuenciales en el tiempo y a construir modelos para predecir valores futuros utilizando técnicas estadísticas y de Machine Learning.",
                "nivel": "Intermedio",
                "temas": ["Componentes de Series Temporales", "Suavizado Exponencial", "Modelos ARIMA/SARIMA", "Machine Learning para Series Temporales (Regresión, Random Forest)", "Deep Learning para Series Temporales (LSTM, GRU)"],
                "prerrequisitos": ["MLBASICO002"],
                "enciclopedia_desbloqueada": "Series_Temporales_Modelado"
            },
            {
                "id_neo4j": "MLOPS008",
                "nombre": "MLOps: Despliegue y Mantenimiento de Modelos de ML",
                "descripcion": "Cubre el ciclo de vida completo de los modelos de Machine Learning, desde el desarrollo hasta el despliegue, monitoreo y mantenimiento en producción.",
                "nivel": "Avanzado",
                "temas": ["Contenerización con Docker", "Orquestación con Kubernetes (básico)", "CI/CD para ML", "Monitoreo de Modelos", "Versionado de Datos y Modelos (DVC, MLflow)", "Infraestructura Cloud para ML (AWS SageMaker, Google Vertex AI - conceptual)"],
                "prerrequisitos": ["DLINTER003", "Conocimientos de desarrollo de software"],
                "enciclopedia_desbloqueada": "MLOps_Ciclo_Vida_ML"
            },
            {
                "id_neo4j": "BIGDATAIA009",
                "nombre": "Big Data e Inteligencia Artificial con Spark",
                "descripcion": "Aprende a procesar grandes volúmenes de datos y aplicar algoritmos de Machine Learning utilizando Apache Spark y su librería MLlib.",
                "nivel": "Avanzado",
                "temas": ["Ecosistema Hadoop y Spark", "RDDs y DataFrames en Spark", "Spark SQL", "MLlib: Algoritmos de Clasificación y Regresión", "Procesamiento de Datos en Streaming con Spark", "Optimización de Jobs en Spark"],
                "prerrequisitos": ["PYAI001", "Conocimientos de SQL", "MLBASICO002"],
                "enciclopedia_desbloqueada": "BigData_Spark_ML"
            },
            {
                "id_neo4j": "ETICAIA010",
                "nombre": "Ética y Responsabilidad en Inteligencia Artificial",
                "descripcion": "Analiza las implicaciones éticas, legales y sociales de la IA. Discute temas como sesgos, privacidad, transparencia y el futuro del trabajo.",
                "nivel": "Todos los niveles",
                "temas": ["Sesgos en Algoritmos", "Privacidad y Protección de Datos", "IA Explicable (XAI)", "Responsabilidad y Rendición de Cuentas en IA", "Impacto Social de la IA", "Regulaciones y Políticas de IA"],
                "prerrequisitos": [],
                "enciclopedia_desbloqueada": "Etica_IA_Desafios"
            },
            {
                "id_neo4j": "IAEXPLICABLE011",
                "nombre": "Inteligencia Artificial Explicable (XAI)",
                "descripcion": "Comprende y aplica técnicas para hacer que los modelos de Machine Learning, especialmente los de Deep Learning, sean más interpretables y transparentes.",
                "nivel": "Avanzado",
                "temas": ["Importancia de la XAI", "Métodos Agnósticos al Modelo (LIME, SHAP)", "Métodos Específicos del Modelo (Attention, Grad-CAM)", "Interpretabilidad vs. Precisión", "Evaluación de Explicaciones"],
                "prerrequisitos": ["DLINTER003"],
                "enciclopedia_desbloqueada": "XAI_Tecnicas_Interpretabilidad"
            },
            {
                "id_neo4j": "IAGEN012",
                "nombre": "Inteligencia Artificial Generativa",
                "descripcion": "Explora el fascinante mundo de la IA que puede crear contenido nuevo, desde texto e imágenes hasta música y código. Incluye modelos como GANs y Transformers.",
                "nivel": "Avanzado",
                "temas": ["Generative Adversarial Networks (GANs) a fondo", "Variational Autoencoders (VAEs)", "Modelos de Difusión", "Modelos de Lenguaje Grandes (LLMs) y Prompt Engineering", "Aplicaciones de IA Generativa"],
                "prerrequisitos": ["DLINTER003", "NLPINTRO004"],
                "enciclopedia_desbloqueada": "IA_Generativa_Modelos"
            },
            {
                "id_neo4j": "ROBOTICAIA013",
                "nombre": "Robótica e Inteligencia Artificial",
                "descripcion": "Aprende cómo la IA potencia a los robots modernos, desde la percepción y la planificación de movimientos hasta la interacción con humanos.",
                "nivel": "Avanzado",
                "temas": ["Cinemática y Dinámica de Robots", "Percepción Robótica (Visión, LiDAR)", "Planificación de Rutas", "Control Robótico", "Aprendizaje por Refuerzo para Robots", "Interacción Humano-Robot (HRI)"],
                "prerrequisitos": ["RLINTRO006", "Conocimientos de física y matemáticas"],
                "enciclopedia_desbloqueada": "Robotica_IA_Integracion"
            },
             {
                "id_neo4j": "QUANTUMML014",
                "nombre": "Computación Cuántica para Machine Learning",
                "descripcion": "Una introducción a los principios de la computación cuántica y cómo podría revolucionar los algoritmos de Machine Learning.",
                "nivel": "Avanzado (Investigación)",
                "temas": ["Fundamentos de Mecánica Cuántica", "Qubits y Compuertas Cuánticas", "Algoritmos Cuánticos (Shor, Grover)", "Machine Learning Cuántico (QSVM, QPCA)", "Plataformas de Programación Cuántica (Qiskit, Cirq)"],
                "prerrequisitos": ["DLINTER003", "Física Cuántica básica", "Álgebra Lineal Avanzada"],
                "enciclopedia_desbloqueada": "Computacion_Cuantica_ML"
            },
            {
                "id_neo4j": "BIOINFOIA015",
                "nombre": "Bioinformática e IA: Análisis Genómico",
                "descripcion": "Aplica técnicas de IA y Machine Learning para analizar datos biológicos complejos, con un enfoque en la genómica y el descubrimiento de fármacos.",
                "nivel": "Avanzado",
                "temas": ["Secuenciación de ADN y ARN", "Análisis de Expresión Génica", "Predicción de Estructura de Proteínas (AlphaFold)", "Descubrimiento de Fármacos Asistido por IA", "Medicina Personalizada"],
                "prerrequisitos": ["MLBASICO002", "Conocimientos de biología molecular"],
                "enciclopedia_desbloqueada": "Bioinformatica_Genomica_IA"
            }
        ]
    }

def cargar_cursos_desde_diccionario():

    print("\nCargando cursos desde el diccionario...")
    diccionario_cursos_data = obtenerDiccionarioCursos()
    count_agregados = 0
    count_omitidos = 0
    for categoria_cursos, cursos_lista in diccionario_cursos_data.items():
        print(f"  Cargando categoría de cursos: {categoria_cursos}")
        for curso_data in cursos_lista:
            # Verificar si el curso ya existe por id_neo4j para no duplicarlo
            existente = coleccion_cursos.find_one({"id_neo4j": curso_data["id_neo4j"]})
            if existente:
                print(f"    Curso '{curso_data['nombre']}' (ID Neo4j: {curso_data['id_neo4j']}) ya existe. Omitiendo.")
                count_omitidos += 1
                continue
            
            crear_curso(
                id_neo4j=curso_data["id_neo4j"],
                nombre=curso_data["nombre"],
                descripcion=curso_data["descripcion"],
                nivel=curso_data["nivel"],
                temas=curso_data["temas"],
                prerrequisitos=curso_data["prerrequisitos"],
                enciclopedia_desbloqueada=curso_data["enciclopedia_desbloqueada"]
            )
            count_agregados += 1
    print(f"Carga de cursos completada. Agregados: {count_agregados}, Omitidos (ya existían): {count_omitidos}.")

# --- Ejemplo de uso ---
if __name__ == "__main__":

    print("=========================================")
    
    # 1. Cargar cursos desde el diccionario de ejemplo
    cargar_cursos_desde_diccionario()

    # 2. Leer todos los cursos
    leer_cursos()
    """
    # 3. Crear un nuevo curso (ejemplo adicional)
    print("\nIntentando crear un curso adicional...")
    id_nuevo_curso_mongo = crear_curso(
        id_neo4j="FINANZASIA016",
        nombre="IA Aplicada a Finanzas (FinTech)",
        descripcion="Descubre cómo la IA está transformando el sector financiero, desde el trading algorítmico hasta la detección de fraude.",
        nivel="Intermedio",
        temas=["Trading Algorítmico", "Análisis de Riesgo Crediticio con ML", "Detección de Fraude", "Robo-Advisors", "Blockchain y Criptomonedas (introducción)"],
        prerrequisitos=["MLBASICO002", "Conocimientos básicos de finanzas"],
        enciclopedia_desbloqueada="FinTech_IA_Aplicaciones"
    )
    if id_nuevo_curso_mongo:
        print(f"Curso de FinTech creado con ID MongoDB: {id_nuevo_curso_mongo}")
        # leer_cursos() # Opcional: Mostrar lista actualizada inmediatamente

    # 4. Actualizar un curso
    # Busquemos el curso de "Python Esencial para Inteligencia Artificial" por su id_neo4j
    print("\nIntentando actualizar un curso...")
    curso_py_ia = coleccion_cursos.find_one({"id_neo4j": "PYAI001"})
    if curso_py_ia:
        id_mongo_curso_py = curso_py_ia['_id']
        print(f"Actualizando el curso '{curso_py_ia['nombre']}' (ID MongoDB: {id_mongo_curso_py})")
        actualizar_curso(
            id_mongo_curso_py,
            {
                "descripcion": "Curso integral de Python para IA, Ciencia de Datos y Desarrollo Backend, con nuevos módulos de APIs y despliegue.",
                "temas": curso_py_ia["temas"] + ["Desarrollo de APIs con Flask/FastAPI", "Introducción a Docker para despliegue"] 
            }
        )
        # leer_cursos() # Opcional: Mostrar lista actualizada inmediatamente
    else:
        print("No se encontró el curso con id_neo4j 'PYAI001' para actualizar.")

    # 5. Eliminar un curso
    # Eliminemos el curso de FinTech que creamos (si se creó)
    print("\nIntentando eliminar un curso...")
    if id_nuevo_curso_mongo: # Usamos el ID que retornó crear_curso
        eliminar_curso(id_nuevo_curso_mongo)
        # leer_cursos() # Opcional: Mostrar lista actualizada inmediatamente
    else:
        curso_fintech_a_eliminar = coleccion_cursos.find_one({"id_neo4j": "FINANZASIA016"})
        if curso_fintech_a_eliminar:
            eliminar_curso(curso_fintech_a_eliminar['_id'])
            # leer_cursos() # Opcional: Mostrar lista actualizada inmediatamente
        else:
            print("No se encontró el curso de FinTech para eliminar (quizás no se creó o ya fue eliminado).")
    
    print("\n--- Lista final de Cursos (después de operaciones) ---")
    leer_cursos()
    """
    print("\n--- Fin del script de demostración ---")

