import os
import pandas as pd
import pickle
import re
from pathlib import Path
import update_pdfs
import update_ocr
import update_clean
import update_split


current_year = 2024
old_files = os.listdir("data")
old_files = ["data/" + x for x in old_files if x.endswith(".csv") and "mp" not in x and "mapping" not in x]
Path("new_data/").mkdir(parents=True, exist_ok=True)
#file = old_files[0]
#update_clean.cut_off(re.match(r'data/(.*).csv', file).group(1))
for file in old_files:

    if "Thü" in file:
        # Download new pdf files:
        old_data = pd.read_csv(file)
        row = old_data.iloc[-1]
        initial_period = row["Period"]
        initial_year = row["Date"][:4]
        initial_session = row["Session"] + 1
        try:
            print(re.match(r'data/(.*).csv', file).group(1), int(initial_year), int(current_year),
                                        int(initial_period), int(initial_session))
            update_pdfs.get_landtag_pdf(re.match(r'data/(.*).csv', file).group(1), int(initial_year), int(current_year),
                                        int(initial_period), int(initial_session), "pdfs")
        except:
            print("not", file)
            raise
    continue
    #os.system(f"python update_pdfs.py -n {re.match(r'data/(.*).csv', file).group(1)} -iy {initial_year} -my {current_year} -ip {initial_period} -is {initial_session}")

    # OCR new pdf files:
    #os.system(f"python update_ocr.py {re.match(r'data/(.*).csv', file).group(1)}")
    update_ocr.ocr(re.match(r'data/(.*).csv', file).group(1))
    #continue
    # Clean and split the speeches:
    update_clean.cut_off(re.match(r'data/(.*).csv', file).group(1))
    print("hier noch date fixen")
    new_data = update_split.split(re.match(r'data/(.*).csv', file).group(1))

    # Update dataframe and save it:
    new_data = new_data[new_data["Date"] > row["Date"]]
    new_data = pd.concat([old_data, new_data], axis=0)
    new_data.to_csv("new_data/" + re.match(r'data/(.*).csv', file + ".csv").group(1), index=False)
