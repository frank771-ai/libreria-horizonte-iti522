# Horizonte Inventory — Librería Horizonte

Aplicación web local para administrar el inventario de la Librería Horizonte.
Fue desarrollada para el Examen Integral ITI-522 y se ejecuta completamente
dentro de una única máquina virtual.

## Autores

- Franklin Josué Castillo Umaña — [@frank771-ai](https://github.com/frank771-ai)
- Esteban Molina Meza — [@esmoliname](https://github.com/esmoliname)

## Tecnologías y entorno

- Sistema operativo: Ubuntu Server 22.04 LTS.
- Lenguaje: Python 3.12.
- Framework: FastAPI.
- Base de datos: PostgreSQL 16.
- Ejecución: Docker y Docker Compose.
- Puerto de la aplicación en la VM: `8080`.

## Funcionalidad

- Crear, consultar, actualizar y eliminar productos.
- Campos: ID, código, nombre, categoría, precio, cantidad y fecha de registro.
- Filtros para todos, disponibles, agotados y categoría.
- Tabla `products` con 20 registros iniciales.
- Endpoint exacto de salud: `{"status":"ok"}`.
- Log de inicio, solicitudes, operaciones CRUD y errores.

## Estructura

```text
.
├── source/       # Aplicación FastAPI, interfaz y Dockerfile
├── database/     # Esquema SQL y carga de 20 productos
├── logs/         # application.log generado en ejecución
├── scripts/      # start.sh, stop.sh y status.sh
├── docs/         # Arquitectura y documentación
├── evidence/     # Capturas requeridas por el examen
├── docker-compose.yml
├── README.md
└── CHANGELOG.md
```

## Inicio

Desde la raíz del repositorio:

```bash
chmod +x scripts/*.sh
./scripts/start.sh
```

El primer inicio solicita la contraseña de `sudo`, genera una contraseña local
aleatoria para PostgreSQL, construye la imagen, crea la base de datos y carga
los 20 productos. El script conserva la credencial solamente en un archivo
`.env` ignorado por Git y con permisos restringidos. No es necesario agregar el
usuario al grupo privilegiado `docker`.

## Acceso

- Aplicación dentro de la VM: <http://localhost:8080>
- Estado de salud: <http://localhost:8080/health>
- Documentación técnica de la API: <http://localhost:8080/docs>

Desde el anfitrión se puede configurar una redirección NAT hacia el mismo
puerto y abrir <http://localhost:8080>.

## Verificación

```bash
./scripts/status.sh
curl http://localhost:8080/health
sudo docker exec horizonte-database psql -U horizonte -d horizonte \
  -c "SELECT id, code, name, category, price, quantity, registration_date FROM products ORDER BY id;"
tail -n 30 logs/application.log
```

La respuesta del endpoint de salud debe ser:

```json
{"status":"ok"}
```

## Detención

```bash
./scripts/stop.sh
```

Este comando detiene los contenedores, pero mantiene los datos en el volumen
`horizonte_inventory_data`. Al ejecutar nuevamente `start.sh`, los productos
creados o modificados siguen disponibles.

## Registro de eventos

El archivo solicitado se encuentra en:

```text
logs/application.log
```

Incluye fecha y hora, inicio y detención, solicitudes recibidas, creación,
actualización y eliminación de productos, además de errores controlados.

## Documentación

- [Arquitectura](docs/architecture.md)
- [Resultados de pruebas](docs/TESTING.md)
- [Índice de evidencias](evidence/VALIDACION.md)
