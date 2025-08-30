#!/bin/bash
# generar-compose.sh
# uso: ./generar-compose.sh <archivo_salida> <cantidad_clientes>

if [ $# -ne 2 ]; then
  echo "Uso: $0 <archivo_salida> <cantidad_clientes>"
  exit 1
fi

echo "Nombre del archivo de salida: $1"
echo "Cantidad de clientes: $2"

OUTPUT="$1"
NUM_CLIENTS="$2"

cat > "$OUTPUT" <<EOF
name: tp0
services:
  server:
    container_name: server
    image: server:latest
    entrypoint: python3 /main.py
    environment:
      - PYTHONUNBUFFERED=1
      - LOGGING_LEVEL=DEBUG
    volumes:
      - ./server/config.ini:/config.ini
    networks:
      - testing_net
EOF

#generar clientes
for i in $(seq 1 "$NUM_CLIENTS"); do
cat >> "$OUTPUT" <<EOF

  client$i:
    container_name: client$i
    image: client:latest
    entrypoint: /client
    environment:
      - CLI_ID=$i
      - CLI_LOG_LEVEL=DEBUG
    volumes:
      - ./client/config.yaml:/config.yaml
    networks:
      - testing_net
    depends_on:
      - server
EOF
done

cat >> "$OUTPUT" <<EOF

networks:
  testing_net:
    ipam:
      driver: default
      config:
        - subnet: 172.25.125.0/24
EOF

echo "Archivo $OUTPUT generado con $NUM_CLIENTS clientes."
