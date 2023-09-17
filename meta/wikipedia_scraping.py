import pickle
#Last 15.09.1935
import pandas as pd
import requests
from bs4 import BeautifulSoup
import re
from tqdm import tqdm
import numpy as np


def get_website(url):
    website = requests.get(url)
    results = BeautifulSoup(website.content, 'html.parser')
    return results


def label_parties(data):
    for df in data:
        orientation = []
        parties = []
        df["Party"] = list(map(lambda x: "".join([char for char in x if char.isalpha()]).lower(), df["Party"]))
        for a, b in df.iterrows():
            if "spd" in b["Party"] or "sps" in b["Party"] or "shb" in b["Party"]:
                orientation.append("sozialdemokratisch")
                parties.append("spd")
            elif "die partei" in b["Party"] or "piraten" in b["Party"]\
                or "ddu" in b["Party"]:
                orientation.append("sozialdemokratisch")
                parties.append(b["Party"])
            elif "afd" in b["Party"] or "dvu" in b["Party"] \
                    or "bp" in b["Party"] or "npd" in b["Party"] or "rep" in b["Party"]\
                    or "rechtsstaatlicher offensive" in b["Party"] or "nlp" in b["Party"]\
                    or "drp" in b["Party"] or "dsp" in b["Party"]\
                    or 'svp (ehemals npd)' in b["Party"] or "biw" in b["Party"]:
                orientation.append("rechtspopulistisch/extrem")
                parties.append(b["Party"])
            elif "bündnis 90" in b["Party"] or "grüne" in b["Party"] \
                    or "gal" in b["Party"] or "neues forum" in b["Party"]\
                    or "bgl" in b["Party"]:
                orientation.append("grün")
                if "bündnis 90" in b["Party"] or "grüne" in b["Party"]:
                    parties.append("die grünen")
                else:
                    parties.append(b["Party"])
            elif "linke" in b["Party"] or "pds" in b["Party"] or "al" in b["Party"]:
                orientation.append("linkspopulistisch/extrem")
                if "al" in b["Party"]:
                    parties.append("sonstige")
                else:
                    parties.append("linke/pds/sed")
            elif "ssw" in b["Party"] or "fdp" in b["Party"] \
                    or "fdv" in b["Party"] or "dps" in b["Party"] \
                    or "bvb" in b["Party"] or "fw" in b["Party"] \
                    or "statt partei" in b["Party"] or "rsf" in b["Party"]\
                    or "lpd" in b["Party"] or "freie wähler" in b["Party"]\
                    or "bdv" in b["Party"]:
                orientation.append("liberal")
                parties.append(b["Party"])
            elif "zentrum" in b["Party"] or "cdu" in b["Party"] \
                    or "csu" in b["Party"] or "lkr" in b["Party"] \
                    or "bvp" in b["Party"] or "dsu" in b["Party"] \
                    or "bhe" in b["Party"] or "gdp" in b["Party"]\
                    or "hamburg-block" in b["Party"] or "dp" in b["Party"]\
                    or "mitte" in b["Party"] or "cvp" in b["Party"]\
                    or "svp" in b["Party"] or "lkr" in b["Party"]:
                orientation.append("konservativ")
                if "cdu" in b["Party"] or "cvp" in b["Party"]:
                    parties.append("cdu")
                elif "csu" in b["Party"]:
                    parties.append("csu")
                else:
                    parties.append(b["Party"])
            elif "kpd" in b["Party"] or "dkp" in b["Party"] or "kp" in b["Party"]:
                orientation.append("kommunistisch")
                parties.append("kpd/dkp")
            elif "dp" in b["Party"]:
                orientation.append("rechtspopulistisch/extrem")
                parties.append("dp")
            else:
                orientation.append("sonstiges")
                parties.append(b["Party"])
        df["political_orientation"] = orientation
        df["Party"] = parties
    return data

def get_base_in_table(elem):
    split_elem = [x.text for x in elem.find_all("th")]
    #split_elem = [x for x in split_elem if x!= ""]
    name_base = np.where(["Name" in x or "name" in x or "Mitglied" in x or "Abgeordneter" in x for x in split_elem])[0][0]
    party_base = np.where(["Partei" in x or "Fraktion" in x for x in split_elem])[0][0]
    born_base = np.where(["Leben" in x or "geb." in x or "Geb" in x or "*" == x for x in split_elem])[0]
    constituency_base = np.where(["Kreis" in x or "kreis" in x for x in split_elem])[0]
    return name_base, party_base, born_base, constituency_base

