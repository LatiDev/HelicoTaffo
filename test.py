import os
import psycopg2
import helicotaffo

def test_resume():
    need = [
        helicotaffo.to_assets(os.environ['RESUME_DATA']),
        helicotaffo.to_assets(os.environ['RESUME_TEMPLATE']),
    ]    
    success, fail = helicotaffo.smart_loads(need)
    (resume_json, resume_tex, ) = success
    original = helicotaffo.parse_to_template(resume_json)
    renderer = helicotaffo.render.Render(resume_tex)

    print(renderer.do(
        original,
        helicotaffo.to_assets("temp.tex"),
        helicotaffo.to_assets("temp.pdf")
    ))

def test_database_connection():
    postgress = psycopg2.connect(
        database=os.environ['DEV_DB_NAME'],
        user=os.environ['DEV_DB_USER'],
        password=os.environ['DEV_DB_PASSWORD'],
        host=os.environ['DEV_DB_HOST'],
        port=os.environ['DEV_DB_PORT']
    ) 
    postgress.set_client_encoding("UTF8")
    cursor = postgress.cursor()

    app_exist = helicotaffo.has_send_application(
        cursor,
        helicotaffo.ApplicationHasSendDTO("0207.725.401")
    )

    cursor.close()
    postgress.close()

def test_data():
    need = [
        helicotaffo.to_assets(os.environ['DEV_DATA_FILE'])
    ]
    success, fail = helicotaffo.smart_loads(need)
    (email_lines, ) = success    
    database = [helicotaffo.CompanyDB(*line) for line in email_lines]

if __name__ == "__main__":
    import dotenv

    dotenv.load_dotenv()
    
    test_resume()