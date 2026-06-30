import oracledb
import sys
import getpass
from utils.config_loader import config

_passwords = {}


def get_connection(config_node="oracle_ods"):
    try:
        user = config.get(f"{config_node}.user")
        dsn = config.get(f"{config_node}.dsn")

        if not user or not dsn:
            print(
                f"ERROR: Oracle user or DSN not set in config.yaml for {config_node}."
            )
            return None

        if config_node not in _passwords:
            _passwords[config_node] = getpass.getpass(prompt=f"Enter password for {user}@{config_node}: ")

        password = _passwords[config_node]

        if not password or "YOUR_" in f"{user}{password}{dsn}":
            print(
                f"ERROR: Oracle credentials not set correctly for {config_node}."
            )
            return None

        return oracledb.connect(user=user, password=password, dsn=dsn)
    except Exception as e:
        print(f"ERROR: Failed to connect to Oracle ({config_node}): {e}")
        return None


def fetch_view_source(view_name, config_node="oracle_ods"):
    conn = get_connection(config_node)
    if not conn:
        return None

    try:
        cursor = conn.cursor()
        # Search all_views for the view text
        cursor.execute(
            "SELECT TEXT FROM ALL_VIEWS WHERE UPPER(VIEW_NAME) = :v",
            {"v": view_name.upper()},
        )
        row = cursor.fetchone()
        if row:
            return row[0]

        # Fallback to all_mviews if not in all_views
        cursor.execute(
            "SELECT QUERY FROM ALL_MVIEWS WHERE UPPER(MVIEW_NAME) = :v",
            {"v": view_name.upper()},
        )
        row = cursor.fetchone()
        if row:
            return row[0]

        print(f"ERROR: View {view_name} not found in ALL_VIEWS or ALL_MVIEWS.")
        return None
    except Exception as e:
        print(f"ERROR: Database query failed: {e}")
        return None
    finally:
        conn.close()


def resolve_schema(object_name, config_node="oracle_ods"):
    """Finds the owner of an object in ALL_OBJECTS."""
    conn = get_connection(config_node)
    if not conn:
        return None

    try:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT OWNER FROM ALL_OBJECTS WHERE UPPER(OBJECT_NAME) = :o AND OBJECT_TYPE <> 'SYNONYM'",
            {"o": object_name.upper()},
        )
        rows = cursor.fetchall()

        if not rows:
            # Check for synonyms
            cursor.execute(
                "SELECT TABLE_OWNER FROM ALL_SYNONYMS WHERE UPPER(SYNONYM_NAME) = :o",
                {"o": object_name.upper()},
            )
            rows = cursor.fetchall()

        if rows:
            # Prefer common schemas if multiple owners exist (e.g. ODSMGR over ODSLOV)
            owners = [r[0] for r in rows]
            if "ODSMGR" in owners:
                return "ODSMGR"
            if "SATURN" in owners:
                return "SATURN"
            return owners[0]

        return None
    except Exception as e:
        print(f"ERROR: Failed to resolve schema for {object_name}: {e}")
        return None
    finally:
        conn.close()