def get_data_from_elem(elem, name_base, party_base, born_base, constituency_base):
    global current_members
    split_elem = elem.find_all("td")
    split_elem = [x.text.lstrip().rstrip().replace("\n", "") for x in split_elem]  # if len(x) > 0]
    name = split_elem[name_base].split(" ")
    current_members["First Name"].append(" ".join(name[0:(len(name) - 1)]).lower())
    current_members["Last Name"].append(name[len(name) - 1].lower())
    try:
        current_members["Party"].append(split_elem[party_base].lower())
    except:
        current_members["Party"].append("")
    if born_base:
        try:
            if split_elem[born_base[0]][0] == "*":
                current_members["Born"].append(int(split_elem[born_base[0]].lower()[2:6]))
            else:
                current_members["Born"].append(int(split_elem[born_base[0]].lower()[0:4]))
        except:
            current_members["Born"].append(-1)
    else:
        current_members["Born"].append(-1)
    if len(constituency_base) > 1:
        current_members["Constituency"].append(split_elem[constituency_base[0]] + ", " + split_elem[constituency_base[1]])
    elif len(constituency_base) > 0:
        current_members["Constituency"].append(split_elem[constituency_base[0]])
    else:
        current_members["Constituency"].append("")
    try:
        current_members["Link"].append(
            "https://de.wikipedia.org/" + re.search(r'a href="(.*?)"', str(elem)).group(1))
    except:
        current_members["Link"].append("")

#------------------------------------------------------------------
# <editor-fold desc="Bundesrepublik">
brd_politicians = []
for periode in range(1, 21):
    count = 0
    url = "https://de.wikipedia.org/wiki/Liste_der_Mitglieder_des_Deutschen_Bundestages_({}._Wahlperiode)".format(periode)
    results = get_website(url)
    current_members = {"First Name": [], "Last Name": [], "Born": [], "Party": [], "Constituency": []}
    data = results.find_all("table")
    if periode > 19:
        data = data[len(data) - 2].find("tbody")
        base = 0
    elif periode > 18:
        data = data[len(data) - 3].find("tbody")
        base = 0
    else:
        data = data[len(data) - 1].find("tbody")
        base = 0
    for elem in data.find_all("tr"):
        if count == 0:
            count += 1
        else:
            split_elem = elem.text.split("\n")
            split_elem = [x.lstrip().rstrip() for x in split_elem if len(x) > 0]
            name = split_elem[base].split(" ")
            current_members["First Name"].append(" ".join(name[0:(len(name) - 1)]))
            current_members["Last Name"].append(name[len(name) - 1])
            current_members["Party"].append(split_elem[base + 2])
            current_members["Born"].append(split_elem[base + 1][0:4])
            current_members["Constituency"].append(split_elem[base + 3])
    brd_politicians.append(pd.DataFrame(current_members))

for df in brd_politicians:
    orientation = []
    df["Party"] = list(map(lambda x: "".join([char for char in x if char.isalpha()]).lower(), df["Party"]))
    for a, b in df.iterrows():
        if "sdp" in b["Party"]:
            orientation.append("sozialdemokratisch")
        elif "afd" in b["Party"] or "dp" in b["Party"] \
                or "bp" in b["Party"]:
            orientation.append("rechtspopulistisch")
            b["Party"] = "afd"
        elif "die partei" in b["Party"]:
            orientation.append("linksliberal")
            b["Party"] = "sonstige"
        elif "kpd" in b["Party"] or "dkp" in b["Party"]:
            orientation.append("kommunistisch")
        elif "bündnis 90" in b["Party"] or "grüne" in b["Party"]:
            orientation.append("grün")
            b["Party"] = "die grünen"
        elif "linke" in b["Party"] or "pds" in b["Party"] or "al" in b["Party"]:
            orientation.append("linkspopulistisch")
            if "al" in b["Party"]:
                b["Party"] = "sonstige"
            b["Party"] = "linke/pds"
        elif "ssw" in b["Party"] or "fdp" in b["Party"] \
                or "fdv" in b["Party"] or "dps" in b["Party"]:
            orientation.append("liberal")
            if "fdp" not in b["Party"]:
                b["Party"] = "sonstige"
        elif "zentrum" in b["Party"] or "cdu" in b["Party"] \
                or "csu" in b["Party"] or "lkr" in b["Party"] \
                or "bvp" in b["Party"] or "dsu" in b["Party"] \
                or "gb/bhe" in b["Party"]:
            orientation.append("konservativ")
            if "cdu" in b["Party"]:
                if "csu" in b["Party"]:
                    if b["Party"].count("cdu") == 2:
                        b["Party"] = "cdu"
                    else:
                        b["Party"] = "csu"
                else:
                    b["Party"] = "cdu"
            elif "csu" in b["Party"]:
                b["Party"] = "csu"
            else:
                b["Party"] = "sonstige"
        else:
            orientation.append("sonstiges")


        if b["Party"] not in parties:
            b["Party"] = "sonstiges"
        if b["Constituency"] not in places:
            b["Constituency"] = "sonstiges"
    df["political_orientation"] = orientation

