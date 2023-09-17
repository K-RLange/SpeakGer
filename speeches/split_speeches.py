import pickle, os, sys, re
from tqdm import tqdm
import pandas as pd
import numpy as np
import warnings
warnings.filterwarnings("ignore")

def split_speeches(session, land):
    def unknown_speaker():
        return pd.DataFrame({"MPID": 0, "Party": [[x for x in list_of_parties if x in line.lower()]],
                             "Constituency": "", "Link": ""})
    def identify_speaker(colon=True):
        if colon:
            split_line = line.lower().split(":")[0]
            important_mps = [x for x in full_names if x in split_line]
            if len(important_mps) == 0:
                important_mps = mp_subset
            else:
                important_mps = mp_subset[mp_subset["Name"].isin(important_mps)]
            speaker = important_mps[[x.lower() in split_line for x in important_mps["LastName"]]]
        else:
            speaker = mp_subset[[x.lower() in line.lower() for x in mp_subset["LastName"]]]

        if not speaker.empty:
            name_index = np.argmax(speaker["LastName"].apply(lambda x: len(x)))
        else:
            # print(line)
            name_index = 0
            speaker = mp_subset[mp_subset["LastName"] == re.search(
                r"(" + "|".join([x for x in mp_subset["LastName"] if ")" not in x]) + ")+[^a-z]*", line.lower()).group(1)]
            if len(speaker) >= 1:
                speaker = speaker.head(1)
            else:
                speaker = unknown_speaker()
                return speaker
        #speaker = pd.DataFrame(speaker).transpose()
        speaker_id = int(speaker["MPID"].iloc[name_index])
        speaker = mapping_subset[mapping_subset["MPID"] == str(speaker_id)]
        speaker["Party"].iloc[0] = [speaker["Party"].iloc[0]]
        speaker = pd.DataFrame(speaker)
        return speaker
    session_text = session["doc"].split("\n")
    period = session["period"]
    if period == "unknown":
        period = 1
    mapping_subset = mapping[mapping["Period"] == int(period)]
    mapping_subset = mapping_subset[mapping_subset["State"] == land[:-7]]
    mapping_ids = {int(x) for x in mapping_subset["MPID"]}
    list_of_parties = set("/".join(mapping_subset["Party"]).split("/"))
    if "linke/pds/sed" in list_of_parties:
        list_of_parties.update({"linke", "sed", "pds"})
    if "die grünen" in list_of_parties:
        list_of_parties.update({"bündnis 90", "bü 90"})
    if "kpd/dkp" in list_of_parties:
        list_of_parties.update({"kpd", "dkp"})
    #list_of_parties.update({"bündnis 90", "bü 90", "linke", "sed"})
    mp_subset = mps[mps["MPID"].isin(mapping_ids)]
    mp_subset["Name"] = [x.lower().replace("ß", "ss") for x in mp_subset["Name"]]
    mp_subset["LastName"] = [x["LastName"].lower().replace("ß", "ss") if isinstance(x["LastName"], str) else x["Name"].split()[-1] for i, x in mp_subset.iterrows()]
    full_names = {x["Name"].lower() for i, x in mp_subset.iterrows()}
    last_names = set(mp_subset["LastName"])
    only_speaker = re.compile(r"[\(\[\{]" + "\s*(abg.|abgeordneter|abgeordnete|präsident|präsidentin|vizepräsident|vizepräsidentin|herr|herrn|frau)?\s?(" + "|".join([x for x in full_names if ")" not in x and "(" not in x]) + ")?\s?(" + "|".join([x for x in last_names if ")" not in x and "(" not in x]) + ")\s*[\)\]\}]")
    speeches = []
    cur_text = ""
    line = session_text[0]
    new_speaker = unknown_speaker()
    speaker = unknown_speaker()
    chair = True
    comment = False
    for line_index, line in enumerate(session_text):
        line = line.replace("ß", "ss")
        if len(line.strip()) > 0:
            #Wenn aktuell ein comment, dann reinstalliere alten speaker
            if comment and line.strip()[-1] in ")]}":
                speeches.append({"Period": session["period"], "Session": session["session"], "Date": session["date"],
                                 "Chair": False, "Interjection": True, "MPID": speaker["MPID"],
                                 "Party": speaker["Party"].iloc[0],
                                 "Constituency": speaker["Constituency"].iloc[0],
                                 "Speech": cur_text + " " + line.strip()[0:-1]})
                cur_text = ""
                speaker = old_speaker
                chair = old_chair
                comment = False
                continue
            if ":" in line and not line.strip()[0] in "([{":
                try:
                    reg_speaker = re.match(r".*?(" + "|".join([x for x in mp_subset["LastName"] if ")" not in x]) + ")+[^a-z]*", line.split(":")[0].lower())
                    if reg_speaker or re.search(r"präsident.*\:", line.lower()):
                        if cur_text:
                            #Alte Speech noch einfuegen, bevor es in die neue geht
                            speeches.append({"Period": session["period"], "Session": session["session"], "Date": session["date"],
                                "Chair": chair, "Interjection": False, "MPID": speaker["MPID"],
                                "Party": speaker["Party"].iloc[0],
                                "Constituency": speaker["Constituency"].iloc[0], "Speech": cur_text})
                        reg_speech = re.match(r".*\:(.*)", line.lower())
                        if reg_speaker:
                            new_speaker = identify_speaker()
                        if not reg_speaker or new_speaker.empty:
                            new_speaker = unknown_speaker()
                        if line.strip()[0] in "({[" and line.strip()[-1] in ")]}":
                            speeches.append({"Period": session["period"], "Session": session["session"], "Date": session["date"],
                                "Chair": False, "Interjection": True, "MPID": new_speaker["MPID"],
                                "Party": new_speaker["Party"].iloc[0],
                                "Constituency": new_speaker["Constituency"].iloc[0],
                                "Speech": reg_speech.group(1)})
                            cur_text = ""
                            continue
                        elif line.strip()[0] in "({[" and not re.search(r"[)\]}]", line.strip()[:-1]):
                            comment = True
                            old_speaker = speaker
                            old_chair = chair
                        else:
                            comment = False
                        if line.split(":")[1]:
                            cur_text = line.split(":")[1]
                        else:
                            cur_text = ""
                        speaker = new_speaker
                        #if re.match(r".*präsident.*\:(.*)", line):
                        chair = (re.match(r".*präsident.*\:(.*)", line) is not
                                 None)
                        continue
                except Exception as e:
                    print(line)
                    print(period)
                    print(speaker)
                    raise e
            #Wenn stattdessen Kommentar zu einer Partei detectet:
            elif line.strip()[0] in "([{":
                #Check if it is a new page and there is only a speaker in a comment (this is the case for e.g. thueringen)
                if only_speaker.search(line.lower()):
                    continue
                if cur_text:
                    speeches.append({"Period": session["period"], "Session": session["session"], "Date": session["date"],
                                    "Chair": chair, "Interjection": False, "MPID": speaker["MPID"],
                                    "Party": speaker["Party"].iloc[0], 
                                    "Constituency": speaker["Constituency"].iloc[0], "Speech": cur_text})
                cur_text = ""
                if re.search(r"[)\]}]", line.strip()[-1]):
                    if re.search(r"(" + "|".join([x for x in mp_subset["LastName"] if ")" not in x]) + ")+[^a-z]*", line.lower()):
                        comment_speaker = identify_speaker(False)
                    else:
                        comment_speaker = unknown_speaker()
                    speeches.append({"Period": session["period"], "Session": session["session"], "Date": session["date"],
                        "Chair": False, "Interjection": True, "MPID": comment_speaker["MPID"],
                        "Party": comment_speaker["Party"].iloc[0],
                        "Constituency": comment_speaker["Constituency"].iloc[0], "Speech": line.strip()[1:-1]})
                    comment = False
                else:
                    comment = True
                    old_speaker = speaker
                    old_chair = chair
                    cur_text += line.strip()[1:]
                    try:
                        if re.search(r"(" + "|".join([x for x in mp_subset["LastName"] if ")" not in x]) + ")+[^a-z]*", line.lower()):
                            speaker = identify_speaker(":" in line)
                        else:
                            speaker = unknown_speaker()
                        #speaker = mp_subset[mp_subset["Last Name"] == re.search(r".*(" + "|".join([x for x in mp_subset["Last Name"] if ")" not in x]) + ")", line.lower()).group(1)]
                        #speaker.iloc[0]["Party"] = [speaker.iloc[0]["Party"]]
                    except:
                        speaker = unknown_speaker()
                    chair = False
                continue
            cur_text += " " + line
    if cur_text:
        speeches.append({"Period": session["period"], "Session": session["session"], "Date": session["date"],
                         "Chair": chair, "Interjection": False, "MPID": speaker["MPID"],
                         "Party": speaker["Party"].iloc[0],
                         "Constituency": speaker["Constituency"].iloc[0], "Speech": cur_text})
    speeches = [x for x in speeches if x is not None and len(x["Speech"]) > 0]
    #speeches = [x for x in speeches if len(x["Speech"].split()) > 0]
    return pd.DataFrame([x for x in speeches if x is not None])


