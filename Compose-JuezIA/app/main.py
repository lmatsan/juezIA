from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, field_validator
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import declarative_base, sessionmaker
import os
import logging
import time

# ---------------------------
# Logging
# ---------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)

# ---------------------------
# Configuración base de datos
# ---------------------------
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://legaluser:legalpassword@db:5432/jueziadb")

# Reintentos para esperar a PostgreSQL al arrancar
for attempt in range(10):
    try:
        engine = create_engine(DATABASE_URL)
        connection = engine.connect()
        connection.close()
        logger.info("Conexión con la base de datos jurídica establecida correctamente.")
        break
    except Exception:
        logger.warning(f"Esperando a la base de datos... intento {attempt + 1}/10")
        time.sleep(3)
else:
    raise Exception("No se pudo conectar a la base de datos.")

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# ---------------------------
# Modelo SQLAlchemy
# ---------------------------
class LeyDB(Base):
    __tablename__ = "leyes"

    id = Column(Integer, primary_key=True, index=True)
    titulo = Column(String, nullable=False)
    tipo_documento = Column(String, nullable=False)
    anio = Column(Integer, nullable=False)

# Crear tabla
Base.metadata.create_all(bind=engine)

# ---------------------------
# Esquema de entrada
# ---------------------------
class LeyCreate(BaseModel):
    titulo: str
    tipo_documento: str
    anio: int

    @field_validator("titulo", "tipo_documento")
    @classmethod
    def validate_text_fields(cls, value: str) -> str:
        if not value or not value.strip():
            raise ValueError("El campo no puede estar vacío")
        return value.strip()

    @field_validator("anio")
    @classmethod
    def validate_year(cls, value: int) -> int:
        if value < 0:
            raise ValueError("El año no puede ser negativo")
        return value

# ---------------------------
# FastAPI
# ---------------------------
app = FastAPI(title="JuezIA API", version="1.0.0")


@app.get("/")
def root():
    logger.info("Acceso al endpoint raíz.")
    return {"message": "JuezIA API de leyes y jurisprudencia funcionando correctamente"}


@app.get("/leyes")
def get_leyes():
    db = SessionLocal()
    try:
        leyes = db.query(LeyDB).all()
        logger.info("Listado de leyes recuperado correctamente.")
        return [
            {
                "id": ley.id,
                "titulo": ley.titulo,
                "tipo_documento": ley.tipo_documento,
                "anio": ley.anio
            }
            for ley in leyes
        ]
    finally:
        db.close()


@app.get("/leyes/{ley_id}")
def get_ley(ley_id: int):
    db = SessionLocal()
    try:
        ley = db.query(LeyDB).filter(LeyDB.id == ley_id).first()
        if not ley:
            logger.warning(f"Documento jurídico con id {ley_id} no encontrado.")
            raise HTTPException(status_code=404, detail="Documento jurídico no encontrado")

        logger.info(f"Documento jurídico con id {ley_id} recuperado correctamente.")
        return {
            "id": ley.id,
            "titulo": ley.titulo,
            "tipo_documento": ley.tipo_documento,
            "anio": ley.anio
        }
    finally:
        db.close()


@app.post("/leyes", status_code=201)
def create_ley(ley: LeyCreate):
    db = SessionLocal()
    try:
        new_ley = LeyDB(
            titulo=ley.titulo,
            tipo_documento=ley.tipo_documento,
            anio=ley.anio
        )
        db.add(new_ley)
        db.commit()
        db.refresh(new_ley)

        logger.info(f"Documento jurídico creado con id {new_ley.id}.")
        return {
            "message": "Documento jurídico creado correctamente",
            "ley": {
                "id": new_ley.id,
                "titulo": new_ley.titulo,
                "tipo_documento": new_ley.tipo_documento,
                "anio": new_ley.anio
            }
        }
    except Exception as e:
        db.rollback()
        logger.error(f"Error al crear documento jurídico: {str(e)}")
        raise HTTPException(status_code=400, detail="Datos inválidos")
    finally:
        db.close()


@app.delete("/leyes/{ley_id}")
def delete_ley(ley_id: int):
    db = SessionLocal()
    try:
        ley = db.query(LeyDB).filter(LeyDB.id == ley_id).first()
        if not ley:
            logger.warning(f"No se pudo borrar el documento jurídico con id {ley_id}: no existe.")
            raise HTTPException(status_code=404, detail="Documento jurídico no encontrado")

        db.delete(ley)
        db.commit()

        logger.info(f"Documento jurídico con id {ley_id} eliminado correctamente.")
        return {"message": f"Documento jurídico con id {ley_id} eliminado correctamente"}
    finally:
        db.close()
