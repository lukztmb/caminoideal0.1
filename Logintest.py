import bcrypt, Caminos
from pymongo import MongoClient
from datetime import datetime

# Conexión a MongoDB local
cli = MongoClient("mongodb://admin:admin123@localhost:27017/")
db = cli["usuarios"]
coleccion = db["usuarios"]

def calcular_edad(fecha_nacimiento):
    hoy = datetime.today()
    edad = hoy.year - fecha_nacimiento.year - ((hoy.month, hoy.day) < (fecha_nacimiento.month, fecha_nacimiento.day))
    return edad

def elegir_vocacion():
    grafo = Caminos.GrafoCaminos()
    opciones = grafo.buscarObjetivos()
    print("\nVocaciones disponibles:")
    for i, opcion in enumerate(opciones, 1):
        print(f"{i}. {opcion}")
    
    while True:
        try:
            eleccion = int(input("Elige una vocación (número): "))
            if 1 <= eleccion <= len(opciones):
                return opciones[eleccion - 1]
            else:
                print("Número inválido. Intenta de nuevo.")
        except ValueError:
            print("Entrada inválida. Debes ingresar un número.")

def registrar_usuario():
    username = input("Elige un nombre de usuario: ").strip()
    if coleccion.find_one({"username": username}):
        print("Ese nombre de usuario ya está en uso.\n")
        return None

    password = input("Elige una contraseña: ").strip()
    hashed_pw = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

    while True:
        fecha_input = input("Fecha de nacimiento (formato YYYY-MM-DD): ").strip()
        try:
            fecha_nac = datetime.strptime(fecha_input, "%Y-%m-%d")
            break
        except ValueError:
            print("Formato inválido. Intenta de nuevo.")

    edad = calcular_edad(fecha_nac)
    vocacion = elegir_vocacion()

    nuevo_usuario = {
        "username": username,
        "password": hashed_pw,
        "fecha_nacimiento": fecha_nac, #datetime
        "edad": edad, #calculado por el sistema
        "vocacion": vocacion,
        "progreso": [],
        "decisiones": [],
        "amistades": [],
    }

    coleccion.insert_one(nuevo_usuario)
    print("Registro exitoso. ¡Bienvenido a Camino Ideal!\n")
    return nuevo_usuario

def login_usuario():
    username = input("Nombre de usuario: ").strip()
    usuario = coleccion.find_one({"username": username})

    if not usuario:
        print("Usuario no encontrado.")
        respuesta = input("¿Deseas registrarte? (s/n): ").strip().lower()
        if respuesta == "s":
            return registrar_usuario()
        else:
            print("Saliendo del sistema.\n")
            return None

    password = input("Contraseña: ").strip()
    if bcrypt.checkpw(password.encode('utf-8'), usuario['password']):
        print(f"Bienvenido, {username}.\n")
        return usuario
    else:
        print("Contraseña incorrecta.\n")
        return None

def inicio():
    print("[ CAMINO IDEAL ]")
    usuario = None
    while not usuario:
        usuario = login_usuario()
    return usuario

def buscarCursos(categoria, dificultad):
    grafo = Caminos.GrafoCaminos()
    grafo.obtener_cursos_por_categoria_dificultad(usuario_activo['vocacion'], categoria, dificultad)

def menu():
    while True:
        print("[  Menú  ]")
        print("1. Ver cursos")
        print("2. Ver cursos completados")
        print("3. Consultar bibliografías")
        print("4. Salir")
        opcion = input("Selecciona una opción: ")
        if opcion == '1' :
            categoria = input('Indique la categoría: ')
            dificultad = input('Indique la dificultad: ')
            buscarCursos(categoria, dificultad)
        break



if __name__ == "__main__":
    usuario_activo = inicio()
    menu()
