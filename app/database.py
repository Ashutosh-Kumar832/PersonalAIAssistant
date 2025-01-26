from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_tools.db_config import read_db_config

# Load database configuration
db_config = read_db_config()

DB_URL = (
    f"postgresql://{db_config['DB_USER']}:{db_config['DB_PASSWORD']}"
    f"@{db_config['DB_URL']}:{db_config['DB_PORT']}/{db_config['DB_NAME']}"
)

# SQLAlchemy Setup
engine = create_engine(DB_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Dependency for FastAPI routes
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
