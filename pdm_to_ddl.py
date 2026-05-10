import xml.etree.ElementTree as ET
import os

def pdm_to_sql_ultra(pdm_file, output_sql):
    ns = {'a': 'attribute', 'c': 'collection', 'o': 'object'}
    
    if not os.path.exists(pdm_file):
        print(f"Error: No se encontró {pdm_file}")
        return

    tree = ET.parse(pdm_file)
    root = tree.getroot()

    # 1. MAPEO GLOBAL: Guardamos TODO lo que tenga un ID
    # Esto es vital porque las PK y FK usan referencias cruzadas de IDs
    id_map = {}
    for elem in root.iter():
        obj_id = elem.get("Id")
        if obj_id:
            code = elem.findtext("a:Code", namespaces=ns)
            id_map[obj_id] = code

    sql_output = []

    # 2. PROCESAR TABLAS
    tables = root.findall(".//o:Table", ns)
    for table in tables:
        t_code = table.findtext("a:Code", namespaces=ns)
        if not t_code: continue
        
        buffer = [f"CREATE TABLE {t_code} ("]
        col_defs = []
        
        # --- COLUMNAS ---
        columns = table.findall(".//o:Column", ns)
        for col in columns:
            c_id = col.get("Id")
            c_code = col.findtext("a:Code", namespaces=ns)
            c_type = col.findtext("a:DataType", namespaces=ns)
            c_mand = "NOT NULL" if col.findtext("a:Column.Mandatory", namespaces=ns) == "1" else ""
            
            if c_code:
                col_defs.append(f"    {c_code:<30} {c_type if c_type else 'VARCHAR(255)'} {c_mand}".strip())

        # --- PRIMARY KEY (Lógica reforzada) ---
        # Buscamos la colección de llaves de la tabla
        keys = table.findall("./c:Keys/o:Key", ns)
        # Buscamos cuál de esas llaves es la primaria
        pk_id_ref = table.find("./c:PrimaryKey/o:Key", ns)
        
        if pk_id_ref is not None:
            pk_ref = pk_id_ref.get("Ref")
            # Buscamos la definición de la llave que coincida con ese Ref
            for key in keys:
                if key.get("Id") == pk_ref:
                    pk_cols = []
                    # Extraemos los IDs de las columnas de esa llave
                    for k_col in key.findall("./c:Key.Columns/o:Column", ns):
                        pk_cols.append(id_map.get(k_col.get("Ref"), "UNKNOWN_COL"))
                    if pk_cols:
                        col_defs.append(f"    PRIMARY KEY ({', '.join(pk_cols)})")

        buffer.append(",\n".join(col_defs))
        buffer.append(");\n")
        sql_output.append("\n".join(buffer))

    # 3. FOREIGN KEYS (Relaciones externas)
    references = root.findall(".//o:Reference", ns)
    for ref in references:
        r_code = ref.findtext("a:Code", namespaces=ns)
        p_ref = ref.find("./c:ParentTable/o:Table", ns)
        c_ref = ref.find("./c:ChildTable/o:Table", ns)
        
        if p_ref is not None and c_ref is not None:
            p_name = id_map.get(p_ref.get("Ref"))
            c_name = id_map.get(c_ref.get("Ref"))
            
            joins = ref.findall(".//o:ReferenceJoin", ns)
            p_cols, c_cols = [], []
            for j in joins:
                o1 = j.find("./c:Object1/o:Column", ns)
                o2 = j.find("./c:Object2/o:Column", ns)
                if o1 is not None and o2 is not None:
                    p_cols.append(id_map.get(o1.get("Ref")))
                    c_cols.append(id_map.get(o2.get("Ref")))
            
            if p_name and c_name and p_cols:
                fk_sql = (f"ALTER TABLE {c_name} ADD CONSTRAINT {r_code}\n"
                          f"    FOREIGN KEY ({', '.join(c_cols)}) REFERENCES {p_name} ({', '.join(p_cols)});\n")
                sql_output.append(fk_sql)

    # GUARDAR ARCHIVO
    with open(output_sql, "w", encoding="utf-8") as f:
        f.write("\n\n".join(sql_output))
    
    print(f"Hecho. SQL completo generado en: {output_sql}")

if __name__ == "__main__":
    pdm_to_sql_ultra("FZHI_master_v39.pdm", "FZHI_master_v39.sql")