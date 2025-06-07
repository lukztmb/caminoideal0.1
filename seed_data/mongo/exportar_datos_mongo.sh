#!/bin/bash

DB_NAME="datos"
MONGO_URI="mongodb://admin:admin123@localhost:27017/"
OUTPUT_DIR="seed_data/mongo"

mkdir -p $OUTPUT_DIR

COLLECTIONS=("usuarios" "bibliografias" "cursos" "vocaciones")

echo "Exportando colecciones de MongoDB..."

for collection in "${COLLECTIONS[@]}"
do
  FILE_PATH="$OUTPUT_DIR/$collection.json"
  echo "-> Exportando la colección '$collection' a '$FILE_PATH'..."
  
  mongoexport --uri="$MONGO_URI/$DB_NAME" \
              --collection="$collection" \
              --out="$FILE_PATH" \
              --pretty \
              --jsonArray

  if [ $? -eq 0 ]; then
    echo "   Exportación de '$collection' completada con éxito."
  else
    echo "   ERROR: Falló la exportación de '$collection'."
  fi
done
read x
echo "Exportación finalizada."