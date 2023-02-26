# Extracting the Kanji meanings from "Remembering the Kanji" by James W. Heisig
# Tested with the german version: ISBN 978-3-465-04157
# Initially written for Kakugo 1.36.2
# Could/Should work with others languages

import sys
import sqlite3

def print_help():
    print("Usage:")
    print("> python extractHeisig.py PDF [OPTION...] [-commit]")
    print("")
    print("     PDF    \"Remembering the Kanji\" in pdf format.")
    print("             When using text or kanji cache PDF does not have to be a valid file")
    print("")
    print("OPTIONS")
    print("     -lang LANG")
    print("             Select between DE and EN")
    print("             Defaults to DE")
    print("     -textDump FILE")
    print("             dump extracted text from pdf into file")
    print("     -textCache FILE")
    print("             read text from dumped cache, skipping the extraction")
    print("             PDF-file name must still be given, because I'm lazy")
    print("     -kanjiDump FILE")
    print("             dump extracted kanji definition file")
    print("     -kanjiCache FILE")
    print("             read kanji definition from dumped cache, skipping the extraction")
    print("")
    print("COMMITING")
    print("     -commit")
    print("             After checking the output for correctness write the information to the database")
    print("")


if len(sys.argv) < 2:
    print("ERROR: expected at least the file name of the pdf")
    print_help()
    exit()
elif len(sys.argv) % 2 != 0 and "-commit" not in sys.argv:
    print("ERROR: Argument missing")
    print_help()
    exit()


# Option parsing
# --------------
pdf_name = sys.argv[1]

lang             = ""
file_text_dump   = ""
file_text_cache  = ""
file_kanji_dump  = ""
file_kanji_cache = ""
commit           = False

for i in range(2, len(sys.argv)):
    o = sys.argv[i]
    if o == "-lang":
        a = sys.argv[i + 1]
        if a.startswith("-"):
            print("ERROR: Missing argument for \"-lang\"")
            exit()

        if a != "DE" and a != "EN":
            print("WARNING: Invalid language; defaulting to german.")
            print("Currently only tested with german (\"DE\") and english (\"EN\")")
            print("It probably does not even work with different versions of the german and english release.")
            lang = "DE"
        else:
            lang = a

    if o == "-textDump":
        a = sys.argv[i + 1]
        if a.startswith("-"):
            print("ERROR: Missing argument for \"-textDump\"")
            exit()
        print("Enabled text dump.")
        file_text_dump = a
    if o == "-textCache":
        a = sys.argv[i + 1]
        if a.startswith("-"):
            print("ERROR: Missing argument for \"-textCache\"")
            exit()
        print("Use text cache.")
        file_text_cache = a

    if o == "-kanjiDump":
        a = sys.argv[i + 1]
        if a.startswith("-"):
            print("ERROR: Missing argument for \"-kanjiDump\"")
            exit()
        print("Enabled kanji dump.")
        file_kanji_dump = a
    if o == "-kanjiCache":
        a = sys.argv[i + 1]
        if a.startswith("-"):
            print("ERROR: Missing argument for \"-kanjiCache\"")
            exit()
        print("Use kanji cache.")
        file_kanji_cache = a

    if o == "-commit":
        commit = True

if lang == "":
    print("WARNING: No language selected; defaulting to german")


# --------------
# Text and kanji
# meaning
# extraction
# --------------

# If kanji cache is provided use it and skip the rest
dict = {"kanji": [], "meaning": []}
if file_kanji_cache != "":
    try:
        with open("heisig_extract/" + file_kanji_cache, 'r', encoding='utf-8') as f:
            print("Reading text cache from \"" + file_kanji_cache + "\"")
            count = 1
            for l in f:
                dict["kanji"].append(l[:-1])
                dict["meaning"].append(next(f)[:-1])
                print(count, ": ", dict["kanji"][-1], ": ", dict["meaning"][-1])
                count += 1
    except EnvironmentError:
        print("ERROR: could not open " + file_kanji_cache + ". Trying other method.")

