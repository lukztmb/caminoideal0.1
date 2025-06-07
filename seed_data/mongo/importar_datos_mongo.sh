#!/bin/bash

DB_NAME="datos"
MONGO_URI="mongodb://admin:admin123@localhost:27017/"
INPUT_DIR="seed_data/mongo"

COLLECTIONS=("usuarios", "bibliografias", "cursos", "vocaciones")

echo "Importando colecciones a MongoDB..."

for collection in "${COLLECTIONS[@]}"
do
  echo "Importando $collection..."
  mongoimport --uri="$MONGO_URI/$DB_NAME" \
              --collection="$collection" \
              --file="$INPUT_DIR/$collection.json" \
              --jsonArray \
              --drop 
done

echo "Importación completa."