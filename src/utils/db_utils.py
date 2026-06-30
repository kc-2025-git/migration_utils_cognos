import oracledb
import sys
import getpass
from utils.config_loader import config

_passwords = {}
_schema_cache = {}

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


def _load_schema_cache(config_node):
    if config_node in _schema_cache:
        return
        
    print(f"Loading schema metadata into memory for {config_node}...")
    conn = get_connection(config_node)
    if not conn:
        return
        
    cache = {
        "objects": set(),           # (owner, object_name)
        "object_owners": {},        # object_name -> [owner1, owner2]
        "synonyms": {},             # (owner, synonym_name) -> table_owner
        "synonym_owners": {},       # synonym_name -> [table_owner1, table_owner2]
    }
    
    try:
        cursor = conn.cursor()
        
        # Load Objects
        cursor.execute("SELECT OWNER, OBJECT_NAME FROM ALL_OBJECTS WHERE OBJECT_TYPE IN ('TABLE', 'VIEW', 'MATERIALIZED VIEW')")
        for owner, obj_name in cursor:
            if not owner or not obj_name:
                continue
            owner, obj_name = owner.upper(), obj_name.upper()
            cache["objects"].add((owner, obj_name))
            
            if obj_name not in cache["object_owners"]:
                cache["object_owners"][obj_name] = []
            cache["object_owners"][obj_name].append(owner)
            
        # Load Synonyms
        cursor.execute("SELECT OWNER, SYNONYM_NAME, TABLE_OWNER FROM ALL_SYNONYMS")
        for owner, syn_name, table_owner in cursor:
            if not owner or not syn_name or not table_owner:
                continue
            owner, syn_name, table_owner = owner.upper(), syn_name.upper(), table_owner.upper()
            
            cache["synonyms"][(owner, syn_name)] = table_owner
            
            if syn_name not in cache["synonym_owners"]:
                cache["synonym_owners"][syn_name] = []
            cache["synonym_owners"][syn_name].append(table_owner)
            
        _schema_cache[config_node] = cache
        print(f"Successfully loaded metadata: {len(cache['objects'])} objects, {len(cache['synonyms'])} synonyms.")
    except Exception as e:
        print(f"ERROR: Failed to load schema cache for {config_node}: {e}")
    finally:
        conn.close()


def resolve_schema(object_name, config_node="oracle_ods"):
    """Finds the owner of an object using the in-memory cache."""
    _load_schema_cache(config_node)
    cache = _schema_cache.get(config_node)
    if not cache:
        return None
        
    obj_name_up = object_name.upper()
    
    owners = cache["object_owners"].get(obj_name_up, [])
    if not owners:
        owners = cache["synonym_owners"].get(obj_name_up, [])
        
    if owners:
        # Prefer common schemas if multiple owners exist (e.g. ODSMGR over ODSLOV)
        if "ODSMGR" in owners:
            return "ODSMGR"
        if "SATURN" in owners:
            return "SATURN"
        return owners[0]

    return None


def resolve_provided_schema(schema, object_name, config_node="oracle_ods"):
    """
    Validates a provided schema for an object using the in-memory cache.
    1. Confirms table/view exists in that schema.
    2. Checks for a private synonym in that schema.
    3. Checks for a public synonym.
    Returns the resolved schema, or None if unresolved.
    """
    _load_schema_cache(config_node)
    cache = _schema_cache.get(config_node)
    if not cache:
        return None
        
    schema_up = schema.upper()
    obj_name_up = object_name.upper()
    
    # 1. Confirm table or view exists in that schema
    if (schema_up, obj_name_up) in cache["objects"]:
        return schema_up
        
    # 2. Check for private synonym in that schema
    if (schema_up, obj_name_up) in cache["synonyms"]:
        return cache["synonyms"][(schema_up, obj_name_up)]
        
    # 3. Check for public synonym
    if ("PUBLIC", obj_name_up) in cache["synonyms"]:
        return cache["synonyms"][("PUBLIC", obj_name_up)]
        
    return None

