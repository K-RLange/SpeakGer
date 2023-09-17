import pandas as pd
from datetime import datetime
import numpy as np
import re

bundeslaender = ["Baden-Württemberg", "Bayern", "Berlin", "Brandenburg", "Bremen", "Hamburg", "Hessen", "Mecklenburg-Vorpommern", "Niedersachsen", "Nordrhein-Westfalen", "Rheinland-Pfalz", "Saarland",
                 "Sachsen", "Sachsen-Anhalt", "Schleswig-Holstein", "Thüringen", "Bundestag"]

def unique_list(large_list):
    seen = []
    for item in large_list:
        if item not in seen:
            seen.append(item)
    if seen == [None]:
        return None
    return seen

all_mps_meta = []
all_mps_mapping = []
mp_id = 1
for land in bundeslaender:
    print(land)
    data = pd.read_csv(f"wikidata/{land}1.csv").fillna(np.nan).replace([np.nan], [None])
    mps = []
    for unique_id in data["item"].unique():
        sub_data = data[data["item"] == unique_id]
        sub_data = sub_data.reset_index()
        if sub_data.loc[0, "born"]:
            born = datetime.strptime(sub_data.loc[0, "born"][0:10], "%Y-%m-%d")
        else:
            born = ""
        mp = {"MPID": mp_id, "WikiDataLink": unique_id, "WikipediaLink": sub_data.loc[0, "article"], "Name": sub_data.loc[0, "itemLabel"], "LastName": sub_data.loc[0, "lastnameLabel"],
              "Born": born, "SexOrGender": sub_data.loc[0, "sexLabel"], "Occupation": [unique_list(sub_data["occupationLabel"])],
              "Religion": sub_data.loc[0, "religionLabel"], "AbgeordnetenwatchID": sub_data.loc[0, "watchLabel"]}
        mp_id += 1
        mp = pd.DataFrame(mp)
        mps.append(mp)
    mps = pd.concat(mps).reset_index()
    pediadata = pd.read_pickle(f"Politiker/{land.lower()}.pickle")
    pediadata["Link"] = pediadata["Link"].apply(lambda x: re.sub(r"([^:])//", r"\1/", x))
    confirmed_mps = set(pediadata["Link"])
    final_mps = pd.DataFrame([row for i, row in mps.iterrows() if row["WikipediaLink"] in confirmed_mps]).drop("index", axis=1)
    confirmed_mps = set(final_mps["WikipediaLink"])
    #Bisher: final_mps = Alle mps, die Teil von WikiData und Wikipedia sind
    #Jetzt neu: zsp, das alle enthaelt, die nicht Teil von Wikidata, aber von Wikipedia sind
    #           all_mps_mapping, das alle Periodenspezifischen Daten enthaelt
    zsp = []
    for i, row in pediadata.iterrows():
        #Wenn kein Link auf Wikipedia, ist er auch nicht im bisherigen Datensatz - hinzufuegen
        if row["Link"] == "":
            #Checken ob Geburtsdatum angegeben
            if row["Born"] == "unknown" or int(row["Born"]) <= 1800:
                zsp.append(pd.DataFrame({"MPID": mp_id, "WikiDataLink": "", "WikipediaLink": "", "Name": row["First Name"] + " " + row["Last Name"], "LastName": row["Last Name"],
                                         "Born": "", "SexOrGender": "", "Occupation": "", "Religion": "", "AbgeordnetenwatchID": ""}, index=[0]))
            else:
                zsp.append(pd.DataFrame({"MPID": mp_id, "WikiDataLink": "", "WikipediaLink": "", "Name": row["First Name"] + " " + row["Last Name"], "LastName": row["Last Name"],
                                         "Born": datetime.strptime(str(row["Born"]) + "06", "%Y%m"), "SexOrGender": "", "Occupation": "",
                                         "Religion": "", "AbgeordnetenwatchID": ""}, index=[0]))
            all_mps_mapping.append({"MPID": mp_id, "State": land, "Period": row["Period"], "Party": row["Party"], "Constituency": row["Constituency"],
                                    "Political Orientation": row["political_orientation"]})
            mp_id += 1
        else:
            #Wenn Link auf Wikipedia, aber nicht in bisherigem Datensatz, hinzufuegen
            if row["Link"] not in set(final_mps["WikipediaLink"]):
                if row["Born"] == "unknown" or int(row["Born"]) <= 1800:
                    zsp.append(pd.DataFrame({"MPID": mp_id, "WikiDataLink": "", "WikipediaLink": row["Link"], "Name": row["First Name"] + " " + row["Last Name"], "LastName": row["Last Name"],
                                             "Born": "", "SexOrGender": "", "Occupation": "", "Religion": "", "AbgeordnetenwatchID": ""}, index=[0]))
                else:
                    zsp.append(pd.DataFrame({"MPID": mp_id, "WikiDataLink": "", "WikipediaLink": row["Link"], "Name": row["First Name"] + " " + row["Last Name"], "LastName": row["Last Name"],
                                             "Born": datetime.strptime(str(row["Born"]) + "06", "%Y%m"), "SexOrGender": "", "Occupation": "", "Religion": "", "AbgeordnetenwatchID": ""}, index=[0]))
                all_mps_mapping.append({"MPID": mp_id, "State": land, "Period": row["Period"], "Party": row["Party"], "Constituency": row["Constituency"],
                                        "Political Orientation": row["political_orientation"]})
                mp_id += 1
            else:
                #Wenn Link auf Wikipedia und in bisherigem Datensatz, dann Daten updaten und all_mps_mapping updaten
                index = np.where([row["Link"] == x for x in final_mps["WikipediaLink"]])[0][0]
                if final_mps["Born"].iloc[index] == "" and row["Born"] != "unknown":
                    final_mps["Born"].iloc[index] = datetime.strptime(str(row["Born"]) + "06", "%Y%m")
                all_mps_mapping.append({"MPID": final_mps["MPID"].iloc[index], "State": land, "Period": row["Period"], "Party": row["Party"], "Constituency": row["Constituency"],
                                        "Political Orientation": row["political_orientation"]})
    zsp = pd.concat(zsp)
    final_mps = pd.concat([final_mps, zsp]).reset_index().drop("index", axis=1)
    all_mps_meta.append(final_mps)

all_mps_meta = pd.concat(all_mps_meta)
all_mps_mapping = pd.DataFrame(all_mps_mapping)

mp_id_replacement = dict()
links = set(all_mps_meta["WikipediaLink"])
for link in links:
    sub_data = all_mps_meta[all_mps_meta["WikipediaLink"] == link]
    if len(sub_data) == 1:
        continue
    names = set(sub_data["Name"])
    for name in names:
        sub_sub_data = sub_data[sub_data["Name"] == name]
        if len(sub_sub_data) == 1:
            continue
        for i, row in sub_sub_data.iterrows():
            if i > 0:
                mp_id_replacement[row["MPID"]] = sub_sub_data.iloc[0]["MPID"]

all_mps_meta = all_mps_meta.set_index("MPID")
all_mps_meta = all_mps_meta.drop(mp_id_replacement.keys())
for i, row in all_mps_mapping.iterrows():
    if row["MPID"] in mp_id_replacement.keys():
        all_mps_mapping["MPID"].iloc[i] = mp_id_replacement[row["MPID"]]

for i, row in all_mps_meta.iterrows():
    if not row["LastName"]:
        all_mps_meta["LastName"].iloc[i] = row["Name"].split()[-1]
all_mps_meta.to_csv("all_mps_meta.csv")
all_mps_mapping.to_csv("all_mps_mapping.csv", index=False)