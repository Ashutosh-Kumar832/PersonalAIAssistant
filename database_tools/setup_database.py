import psycopg2
from psycopg2 import sql
import getpass

DB_HOST = "localhost"
DB_PORT = 5432
DB_NAME = "task_manager"
DB_USER = "task_user"
DB_PASSWORD = "securepassword"
ADMIN_USER = getpass.getuser()  # macOS/Linux: use current user; Windows: use "postgres"
ADMIN_PASSWORD = None           # macOS/Linux: None; Windows: enter PostgreSQL password -> "postgres"

def initialize_database():
    try:
        # Connect to PostgreSQL with admin user
        conn = psycopg2.connect(
            dbname="postgres",
            user=ADMIN_USER,
            password=ADMIN_PASSWORD,
            host=DB_HOST,
            port=DB_PORT
        )
        conn.autocommit = True
        cur = conn.cursor()

        # Create database if not exists
        cur.execute(f"SELECT 1 FROM pg_database WHERE datname = '{DB_NAME}'")
        if not cur.fetchone():
            cur.execute(sql.SQL("CREATE DATABASE {}").format(sql.Identifier(DB_NAME)))
            print(f"Database '{DB_NAME}' created successfully.")

        # Create user if not exists
        cur.execute(f"SELECT 1 FROM pg_roles WHERE rolname = '{DB_USER}'")
        if not cur.fetchone():
            cur.execute(
                sql.SQL("CREATE USER {} WITH PASSWORD %s")
                .format(sql.Identifier(DB_USER)),
                [DB_PASSWORD]
            )
            print(f"User '{DB_USER}' created successfully.")

        # Grant privileges
        cur.execute(
            sql.SQL("GRANT ALL PRIVILEGES ON DATABASE {} TO {}")
            .format(sql.Identifier(DB_NAME), sql.Identifier(DB_USER))
        )
        print(f"Granted all privileges on database '{DB_NAME}' to user '{DB_USER}'.")

        # Close connection
        cur.close()
        conn.close()

        # Connect to the new database to create/update tables
        conn = psycopg2.connect(
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT
        )
        cur = conn.cursor()

        # Create or update the tasks table
        cur.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            description TEXT NOT NULL,
            due_date DATE,
            status VARCHAR(50) DEFAULT 'pending',
            priority INT DEFAULT 0,
            recurrence VARCHAR(50),
            celery_task_id VARCHAR(255)
        );
        """)

        # Check and add missing columns
        columns_to_add = [
            ("deleted_at", "TIMESTAMP NULL"),
            ("archived_at", "TIMESTAMP NULL")
        ]

        for column, datatype in columns_to_add:
            cur.execute(f"""
            DO $$
            BEGIN
                IF NOT EXISTS (
                    SELECT 1 FROM information_schema.columns 
                    WHERE table_name='tasks' AND column_name='{column}'
                ) THEN
                    ALTER TABLE tasks ADD COLUMN {column} {datatype};
                    RAISE NOTICE 'Added missing column: {column}';
                END IF;
            END $$;
            """)

        conn.commit()
        print("Table 'tasks' created/updated successfully.")

        # Close connection
        cur.close()
        conn.close()

    except Exception as e:
        print(f"Error initializing database: {e}")

if __name__ == "__main__":
    initialize_database()