pickle.dump(brd_politicians, open("politiker/brd.pickle", "wb"))

general_url = "https://de.wikipedia.org/wiki/Liste_der_Mitglieder_des_Deutschen_Bundestages_({}._Wahlperiode)"
brd_politicians = []
for periode in range(1, 21):
    count = 0
    url = general_url.format(periode)
    results = get_website(url)
    current_members = {"First Name": [], "Last Name": [], "Born": [], "Party": [], "Period": [], "Constituency": [], "Link": []}
    base_text = results.find_all("p")[0].text
    orig_data = results.find_all("table")
    list_data = [x.find("tbody") for x in orig_data if ("Name" in x.find_all("tr")[0].text or "Mitglied des" in x.find_all("tr")[0].text)
                 and "abgegebene Stimmen" not in x.find_all("tr")[0].text]

    for data in list_data:
        count = 0
        for elem in data.find_all("tr"):
            if count == 0:
                name_base, party_base, born_base, constituency_base = get_base_in_table(elem)
                count += 1
            else:
                current_members["Period"].append(periode)
                if elem.text == "\nManfred Wimmer (Eggenfelden)\n1937–1993\nSPD\nBayern\n":
                    current_members["First Name"].append("Manfred")
                    current_members["Last Name"].append("Wimmer")
                    current_members["Born"].append("1937")
                    current_members["Party"].append("SPD")
                    current_members["Constituency"].append("Bayern")
                    current_members["Link"].append("https://de.wikipedia.org/wiki/Manfred_Wimmer")
                    continue
                get_data_from_elem(elem, name_base, party_base, born_base, constituency_base)
    if len(current_members["First Name"]) == 0:
        print(periode)
    brd_politicians.append(pd.DataFrame(current_members))
brd_politicians = label_parties(brd_politicians)
brd = pd.concat(brd_politicians)
pickle.dump(brd, open("politiker/brd.pickle", "wb"))
# </editor-fold>
#------------------------------------------------------------------
# <editor-fold desc="Bayern">
general_url = "https://de.wikipedia.org/wiki/Liste_der_Mitglieder_des_Bayerischen_Landtags_({}._Wahlperiode)"
bayern_politicians = []
for periode in range(1, 19):
    url = general_url.format(periode)
    results = get_website(url)
    current_members = {"First Name": [], "Last Name": [], "Born": [], "Party": [], "Period": [], "Constituency": [], "Link": []}
    base_text = results.find_all("p")[0].text
    orig_data = results.find_all("table")
    list_data = [x.find("tbody") for x in orig_data if "Name" in x.find_all("tr")[0].text or "Mitglied des" in x.find_all("tr")[0].text]
    #list_data = [orig_data[len(orig_data) - 1].find("tbody")]
    #if periode > 16:
    #    list_data.append(orig_data[len(orig_data) - 2].find("tbody"))
    base = 0
    for data in list_data:
        count = 0
        for elem in data.find_all("tr"):
            if count == 0:
                name_base, party_base, born_base, constituency_base = get_base_in_table(elem)
                count += 1
            else:
                current_members["Period"].append(periode)
                get_data_from_elem(elem, name_base, party_base, born_base, constituency_base)
    bayern_politicians.append(pd.DataFrame(current_members))


bayern_politicians = label_parties(bayern_politicians)
bayern = pd.concat(bayern_politicians)
pickle.dump(bayern, open("politiker/bayern.pickle", "wb"))
# </editor-fold>
#------------------------------------------------------------------
# <editor-fold desc="Berlin">
general_url = "https://de.wikipedia.org/wiki/Liste_der_Mitglieder_des_Abgeordnetenhauses_von_Berlin_({}._Wahlperiode)"
berlin_politicians = []
for periode in range(1, 20):
    count = 0
    url = general_url.format(periode)
    results = get_website(url)
    current_members = {"First Name": [], "Last Name": [], "Born": [], "Party": [], "Period": [], "Constituency": [], "Link": []}
    base_text = results.find_all("p")[0].text
    orig_data = results.find_all("table")
    list_data = [x.find("tbody") for x in orig_data if "Name" in x.find_all("tr")[0].text or "Mitglied des" in x.find_all("tr")[0].text]

    for data in list_data:
        count = 0
        for elem in data.find_all("tr"):
            if count == 0:
                name_base, party_base, born_base, constituency_base = get_base_in_table(elem)
                count += 1
            else:
                current_members["Period"].append(periode)
                get_data_from_elem(elem, name_base, party_base, born_base, constituency_base)
    if len(current_members["First Name"]) == 0:
        print(periode)
    berlin_politicians.append(pd.DataFrame(current_members))

