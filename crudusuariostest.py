from pymongo import MongoClient
from bson.objectid import ObjectId
from datetime import datetime, date
import bcrypt 

COLLECTION_NAME_USUARIOS = "usuarios" 
COLLECTION_NAME_VOCACIONES = "vocaciones" 
class UsuariosCRUD:
    def __init__(self):
        try:
            self.client = MongoClient("mongodb://admin:admin123@localhost:27017/")
            self.db = self.client["datos"]
            print(f"Conexión a MongoDB (datos) establecida.")
        except Exception as e:
            print(f"Error al conectar a MongoDB: {e}")
            return None
    
    # --- Funciones Auxiliares (reutilizadas o adaptadas) ---
    def hashear_password(self, password_texto_plano):
        try:
            salt = bcrypt.gensalt()
            hashed_pw = bcrypt.hashpw(password_texto_plano.encode('utf-8'), salt)
            return hashed_pw 
        except Exception as e:
            print(f"Error al hashear la contraseña: {e}")
            return None
    
    def calcular_edad(self, fecha_nacimiento_dt):
        if not isinstance(fecha_nacimiento_dt, (date, datetime)):
            raise ValueError("fecha_nacimiento_dt debe ser un objeto date o datetime.")
        hoy = datetime.today()
        if isinstance(fecha_nacimiento_dt, datetime):
            fecha_nacimiento_dt = fecha_nacimiento_dt.date()
            
        edad = hoy.year - fecha_nacimiento_dt.year - ((hoy.month, hoy.day) < (fecha_nacimiento_dt.month, fecha_nacimiento_dt.day))
        return edad

    def validar_vocacion_existente(self, nombre_vocacion):
        """Verifica si una vocación existe en la colección de vocaciones."""
        if self.db is None:
            return False
        if self.db[COLLECTION_NAME_VOCACIONES].find_one({"nombre": nombre_vocacion}):
            return True
        return False

    # --- CRUD Usuarios ---

    def crear_usuario(self, username, password_plano, fecha_nacimiento, vocacion, progreso=None):
        """
        Crea un nuevo usuario en la base de datos.
        :param self.db: Objeto de la base de datos MongoDB.
        :param username: String, nombre de usuario (debe ser único).
        :param password_plano: String, contraseña en texto plano.
        :param fecha_nacimiento: Objeto date o datetime para la fecha de nacimiento.
        :param vocacion: String, nombre de la vocación del usuario.
        :param progreso: Lista opcional de strings (IDs de cursos, etc.).
        :return: El ID del documento insertado o None si hay error.
        """
        if self.db is None:
            print("Error: No hay conexión a la base de datos.")
            return None

        if not all([username, password_plano, fecha_nacimiento, vocacion]):
            print("Error: Username, password, fecha de nacimiento y vocación son requeridos.")
            return None
        if not isinstance(username, str) or not isinstance(password_plano, str) or not isinstance(vocacion, str):
            print("Error: Username, password y vocación deben ser strings.")
            return None
        if not isinstance(fecha_nacimiento, (date, datetime)):
            print("Error: La fecha de nacimiento debe ser un objeto date o datetime.")
            return None
        
        if not self.validar_vocacion_existente(self.db, vocacion):
            print(f"Error: La vocación '{vocacion}' no es válida o no existe en la base de datos.")

        if self.db[COLLECTION_NAME_USUARIOS].find_one({"username": username}):
            print(f"Error: El nombre de usuario '{username}' ya existe.")
            return None

        hashed_pw = self.hashear_password(password_plano)
        if hashed_pw is None:
            return None 

        try:
            edad = self.calcular_edad(fecha_nacimiento)
        except ValueError as ve:
            print(f"Error al calcular edad: {ve}")
            return None
            
        if isinstance(fecha_nacimiento, date) and not isinstance(fecha_nacimiento, datetime):
            fecha_nac_dt_para_db = datetime.combine(fecha_nacimiento, datetime.min.time())
        else:
            fecha_nac_dt_para_db = fecha_nacimiento

        usuario_doc = {
            "username": username,
            "password": hashed_pw, 
            "fecha_nacimiento": fecha_nac_dt_para_db,
            "edad": edad,
            "vocacion": vocacion,
            "progreso": progreso if progreso is not None else []
        }

        try:
            resultado = self.db[COLLECTION_NAME_USUARIOS].insert_one(usuario_doc)
            print(f"Usuario '{username}' creado con ID: {resultado.inserted_id}")
            return resultado.inserted_id
        except Exception as e:
            print(f"Error al crear el usuario '{username}': {e}")
            return None

    def leer_usuarios(self, filtro=None):
        """
        Lee y muestra los usuarios de la base de datos.
        :param self.db: Objeto de la base de datos MongoDB.
        :param filtro: Diccionario opcional para filtrar los resultados.
        """
        if self.db is None:
            print("Error: No hay conexión a la base de datos.")
            return

        if filtro is None:
            filtro = {}
        
        print("\n--- Lista de Usuarios ---")
        usuarios_encontrados = list(self.db[COLLECTION_NAME_USUARIOS].find(filtro))
        
        if not usuarios_encontrados:
            print("No se encontraron usuarios que coincidan con el filtro o la colección está vacía.")
            return

        for usuario in usuarios_encontrados:
            print(f"  ID MongoDB: {usuario['_id']}")
            print(f"  Username: {usuario['username']}") 
            print(f"  Fecha de Nacimiento: {usuario['fecha_nacimiento'].strftime('%d/%m/%Y') if usuario.get('fecha_nacimiento') else 'N/A'}")
            print(f"  Edad: {usuario.get('edad', 'N/A')}")
            print(f"  Vocación: {usuario.get('vocacion', 'N/A')}")
            print(f"  Progreso: {', '.join(usuario.get('progreso', [])) if usuario.get('progreso') else 'Ninguno'}")
            print("-" * 20)

    def leer_usuario_por_id(self, id_usuario_mongo):
        """
        Busca y muestra un usuario por su _id de MongoDB.
        :param id_usuario_mongo: String o ObjectId, el _id del usuario a buscar.
        """
        if self.db is None:
            print("Error: No hay conexión a la base de datos.")
            return

        try:
            obj_id = ObjectId(id_usuario_mongo)
        except Exception:
            print(f"Error: El ID de usuario '{id_usuario_mongo}' no es un ObjectId válido.")
            return

        usuario = self.db[COLLECTION_NAME_USUARIOS].find_one({"_id": obj_id})
        
        if usuario:
            """
            print(f"Usuario encontrado: {usuario['username']}")
            print(f"  ID MongoDB: {usuario['_id']}")
            print(f"  Fecha de Nacimiento: {usuario['fecha_nacimiento'].strftime('%d/%m/%Y') if usuario.get('fecha_nacimiento') else 'N/A'}")
            print(f"  Edad: {usuario.get('edad', 'N/A')}")
            print(f"  Vocación: {usuario.get('vocacion', 'N/A')}")
            print(f"  Progreso: {', '.join(usuario.get('progreso', [])) if usuario.get('progreso') else 'Ninguno'}")
            """
            return usuario
        else:
            print(f"No se encontró ningún usuario con ID '{id_usuario_mongo}'.")
            return None

    def leer_usuario(self, nombre_buscado):
        """
        Busca y muestra un usuario por su nombre de usuario.
        :param nombre_buscado: String, el nombre de usuario a buscar.
        """
        if self.db is None:
            print("Error: No hay conexión a la base de datos.")
            return

        usuario = self.db[COLLECTION_NAME_USUARIOS].find_one({"username": nombre_buscado})
        
        if usuario:
            """
            print(f"Usuario encontrado: {usuario['username']}")
            print(f"  ID MongoDB: {usuario['_id']}")
            print(f"  Fecha de Nacimiento: {usuario['fecha_nacimiento'].strftime('%d/%m/%Y') if usuario.get('fecha_nacimiento') else 'N/A'}")
            print(f"  Edad: {usuario.get('edad', 'N/A')}")
            print(f"  Vocación: {usuario.get('vocacion', 'N/A')}")
            print(f"  Progreso: {', '.join(usuario.get('progreso', [])) if usuario.get('progreso') else 'Ninguno'}")
            """
            return usuario
        else:
            print(f"No se encontró ningún usuario con el nombre '{nombre_buscado}'.")
            return None

    def actualizar_usuario(self, id_usuario_mongo, datos_para_actualizar):
        """
        Actualiza un usuario existente.
        :param self.db: Objeto de la base de datos MongoDB.
        :param id_usuario_mongo: String o ObjectId, el _id del usuario a actualizar.
        :param datos_para_actualizar: Diccionario con los campos a actualizar.
                                    Si se incluye 'password', se hasheará.
                                    Si se incluye 'fecha_nacimiento', se recalculará 'edad'.
        :return: True si la actualización fue exitosa, False si hubo un error.
        """
        if self.db is None:
            print("Error: No hay conexión a la base de datos.")
            return False

        try:
            obj_id = ObjectId(id_usuario_mongo)
        except Exception:
            print(f"Error: El ID de usuario '{id_usuario_mongo}' no es un ObjectId válido.")
            return False
        
        if not datos_para_actualizar or not isinstance(datos_para_actualizar, dict):
            print("Error: No se proporcionaron datos válidos para actualizar.")
            return False

        campos_set = {} 
        if "username" in datos_para_actualizar:
            nuevo_username = datos_para_actualizar["username"]
            usuario_existente = self.db[COLLECTION_NAME_USUARIOS].find_one({
                "username": nuevo_username,
                "_id": {"$ne": obj_id}
            })
            if usuario_existente:
                print(f"Error: El username '{nuevo_username}' ya está en uso por otro usuario.")
                return False
            campos_set["username"] = nuevo_username

        if "password" in datos_para_actualizar:
            nuevo_password_plano = datos_para_actualizar["password"]
            if not isinstance(nuevo_password_plano, str) or not nuevo_password_plano:
                print("Error: La nueva contraseña no puede estar vacía y debe ser un string.")
                return False
            hashed_pw = self.hashear_password(nuevo_password_plano)
            if hashed_pw is None:
                return False 
            campos_set["password"] = hashed_pw

        if "fecha_nacimiento" in datos_para_actualizar:
            nueva_fecha_nac = datos_para_actualizar["fecha_nacimiento"]
            if not isinstance(nueva_fecha_nac, (date, datetime)):
                print("Error: La nueva fecha de nacimiento debe ser un objeto date o datetime.")
                return False
            try:
                campos_set["edad"] = self.calcular_edad(nueva_fecha_nac)
                if isinstance(nueva_fecha_nac, date) and not isinstance(nueva_fecha_nac, datetime):
                    campos_set["fecha_nacimiento"] = datetime.combine(nueva_fecha_nac, datetime.min.time())
                else:
                    campos_set["fecha_nacimiento"] = nueva_fecha_nac
            except ValueError as ve:
                print(f"Error al procesar nueva fecha de nacimiento: {ve}")
                return False
                
        if "vocacion" in datos_para_actualizar:
            nueva_vocacion = datos_para_actualizar["vocacion"]
            if not isinstance(nueva_vocacion, str) or not nueva_vocacion:
                print("Error: La nueva vocación no puede estar vacía y debe ser un string.")
                return False
            if not self.validar_vocacion_existente(self.db, nueva_vocacion):
                print(f"Advertencia: La vocación '{nueva_vocacion}' no está en la lista de vocaciones válidas.")
            campos_set["vocacion"] = nueva_vocacion

        if "progreso" in datos_para_actualizar:
            nuevo_progreso = datos_para_actualizar["progreso"]
            if not isinstance(nuevo_progreso, list) or not all(isinstance(item, str) for item in nuevo_progreso):
                print("Error: El progreso debe ser una lista de strings.")
                return False
            campos_set["progreso"] = nuevo_progreso
        
        for key, value in datos_para_actualizar.items():
            if key not in ["username", "password", "fecha_nacimiento", "vocacion", "progreso", "_id", "edad"]:
                campos_set[key] = value


        if not campos_set:
            print("No hay campos válidos para actualizar.")
            return False

        try:
            resultado = self.db[COLLECTION_NAME_USUARIOS].update_one(
                {"_id": obj_id},
                {"$set": campos_set}
            )
            if resultado.matched_count == 0:
                print(f"No se encontró ningún usuario con ID: {id_usuario_mongo}")
                return False
            if resultado.modified_count > 0:
                print(f"Usuario con ID {id_usuario_mongo} actualizado exitosamente.")
                return True
            else:
                print(f"Usuario con ID {id_usuario_mongo} encontrado, pero no se realizaron modificaciones.")
                return True
        except Exception as e:
            print(f"Error al actualizar el usuario con ID {id_usuario_mongo}: {e}")
            return False

    def eliminar_usuario(self, id_usuario_mongo):
        """
        Elimina un usuario de la base de datos por su _id de MongoDB.
        :param self.db: Objeto de la base de datos MongoDB.
        :param id_usuario_mongo: String o ObjectId, el _id del usuario a eliminar.
        :return: True si la eliminación fue exitosa, False en caso contrario.
        """
        if self.db is None:
            print("Error: No hay conexión a la base de datos.")
            return False

        try:
            obj_id = ObjectId(id_usuario_mongo)
        except Exception:
            print(f"Error: El ID de usuario '{id_usuario_mongo}' no es un ObjectId válido.")
            return False
            
        try:
            resultado = self.db[COLLECTION_NAME_USUARIOS].delete_one({"_id": obj_id})
            if resultado.deleted_count > 0:
                print(f"Usuario con ID {id_usuario_mongo} eliminado exitosamente.")
                return True
            else:
                print(f"No se encontró ningún usuario con ID {id_usuario_mongo} para eliminar.")
                return False
        except Exception as e:
            print(f"Error al eliminar el usuario con ID {id_usuario_mongo}: {e}")
            return False



