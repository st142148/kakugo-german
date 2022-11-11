import sqlite3
import sys
import time
from multiprocessing import Pool as ThreadPool

# In debug mode the only the first kakugo word is looked up single-threaded, with verbose terminal output
DEBUG = False
VOCAB_SEPERATOR = " | "

def create_connection(db_file):
    print("connecting to database")
    conn = None
    try:
        conn = sqlite3.connect(db_file)
    except Error as e:
        print(e)

    print("…done")
    return conn


wadoku = []
pool_no_results = []

def fetch_wadoku(row):
        global pool_no_results
        global wadoku

        result = ""

        # Seperating database entry
        id = row[0]
        kanji = row[1]
        hiragana = row[2]
        en = row[3]
        de = row[6]
        # Best wadoku result
        de_better_choice = []
        de_lesser_choice = []

        if DEBUG == True:
            print("kanji / hiragana / id / en / de ")
            print(kanji + " / " + hiragana + " / " + str(id) + " / " + en + " / " + de)
            print("----- WADOKU:")
            print("NT | ", end='')

        for line in wadoku:
            s = line.split()
            # remove symbols from phrases/prefixes/postfixes
            w_kanjis = s[0].replace('…', '').replace('。', '').split(';')
            w_hiragana = (s[1].replace('…', '').replace('。', ''))[1:-1]

            # Filter out some useless dictionary stuff then reassemble the first three meanings into a string
            meanings_de = []
            for i in range(2, len(s)):
                if '/' in s[i]:
                    o = " ".join(s[i:])
                    meanings_de = o[o.find('/')+1:-1].split('/')
                    meanings_de = VOCAB_SEPERATOR.join(meanings_de)
                    break

            # If no meaning is found.
            # Happens for some wadoku entries, but does not effect the kakugo words
            if meanings_de == [] or meanings_de == ['']:
                if DEBUG == True:
                    print("NO MEANING: " + str(s))
                continue

            if DEBUG == True:
                print(str(w_kanjis) + str(w_hiragana) + str(meanings_de), end='\r')

            # Check if wadoku entry fits
            if hiragana == w_hiragana:
                if kanji in w_kanjis: 
                    de_better_choice.append(meanings_de)
                    if DEBUG == True:
                        print("OK | ")
                    break
                elif hiragana in w_kanjis and de_better_choice == []:
                    de_lesser_choice.append(meanings_de)
                    if DEBUG == True:
                        print("OK | ")
                else:
                    if DEBUG == True:
                        print("ER | ", end='')
            else:
                if DEBUG == True:
                    print("ER | ", end='')
            
            # Make debug output readable
            if DEBUG == True:
                time.sleep(0.01)
        
        # information written to file for quality control and db injestion
        if de_better_choice != [] or de_lesser_choice != []:
            result += str(id) + "\n"
            result += kanji + " " + hiragana + "\n"
            result += en + "\n"
            result += de + "\n"
            for bc in de_better_choice:
                result += bc + "\n"
            if de_better_choice == []:
                for lc in de_lesser_choice:
                    result += lc + "\n"
        else:
            pool_no_results.append(row)

        return result

if __name__ == "__main__":
    print("wadoku extraction")

    print("Loading Wadoku")
    with open("./wadokudict2_20220703/wadokudict2", 'r+') as w_file:
        for line in w_file:
            wadoku.append(line)
    print("…done")

    database = r"./dict.sqlite"

    conn = create_connection(database)
    with conn:
        cur = conn.cursor()
        cur.execute("SELECT * FROM words")

        rows = cur.fetchall()

        if DEBUG == True:
            fetch_wadoku(rows[0])
            exit()

        pool = ThreadPool(10)
        results = pool.map(fetch_wadoku, rows)

        pool.close()
        pool.join()

        with open("wadoku_extract", 'w') as findings:
            for r in results:
                findings.write(r)

        print(str(len(pool_no_results)) + " words not found in wadoku")
        for no in pool_no_results:
            print(str(no))