berlin_politicians = label_parties(berlin_politicians)
berlin = pd.concat(berlin_politicians)
pickle.dump(berlin, open("politiker/berlin.pickle", "wb"))
# </editor-fold>
#------------------------------------------------------------------
# <editor-fold desc="Brandenburg">
general_url = "https://de.wikipedia.org/wiki/Liste_der_Mitglieder_des_Landtags_Brandenburg_({}._Wahlperiode)"
brandenburg_politicians = []
for periode in range(1, 8):
    url = general_url.format(periode)
    results = get_website(url)
    current_members = {"First Name": [], "Last Name": [], "Born": [], "Party": [], "Period": [], "Constituency": [], "Link": []}
    base_text = results.find_all("p")[0].text
    orig_data = results.find_all("table")
    list_data = [x.find("tbody") for x in orig_data if "Name" in x.find_all("tr")[0].text or "Mitglied" in x.find_all("tr")[0].text]
    for data in list_data:
        count = 0
        for elem in data.find_all("tr"):
            if count == 0:
                name_base, party_base, born_base, constituency_base = get_base_in_table(elem)
                count += 1
            else:
                current_members["Period"].append(periode)
                get_data_from_elem(elem, name_base, party_base, born_base, constituency_base)
    brandenburg_politicians.append(pd.DataFrame(current_members))


brandenburg_politicians = label_parties(brandenburg_politicians)
brandenburg = pd.concat(brandenburg_politicians)
pickle.dump(brandenburg, open("politiker/brandenburg.pickle", "wb"))
# </editor-fold>
#------------------------------------------------------------------
# <editor-fold desc="Bremen">
general_url = "https://de.wikipedia.org/wiki/Liste_der_Mitglieder_der_Bremischen_B%C3%BCrgerschaft_({}._Wahlperiode)"
bremen_politicians = []
for periode in range(1, 21):
    url = general_url.format(periode)
    results = get_website(url)
    current_members = {"First Name": [], "Last Name": [], "Born": [], "Party": [], "Period": [], "Constituency": [], "Link": []}
    base_text = results.find_all("p")[0].text
    if periode == 8 or periode == 7:
        sub_res = results.find("div", id="mw-content-text").find_all("ul")
        for buchstabe in sub_res[2:(len(sub_res) - 4)]:
            text = buchstabe.find_all("li")
            #text = buchstabe.text.split("\n")
            for elem in text:
                try:
                    current_members["Link"].append(
                        "https://de.wikipedia.org/" + re.search(r'a href="(.*?)"', str(elem)).group(1))
                except:
                    current_members["Link"].append("")
                elem = elem.text
                current_members["Last Name"].append(elem[0:elem.index(",")].lower())
                current_members["First Name"].append(elem[(elem.index(",")+1):elem.index("(")])
                current_members["Party"].append(elem[(elem.index("(")+1):elem.index(")")])
                current_members["Born"].append("unknown")
                current_members["Period"].append(periode)
                current_members["Constituency"].append("")

        bremen_politicians.append(pd.DataFrame(current_members))
        continue
    orig_data = results.find_all("table")
    list_data = [x.find("tbody") for x in orig_data if "Name" in x.find_all("tr")[0].text or "Mitglied" in x.find_all("tr")[0].text]
    for data in list_data:
        count = 0
        for elem in data.find_all("tr"):
            if count == 0:
                name_base, party_base, born_base, constituency_base = get_base_in_table(elem)
                count += 1
            else:
                current_members["Period"].append(periode)
                get_data_from_elem(elem, name_base, party_base, born_base, constituency_base)
    bremen_politicians.append(pd.DataFrame(current_members))
    #list_data = [orig_data[len(orig_data) - 1].find("tbody")]
    #if periode > 17:
    #    list_data.append(orig_data[len(orig_data) - 2].find("tbody"))
    #    if periode == 19:
    #        list_data.append(orig_data[len(orig_data) - 3].find("tbody"))
    #elif periode == 18:
    #    sub_res = results.find("div", id="mw-content-text").find_all("ul")
    #    for buchstabe in sub_res[2:(len(sub_res) - 4)]:
    #        text = buchstabe.text.split("\n")
    #        for elem in text:
    #            current_members["Party"].append(elem[(elem.index("(") + 1):elem.index(")")])
    #            split_elem = elem[0:(elem.index("(")-1)].split()
    #            current_members["Last Name"].append(split_elem[-1])
    #            current_members["First Name"].append(" ".join(split_elem[0:-1]))
    #            current_members["Born"].append("unknown")
    #            current_members["Period"].append(18)
    #base = 0
    #for data in list_data:
    #    count = 0
    #    for elem in data.find_all("tr"):
    #        if count == 0:
    #            count += 1
    #        else:
    #            split_elem = elem.text.split("\n")
    #            split_elem = [x.lstrip().rstrip() for x in split_elem if len(x) > 0]
    #            name = split_elem[base].split(" ")
    #            current_members["First Name"].append(" ".join(name[0:(len(name) - 1)]))
    #            current_members["Last Name"].append(name[len(name) - 1])
    #            if periode == 3:
    #                current_members["Party"].append(split_elem[base + 2])
    #                current_members["Born"].append(split_elem[base + 1])
    #            else:
    #                if periode == 20 and split_elem[1] != "CDU":
    #                    current_members["Party"].append(split_elem[base + 2])
    #                else:
    #                    current_members["Party"].append(split_elem[base + 1])
    #                current_members["Born"].append("unknown")
    #            current_members["Period"].append(periode)
    #    bremen_politicians.append(pd.DataFrame(current_members))

