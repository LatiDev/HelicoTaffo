if __name__ == "__main__":
    import psycopg2, dotenv, pathlib, os, argparse

    query_path = pathlib.Path("db.sql")
    if not query_path.exists():
        raise Exception(f"{query_path} not found")

    with open(query_path, 'r', encoding="UTF-8") as file:
        query = file.read()

    parser = argparse.ArgumentParser()
    parser.add_argument("--launch", choices=["DEV", "PROD"], default="DEV")

    args = parser.parse_args()

    DEV = args.launch == "DEV"

    dotenv.load_dotenv()

    ptgs = psycopg2.connect(
        database=os.environ['DEV_DB_NAME'] if DEV else os.environ['MAIN_DB_NAME'],
        user=os.environ['DEV_DB_USER'] if DEV else os.environ['MAIN_DB_USER'],
        password=os.environ['DEV_DB_PASSWORD'] if DEV else os.environ['MAIN_DB_PASSWORD'],
        host=os.environ['DEV_DB_HOST'] if DEV else os.environ['MAIN_DB_HOST'],
        port=os.environ['DEV_DB_PORT'] if DEV else os.environ['MAIN_DB_PORT']
    )

    ptgs.set_client_encoding("UTF8")
    cursor = ptgs.cursor()

    cursor.execute(query)

    ptgs.commit()

    cursor.close()
    ptgs.close()
