CREATE TABLE IF NOT EXISTS products (
    id SERIAL PRIMARY KEY,
    code VARCHAR(20) UNIQUE NOT NULL,
    name VARCHAR(150) NOT NULL,
    category VARCHAR(80) NOT NULL,
    price NUMERIC(10, 2) NOT NULL CHECK (price >= 0),
    quantity INTEGER NOT NULL CHECK (quantity >= 0),
    registration_date TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_products_category ON products (category);
CREATE INDEX IF NOT EXISTS idx_products_quantity ON products (quantity);

INSERT INTO products (code, name, category, price, quantity) VALUES
    ('LIB-001', 'Cien años de soledad', 'Literatura', 12500.00, 8),
    ('LIB-002', 'El principito', 'Literatura', 6500.00, 15),
    ('LIB-003', 'Don Quijote de la Mancha', 'Literatura', 14800.00, 4),
    ('LIB-004', 'La Odisea', 'Literatura', 8900.00, 0),
    ('INF-001', 'Cuentos para soñar', 'Infantil', 7200.00, 12),
    ('INF-002', 'Aventuras en el bosque', 'Infantil', 6800.00, 7),
    ('INF-003', 'Mi primer atlas', 'Infantil', 9900.00, 5),
    ('INF-004', 'Fábulas ilustradas', 'Infantil', 7500.00, 0),
    ('EDU-001', 'Matemática esencial', 'Educación', 11500.00, 10),
    ('EDU-002', 'Gramática práctica', 'Educación', 10300.00, 6),
    ('EDU-003', 'Introducción a la programación', 'Educación', 18500.00, 9),
    ('EDU-004', 'Ciencias naturales', 'Educación', 12400.00, 3),
    ('REF-001', 'Diccionario de la lengua española', 'Referencia', 16900.00, 2),
    ('REF-002', 'Atlas universal', 'Referencia', 15800.00, 4),
    ('REF-003', 'Enciclopedia estudiantil', 'Referencia', 21500.00, 0),
    ('PAP-001', 'Cuaderno universitario', 'Papelería', 2200.00, 35),
    ('PAP-002', 'Juego de bolígrafos', 'Papelería', 1800.00, 24),
    ('PAP-003', 'Marcadores de colores', 'Papelería', 3600.00, 18),
    ('PAP-004', 'Carpeta archivadora', 'Papelería', 2900.00, 11),
    ('PAP-005', 'Agenda académica', 'Papelería', 5800.00, 0)
ON CONFLICT (code) DO NOTHING;
