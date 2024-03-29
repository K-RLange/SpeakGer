import pickle
import re
import os
import datetime
import pandas as pd
import locale
from pathlib import Path
locale.setlocale(locale.LC_TIME, "de_DE.UTF-8")

# <editor-fold desc="RegEx Patterns">

days = ["montag", "dienstag", "mittwoch", "donnerstag", "freitag", "samstag", "sonntag"]
months = ['januar', 'februar', 'märz', 'april', 'mai', 'juni', 'juli', 'august', 'september', 'oktober',
          'november', 'dezember']
months_preset = ["0"] * 9 + [""] * 3

session_date_patterns = re.compile("|".join(
    [
        r"\A\d+(\.|,|;|:|\s)+sitzung\s+(am|vom)*\s*\d+(.*)",
        r"(\.|,|;|:)?\s*(montag|dienstag|mittwoch|donnerstag|freitag|samstag|sonntag)(\.|,|;|:)+\s*\d+(\.\s*|\s)(\w+\s|\d+.)\d+(\s*,\s*\d+\s*uhr)?",
        r"\A\s*\d+(\s|\.|,|;)+\d+(\s|\.|,|;|:)+\d+\s*$",
        r"wahlperiode\s*\d+\s*(\s|\.|,|;|:)+\d+(\s|\.|,|;|:)+\d+\s*$",
        r"\A\s*\d+(\s|\.|,|;|:)+(" + "|".join([month for month in months]) + ")(\s+|\.|,|;|:)\d+\s*$",
        r"\A(\s|am)*(dem|den|" + "|".join([day for day in days]) + ")*\d+(\s+|\.|,|;|:)+(" +
            "|".join([month for month in months]) + "|".join([str(x) for x in range(13)]) + ")(\s+|\.|,|;|:)+\d+"
    ]
))

start_patterns = re.compile('|'.join(
    [r'sitzung(.| )ist eröffnet',
     r'eröffne ich (hiermit )?die sitzung',
     r"(er)?öffne(t)? die (\d+|erste )?sitzung",
     r'(er)?öffne(t)? die (\d+|erste )',
     r'sitzung für eröffnet',
     r"(I|i)ch begrüße Sie",
     r'(m|M)eine damen',
     r"(M|m)eine herren",
     r"damen und herren",
     r"meine sehr ver",
     r"(i|I)n die tagesordnung ein",
     r"treten in die",
     r"(m|M)eine sehr verehrten",
     r"sehr (verehrte|geehrte)",
     r"(b|B)eginn(;|:)",
     r"(präsident|präsidentin|vizepräsident|vizepräsidentin|prlsdentln|präskdent|peksidenr|präsigent|prasidem|präskdere)(:| \w+:|;| \w;) \w+"]
))

end_patterns = re.compile('|'.join(
    [r'(schluß|schluss|sckluß|sckuss) der sitzung',
     r'si(l|t)zung ist (damit |hiermit)?geschlossen',
     r"schlie(ß|b|B|ss)e (damit )?die.*si(l|t)zung",
     r"(schluß|schluss|sckluß|sckuss).?\s*\d+.\d+\s*u(k|h)r",
     r"ende.?\s*\d+.\d+\s*uhr",
     r"ende der.*si(l|t)zung",
     ]))
# </editor-fold>

# <editor-fold desc="Functions">


#Ideen:
# stelle präsident -- stelle kommt durch stellv. -- ersetzen
# pos durch pds ersetzen wenn nach 1988 und vor 2008

def get_date_from_line(line):
    line = re.sub(r"\s+", " ", line).strip()
    line = line.replace(".", ".").replace(",", ".")
    for month in months:
        index = months.index(month)
        line = line.replace(month, months_preset[index] + str(index + 1))
    line = re.sub(r"\.+", ".", re.sub(r"\s+", ".", line))
    date = re.search(r"\d+.\d+.\d+", line)
    if date:
        date = date.group(0)
        try:
            if len(date.split(".")[-1]) == 4:
                date = datetime.datetime.strptime(date, "%d.%m.%Y")
            elif len(date.split(".")[-1]) == 2:
                date = datetime.datetime.strptime(date, "%d.%m.%y")
            else:
                return "unknown"
            return date
        except:
            # print(line)
            return "unknown"
    else:
        return "unknown"


