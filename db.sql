DROP TABLE IF EXISTS file;
DROP TABLE IF EXISTS application;
DROP TABLE IF EXISTS company;

CREATE TABLE company (
    number VARCHAR PRIMARY KEY,
    name VARCHAR NOT NULL,
    city VARCHAR NOT NULL,
    classification VARCHAR  NOT NULL,
    size INT NOT NULL,
    job VARCHAR NOT NULL,
    email VARCHAR NOT NULL
);

CREATE TABLE application (
    id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    title VARCHAR NOT NULL,
    mail VARCHAR NOT NULL,
    sent_at TIMESTAMP NOT NULL,
    company_id VARCHAR REFERENCES company(number)
);

CREATE TABLE file (
    id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    filename VARCHAR,
    hash VARCHAR,
    application_id INT REFERENCES application(id)
);