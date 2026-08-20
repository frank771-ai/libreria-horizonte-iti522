# Validación funcional

Fecha de ejecución: 20 de agosto de 2026.

## Entorno verificado

- Ubuntu Server 22.04.5 LTS.
- Hostname: `libreria-horizonte`.
- 4 vCPU, 7.8 GiB de memoria visible y disco virtual de 80 GB.
- Docker 29.1.3 y Docker Compose 1.29.2.

## Resultados

| Prueba | Resultado |
| --- | --- |
| `GET /health` | HTTP 200 y `{"status":"ok"}` |
| Carga inicial | 20 productos |
| Filtro disponibles inicial | 16 productos |
| Filtro agotados | 4 productos |
| Creación | `TMP-001` creado con HTTP 201 |
| Actualización | ID 21 actualizado a `LIB-021` con HTTP 200 |
| Eliminación | `TMP-001` eliminado con HTTP 200 |
| Estado final | 21 productos: 17 disponibles y 4 agotados |
| Persistencia | `LIB-021` permaneció después de `stop.sh` y `start.sh` |
| Inicio repetido | `start.sh` ejecutado dos veces consecutivas sin pérdida de datos |
| Registro | Inicio, solicitudes, CRUD, errores y detención en `logs/application.log` |

## Prueba de persistencia

`stop.sh` retiró los contenedores y la red de Compose sin eliminar el volumen
`horizonte_inventory_data`. Después de ejecutar `start.sh`, la aplicación
informó `productos=21` y la consulta `GET /api/products/21` devolvió:

```json
{
  "id": 21,
  "code": "LIB-021",
  "name": "Fundamentos de programación",
  "category": "Tecnología",
  "price": 13500.0,
  "quantity": 6
}
```

## Seguridad de la entrega

- `.env` está ignorado por Git y tiene permisos `0600`.
- La contraseña de PostgreSQL se genera localmente mediante `openssl`.
- El historial público no contiene la contraseña usada durante las pruebas.
- La aplicación y PostgreSQL se ejecutan localmente dentro de la VM.
