def is_name_consistent(extracted_docs: dict, supplier_name: str) -> bool:
    for fields in extracted_docs.values():
        if supplier_name.lower() not in fields.get("organization_name", "").lower():
            return False
    return True
