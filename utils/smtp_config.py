import xml.etree.ElementTree as ET

def read_smtp_config(file_path="config/smtp_config.xml"):
    """Read SMTP configuration from an XML file."""
    try:
        tree = ET.parse(file_path)
        root = tree.getroot()
        return {
            "server": root.findtext("server"),
            "port": int(root.findtext("port")),
            "username": root.findtext("username"),
            "password": root.findtext("password"),
            "use_tls": root.findtext("use_tls") == "true",
        }
    except Exception as e:
        raise ValueError(f"Error reading SMTP config: {e}")
