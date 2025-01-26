import xml.etree.ElementTree as ET

def read_db_config(file_path="config/db_config.xml"):
    """Read database configuration from an XML file."""
    root = ET.parse(file_path).getroot()

    # Navigate to the PostgreSQL node and extract configuration values
    return {
        "DB_URL": root.findtext("postgresql/url"),
        "DB_PORT": root.findtext("postgresql/port"),
        "DB_NAME": root.findtext("postgresql/name"),
        "DB_USER": root.findtext("postgresql/username"),
        "DB_PASSWORD": root.findtext("postgresql/password"),
    }