bremen_politicians = label_parties(bremen_politicians)
bremen = pd.concat(bremen_politicians)
pickle.dump(bremen, open("politiker/bremen.pickle", "wb"))
# </editor-fold>
#------------------------------------------------------------------
# <editor-fold desc="BW">
general_url = "https://de.wikipedia.org/wiki/Liste_der_Mitglieder_des_Landtags_von_Baden-W%C3%BCrttemberg_({}._Wahlperiode)"
bw_politicians = []
for periode in range(1, 18):
    url = general_url.format(periode)
    results = get_website(url)
    current_members = {"First Name": [], "Last Name": [], "Born": [], "Party": [], "Period": [], "Constituency": [],
                       "Link": []}
    base_text = results.find_all("p")[0].text
    orig_data = results.find_all("table")
    list_data = [x.find("tbody") for x in orig_data if
                 "Name" in x.find_all("tr")[0].text or "Mitglied" in x.find_all("tr")[0].text]
    for data in list_data:
        try:
            count = 0
            for elem in data.find_all("tr"):
                if count == 0:
                    name_base, party_base, born_base, constituency_base = get_base_in_table(elem)
                    count += 1
                else:
                    current_members["Period"].append(periode)
                    get_data_from_elem(elem, name_base, party_base, born_base, constituency_base)
        except:
            pass
    bw_politicians.append(pd.DataFrame(current_members))


bw_politicians = label_parties(bw_politicians)
bw = pd.concat(bw_politicians)
pickle.dump(bw, open("politiker/bw.pickle", "wb"))
# </editor-fold>
#------------------------------------------------------------------
# <editor-fold desc="Hamburg">
general_url = "https://de.wikipedia.org/wiki/Liste_der_Mitglieder_der_Hamburgischen_B%C3%BCrgerschaft_({}._Wahlperiode)"
hamburg_politicians = []
for periode in range(1, 23):
    url = general_url.format(periode)
    results = get_website(url)
    current_members = {"First Name": [], "Last Name": [], "Born": [], "Party": [], "Period": [], "Constituency": [],
                       "Link": []}
    base_text = results.find_all("p")[0].text
    orig_data = results.find_all("table")
    list_data = [x.find("tbody") for x in orig_data if
                 "Name" in x.find_all("tr")[0].text or "Mitglied" in x.find_all("tr")[0].text]
    for data in list_data:
        count = 0
        for elem in data.find_all("tr"):
            if count == 0:
                name_base, party_base, born_base, constituency_base = get_base_in_table(elem)
                count += 1
            else:
                current_members["Period"].append(periode)
                get_data_from_elem(elem, name_base, party_base, born_base, constituency_base)
    hamburg_politicians.append(pd.DataFrame(current_members))


