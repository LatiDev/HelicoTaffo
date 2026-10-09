import model, render, mail, watermark
import psycopg2
import dataclasses, json, random, typing, hashlib, shutil, copy, csv, pathlib, time, os, datetime, types, uuid

@dataclasses.dataclass
class Experience:
    title: str
    company: str
    date: str
    learnings: list[str]

@dataclasses.dataclass
class Hobby:
    title: str
    description: str
    link: str
    technologies: list[str]

@dataclasses.dataclass
class TemplateParams:
    sidebar_bg_color: str
    title_block_color: str
    content_block_color: str
    contacts: dict[str, str]
    qualities: str
    skills: list[str]
    about: str
    fullname: str
    job: str
    experiences: list[Experience]
    trainings: list[Experience]
    hobbies: list[Hobby]

@dataclasses.dataclass
class CompanyDB:
    number: str
    name: str
    city: str
    classification: str
    size: int
    job: str
    email: str

@dataclasses.dataclass
class CompanyFindDTO:
    number: str

@dataclasses.dataclass
class CompanyFetchDTO:
    number: str

@dataclasses.dataclass
class CompanyInsertDTO:
    number: str
    name: str
    city: str
    classification: str
    size: int
    job: str
    email: str

@dataclasses.dataclass
class CompanyEnsureDTO:
    number: str
    name: str
    city: str
    classification: str
    size: int
    job: str
    email: str

@dataclasses.dataclass
class ApplicationDB:
    id_: int
    title: str
    mail: str
    sent_at: datetime.datetime
    company_id: str

@dataclasses.dataclass
class ApplicationInsertDTO:
    title: str
    mail: str
    sent_at: float
    company_id: str

@dataclasses.dataclass
class ApplicationHasSendDTO:
    company_id: str

@dataclasses.dataclass
class FileDB:
    id_: int
    filename: str
    hash_: str
    application_id: int

@dataclasses.dataclass
class FileInsertDTO:
    filename: str
    hash_: str
    application_id: int

@dataclasses.dataclass
class Me:
    fullname: str
    job: str
    email: str
    password: str
    error_email: str

@dataclasses.dataclass
class Config:
    mail_min: int
    mail_max: int
    session_time: int

@dataclasses.dataclass
class FetchCompanyException(Exception):
    number: str
    message: str

@dataclasses.dataclass
class InsertCompanyException(Exception):
    number: str
    message: str

@dataclasses.dataclass
class FindApplicationException(Exception):
    id_: str
    message: str

@dataclasses.dataclass
class InsertApplicationException(Exception):
    mail: str
    message: str

@dataclasses.dataclass
class LatestApplicationException(Exception):
    message: str

@dataclasses.dataclass
class InsertFileException(Exception):
    hash_: str
    message: str

def parse_to_template(data: dict) -> TemplateParams:    
    return TemplateParams(
        sidebar_bg_color=data["sidebar_bg_color"],
        title_block_color=data["title_block_color"],
        content_block_color=data["content_block_color"],
        contacts=dict([(key.title(), value) for key, value in data["contacts"].items()]),
        qualities=data["qualities"],
        skills=data["skills"],
        about=data["about"],
        fullname=data["fullname"],
        job=data["job"],
        experiences=[Experience(**value) for value in data["experiences"]],
        trainings=[Experience(**value) for value in data["trainings"]],
        hobbies=[Hobby(**value) for value in data["hobbies"]]
    )

def random_color():
    #https://www.w3schools.com/colors/colors_groups.asp
    colors = [
        #BLUE
        "5F9EA0",
        "4682B4",
        "6495ED",
        "00BFFF",
        "1E90FF",
        "4169E1",
        "0000FF",
        "0000CD",
        "00008B",
        "000080",
        "191970",

        #RED
        "A52A2A",
        "A0522D",
        "8B4513",

        #BLACK/WHITE (SHADES)
        "000000",
        "2F4F4F",
        "708090",
        "778899",

        #GREEN
        "006400",
        "008000",
        "228B22"
    ]

    return colors[random.randint(0, len(colors) - 1)]

