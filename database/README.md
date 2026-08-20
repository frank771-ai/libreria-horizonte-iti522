# Base de datos

`init.sql` crea la tabla obligatoria `products`, aplica restricciones de
integridad y carga 20 productos iniciales. PostgreSQL ejecuta este archivo
automáticamente la primera vez que se crea el volumen de datos.

Campos:

- `id`: identificador autoincremental.
- `code`: código único del producto.
- `name`: nombre.
- `category`: categoría.
- `price`: precio en colones.
- `quantity`: cantidad disponible.
- `registration_date`: fecha y hora de registro.