hamburg_politicians = label_parties(hamburg_politicians)
hamburg = pd.concat(hamburg_politicians)
pickle.dump(hamburg, open("politiker/hamburg.pickle", "wb"))
# </editor-fold>
#------------------------------------------------------------------
# <editor-fold desc="Hessen">
general_url = "https://de.wikipedia.org/wiki/Liste_der_Mitglieder_des_Hessischen_Landtags_({}._Wahlperiode)"
hessen_politicians = []
for periode in range(1, 21):
    url = general_url.format(periode)
    results = get_website(url)
    current_members = {"First Name": [], "Last Name": [], "Born": [], "Party": [], "Period": [], "Constituency": [],
                       "Link": []}
    base_text = results.find_all("p")[0].text
    orig_data = results.find_all("table")
    list_data = [x.find("tbody") for x in orig_data if
                 "Name" in x.find_all("tr")[0].text or "Mitglied" in x.find_all("tr")[0].text]
    for data in list_data:
        count = 0
        for elem in data.find_all("tr"):
            if count == 0:
                name_base, party_base, born_base, constituency_base = get_base_in_table(elem)
                count += 1
            else:
                current_members["Period"].append(periode)
                get_data_from_elem(elem, name_base, party_base, born_base, constituency_base)
    hessen_politicians.append(pd.DataFrame(current_members))

hessen_politicians = label_parties(hessen_politicians)
hessen = pd.concat(hessen_politicians)
pickle.dump(hessen, open("politiker/hessen.pickle", "wb"))
# </editor-fold>
#------------------------------------------------------------------
# <editor-fold desc="Niedersachsen">
general_url = "https://de.wikipedia.org/wiki/Liste_der_Mitglieder_des_Nieders%C3%A4chsischen_Landtages_({}._Wahlperiode)"
ls_politicians = []
for periode in range(1, 19):
    url = general_url.format(periode)
    results = get_website(url)
    current_members = {"First Name": [], "Last Name": [], "Born": [], "Party": [], "Period": [], "Constituency": [],
                       "Link": []}
    base_text = results.find_all("p")[0].text
    orig_data = results.find_all("table")
    list_data = [x.find("tbody") for x in orig_data if
                 "Name" in x.find_all("tr")[0].text or "Mitglied" in x.find_all("tr")[0].text]
    for data in list_data:
        count = 0
        for elem in data.find_all("tr"):
            if count == 0:
                name_base, party_base, born_base, constituency_base = get_base_in_table(elem)
                count += 1
            else:
                current_members["Period"].append(periode)
                get_data_from_elem(elem, name_base, party_base, born_base, constituency_base)
    ls_politicians.append(pd.DataFrame(current_members))

ls_politicians = label_parties(ls_politicians)
ls = pd.concat(ls_politicians)
pickle.dump(ls, open("politiker/ls.pickle", "wb"))
# </editor-fold>
#------------------------------------------------------------------
# <editor-fold desc="NRW">
general_url = "https://de.wikipedia.org/wiki/Liste_der_Mitglieder_des_Landtages_Nordrhein-Westfalen_({}._Wahlperiode)"
nrw_politicians = []
for periode in range(1, 19):
    url = general_url.format(periode)
    results = get_website(url)
    current_members = {"First Name": [], "Last Name": [], "Born": [], "Party": [], "Period": [], "Constituency": [],
                       "Link": []}
    base_text = results.find_all("p")[0].text
    orig_data = results.find_all("table")
    list_data = [x.find("tbody") for x in orig_data if
                 "Name" in x.find_all("tr")[0].text or "Mitglied" in x.find_all("tr")[0].text]
    for data in list_data:
        count = 0
        for elem in data.find_all("tr"):
            if count == 0:
                name_base, party_base, born_base, constituency_base = get_base_in_table(elem)
                count += 1
            else:
                current_members["Period"].append(periode)
                get_data_from_elem(elem, name_base, party_base, born_base, constituency_base)
    nrw_politicians.append(pd.DataFrame(current_members))

nrw_politicians = label_parties(nrw_politicians)
nrw = pd.concat(nrw_politicians)
pickle.dump(nrw, open("politiker/nrw.pickle", "wb"))
# </editor-fold>
#------------------------------------------------------------------
# <editor-fold desc="RLP">
general_url = "https://de.wikipedia.org/wiki/Liste_der_Mitglieder_des_Landtages_Rheinland-Pfalz_({}._Wahlperiode)"
rlp_politicians = []
for periode in range(1, 19):
    url = general_url.format(periode)
    results = get_website(url)
    current_members = {"First Name": [], "Last Name": [], "Born": [], "Party": [], "Period": [], "Constituency": [], "Link": []}
    base_text = results.find_all("p")[0].text
    orig_data = results.find_all("table")
    #TODO Hier noch umarbeiten, wann welcher Abschnitt
    list_data = [x.find("tbody") for x in orig_data if "Name" in x.find_all("tr")[0].text]
    #TODO Base richtig?
    base = 0
    for data in list_data:
        count = 0
        for elem in data.find_all("tr"):
            if count == 0:
                name_base, party_base, born_base, constituency_base = get_base_in_table(elem)
                count += 1
            else:
                current_members["Period"].append(periode)
                get_data_from_elem(elem, name_base, party_base, born_base, constituency_base)
        rlp_politicians.append(pd.DataFrame(current_members))