# Extract text from pdf
# Skip, if kanji cache is used
content = ""
if len(dict["kanji"]) == 0:
    if file_text_cache != "":
        try:
            with open("heisig_extract/" + file_text_cache, 'r', encoding='utf-8') as f:
                print("Reading text cache from \"" + file_text_cache + "\"")
                for l in f:
                    content += l
        except EnvironmentError:
            print("ERROR: could not open " + file_text_cache + ". Trying to extract from pdf again.")
    #print(content)

    # No text cache available, use PDF
    if content == "":
        try:
            from PyPDF2 import PdfFileReader
        except ImportError:
            print("ERROR: could not import PyPDF2. Please make shure it is installed correctly")

        print("Converting \"" + pdf_name + "\" to text...")

        try:
            with open(pdf_name, 'rb') as f:
                reader = PdfFileReader(f)
                # roughly skip introduction and index
                pages = len(reader.pages)
                for i in range(20, pages):
                    print("Page " + str(i) + "/" + str(pages), end='\r')
                    content += (reader.getPage(i).extract_text()) + "\n"
                print("Page " + str(pages) + "/" + str(pages))
        except EnvironmentError:
            print("ERROR: could not open " + pdf_name + ". Make shure the name is correct.")
            exit()
    print("... done!")

    # dump extracted text
    if file_text_dump != "":
        try:
            with open("heisig_extract/" + file_text_dump, 'w', encoding='utf-8') as f:
                print("Dumping extracted text to: " + file_text_dump + "\"")
                f.write(content)
        except EnvironmentError:
            print("ERROR: failed to dump extracted text to: \"" + file_text_dump + "\"")
        print("... done!")



    # Extract Kanji + Meaning from text
    dump = False
    dump_file = ""
    if file_kanji_dump != "":
        try:
            dump_file = open("heisig_extract/" + file_kanji_dump, 'w', encoding='utf-8')
            dump = True
        except EnvironmentError:
            print("WARNING: could not write to " + file_kanji_dump + ". Make shure the name is correct.")

    #dict = {"kanji": [], "meaning": []}
    next_kanji = 1
    current_line = -1
    content_iter = iter(content.splitlines())

    print("Starting kanji/meaning extraction...")

    # GERMAN DE
    # Structure: Number and meaning on one line, kanji on the next
    # Strategy: Detect number
    if lang == "DE":
        for l in content_iter:
            current_line += 1

            # l[1:] because of a rogue period at kanji 961
            stripped = l[1:].strip()
            substrings = stripped.split()

            if len(substrings) > 0 and substrings[0].isdigit():
                #in case a page number or similar is caught
                if int(substrings[0]) != next_kanji:
                    continue

                next_kanji += 1
                dict["meaning"].append(' '.join(substrings[1:]))
                next_line = next(content_iter).strip().split()
                current_line += 1
                dict["kanji"].append(next_line[0])

                print(next_kanji - 1, ": ", dict["kanji"][-1], ": ", dict["meaning"][-1])
                if dump == True:
                    dump_file.write(dict["kanji"][-1] + "\n")
                    dump_file.write(dict["meaning"][-1] + "\n")

                if next_kanji == 2201:
                    break

    # ENGLISH EN
    # Structure: Number, meaning and kanji on seperate lines after each other
    # Strategy: Detect the kanji number 
    elif lang == "EN":
        prev_line = ["", ""]
        for l in content_iter:
            current_line += 1

            stripped = l.strip()

            #print("P1: " + str(prev_line[1]))
            #print("P0: " + str(prev_line[0]))
            #print("CL: " + stripped)

            if len(stripped) == 1 and stripped >= '⼀' and stripped <= '拿':
                #print("Step 1 passed")
                if len(prev_line[1]) == 1:
                    #print("Step 2 passed")
                    if prev_line[1][0].isdigit() and int(prev_line[1][0]) == next_kanji:
                        #print("Step 3 passed")
                        if len(prev_line[0]) <= 4 and len(prev_line[0]) > 0:
                            #print("Step 4 passed")
                            if len(prev_line[0][0]) > 1:
                                #print("Step 5 passed")
                                next_kanji += 1
                                dict["meaning"].append(prev_line[0])
                                dict["kanji"].append(stripped)

                                print(next_kanji - 1, ": ", dict["kanji"][-1], ": ", dict["meaning"][-1])
                                if dump == True:
                                    dump_file.write(dict["kanji"][-1] + "\n")
                                    dump_file.write(dict["meaning"][-1] + "\n")

                                if next_kanji == 2201:
                                    break

            prev_line[1] = prev_line[0]
            prev_line[0] = stripped.split()

            #if current_line == 60:
            #    break

    print("... done")

    if dump == True:
        dump_file.close()

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

# Commit data to database
if commit == False:
    print("Extraction finished! \nIf you are happy with the result run the script with \"-commit\" to write the data to the database")
else:
    lang = lang.lower()

    database = r"./dict_new.sqlite"
    conn = create_connection(database)
    with conn:
        cur = conn.cursor()
        for i in range(0, len(dict["kanji"])):
            id = str(ord(dict["kanji"][i]))
            m = dict["meaning"][i]
            cur.execute("UPDATE kanjis SET meanings_" + lang + "='" + m + "' WHERE id=" + id)
