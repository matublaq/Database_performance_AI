from lxml import etree
import json

pdm_file = "data/pdm/FZHI_master_v39.pdm"

NS = {
    "a": "attribute",
    "c": "collection",
    "o": "object"
}

tree = etree.parse(pdm_file)
root = tree.getroot()

resultado = {
    "model": None,
    "tables": []
}

# ==========================================
# NOMBRE DEL MODELO
# ==========================================

model_name = root.find(".//o:Model/a:Name", namespaces=NS)

if model_name is not None:
    resultado["model"] = model_name.text

# ==========================================
# TABLAS
# ==========================================

tables = root.xpath("//o:Table", namespaces=NS)

for table in tables:

    tabla = {
        "id": table.get("Id"),
        "name": None,
        "code": None,
        "columns": []
    }

    # Nombre lógico
    name = table.find("a:Name", namespaces=NS)
    if name is not None:
        tabla["name"] = name.text

    # Nombre físico
    code = table.find("a:Code", namespaces=NS)
    if code is not None:
        tabla["code"] = code.text

    # ==========================================
    # COLUMNAS
    # ==========================================

    columns = table.xpath(
        "./c:Columns/o:Column",
        namespaces=NS
    )

    for column in columns:

        col = {
            "id": column.get("Id"),
            "name": None,
            "code": None,
            "datatype": None,
            "mandatory": False
        }

        # Nombre lógico
        col_name = column.find("a:Name", namespaces=NS)
        if col_name is not None:
            col["name"] = col_name.text

        # Nombre físico
        col_code = column.find("a:Code", namespaces=NS)
        if col_code is not None:
            col["code"] = col_code.text

        # Tipo
        datatype = column.find("a:DataType", namespaces=NS)
        if datatype is not None:
            col["datatype"] = datatype.text

        # Mandatory
        mandatory = column.find("a:Mandatory", namespaces=NS)
        if mandatory is not None:
            col["mandatory"] = mandatory.text == "1"

        tabla["columns"].append(col)

    resultado["tables"].append(tabla)

# ==========================================
# EXPORTAR JSON
# ==========================================

with open("modelo.json", "w", encoding="utf-8") as f:
    json.dump(resultado, f, indent=2, ensure_ascii=False)

print("Modelo parseado correctamente")
print(f"Tablas encontradas: {len(resultado['tables'])}")