rlp_politicians = label_parties(rlp_politicians)
rlp = pd.concat(rlp_politicians)
pickle.dump(rlp, open("politiker/rlp.pickle", "wb"))
# </editor-fold>
#------------------------------------------------------------------
# <editor-fold desc="Saarland">
general_url = "https://de.wikipedia.org/wiki/Liste_der_Mitglieder_des_Landtages_des_Saarlandes_({}._Wahlperiode)"
saar_politicians = []
for periode in range(1, 18):
    url = general_url.format(periode)
    results = get_website(url)
    current_members = {"First Name": [], "Last Name": [], "Born": [], "Party": [], "Period": [], "Constituency": [],
                       "Link": []}
    orig_data = results.find_all("table")
    if periode > 16:
        list_data = [x.find("tbody") for x in orig_data if
                     "Name" in x.find_all("tr")[0].text]
    elif periode >= 15:
        list_data = [x.find("tbody") for x in orig_data if "Mitglied" in x.find_all("tr")[0].text and
                     "Bild" in x.find_all("tr")[0].text]
    else:
        list_data = [x.find("tbody") for x in orig_data if
                     "Name" in x.find_all("tr")[0].text or "Mitglied" in x.find_all("tr")[0].text]
    for data in list_data:
        count = 0
        for elem in data.find_all("tr"):
            if count == 0:
                name_base, party_base, born_base, constituency_base = get_base_in_table(elem)
                count += 1
            else:
                current_members["Period"].append(periode)
                get_data_from_elem(elem, name_base, party_base, born_base, constituency_base)
    saar_politicians.append(pd.DataFrame(current_members))

saar_politicians = label_parties(saar_politicians)
saar = pd.concat(saar_politicians)
pickle.dump(saar, open("politiker/saar.pickle", "wb"))
# </editor-fold>
#------------------------------------------------------------------
# <editor-fold desc="Sachsen">
general_url = "https://de.wikipedia.org/wiki/Liste_der_Mitglieder_des_S%C3%A4chsischen_Landtags_({}._Wahlperiode)"
sachsen_politicians = []
for periode in range(1, 8):
    url = general_url.format(periode)
    results = get_website(url)
    current_members = {"First Name": [], "Last Name": [], "Born": [], "Party": [], "Period": [], "Constituency": [],
                       "Link": []}
    base_text = results.find_all("p")[0].text
    orig_data = results.find_all("table")
    list_data = [x.find("tbody") for x in orig_data if
                 "Name" in x.find_all("tr")[0].text or "Mitglied" in x.find_all("tr")[0].text]
    for data in list_data:
        count = 0
        for elem in data.find_all("tr"):
            if count == 0:
                name_base, party_base, born_base, constituency_base = get_base_in_table(elem)
                count += 1
            else:
                current_members["Period"].append(periode)
                get_data_from_elem(elem, name_base, party_base, born_base, constituency_base)
    sachsen_politicians.append(pd.DataFrame(current_members))

sachsen_politicians = label_parties(sachsen_politicians)
sachsen = pd.concat(sachsen_politicians)
pickle.dump(sachsen, open("politiker/sachsen.pickle", "wb"))
# </editor-fold>
#------------------------------------------------------------------
# <editor-fold desc="Sachsen-Anhalt">
general_url = "https://de.wikipedia.org/wiki/Liste_der_Mitglieder_des_Landtages_von_Sachsen-Anhalt_({}._Wahlperiode)"
sa_politicians = []
for periode in range(1, 9):
    url = general_url.format(periode)
    results = get_website(url)
    current_members = {"First Name": [], "Last Name": [], "Born": [], "Party": [], "Period": [], "Constituency": [],
                       "Link": []}
    base_text = results.find_all("p")[0].text
    orig_data = results.find_all("table")
    list_data = [x.find("tbody") for x in orig_data if
                 "Name" in x.find_all("tr")[0].text or "Mitglied" in x.find_all("tr")[0].text]
    for data in list_data:
        count = 0
        for elem in data.find_all("tr"):
            if count == 0:
                name_base, party_base, born_base, constituency_base = get_base_in_table(elem)
                count += 1
            else:
                current_members["Period"].append(periode)
                get_data_from_elem(elem, name_base, party_base, born_base, constituency_base)
    sa_politicians.append(pd.DataFrame(current_members))