#data = pickle.load(open("C:/Users/kalange/Documents/Daten_large/Landtage_corrected/Berlin.pickle", "rb"))
#data = pickle.load(open("C:/Users/kalange/Documents/Daten_large/Landtage_clean/Berlin.pickle", "rb"))
#mps = pickle.load(open("Politiker/berlin.pickle", "rb"))
#split_speeches(data.iloc[330])

from pathlib import Path
kuerzel = [x for x in os.listdir("dates/") if ".pickle" in x and x not in os.listdir("split/")][int(sys.argv[1])]
print(kuerzel)

data = pickle.load(open("dates/" + kuerzel, "rb"))
data = data[data["doc"] != ""]
mps = pd.read_csv("all_mps_meta_final.csv")
mapping = pd.read_csv("all_mps_mapping_no_duplicates.csv")
result = list(map(lambda x: split_speeches(x[1], kuerzel), tqdm(data.iterrows(), total=len(data))))
Path("split/" + kuerzel[:-7]).mkdir(parents=True, exist_ok=True)
path = "split/"
for session in result:
    if not session.empty:
        id = str(session.iloc[0]["Period"]) + "_" + str(session.iloc[0]["Session"])
        session.to_json(path + kuerzel[:-7] + "/" + id + ".json", orient="records", lines=True)
result = pd.concat(result)
result.to_pickle(path + kuerzel)
result.to_csv(path + kuerzel[:-7] + ".csv")
#pickle.dump(result, open(path + kuerzel, "wb"))