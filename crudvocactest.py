from pymongo import MongoClient
from bson.objectid import ObjectId

# Configuración de la conexión a MongoDB
# Asegúrate de que MongoDB esté corriendo y accesible.
# Modifica la URI de conexión si es necesario (usuario, contraseña, host, puerto).
conexion = "mongodb://admin:admin123@localhost:27017/"
datos = "datos"
coleccion = "vocaciones"

def conectar_db():
    """Establece conexión con la base de datos MongoDB."""
    try:
        client = MongoClient(conexion)
        client.admin.command('ping')  # Verificar la conexión
        db = client[datos]
        print(f"Conexión a MongoDB ('{datos}') exitosa.")
        return db
    except Exception as e:
        print(f"Error al conectar a MongoDB: {e}")
        return None

def crear_vocacion(db, nombre_vocacion, categorias_vocacion):
    """
    Crea una nueva vocación en la base de datos.
    :param db: Objeto de la base de datos MongoDB.
    :param nombre_vocacion: String, el nombre de la vocación.
    :param categorias_vocacion: Lista de strings, las categorías asociadas.
    :return: El ID del documento insertado o None si hay error.
    """
    if db is None: # Modificado aquí
        print("Error: No hay conexión a la base de datos.")
        return None
    if not nombre_vocacion or not isinstance(nombre_vocacion, str):
        print("Error: El nombre de la vocación es requerido y debe ser un string.")
        return None
    if not isinstance(categorias_vocacion, list) or not all(isinstance(cat, str) for cat in categorias_vocacion):
        print("Error: Las categorías deben ser una lista de strings.")
        return None

    # Verificar si la vocación ya existe por nombre
    if db[coleccion].find_one({"nombre": nombre_vocacion}):
        print(f"Error: La vocación '{nombre_vocacion}' ya existe.")
        return None

    vocacion_doc = {
        "nombre": nombre_vocacion,
        "categorias": categorias_vocacion
    }
    try:
        resultado = db[coleccion].insert_one(vocacion_doc)
        print(f"Vocación '{nombre_vocacion}' creada con ID: {resultado.inserted_id}")
        return resultado.inserted_id
    except Exception as e:
        print(f"Error al crear la vocación '{nombre_vocacion}': {e}")
        return None

def leer_vocaciones(db, filtro=None):
    """
    Lee y muestra las vocaciones de la base de datos.
    :param db: Objeto de la base de datos MongoDB.
    :param filtro: Diccionario opcional para filtrar los resultados (ej: {"nombre": "Tecnología"}).
    """
    if db is None: # Modificado aquí
        print("Error: No hay conexión a la base de datos.")
        return

    if filtro is None:
        filtro = {}
    
    print("\n--- Lista de Vocaciones ---")
    vocaciones_encontradas = list(db[coleccion].find(filtro))
    
    if not vocaciones_encontradas:
        print("No se encontraron vocaciones que coincidan con el filtro o la colección está vacía.")
        return

    for vocacion in vocaciones_encontradas:
        print(f"  ID MongoDB: {vocacion['_id']}")
        print(f"  Nombre: {vocacion['nombre']}")
        print(f"  Categorías: {', '.join(vocacion['categorias']) if vocacion['categorias'] else 'Ninguna'}")
        print("-" * 20)

def actualizar_vocacion(db, id_vocacion_mongo, datos_para_actualizar):
    """
    Actualiza una vocación existente en la base de datos.
    :param db: Objeto de la base de datos MongoDB.
    :param id_vocacion_mongo: String o ObjectId, el _id de la vocación a actualizar.
    :param datos_para_actualizar: Diccionario con los campos y nuevos valores.
                                  Ej: {"nombre": "Nuevo Nombre", "categorias": ["CatNueva1"]}
    :return: True si la actualización fue exitosa (o no se necesitaron cambios), False si hubo un error.
    """
    if db is None: # Modificado aquí
        print("Error: No hay conexión a la base de datos.")
        return False

    try:
        obj_id = ObjectId(id_vocacion_mongo)
    except Exception:
        print(f"Error: El ID de vocación '{id_vocacion_mongo}' no es un ObjectId válido.")
        return False
    
    if not datos_para_actualizar or not isinstance(datos_para_actualizar, dict):
        print("Error: No se proporcionaron datos válidos para actualizar o el formato es incorrecto.")
        return False

    # Opcional: Validar que el nuevo nombre no exista ya en otra vocación (si el nombre es único)
    if "nombre" in datos_para_actualizar:
        vocacion_existente = db[coleccion].find_one({
            "nombre": datos_para_actualizar["nombre"],
            "_id": {"$ne": obj_id} # Excluir el documento actual de la búsqueda
        })
        if vocacion_existente:
            print(f"Error: Ya existe otra vocación con el nombre '{datos_para_actualizar['nombre']}'.")
            return False
            
    try:
        resultado = db[coleccion].update_one(
            {"_id": obj_id},
            {"$set": datos_para_actualizar}
        )
        if resultado.matched_count == 0:
            print(f"No se encontró ninguna vocación con ID: {id_vocacion_mongo}")
            return False
        if resultado.modified_count > 0:
            print(f"Vocación con ID {id_vocacion_mongo} actualizada exitosamente.")
            return True
        else:
            print(f"Vocación con ID {id_vocacion_mongo} encontrada, pero no se realizaron modificaciones (los datos podrían ser los mismos).")
            return True
    except Exception as e:
        print(f"Error al actualizar la vocación con ID {id_vocacion_mongo}: {e}")
        return False