def resume_variation(original: TemplateParams, ollama: model.Model):
    template_copy = copy.deepcopy(original)
    
    rand_color = random_color()
    rephrase = lambda text : f"""
        In a resume context, reformulate this text in professional/polite in belgian french : {text}. 
        Output only the text and nothing else.
        This text is meant for direct use, do not output a template to be filled.
    """

    template_copy.sidebar_bg_color = rand_color
    template_copy.title_block_color = rand_color
    template_copy.content_block_color = rand_color

    template_copy.about = ollama.ask(rephrase(original.about))
    template_copy.experiences = [
        Experience(
            experience.title, 
            experience.company, 
            experience.date, 
            [ollama.ask(rephrase(learning)) for learning in experience.learnings]
        ) for experience in original.experiences
    ] 
    template_copy.trainings = [
        Experience(
            training.title, 
            training.company, 
            training.date, 
            [ollama.ask(rephrase(learning)) for learning in training.learnings]
        ) for training in original.trainings
    ]

    return template_copy

def filename_variation(company: str):
    version = lambda: str(random.randint(1, 10))
    date = lambda: str(26)
    enterprise = lambda: company.lower().strip().title().replace(" ", "_")

    examples: list[tuple[str, typing.Callable, typing.Callable]] = [
        ("cv.pdf", None, None),
        ("cvVXXYY.pdf", version, enterprise),
        ("cv_VXX_YY.pdf", version, enterprise),
        ("CV_VXX_YY.pdf", version, enterprise),
        ("cv_20XX_YY.pdf", date, enterprise),
        ("cv20XXYY.pdf", date, enterprise)
    ]
    
    template, ver_fn, enter_fn = examples[random.randint(0, len(examples) - 1)]

    if ver_fn:
        template = template.replace("XX", ver_fn())

    if enter_fn:
        template = template.replace("YY", enter_fn())

    return template

def title_variation(company: str, job: str):
    expertise = lambda: job.lower().strip().title()
    enterprise = lambda: company.lower().strip().title()

    examples: list[tuple[str, typing.Callable, typing.Callable]] = [
        ("Candidature spontanée – XX", expertise, None),
        ("Candidature spontanée – YY", None, enterprise),
        ("Candidature spontanée au sein de YY", None, enterprise),
        ("Candidature spontanée – Profil YY", None, enterprise),
        ("XX – Candidature spontanée", expertise, None),
        ("Recherche d’opportunité – XX", expertise, None),
        ("Profil XX disponible pour de nouvelles opportunités", expertise, None),
        ("À la recherche d’une opportunité en XX", expertise, None)
    ]

    template, exp_fn, enter_fn = examples[random.randint(0, len(examples) - 1)]

    if exp_fn:
        template = template.replace("XX", exp_fn())

    if enter_fn:
        template = template.replace("YY", enter_fn())

    return template

def fill_mail(template: str, fullname: str, job: str):
    return template.format(fullname=fullname, job=job)

def mail_variation(ollama: model.Model, mail: str):   
    rephrase = lambda text : f"""
        Reformulate this text in casual and polite in belgian french : {text}. 
        Output only the text and nothing else.
        This text is meant for direct use, do not output a template to be filled.
    """

    return ollama.ask(rephrase(mail))

def hash_file(filename: str):
    return hashlib.sha256(open(filename, "rb").read()).hexdigest()

def smart_load(to: list):
    success, fail = [], []
    
    for file in to:
        path = pathlib.Path(file)
        
        if not path.exists():
            fail.append(path)
            continue

        if path.match("*.json"):
            success.append(json.loads(path.read_text(encoding="UTF-8")))

        elif path.match("*.csv"):
            with open(path, 'r', encoding="UTF-8", newline='') as file:
                reader = csv.reader(file)
                next(reader)
                success.append([row for row in reader])

        elif path.match("*.txt"):
            success.append(path.read_text(encoding="UTF-8"))

        elif path.match("*.tex"):
            success.append(path.read_text(encoding="UTF-8"))

        else:
            raise NotImplemented(f"{path} extension not supported")

    return success, fail

def wait(sec: int):
    now = time.time()
    while time.time() - now < sec:
        pass

def gen_wait(limit: int, count: int):
    value = limit // count
    delta = value // 2

    return [round(random.uniform(value - delta, value + delta)) for _ in range(count + 1)]

def find_company(
    cursor: psycopg2.extensions.cursor, 
    dto: CompanyFindDTO
) -> typing.Optional[CompanyDB]:
    try:
        cursor.execute(
            """
            SELECT *
            FROM company
            WHERE number = %s;
            """, 
            (
                dto.number,
            )
        )

        data = cursor.fetchone()
    except Exception:
        return None

    return CompanyDB(*data) if data else None

