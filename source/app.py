import logging
import os
import time
from contextlib import asynccontextmanager
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Literal

import psycopg2
from psycopg2 import IntegrityError
from psycopg2.extras import RealDictCursor
from fastapi import FastAPI, HTTPException, Query, Request, status
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, Field, field_validator


BASE_DIR = Path(__file__).resolve().parent
LOG_FILE = Path(os.getenv("LOG_FILE", "/app/logs/application.log"))
LOG_FILE.parent.mkdir(parents=True, exist_ok=True)

logger = logging.getLogger("horizonte")
logger.setLevel(logging.INFO)
formatter = logging.Formatter("%(asctime)s | %(levelname)s | %(message)s")

file_handler = RotatingFileHandler(
    LOG_FILE, maxBytes=2_000_000, backupCount=3, encoding="utf-8"
)
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)


def get_connection():
    return psycopg2.connect(
        host=os.getenv("DB_HOST", "database"),
        port=int(os.getenv("DB_PORT", "5432")),
        dbname=os.getenv("DB_NAME", "horizonte"),
        user=os.getenv("DB_USER", "horizonte"),
        password=os.environ["DB_PASSWORD"],
        connect_timeout=5,
    )


class ProductPayload(BaseModel):
    code: str = Field(min_length=2, max_length=20)
    name: str = Field(min_length=2, max_length=150)
    category: str = Field(min_length=2, max_length=80)
    price: float = Field(ge=0)
    quantity: int = Field(ge=0)

    @field_validator("code", "name", "category")
    @classmethod
    def clean_text(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("El valor no puede quedar vacío")
        return cleaned

    @field_validator("code")
    @classmethod
    def uppercase_code(cls, value: str) -> str:
        return value.upper()


@asynccontextmanager
async def lifespan(_: FastAPI):
    logger.info("Inicio de Horizonte Inventory")
    try:
        with get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute("SELECT COUNT(*) FROM products")
                total = cursor.fetchone()[0]
        logger.info("Conexión a base de datos correcta; productos=%s", total)
    except Exception:
        logger.exception("Error de conexión a la base de datos durante el inicio")
    yield
    logger.info("Detención de Horizonte Inventory")


app = FastAPI(
    title="Horizonte Inventory",
    version="1.0.0",
    lifespan=lifespan,
)
app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")
templates = Jinja2Templates(directory=BASE_DIR / "templates")


@app.middleware("http")
async def request_logger(request: Request, call_next):
    started = time.perf_counter()
    logger.info("Solicitud recibida: %s %s", request.method, request.url.path)
    try:
        response = await call_next(request)
    except Exception:
        logger.exception("Error no controlado: %s %s", request.method, request.url.path)
        raise
    elapsed_ms = (time.perf_counter() - started) * 1000
    logger.info(
        "Solicitud completada: %s %s estado=%s tiempo_ms=%.2f",
        request.method,
        request.url.path,
        response.status_code,
        elapsed_ms,
    )
    return response


@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse(request=request, name="index.html")


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/api/categories")
def categories():
    try:
        with get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute("SELECT DISTINCT category FROM products ORDER BY category")
                return [row[0] for row in cursor.fetchall()]
    except Exception as exc:
        logger.exception("Error al consultar categorías")
        raise HTTPException(status_code=500, detail="No se pudieron consultar las categorías") from exc


@app.get("/api/products")
def list_products(
    stock: Literal["all", "available", "out-of-stock"] = "all",
    category: str | None = Query(default=None, max_length=80),
):
    clauses: list[str] = []
    parameters: list[object] = []

    if stock == "available":
        clauses.append("quantity > 0")
    elif stock == "out-of-stock":
        clauses.append("quantity = 0")
    if category:
        clauses.append("category = %s")
        parameters.append(category)

    where = f" WHERE {' AND '.join(clauses)}" if clauses else ""
    query = (
        "SELECT id, code, name, category, price, quantity, registration_date "
        f"FROM products{where} ORDER BY id"
    )
    try:
        with get_connection() as connection:
            with connection.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute(query, parameters)
                return cursor.fetchall()
    except Exception as exc:
        logger.exception("Error al consultar productos")
        raise HTTPException(status_code=500, detail="No se pudieron consultar los productos") from exc


@app.get("/api/products/{product_id}")
def get_product(product_id: int):
    try:
        with get_connection() as connection:
            with connection.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute(
                    "SELECT id, code, name, category, price, quantity, registration_date "
                    "FROM products WHERE id = %s",
                    (product_id,),
                )
                product = cursor.fetchone()
        if not product:
            raise HTTPException(status_code=404, detail="Producto no encontrado")
        return product
    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("Error al consultar producto id=%s", product_id)
        raise HTTPException(status_code=500, detail="No se pudo consultar el producto") from exc


@app.post("/api/products", status_code=status.HTTP_201_CREATED)
def create_product(payload: ProductPayload):
    try:
        with get_connection() as connection:
            with connection.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute(
                    "INSERT INTO products (code, name, category, price, quantity) "
                    "VALUES (%s, %s, %s, %s, %s) "
                    "RETURNING id, code, name, category, price, quantity, registration_date",
                    (payload.code, payload.name, payload.category, payload.price, payload.quantity),
                )
                product = cursor.fetchone()
        logger.info("Producto creado: id=%s código=%s", product["id"], product["code"])
        return product
    except IntegrityError as exc:
        logger.warning("Creación rechazada por integridad: código=%s", payload.code)
        raise HTTPException(status_code=409, detail="El código ya existe o los datos son inválidos") from exc
    except Exception as exc:
        logger.exception("Error al crear producto: código=%s", payload.code)
        raise HTTPException(status_code=500, detail="No se pudo crear el producto") from exc


@app.put("/api/products/{product_id}")
def update_product(product_id: int, payload: ProductPayload):
    try:
        with get_connection() as connection:
            with connection.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute(
                    "UPDATE products SET code=%s, name=%s, category=%s, price=%s, quantity=%s "
                    "WHERE id=%s RETURNING id, code, name, category, price, quantity, registration_date",
                    (
                        payload.code,
                        payload.name,
                        payload.category,
                        payload.price,
                        payload.quantity,
                        product_id,
                    ),
                )
                product = cursor.fetchone()
        if not product:
            raise HTTPException(status_code=404, detail="Producto no encontrado")
        logger.info("Producto actualizado: id=%s código=%s", product_id, payload.code)
        return product
    except HTTPException:
        raise
    except IntegrityError as exc:
        logger.warning("Actualización rechazada por integridad: id=%s", product_id)
        raise HTTPException(status_code=409, detail="El código ya existe o los datos son inválidos") from exc
    except Exception as exc:
        logger.exception("Error al actualizar producto: id=%s", product_id)
        raise HTTPException(status_code=500, detail="No se pudo actualizar el producto") from exc


@app.delete("/api/products/{product_id}")
def delete_product(product_id: int):
    try:
        with get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute("DELETE FROM products WHERE id=%s RETURNING code", (product_id,))
                deleted = cursor.fetchone()
        if not deleted:
            raise HTTPException(status_code=404, detail="Producto no encontrado")
        logger.info("Producto eliminado: id=%s código=%s", product_id, deleted[0])
        return {"message": "Producto eliminado", "id": product_id}
    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("Error al eliminar producto: id=%s", product_id)
        raise HTTPException(status_code=500, detail="No se pudo eliminar el producto") from exc