#Hier werden erstmal nur die Sitzungen gesplittet, nicht die Reden!
def split_texts(full_texts, single_text=True, file=""):
    """Cuts of the table of contents and appendix of a session"""
    full_texts = "\n".join(full_texts)
    full_texts = full_texts.replace("-\n", "")
    if not single_text:
        split_text = [full_texts.split("\n")]
    else:
        if isinstance(full_texts, list):
            split_text = list(map(lambda x: x.split("\n"), full_texts))
        else:
            split_text = [full_texts.split("\n")]
    list_of_docs = []
    for text in split_text:
        date = "unknown"
        session_number = "unknown"
        periode = "unknown"
        started = False
        sitzung = False
        current_doc = ""
        for line_index, line in enumerate(text):
            if "11111111111111111111111111111111111111111111111111111111111111!11111111111111111111111111111111111111111111111111111111111111111111111111 " in line:
                print(line)
            if line:
                lower_line = line.lower()
                if '                                       Hessischer Landtag  ·  18. Wahlperiode  ·  116. Sitzung  ·  6. September 2012' in line:
                    continue
                if "                                       Hessischer Landtag  ·  18. Wahlperiode  ·  114. Sitzung  ·  4. September 2012" in line:
                    continue
                if re.search(r"Hessischer Landtag.*\d+. Wahlperiode.*\d+. Sitzung.*\d. (September|Juni) 2012", line):
                    continue
                if session_date_patterns.search(lower_line):
                    if date == "unknown":
                        date = get_date_from_line(lower_line)
                        #print(date)
                        continue
                reg_too_many_spaces = re.match(r"(\w\s){2,}", line)
                if reg_too_many_spaces:
                    line = line.replace(reg_too_many_spaces.group(0).rstrip(), "".join([x for x in reg_too_many_spaces.group(0).rstrip() if x.isalpha()]))
                line = line.replace("\x01", " ").replace("\x02", " ")
                start = start_patterns.search(lower_line)
                end = end_patterns.search(lower_line)
                if start and not sitzung:
                    sitzung = True
                    if not re.search(re.compile("(eröffent|eröffnet) die sitzung um"), lower_line):
                        if line[-1] == "-":
                            current_doc += line
                        else:
                            current_doc += line + "\n"
                    started = True
                    continue
                elif end and sitzung and current_doc:
                    list_of_docs.append({"date": date, "period": periode, "session": session_number, "doc": current_doc, "file": file})
                    current_doc = ""
                    temp_end = end
                    if not single_text:
                        sitzung = False
                    continue
                elif end:
                    temp_end = line_index
                elif sitzung:
                    if len(line) > 1:
                        if line[-1] == "-":
                            current_doc += line[0:-1]
                        else:
                            current_doc += line + "\n"
        if current_doc and not single_text:
            list_of_docs.append({"date": date, "period": periode, "session": session_number, "doc": current_doc, "file": file})
        elif not started:
            try:
                list_of_docs.append({"date": date, "period": periode, "session": session_number, "doc": " ".join(text)[min(1000, round(len(text)/2)):temp_end], "file": file})
            except:
                list_of_docs.append({"date": date, "period": periode, "session": session_number, "doc": " ".join(text)[min(1000, round(len(text)/2)):-100], "file": file})
    if not list_of_docs:
        try:
            if started:
                list_of_docs.append({"date": date, "period": periode, "session": session_number, "doc": current_doc[0:max(-10000, -len(current_doc)/5)], "file": file})
            else:
                list_of_docs = [{"date": date, "period": periode, "session": session_number, "doc": "\n".join(full_texts)}]
        except:
            list_of_docs = [{"date": "unknown", "period": "unknown", "session": "unknown", "doc": "\n".join(full_texts)}]
    if single_text:
        list_of_docs = [{"date": date, "period": periode, "session": session_number, "doc": "\n".join([x["doc"] for x in list_of_docs])}]
    docs_old = pd.DataFrame(list_of_docs)
    return docs_old
# </editor-fold>

# <editor-fold desc="Execution and date/session correction">
#Baden-Württemberg has a different procedure as the pdf-files contained multiple plenary sessions at once
def cut_off(state):
    def get_period_from_file(file):
        """Get the period and session number from a file name. Special cases if the parliament is Bayern or it is an early legislative period of Baden-Württemberg"""
        try:
            if state == "BWOld":
                if re.search("\D*([\d]+)-([\d]+).pickle", file):
                    return {"date": datetime.datetime(int(re.search("\D*([\d]+)-([\d]+).pickle", file).group(1)), 10, 1), "period": "unknown", "session": "unknown"}
                else:
                    return {"date": datetime.datetime(int(re.search("\D*([\d]+).pickle", file).group(1)), 4, 1), "period": "unknown", "session": "unknown"}
            elif "Bayern" in state:
                reg = re.search(r"\D*([\d-]+)\D+([\d-]+)\D*.*.pickle", file)
                if reg:
                    date = datetime.datetime.strptime(reg.group(2), "%d%m%y")
                    if date.year > 2023:
                        date = date.replace(year=date.year - 100)
                    return {"date": date, "period": "unknown", "session": int(reg.group(1))}
                else:
                    print(reg)
                    return {"date": "unknown", "period": "unknown", "session": "unknown"}
            else:
                reg = re.search("\D*(\d+)_(\d+).pickle", file)
            return {"date": "unknown", "period": int(reg.group(1)), "session": int(reg.group(2))}
        except:
            return {"date": "unknown", "period": "unknown", "session": "unknown"}

    path = f"ocr/{state}/"
    files = os.listdir(path)
    full_data = []
    for x in files:
        id = get_period_from_file(x)
        id = f"{id['period']}_{id['session']}"
        if not os.path.isfile(f"clean/{state}/{id}.json") or state == "Bayern":
            data = pickle.load(open(path + x, "rb"))
            split_data = split_texts(data, file=x)
            split_data["file"] = x
            full_data.append(split_data)
    full_data = pd.concat(full_data, ignore_index=True)

    #print(full_data["date"])
    true_periods = list(map(get_period_from_file, full_data["file"]))
    for x in range(len(full_data)):
        for key in true_periods[x].keys():
            #full_data[key].iloc[x] = true_periods[x][key]
            if true_periods[x][key] != "unknown":
                full_data[key].iloc[x] = true_periods[x][key]

    if state == "Bayern":
        full_data = full_data.sort_values("date")
        period = 2
        for x in range(len(full_data) - 1):
            full_data["period"].iloc[x] = period
            if full_data["session"].iloc[x+1] < full_data["session"].iloc[x]:
                if full_data["session"].iloc[x+2] < full_data["session"].iloc[x]:
                    period += 1
        full_data["period"].iloc[len(full_data)-1] = period



    try:
        full_data = full_data.sort_values("date")
    except:
        full_data = full_data.sort_values(["period", "session"])
    full_data = full_data.set_index("file")
    path = Path("clean")
    path.mkdir(parents=True, exist_ok=True)
    pickle.dump(full_data, open("clean/" + state + ".pickle", "wb"))
# </editor-fold>