def fetch_company(
    cursor: psycopg2.extensions.cursor, 
    dto: CompanyFetchDTO
) -> CompanyDB:
    try:
        cursor.execute(
            """
            SELECT *
            FROM company
            WHERE number = %s;
            """, 
            (
                dto.number,
            )
        )

        data = cursor.fetchone()
    except psycopg2.Error as error:
        raise FetchCompanyException(
            dto.number, 
            f"database error while finding company {dto.number}"
        )  from error

    if not data:
        raise FetchCompanyException(
            dto.number, 
            f"company {dto.number} not found"
        )
    
    return CompanyDB(*data)
    

def insert_company(
    cursor: psycopg2.extensions.cursor, 
    dto: CompanyInsertDTO
) -> CompanyDB:
    try:
        cursor.execute(
            """
            INSERT INTO company (number, name, city, classification, size, job, email) 
            VALUES (%s, %s, %s, %s, %s, %s, %s) 
            RETURNING *;
            """, 
            (
                dto.number, 
                dto.name, 
                dto.city, 
                dto.classification,
                dto.size, 
                dto.job, 
                dto.email
            )
        )

        data = cursor.fetchone()
    except psycopg2.Error as error:
        raise InsertCompanyException(
            dto.number, 
            f"database error while inserting company {dto.number}"
        )  from error

    if not data:
        raise InsertCompanyException(
            dto.number, 
            f"couldn't insert company {dto.number}"
        )
    
    return CompanyDB(*data)

def ensure_company(
    cursor: psycopg2.extensions.cursor, 
    dto: CompanyEnsureDTO
) -> CompanyDB:
    company = find_company(
        cursor, 
        CompanyFindDTO(
            dto.number
        )
    )
    
    if company:
        return company

    company = insert_company(
        cursor, 
        CompanyInsertDTO(
            dto.number,
            dto.name,
            dto.city,
            dto.classification,
            dto.size,
            dto.job,
            dto.email
        )
    )

    return company

def insert_application(
    cursor: psycopg2.extensions.cursor, 
    dto: ApplicationInsertDTO
) -> ApplicationDB:
    try:    
        cursor.execute(
            """
            INSERT INTO application (title, mail, sent_at, company_id) 
            VALUES (%s, %s, %s, %s)
            RETURNING *;
            """,
            (
                dto.title, 
                dto.mail, 
                datetime.datetime.fromtimestamp(dto.sent_at, datetime.UTC), 
                dto.company_id
            )
        )

        data = cursor.fetchone()
    except psycopg2.Error as error:
        raise InsertApplicationException(
            dto.mail, 
            f"database error while inserting application at {dto.mail}"
        )  from error

    if not data:
        raise InsertApplicationException(
            dto.mail, 
            f"couldn't insert application at {dto.mail}"
        )
    
    return ApplicationDB(*data)

def has_send_application(
    cursor: psycopg2.extensions.cursor,
    dto: ApplicationHasSendDTO
):
    try:
        cursor.execute(
            """
            SELECT *
            FROM application
            WHERE company_id = %s;
            """, 
            (
                dto.company_id,
            )
        )

        data = cursor.fetchone()
    except Exception:
        return None

    return ApplicationDB(*data) if data else None

def latest_application(
    cursor: psycopg2.extensions.cursor, 
) -> typing.Optional[ApplicationDB]:
    try:
        cursor.execute(
            """
            SELECT *
            FROM application
            ORDER BY id DESC
            LIMIT 1;
            """
        )

        data = cursor.fetchone()
    except psycopg2.Error as error:
        return None

    return ApplicationDB(*data) if data else None

def insert_file(
    cursor: psycopg2.extensions.cursor,
    dto: FileInsertDTO
) -> FileDB:
    try:
        cursor.execute(
            """
            INSERT INTO file (filename, hash, application_id) 
            VALUES (%s, %s, %s)
            RETURNING *;
            """,
            (
                dto.filename, 
                dto.hash_, 
                dto.application_id,
            )
        )

        data = cursor.fetchone()
    except psycopg2.Error as error:
        raise InsertFileException(
            dto.hash_, 
            f"database error while inserting file {dto.filename}"
        )  from error

    if not data:
        raise InsertFileException(
            dto.hash_,
            f"database error while inserting file {dto.filename}"
        )
    
    return FileDB(*data)

