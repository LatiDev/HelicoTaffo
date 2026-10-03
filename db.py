if __name__ == "__main__":
    import psycopg2, json, pathlib

    query_path = pathlib.Path("db.sql")
    if not query_path.exists():
        raise Exception(f"{query_path} not found")

    with open(query_path, 'r', encoding="UTF-8") as file:
        query = file.read()

    db_path = pathlib.Path("database.json")
    if not db_path.exists():
        raise Exception(f"{db_path} not found")

    with open(db_path, 'r', encoding="UTF-8") as file:
        db = json.load(file)

    ptgs = psycopg2.connect(**db)
    ptgs.set_client_encoding("UTF8")
    cursor = ptgs.cursor()

    cursor.execute(query)

    ptgs.commit()

    cursor.close()
    ptgs.close()
