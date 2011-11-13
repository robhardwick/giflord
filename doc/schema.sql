CREATE TABLE images (
    id INTEGER PRIMARY KEY,
    url TEXT NOT NULL,
    referrer TEXT NOT NULL,
    hash TEXT NOT NULL,
    created INTEGER NOT NULL,
    updated INTEGER NOT NULL,
    UNIQUE(url)
);
