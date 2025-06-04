from pymongo import MongoClient
from bson.objectid import ObjectId

class BiblioCRUD:
    def __init__(self):
        try:
            self.client = MongoClient("mongodb://admin:admin123@localhost:27017/")
            self.db = self.client["datos"]
            self.collection = self.db["bibliografias"]
            print(f"Conexión a MongoDB (datos) establecida.")
        except Exception as e:
            print(f"Error al conectar a MongoDB: {e}")
            return None
        


    def crear_bibliografia(self, titulo, autor, enlace, descripcion):
        bibliografia = {
            "titulo": titulo,
            "autor": autor,
            "enlace": enlace,
            "descripcion": descripcion
        }
        resultado = self.collection.insert_one(bibliografia)
        print(f"Bibliografía creada con ID: {resultado.inserted_id}")

    def leer_bibliografias(self):
        print("\nLista de bibliografías:")
        for biblio in self.collection.find():
            print(f"ID: {biblio['_id']} | Título: {biblio['titulo']} | Autor: {biblio['autor']} | Enlace: {biblio['enlace']}")

    def leer_bibliografias_por_titulos(self, lista_titulos):
        return list(self.collection.find(
        {"titulo": {"$in": lista_titulos}}
        ))

    def actualizar_bibliografia(self, id_biblio, nuevo_titulo=None, nuevo_autor=None, nuevo_enlace=None, nueva_descripcion=None):
        campos_a_actualizar = {}
        if nuevo_titulo:
            campos_a_actualizar["titulo"] = nuevo_titulo
        if nuevo_autor:
            campos_a_actualizar["autor"] = nuevo_autor
        if nuevo_enlace:
            campos_a_actualizar["enlace"] = nuevo_enlace
        if nueva_descripcion:
            campos_a_actualizar["descripcion"] = nueva_descripcion

        if campos_a_actualizar:
            resultado = self.collection.update_one(
                {"_id": ObjectId(id_biblio)},
                {"$set": campos_a_actualizar}
            )
            print("Bibliografía actualizada." if resultado.modified_count else "No se encontró la bibliografía.")
        else:
            print("No se proporcionaron campos para actualizar.")

    def eliminar_bibliografia(self, id_biblio):
        resultado = self.collection.delete_one({"_id": ObjectId(id_biblio)})
        print("Bibliografía eliminada." if resultado.deleted_count else "No se encontró la bibliografía.")

    @staticmethod
    def obtenerDiccionario():
        return {
            "principiantes": [
                {
                    "titulo": "Inteligencia Artificial: Una Introducción",
                    "autor": "John D. Kelleher, Brendan Tierney",
                    "enlace": "https://www.amazon.com/Inteligencia-Artificial-Introduccion-John-Kelleher/dp/8426727221",
                    "descripcion": "Un excelente punto de partida para quienes no tienen experiencia. Cubre los conceptos fundamentales de la IA, el aprendizaje automático, el procesamiento del lenguaje natural y la visión artificial de manera clara y concisa."
                },
                {
                    "titulo": "Superinteligencia: Caminos, Peligros, Estrategias",
                    "autor": "Nick Bostrom",
                    "enlace": "https://www.amazon.com/Superinteligencia-Caminos-Peligros-Estrategias-Spanish/dp/8499424785",
                    "descripcion": "Aunque no es un libro técnico, ofrece una visión crucial sobre el futuro de la IA y los desafíos éticos y existenciales que plantea. Ideal para comprender el panorama general y las implicaciones."
                },
                {
                    "titulo": "AI for Dummies",
                    "autor": "John Paul Mueller, Luca Massaron",
                    "enlace": "https://www.dummies.com/book/technology/artificial-intelligence/ai-for-dummies-282121/",
                    "descripcion": "Como todos los libros 'For Dummies', este ofrece una explicación sencilla y práctica de los conceptos de IA, con ejemplos accesibles y una curva de aprendizaje suave."
                }
            ],
            "intermedio": [
                {
                    "titulo": "Inteligencia Artificial: Un Enfoque Moderno",
                    "autor": "Stuart Russell, Peter Norvig",
                    "enlace": "https://www.amazon.com/Artificial-Intelligence-Modern-Approach-4th/dp/0134610997",
                    "descripcion": "Considerado la biblia de la IA. Es un libro de texto completo que abarca una amplia gama de temas, desde la búsqueda y la lógica hasta el aprendizaje automático y la robótica. Requiere cierta base en matemáticas y computación."
                },
                {
                    "titulo": "Aprendizaje Profundo",
                    "autor": "Ian Goodfellow, Yoshua Bengio, Aaron Courville",
                    "enlace": "https://www.deeplearningbook.org/",
                    "descripcion": "Un recurso fundamental para entender las redes neuronales profundas. Es un libro técnico que profundiza en la teoría y los algoritmos del deep learning. Es gratuito en línea."
                },
                {
                    "titulo": "The Hundred-Page Machine Learning Book",
                    "autor": "Andriy Burkov",
                    "enlace": "https://theMLbook.com/",
                    "descripcion": "Un libro conciso que condensa los conceptos esenciales del aprendizaje automático en solo 100 páginas. Ideal para consolidar conocimientos intermedios y como referencia rápida."
                }
            ],
            "avanzado": [
                {
                    "titulo": "Pattern Recognition and Machine Learning",
                    "autor": "Christopher M. Bishop",
                    "enlace": "https://www.microsoft.com/en-us/research/people/cmbishop/prml-book/",
                    "descripcion": "Un clásico para quienes buscan una comprensión profunda de los principios estadísticos y matemáticos detrás del aprendizaje automático y el reconocimiento de patrones. Muy riguroso y completo."
                },
                {
                    "titulo": "Reinforcement Learning: An Introduction",
                    "autor": "Richard S. Sutton, Andrew G. Barto",
                    "enlace": "https://www.incompleteideas.net/book/the-book-2nd.html",
                    "descripcion": "El texto definitivo sobre el aprendizaje por refuerzo. Cubre desde los fundamentos hasta algoritmos avanzados. Es esencial para aquellos interesados en sistemas de toma de decisiones autónomos y agentes inteligentes. Versión en línea gratuita."
                },
                {
                    "titulo": "Probabilistic Graphical Models: Principles and Techniques",
                    "autor": "Daphne Koller, Nir Friedman",
                    "enlace": "https://www.cs.princeton.edu/courses/archive/fall09/cos424/PMBook/PGM-V2-0-notes.pdf",
                    "descripcion": "Un tratado exhaustivo sobre los modelos gráficos probabilísticos, esenciales para entender cómo los sistemas de IA manejan la incertidumbre y las relaciones complejas entre variables. Requiere una fuerte base en probabilidad y estadística."
                }
            ]
        }

    def cargar_bibliografias_desde_diccionario(self):
        print("\nCargando bibliografías desde el diccionario...")
        diccionario_biblios = self.obtenerDiccionario()
        for categoria, biblios_lista in diccionario_biblios.items():
            print(f"Cargando categoría: {categoria}")
            for biblio_data in biblios_lista:
                existente = self.collection.find_one({"titulo": biblio_data["titulo"], "autor": biblio_data["autor"]})
                if existente:
                    print(f"Bibliografía '{biblio_data['titulo']}' ya existe. Omitiendo.")
                    continue
                
                self.crear_bibliografia(
                    titulo=biblio_data["titulo"],
                    autor=biblio_data["autor"],
                    enlace=biblio_data["enlace"],
                    descripcion=biblio_data["descripcion"]
                )
        print("Carga de bibliografías desde el diccionario completada.")


