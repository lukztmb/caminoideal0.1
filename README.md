# Camino Ideal 
Este es un prototipo para una aplicación de recomendación de rutas de aprendizaje. El proyecto proporciona la base para poder desarrollar una plataforma completa integrando machine learning y utilizando una base de datos en grafo como Neo4j AuraDB en el futuro.

Instalación
Sigue estos pasos para configurar el entorno de desarrollo y poner en marcha el proyecto.

Prerrequisitos
Asegúrate de tener instalado el siguiente software en tu sistema:

Python 3.13
Docker Desktop
1. Configuración de la Base de Datos (MongoDB)
El proyecto utiliza una instancia de MongoDB gestionada a través de Docker.

a.  Crea un archivo llamado docker-compose.yml en la raíz de tu proyecto con el siguiente contenido:

```yaml
version: '3.8'
services:
  mongo:
    image: mongo:4.4
    container_name: mongo-container
    ports:
      - "27017:27017"
    environment:
      # Estas credenciales están definidas en el código.
      # Si las cambias aquí, debes actualizarlas en los archivos de conexión a la base de datos.
      MONGO_INITDB_ROOT_USERNAME: admin
      MONGO_INITDB_ROOT_PASSWORD: admin123
    volumes:
      - ./data:/data/db
```
b.  Abre una terminal en el directorio donde creaste el archivo docker-compose.yml y levanta el contenedor con el siguiente comando:

```bash
docker compose up -d
```
c.  Verifica que el contenedor de Docker (mongo-container) esté corriendo antes de continuar con los siguientes pasos.

2. Configuración del Proyecto
a.  Instala todas las dependencias de Python necesarias ejecutando el siguiente comando en la raíz del proyecto:

```bash
pip install -r requirements.txt
```
b.  Para poblar la base de datos con los datos iniciales, ejecuta el script de creación de colecciones:

```bash
python seed_data/mongo/crear_colecciones.py
```
¡Y listo! Con esto, el entorno del proyecto ya está configurado y la base de datos inicializada.

# Uso
Correr archivos desde la raiz del proyecto

```bash
python <nombre_archivo>
```

# Estructura del Proyecto
Pendiente

# Licencia
No licenciado