# --- Ejemplo de Uso ---
if __name__ == "__main__":
    db_conn = UsuariosCRUD()

    if db_conn is not None:
        print("\n--- DEMO CRUD USUARIOS ---")
        """
        # (Opcional) Crear algunas vocaciones de ejemplo si no existen
        if db_conn[COLLECTION_NAME_VOCACIONES].count_documents({}) == 0:
            print("Poblando vocaciones de ejemplo...")
            vocaciones_ejemplo = [
                {"nombre": "Ingeniería de Software", "categorias": ["Tecnología"]},
                {"nombre": "Diseño Gráfico", "categorias": ["Creatividad"]},
                {"nombre": "Medicina", "categorias": ["Salud"]}
            ]
            try:
                db_conn[COLLECTION_NAME_VOCACIONES].insert_many(vocaciones_ejemplo)
            except Exception as e:
                 print(f"Error poblando vocaciones: {e}")

        # 1. Crear nuevos usuarios
        print("\n1. Creando usuarios...")
        fecha_nac_user1 = date(1990, 5, 15)
        id_user1 = db_conn.crear_usuario(db_conn, "lucasg", "Password123!", fecha_nac_user1, "Ingeniería de Software", ["CURSO_PYTHON_BASICO", "CURSO_GIT"])
        
        fecha_nac_user2 = datetime(1985, 8, 22, 10, 30, 0) # Con hora
        id_user2 = db_conn.crear_usuario(db_conn, "anap", "AnaP_SecurePass", fecha_nac_user2, "Diseño Gráfico")
        
        db_conn.crear_usuario(db_conn, "lucasg", "OtraPass", date(1992,1,1), "Medicina") # Intentar crear username duplicado
        """
        # 2. Leer todos los usuarios
        db_conn.leer_usuarios()
        """
        # 3. Actualizar un usuario (si se creó)
        if id_user1:
            print(f"\n3. Actualizando usuario con ID: {id_user1}...")
            db_conn.actualizar_usuario(db_conn, id_user1, 
                               {
                                   "vocacion": "Medicina", 
                                   "progreso": ["CURSO_PYTHON_BASICO", "CURSO_GIT", "CURSO_IA_INTRO"],
                                   "fecha_nacimiento": date(1991, 6, 20) # Esto recalculará la edad
                               })
            db_conn.leer_usuarios(db_conn, {"_id": ObjectId(id_user1)}) # Leer solo el usuario actualizado

        # Intentar actualizar username a uno ya existente
        if id_user1 and id_user2:
            print(f"\nIntentando actualizar username de usuario {id_user1} a 'anap' (que ya existe)...")
            db_conn.actualizar_usuario(db_conn, id_user1, {"username": "anap"})


        # 4. Eliminar un usuario (si se creó)
        if id_user2:
            user_a_eliminar = db_conn[COLLECTION_NAME_USUARIOS].find_one({"_id": ObjectId(id_user2)})
            if user_a_eliminar is not None:
                 print(f"\n4. Eliminando usuario '{user_a_eliminar['username']}' (ID: {id_user2})...")
                 db_conn.eliminar_usuario(db_conn, id_user2)
                 db_conn.leer_usuarios(db_conn) # Mostrar lista actualizada
            else:
                 print(f"El usuario con ID {id_user2} no fue encontrado para eliminar.")
        """
        # Cerrar la conexión al finalizar (opcional, PyMongo la maneja al salir del script)
        # if db_conn.client is not None:
        #     db_conn.client.close()
        #     print("\nConexión a MongoDB cerrada.")
    else:
        print("No se pudo ejecutar la demostración del CRUD de usuarios debido a un error de conexión.")