# Ejemplo de uso
if __name__ == "__main__":
    # Crear una nueva bibliografía manualmente (opcional, puedes comentarlo)
    # crear_bibliografia("Título de ejemplo", "Autor de ejemplo", "http://ejemplo.com", "Descripción de ejemplo")
    db_conn = BiblioCRUD()
    # Cargar bibliografías desde el diccionario
    #db_conn.cargar_bibliografias_desde_diccionario()

    # Leer todas las bibliografías
    db_conn.leer_bibliografias()

    # Actualizar una bibliografía (reemplaza 'ID_DE_EJEMPLO' con un ID real)
    # Deberás obtener un ID válido de la salida de leer_bibliografias()
    # Ejemplo: si una bibliografía tiene ID "60abc123def456ghi789", usa ese ID.
    # id_para_actualizar = "PON_UN_ID_VALIDO_AQUI" 
    # if id_para_actualizar != "PON_UN_ID_VALIDO_AQUI": # Solo ejecutar si se ha cambiado el ID placeholder
    #     actualizar_bibliografia(id_para_actualizar, nuevo_titulo="Nuevo Título Actualizado")
    # else:
    #     print("\nPara actualizar, primero descomenta y reemplaza 'PON_UN_ID_VALIDO_AQUI' con un ID real de tu base de datos.")


    # Eliminar una bibliografía (reemplaza 'ID_DE_EJEMPLO' con un ID real)
    # id_para_eliminar = "PON_UN_ID_VALIDO_AQUI"
    # if id_para_eliminar != "PON_UN_ID_VALIDO_AQUI": # Solo ejecutar si se ha cambiado el ID placeholder
    #     eliminar_bibliografia(id_para_eliminar)
    # else:
    #     print("\nPara eliminar, primero descomenta y reemplaza 'PON_UN_ID_VALIDO_AQUI' con un ID real de tu base de datos.")