import test.Caminos as Caminos

from pymongo import MongoClient
from bson.objectid import ObjectId

# Conexión a MongoDB local
client = MongoClient("mongodb://localhost:27017/")
db = client["camino_ideal"]
coleccion = db["usuarios"]

def crear_usuario():
    try:
        grafo = Caminos.GrafoCaminos()
        listaObjetivos = grafo.buscar_objetivos()
    except Exception:
        return
    n = len(listaObjetivos)
    nombre = input("Nombre: ")
    edad = int(input("Edad: "))
    imprimirLista(["Objetivos"], listaObjetivos)
    aux = int(input("Indique su vocación: "))
    while aux < 1 or aux > n:
        aux = int(input("Opción fuera de rango: "))
    vocacion = listaObjetivos[aux]
    usuario = {
        "nombre": nombre,
        "edad": edad,
        "vocacion": vocacion
    }
    print("Usuario creado exitosamente.")
    insertarUsuario(usuario=usuario)

def insertarUsuario(usuario):
    coleccion.insert_one(usuario)
    print("Usuario cargado exitosamente.")

def imprimirLista(cabecera, lista):
    longitud = len(lista)
    print("")
    print(f"{' ':^5}", end=" ")
    for cab in cabecera:
        print(f"|{cab:^10}|", end=" ")
    print("")
    i = 1
    for str in lista:
        print(f"{i:^5}|{str:^10}|")
        i += 1



def leer_usuarios():
    print("\nUsuarios registrados:")
    for usuario in coleccion.find():
        print(f"ID: {usuario['_id']} | Nombre: {usuario['nombre']} | Edad: {usuario['edad']} | Vocación: {usuario['vocacion']}")
    print()

def actualizar_usuario():
    id_usuario = input("Ingresa el ID del usuario a actualizar: ")
    nuevo_nombre = input("Nuevo nombre: ")
    nueva_edad = int(input("Nueva edad: "))
    nueva_vocacion = input("Nueva vocación: ")
    resultado = coleccion.update_one(
        {"_id": ObjectId(id_usuario)},
        {"$set": {"nombre": nuevo_nombre, "edad": nueva_edad, "vocacion": nueva_vocacion}}
    )
    print("Usuario actualizado.\n" if resultado.modified_count else "No se encontró el usuario.\n")

def eliminar_usuario():
    id_usuario = input("Ingresa el ID del usuario a eliminar: ")
    resultado = coleccion.delete_one({"_id": ObjectId(id_usuario)})
    print("Usuario eliminado.\n" if resultado.deleted_count else "No se encontró el usuario.\n")

def menu():
    while True:
        print("[  Usuarios  ]")
        print("1. Crear usuario")
        print("2. Leer usuarios")
        print("3. Actualizar usuario")
        print("4. Eliminar usuario")
        print("5. Salir")
        opcion = input("Selecciona una opción: ")

        if opcion == "1":
            crear_usuario()
        elif opcion == "2":
            leer_usuarios()
        elif opcion == "3":
            actualizar_usuario()
        elif opcion == "4":
            eliminar_usuario()
        elif opcion == "5":
            print("Saliendo del sistema...")
            break
        else:
            print("Opción inválida. Intenta de nuevo.\n")

if __name__ == "__main__":
    #imprimirLista(["a", "b", "c"], ["xd", "tralalero", "tralala"])
    menu()
