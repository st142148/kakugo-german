import sqlite3

#SQLite connection
def create_connection(db_file):
    print("connecting to database")
    conn = None
    try:
        conn = sqlite3.connect(db_file)
    except Error as e:
        print(e)
    print("…done")
    return conn


database = r"./dict_new.sqlite"
conn = create_connection(database)
with conn:
    cur = conn.cursor()
    with open("wadoku_filtered") as f:
        for l in f:
            id = l
            m = next(f).strip()
            cur.execute("UPDATE words SET meanings_de='" + m + "' WHERE id=" + id)