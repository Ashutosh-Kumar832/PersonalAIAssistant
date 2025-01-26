import psycopg2
from sqlalchemy import create_engine
from database_tools.db_config import read_db_config
from database_tools.models import Base

# Load database configuration
db_config = read_db_config()

DB_URL = (
    f"postgresql://{db_config['DB_USER']}:{db_config['DB_PASSWORD']}"
    f"@{db_config['DB_URL']}:{db_config['DB_PORT']}/{db_config['DB_NAME']}"
)

def recreate_database():
    """Recreate the PostgreSQL database."""
    conn = psycopg2.connect(
        dbname="postgres",
        user=db_config["DB_USER"],
        password=db_config["DB_PASSWORD"],
        host=db_config["DB_URL"],
        port=db_config["DB_PORT"]
    )
    conn.autocommit = True
    cursor = conn.cursor()

    # Drop and recreate the database
    cursor.execute(f"DROP DATABASE IF EXISTS {db_config['DB_NAME']}")
    cursor.execute(f"CREATE DATABASE {db_config['DB_NAME']}")

    conn.close()
    print(f"Database '{db_config['DB_NAME']}' recreated successfully.")

def setup_tables():
    """Set up the tables using SQLAlchemy."""
    engine = create_engine(DB_URL)
    Base.metadata.drop_all(bind=engine)  # Drop all existing tables
    Base.metadata.create_all(bind=engine)  # Create all tables
    print("Tables created successfully.")

def main():
    print("Starting database setup...")
    recreate_database()
    setup_tables()
    print("Database setup complete.")

if __name__ == "__main__":
    main()