def eliminar_vocacion(db, id_vocacion_mongo):
    """
    Elimina una vocación de la base de datos por su _id de MongoDB.
    :param db: Objeto de la base de datos MongoDB.
    :param id_vocacion_mongo: String o ObjectId, el _id de la vocación a eliminar.
    :return: True si la eliminación fue exitosa, False en caso contrario.
    """
    if db is None: # Modificado aquí
        print("Error: No hay conexión a la base de datos.")
        return False

    try:
        obj_id = ObjectId(id_vocacion_mongo)
    except Exception:
        print(f"Error: El ID de vocación '{id_vocacion_mongo}' no es un ObjectId válido.")
        return False
        
    try:
        resultado = db[coleccion].delete_one({"_id": obj_id})
        if resultado.deleted_count > 0:
            print(f"Vocación con ID {id_vocacion_mongo} eliminada exitosamente.")
            return True
        else:
            print(f"No se encontró ninguna vocación con ID {id_vocacion_mongo} para eliminar.")
            return False
    except Exception as e:
        print(f"Error al eliminar la vocación con ID {id_vocacion_mongo}: {e}")
        return False

def obtener_vocaciones_para_dropdown():
    """
    Obtiene una lista de nombres de vocaciones para usar en un dropdown.
    :return: Lista de strings con los nombres de las vocaciones.
    """
    cliaux = MongoClient(conexion)
    dbaux = cliaux[datos]
    if dbaux is None:
        return []
    try:
        lista_vocaciones = [doc["nombre"] for doc in dbaux[coleccion].find({}, {"nombre": 1}).sort("nombre", 1)]
        return lista_vocaciones
    except Exception as e:
        print(f"Error al obtener nombres de vocaciones: {e}")
        dbaux.client.close()
        return []

# --- Ejemplo de Uso ---
if __name__ == "__main__":
    db_conn = conectar_db()

    if db_conn is not None: # Modificado aquí
        print("\n--- DEMO CRUD VOCACIONES ---")
        """
        # 1. Crear nuevas vocaciones
        print("\n1. Creando vocaciones...")
        id_voc1 = crear_vocacion(db_conn, "Ciencia de Datos", ["Tecnología", "Ciencia", "Informática"])
        
        id_voc2 = crear_vocacion(db_conn, "Diseño Gráfico", ["Creatividad", "Arte Digital", "Comunicación Visual"])
        id_voc3 = crear_vocacion(db_conn, "Medicina", ["Salud", "Ciencia", "Cuidado Humano"])
        crear_vocacion(db_conn, "Marketing Digital", ["Negocios", "Tecnología", "Comunicación"]) # Para probar duplicado
        crear_vocacion(db_conn, "Ingeniería de Software", ["Tecnología"]) # Intentar crear duplicado por nombre
        
        # 2. Leer todas las vocaciones
        leer_vocaciones(db_conn)
        
        # 3. Actualizar una vocación (si se creó)
        if id_voc2: # Si la vocación "Diseño Gráfico" se creó correctamente
            print(f"\n3. Actualizando vocación con ID: {id_voc2}...")
            actualizar_vocacion(db_conn, id_voc2, 
                                {"nombre": "Diseño UX/UI", "categorias": ["Tecnología", "Diseño de Interacción", "Experiencia de Usuario"]})
            leer_vocaciones(db_conn, {"_id": ObjectId(id_voc2)}) # Leer solo la vocación actualizada

        # Intentar actualizar con nombre duplicado
        if id_voc1 and id_voc3:
             print(f"\nIntentando actualizar vocación ID {id_voc3} con nombre de ID {id_voc1}...")
             actualizar_vocacion(db_conn, id_voc3, {"nombre": "Ingeniería de Software"})


        # 4. Eliminar una vocación (si se creó)
        if id_voc3: # Si la vocación "Medicina" (o su nombre actualizado) se creó
            voc_medicina = db_conn[coleccion].find_one({"_id": ObjectId(id_voc3)})
            if voc_medicina: # Modificado aquí para verificar si voc_medicina no es None
                 print(f"\n4. Eliminando vocación '{voc_medicina['nombre']}' (ID: {id_voc3})...")
                 eliminar_vocacion(db_conn, id_voc3)
                 leer_vocaciones(db_conn) # Mostrar lista actualizada
            else: 
                 print(f"La vocación con ID original {id_voc3} ya no existe o fue modificada y eliminada.")

        """
        # 5. Obtener lista para dropdown (ejemplo de uso)
        print("\n5. Nombres de vocaciones para un dropdown:")
        lista_nombres = obtener_vocaciones_para_dropdown()
        if lista_nombres: # Se puede mantener así, ya que es una lista
            for nombre_voc in lista_nombres:
                print(f" - {nombre_voc}")
        else:
            print("No hay vocaciones para mostrar en el dropdown.")
            
        # Cerrar la conexión al finalizar (opcional, depende de la gestión de la app)
        # if db_conn.client is not None: # Verificar si client no es None antes de cerrar
        #     db_conn.client.close()
        #     print("\nConexión a MongoDB cerrada.")
    else:
        print("No se pudo ejecutar la demostración del CRUD de vocaciones debido a un error de conexión.")