sa_politicians = label_parties(sa_politicians)
sa = pd.concat(sa_politicians)
pickle.dump(sa, open("politiker/sachsen_anhalt.pickle", "wb"))
# </editor-fold>
#------------------------------------------------------------------
# <editor-fold desc="Schleswig-Holstein">
general_url = "https://de.wikipedia.org/wiki/Liste_der_Mitglieder_des_Landtages_Schleswig-Holstein_({}._Wahlperiode)"
sh_politicians = []
for periode in range(1, 21):
    url = general_url.format(periode)
    results = get_website(url)
    current_members = {"First Name": [], "Last Name": [], "Born": [], "Party": [], "Period": [], "Constituency": [],
                       "Link": []}
    base_text = results.find_all("p")[0].text
    orig_data = results.find_all("table")
    list_data = [x.find("tbody") for x in orig_data if
                 "Name" in x.find_all("tr")[0].text or "Mitglied" in x.find_all("tr")[0].text]
    for data in list_data:
        count = 0
        for elem in data.find_all("tr"):
            if count == 0:
                name_base, party_base, born_base, constituency_base = get_base_in_table(elem)
                count += 1
            else:
                current_members["Period"].append(periode)
                get_data_from_elem(elem, name_base, party_base, born_base, constituency_base)
    sh_politicians.append(pd.DataFrame(current_members))


sh_politicians = label_parties(sh_politicians)
sh = pd.concat(sh_politicians)
pickle.dump(sh, open("politiker/sh.pickle", "wb"))
# </editor-fold>
#------------------------------------------------------------------
# <editor-fold desc="Thueringen">
general_url = "https://de.wikipedia.org/wiki/Liste_der_Mitglieder_des_Th%C3%BCringer_Landtags_({}._Wahlperiode)"
thueringen_politicians = []
for periode in range(1, 8):
    url = general_url.format(periode)
    results = get_website(url)
    current_members = {"First Name": [], "Last Name": [], "Born": [], "Party": [], "Period": [], "Constituency": [],
                       "Link": []}
    base_text = results.find_all("p")[0].text
    orig_data = results.find_all("table")
    list_data = [x.find("tbody") for x in orig_data if
                 "Name" in x.find_all("tr")[0].text or "Mitglied" in x.find_all("tr")[0].text]
    for data in list_data:
        count = 0
        for elem in data.find_all("tr"):
            if count == 0:
                name_base, party_base, born_base, constituency_base = get_base_in_table(elem)
                count += 1
            else:
                current_members["Period"].append(periode)
                get_data_from_elem(elem, name_base, party_base, born_base, constituency_base)
    thueringen_politicians.append(pd.DataFrame(current_members))


thueringen_politicians = label_parties(thueringen_politicians)
thueringen = pd.concat(thueringen_politicians)
pickle.dump(thueringen, open("politiker/thueringen.pickle", "wb"))
# </editor-fold>
#------------------------------------------------------------------
# <editor-fold desc="Mecklenburg-Vorpommern">
general_url = "https://de.wikipedia.org/wiki/Liste_der_Mitglieder_des_Landtages_Mecklenburg-Vorpommern_({}._Wahlperiode)"
mv_politicians = []
for periode in range(1, 9):
    url = general_url.format(periode)
    results = get_website(url)
    current_members = {"First Name": [], "Last Name": [], "Born": [], "Party": [], "Period": [], "Constituency": [],
                       "Link": []}
    base_text = results.find_all("p")[0].text
    orig_data = results.find_all("table")
    list_data = [x.find("tbody") for x in orig_data if
                 "Name" in x.find_all("tr")[0].text or "Mitglied" in x.find_all("tr")[0].text]
    for data in list_data:
        count = 0
        for elem in data.find_all("tr"):
            if count == 0:
                name_base, party_base, born_base, constituency_base = get_base_in_table(elem)
                count += 1
            else:
                current_members["Period"].append(periode)
                get_data_from_elem(elem, name_base, party_base, born_base, constituency_base)
    mv_politicians.append(pd.DataFrame(current_members))


mv_politicians = label_parties(mv_politicians)
mv = pd.concat(mv_politicians)
pickle.dump(mv, open("politiker/mv.pickle", "wb"))
# </editor-fold>