def run():
    import logging, datetime
    
    if not os.path.exists("logs"):
        os.mkdir("logs")

    if not os.path.exists("certification"):
        os.mkdir("certification")

    debug_log = f"./logs/run-{datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d_%H-%M-%S.%f+00-00")}.log"

    logging.basicConfig(
        filename=debug_log,
        filemode="w",
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s"
    )

    logger = logging.getLogger(__name__)

    need = [
        "config.json",
        "template.json",
        "template.tex",
        "mail-main.txt",
        "mail-second.txt",
        "me.json",
        "database.json",
        "data.csv"
    ]

    logger.info("loading all files...")
    success, fail = smart_load(need)

    if len(fail) > 0:
        raise Exception(f"failed to load : {fail}")

    (
        config_json,
        resume_json, 
        resume_tex, 
        mail_main_template,
        mail_seco_template,
        me_json, 
        database_json, 
        email_lines
    ) = success

    config = Config(**config_json)
    original = parse_to_template(resume_json)
    renderer = render.Render(resume_tex)
    mail_main_template = mail_main_template
    mail_seco_template = mail_seco_template
    me = Me(**me_json)
    postgress = psycopg2.connect(**database_json)
    database = [CompanyDB(*line) for line in email_lines]

    start_date = datetime.datetime.now()

    logger.info("loading ollama...")
    ollama = model.Model("localhost", "llama3.2:3b")

    postgress.set_client_encoding("UTF8")
    cursor = postgress.cursor()

    mail_count = random.randint(config.mail_min, config.mail_max)
    times = gen_wait(config.session_time, mail_count)

    if not os.path.exists("cvs"):
        os.mkdir("cvs")

    sended = 0
    skipped = 0
    index = 0

    logger.info("sending emails...")
    while sended < mail_count:
        try:            
            to_wait = times[mail_count]
            logger.info(f"waiting {to_wait} sec...")
            wait(to_wait)

            logger.info(f"processing company")
            company = database[index]
            
            has_send = has_send_application(
                cursor,
                ApplicationHasSendDTO(company.number)
            )
            
            if has_send:
                logger.info(f"already send application to {company.number}. Skipping...")
                skipped += 1
                index += 1
                continue

            company_db = ensure_company(
                cursor,
                CompanyEnsureDTO(
                    company.number,
                    company.name,
                    company.city,
                    company.classification,
                    company.size,
                    company.job,
                    company.email
                )
            )

            logger.info(f"processing mail...")
            title = title_variation(company.name, me.job)
            message = mail_variation(
                ollama, 
                fill_mail(
                    mail_main_template if company.classification == "MAIN" else mail_seco_template, 
                    me.fullname, 
                    company.job
                )
            )

            email = mail.base(me.email, "bl@dtd.be", title, message)

            logger.info(f"processing application...")
            application_db = insert_application(
                cursor, 
                ApplicationInsertDTO(
                    title, 
                    message,
                    datetime.datetime.now().timestamp(),
                    company_db.number
                )
            )

            if company.classification == "MAIN":
                logger.info(f"adding files to application")
                
                resume_filename = filename_variation(company.name)
                pdf_filename = renderer.do(resume_variation(original, ollama))

                watermark.print(
                    "attachment.pdf", 
                    "attestation.pdf", 
                    f"from {me.email} to {company.email}", 
                    28
                )

                email_files = [
                    (pdf_filename, resume_filename, f"./cvs/{resume_filename}"),
                    ("attestation.pdf", "attestation.pdf", f"./certification/attestation.pdf")
                ]

                for name, filename, path in email_files:
                    shutil.copy(name, path)

                    logger.info(f"inserting {path} into mail")

                    insert_file(
                        cursor, 
                        FileInsertDTO(
                            filename,
                            hash_file(path),
                            application_db.id_
                        )
                    )
                
                mail.add_files(email, [path for name, filename, path in email_files])

            logger.info(f"sending mail...")
            mail.send(email, me.email, me.password)

            postgress.commit()
            logger.info(f"sended email to {company.email}")

            sended += 1
        except Exception as error:
            postgress.rollback()
            logger.exception(error)

            error_email = mail.base(me.email, me.error_email, "HelicoTaffo Error", str(error))
            mail.add_file(email, debug_log)
            mail.send(error_email, me.email, me.password)

            skipped += 1
            continue

        index += 1

    finish_date = datetime.datetime.now()

    logger.info(f"""
        {index} company visited, 
        {sended} company contacted, 
        {skipped} company skipped,
        started at {start_date},
        finished at {finish_date}
    """)

    cursor.close()
    postgress.close()

if __name__ == "__main__":
    run()