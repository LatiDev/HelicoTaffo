import psycopg2
import helicotaffo

def test_resume():
    need = ["template.json", "template.tex"]    
    success, fail = helicotaffo.smart_load(need)
    (resume_json, resume_tex, ) = success
    original = helicotaffo.parse_to_template(resume_json)
    renderer = helicotaffo.render.Render(resume_tex)

    print(renderer.do(original))

def test_database_connection():
    need = ["database.json"]
    success, fail = helicotaffo.smart_load(need)
    (database_json, ) = success
    postgress = psycopg2.connect(**database_json)
    postgress.set_client_encoding("UTF8")
    cursor = postgress.cursor()

    app_exist = helicotaffo.has_send_application(
        cursor,
        helicotaffo.ApplicationHasSendDTO("0207.725.401")
    )

    cursor.close()
    postgress.close()

def test_data():
    need = ["data.csv"]
    success, fail = helicotaffo.smart_load(need)
    (email_lines, ) = success    
    database = [helicotaffo.CompanyDB(*line) for line in email_lines]

if __name__ == "__main__":
    pass