import os
import sys
import signal
import time

ABORT = False

def signal_handler(sig, frame):
    print("\nCtrl+C pressed. Saving and exiting on the next opportunity.")
    #global ABORT 
    #ABORT = True
    os.system("wmctrl -a Chromium; xdotool key Ctrl+w;")
    quit()
signal.signal(signal.SIGINT, signal_handler)

STATS = False

dic = dict()

if len(sys.argv) > 1:
    bookmark = int(sys.argv[1])

def select_definitions(d):
    for i in range(0, len(d)):
        print(str(i) + ": " + d[i])
    selection = input("Please select the desired translations (0-n, -1 to type your own):").split()
    def_list = []
    while len(selection) == 1:
        if selection[0] == "-1" or selection[0].isdigit():
            break
        selection = input("Invalid input; (0-n, -1 to type your own):").split()
    if int(selection[0]) == -1:
        def_list = input("Please type your comma-seperated list:").split(',')
    else:
        for s in selection:
            if s.isdigit() and int(s) < len(d):
                def_list.append(d[int(s)])

    print("Selection: " + str(def_list))
    done = input("Done?(y/n)")
    if done == "y" or done == "":
        return def_list
    else:
        return select_definitions(d)

with open("wadoku_extract", 'r', encoding='utf-8') as w:

    os.system("chromium 2>/dev/null &")
    time.sleep(5)
    os.system("wmctrl -a filterWadoku")
    
    f = open("wadoku_filtered", 'a+', encoding='utf-8', buffering=1)
    f.seek(0)
    for line in f:
        dic[line.strip()] = next(f).strip()    

    lines = w.readlines()

    line_count = 0

    word_count = 0

    # Just for statistics
    max_count   = 0
    mc_id       = 0
    more_than_ten = 0
    max_length  = 0
    ml_id       = 0
    one_to_one  = 0
    first_three = 0
    no_match    = 0
    no_old      = 0
    no_new      = 0
    multiple_new = 0

    while line_count + 4 < len(lines):
        if ABORT == True:
            break

        id     = lines[line_count][:-1]
        ja     = lines[line_count + 1][:-1]
        en     = lines[line_count + 2][:-1]
        de_old = lines[line_count + 3][:-1]
        de_new = []
        i = 4
        while True:
            if line_count + i >= len(lines):
                break
            if lines[line_count + i][:-1].isdigit():
                break
            de_new.append(lines[line_count + 4][:-1].split(" | "))
            i += 1

        line_count += i

        if id in dic:
            #f.write(id + '\n')
            #f.write(dic[id] + '\n')
            continue

        print("------------------------------------")
        print("ID: " + id)
        print(ja)
        print(en)
        print(de_old)
        #print(de_new)

        # Just collect statistics and print them
        if STATS == True:
            if de_old == "":
                no_old += 1
            if de_new == []:
                no_new += 1
            if de_old == de_new[0][0] and len(de_new[0]) == 1:
                one_to_one += 1
            if len(de_new) > 1:
                multiple_new += 1

            not_found = 1
            for d in de_new:
                if de_old in d[:3]:
                    first_three += 1
                    not_found = 0
                elif de_old in d:
                    not_found = 0
                if len(d) > max_count:
                    max_count = len(d)
                    mc_id = id
                if len(d) > 10:
                    more_than_ten += 1
                for dd in d:
                    if len(dd) > max_length:
                        max_length = len(dd)
                        ml_id = id

            no_match += not_found
            word_count += 1

        # Do the filtering
        else:
            if len(de_new) > 1:
                for d in de_new:
                    print(d)
                s = input("More than one match. Select wanted one:")
                de_new[0] = de_new[max(int(s), len(de_new) - 1)]

            #if de_old == de_new[0][0]:
            #    # 1 to 1 and done
            #    if len(de_new[0]) == 1:
            #        dic[id] = de_new[0][0] + '\n'
            #        #f.write(id + '\n')
            #        #f.write(de_new[0][0] + '\n')
            #        print(de_new[0][0])
            if de_old in de_new[0][:3]:
                # [0:3] to n; n < 5; probably only slight variations, take the first three
                if len(de_new[0]) < 7:
                    dic[id] = ' | '.join(de_new[0][:3])
                    f.write(id + '\n')
                    f.write(dic[id] + '\n')
                    print(' | '.join(de_new[0][:3]))
                # [0:3] to n; n > 5; probably multiple more distinct meanings, manual selection
                else:
                    os.system("chromium \"jisho.org/search/" + ja.split()[0] +"\"")
                    os.system("firefox \"duckduckgo.com/?q=" + ja.split()[0] +"&iar=images&iax=images&ia=images\"")
                    os.system("wmctrl -a filterWadoku")
                    dic[id] = ' | '.join(select_definitions(de_new[0]))
                    f.write(id + '\n')
                    f.write(dic[id] + '\n')
                    os.system("wmctrl -a Chromium; xdotool key Ctrl+w; wmctrl -a filterWadoku")
                    os.system("wmctrl -a firefox; xdotool key Ctrl+w; wmctrl -a filterWadoku")
                continue
            elif de_old in de_new[0]:
                # old entry is somewhere in the new list. correct meaning needs to be selected
                os.system("chromium \"jisho.org/search/" + ja.split()[0] +"\"")
                os.system("firefox \"duckduckgo.com/?q=" + ja.split()[0] +"&iar=images&iax=images&ia=images\"")
                os.system("wmctrl -a filterWadoku")
                dic[id] = ' | '.join(select_definitions(de_new[0]))
                f.write(id + '\n')
                f.write(dic[id] + '\n')
                os.system("wmctrl -a Chromium; xdotool key Ctrl+w; wmctrl -a filterWadoku")
                os.system("wmctrl -a firefox; xdotool key Ctrl+w; wmctrl -a filterWadoku")
            # no direct match
            else:
                # less than four variants; probably the right meaning
                if len(de_new[0]) <= 3:
                    dic[id] = ' | '.join(de_new[0][:3])
                    f.write(id + '\n')
                    f.write(dic[id] + '\n')
                    print(' | '.join(de_new[0][:3]))
                # more four or more variants; manual selection
                else:
                    os.system("chromium \"jisho.org/search/" + ja.split()[0] +"\"")
                    os.system("firefox \"duckduckgo.com/?q=" + ja.split()[0] +"&iar=images&iax=images&ia=images\"")
                    os.system("wmctrl -a filterWadoku")
                    dic[id] = ' | '.join(select_definitions(de_new[0]))
                    f.write(id + '\n')
                    f.write(dic[id] + '\n')
                    os.system("wmctrl -a Chromium; xdotool key Ctrl+w; wmctrl -a filterWadoku")
                    os.system("wmctrl -a firefox; xdotool key Ctrl+w; wmctrl -a filterWadoku")



            #print("ID: " + id)
            #print(ja)
            #print(en)
            #print(de_old)
            #print(de_new)

    #print("Saving progress")
    #for i in dic.items():
    #    f.write(i[0] + '\n')
    #    f.write(i[1] + '\n')
    #print("Done")

    os.system("wmctrl -a Chromium; xdotool key Ctrl+w;")

    if STATS == True:
        print("max_count :" + str(max_count))
        print("mc_id :" + str(mc_id))
        print("more_than_ten :" + str(more_than_ten))
        print("max_length :" + str(max_length))
        print("ml_id :" + str(ml_id))
        print("one_to_one :" + str(one_to_one))
        print("first_three :" + str(first_three))
        print("no_match :" + str(no_match))
        print("no_old :" + str(no_old))
        print("no_new :" + str(no_new))
        print("multiple_new :" + str(multiple_new))
        print("word_count: " + str(word_count))


