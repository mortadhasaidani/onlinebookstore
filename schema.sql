
CREATE TABLE IF NOT EXISTS categories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    description TEXT NOT NULL
);


CREATE TABLE IF NOT EXISTS books (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    description TEXT NOT NULL,
    category_id INTEGER,
    url TEXT,
    nombre INTEGER NOT NULL,
    FOREIGN KEY (category_id) REFERENCES categories(id)
);

DROP TABLE USER;

CREATE TABLE IF NOT EXISTS USER (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username VARCHAR(20),
    password VARCHAR(20),
    nom VARCHAR(20),
    prenom VARCHAR(20),
    user_role VARCHAR(20)
);
