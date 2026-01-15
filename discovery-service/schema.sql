DROP TABLE IF EXISTS rooms;
CREATE TABLE rooms (
    uuid TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    url TEXT NOT NULL,
    metadata TEXT,
    last_seen INTEGER NOT NULL
);
