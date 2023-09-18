import os
import pandas as pd
from datetime import datetime, timedelta
from pathlib import Path
import locale
import warnings
warnings.filterwarnings("ignore")
locale.setlocale(locale.LC_TIME, 'de_DE.UTF-8')

df = pd.read_excel("processed_session_dates.xlsx", "Sitzungsdaten")
kuerzel_list = set(df["Bundesland"])
all_kuerzel = [x[:-7] for x in os.listdir("clean/") if ".pickle" in x and "Bundestag" not in x and "Bayern" not in x and x not in os.listdir("dates")]
path = "clean/"

for kuerzel in all_kuerzel:
    data = pd.read_pickle(path + kuerzel + ".pickle")
    #data = data.reset_index()
    data = data.sort_values(["period", "session"])
    data = data.reset_index()
    df = pd.read_excel("processed_session_dates.xlsx", "Sitzungsdaten")
    df = df[df["Bundesland"] == kuerzel]
    for i, session in data.iterrows():
        period = session["period"]
        session_nr = session["session"]
        correct_date = df[df["WP"] == period][df["Sitzung"] == session_nr]["Datum"]
        if not correct_date.empty:
            if isinstance(correct_date.iloc[0], str):
                data.iloc[i]["date"] = datetime.strptime(correct_date.iloc[0].strip(), "%d.%m.%Y")
            else:
                data.iloc[i]["date"] = correct_date.iloc[0]
        else:
            if isinstance(data.iloc[i-1]["date"], str):
                if data.iloc[i-1]["date"] == "unknown":
                    pass
                else:
                    datetime.strptime(data.iloc[i-1]["date"], "%d.%m.%Y") + timedelta(days=7)
            else:
                data.iloc[i]["date"] = data.iloc[i-1]["date"] + timedelta(days=7)
    Path("dates/" + kuerzel).mkdir(parents=True, exist_ok=True)
    data = data.sort_values(["period", "session"])
    data.to_pickle("dates/" + kuerzel + ".pickle")
