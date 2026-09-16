import os
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import sessionmaker, declarative_base

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./learning_center.db")
if DATABASE_URL.startswith("postgres://"):
    # Neon/Render hand out "postgres://" URLs; SQLAlchemy needs an explicit dialect+driver.
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql+psycopg://", 1)
elif DATABASE_URL.startswith("postgresql://"):
    # Force the modern psycopg (v3) driver instead of SQLAlchemy's default psycopg2.
    DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+psycopg://", 1)

connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
engine = create_engine(DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def sync_columns():
    """Add any model column that is missing from an existing table.

    There is no migration tool here and Base.metadata.create_all() only creates
    whole tables, never new columns on a table that already exists. Without this,
    adding a column works on a fresh database and breaks every deployed one.

    Additive only: it never drops, renames, or retypes anything.
    """
    inspector = inspect(engine)
    existing_tables = set(inspector.get_table_names())

    for table in Base.metadata.sorted_tables:
        if table.name not in existing_tables:
            continue  # create_all() will build it in full
        present = {c["name"] for c in inspector.get_columns(table.name)}
        for column in table.columns:
            if column.name in present:
                continue
            ddl_type = column.type.compile(dialect=engine.dialect)
            default = ""
            if column.default is not None and getattr(column.default, "is_scalar", False):
                value = column.default.arg
                default = f" DEFAULT {value!r}" if isinstance(value, str) else f" DEFAULT {value}"
            with engine.begin() as conn:
                conn.execute(text(
                    f'ALTER TABLE "{table.name}" ADD COLUMN "{column.name}" {ddl_type}{default}'
                ))
            print(f"[setup] Added column {table.name}.{column.name}")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
