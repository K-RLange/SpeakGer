import os
import numpy as np
import requests
import pathlib
import time
import webbrowser
from pathlib import Path
from math import ceil

max_year = 2024
start_path = "C:/Users/kalange/Documents/Daten_large/Landtage_pdfs"


def get_pdfs(orig_url, kuerzel, additional_zeroes=True, double=False, switch=False,
             start_period=19):
    path = pathlib.Path(f'{start_path}/{kuerzel}')
    path.mkdir(parents=True, exist_ok=True)
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:66.0) Gecko/20100101 Firefox/66.0",
        "Accept-Encoding": "*",
        "Connection": "keep-alive"
    }
    for period in range(start_period, (start_period+ceil((max_year-2022)/4))):
        if period < 10:
            period_str = "0" + str(period)
        else:
            period_str = str(period)

        for session in range(1, 360):
            if additional_zeroes:
                if session < 10:
                    session_str = "00" + str(session)
                elif session < 100:
                    session_str = "0" + str(session)
                else:
                    session_str = str(session)
                url = orig_url.format(period_str, session_str[-1], session_str)
            else:
                if double:
                    url = orig_url.format(period_str, period_str, session)
                else:
                    if switch:
                        url = orig_url.format(session, period_str)
                    else:
                        url = orig_url.format(period_str, session, session)
            r = requests.get(url, stream=True, headers=headers)
            if r.status_code == 404:
                print(url)
                break
            with open(f'{path}/{periode}_{session}.pdf', 'wb') as f:
                f.write(r.content)


def transform_month(month):
    if month < 10:
        return "0" + str(month)
    else:
        return str(month)


def transform_session(session):
    if session < 10:
        return "00" + str(session)
    elif session < 100:
        return "0" + str(session)
    else:
        return str(session)


# <editor-fold desc="Nordrhein Westfahlen">
path = Path(f"{start_path}/Nordrhein-Westfalen")
path.mkdir(parents=True, exist_ok=True)
for periode in range(18, (18+ceil((max_year-2022)/4))):
    for session in range(1, 360):
        if os.path.exists(f'{path}/{periode}_{session}.pdf'):
            continue
        url = 'https://www.landtag.nrw.de/portal/WWW/dokumentenarchiv' \
              '/Dokument/MMP{}-{}.pdf'.format(periode, session)
        r = requests.get(url, stream=True)
        if r.status_code == 404:
            break
        with open(f'{path}/{periode}_{session}.pdf', 'wb') as f:
            f.write(r.content)
# </editor-fold>

# <editor-fold desc="Baden-Württemberg">
alternative_url = "https://www.landtag-bw.de/files/live/sites/LTBW/files/dokumente/WP{}/Plp/{}_0{}_{}{}{}.pdf"
periode = 17
session = 67
for year in range(2022, max_year):
    for month in range(1, 13):
        month_str = transform_month(month)
        for day in range(1, 32):
            day_str = transform_month(day)
            url = alternative_url.format(periode, periode, transform_session(session), day_str, month_str, year)
            r = requests.get(url, stream=True)
            if r.status_code != 404 and r.status_code != 403:
                with open(f'{path}/{periode}_{session}.pdf', 'wb') as f:
                    f.write(r.content)
                session += 1
                while True:
                    url = alternative_url.format(periode, periode, transform_session(session), day_str, month_str, year)
                    r = requests.get(url, stream=True)
                    if r.status_code != 404 and r.status_code != 403:
                        with open(f'{path}/{periode}_{session}.pdf', 'wb') as f:
                            f.write(r.content)
                        session += 1
                    else:
                        break
            else:
                url = alternative_url.format(periode + 1, periode + 1, transform_session(1), day_str, month_str, year)
                r = requests.get(url, stream=True)
                if r.status_code != 404 and r.status_code != 403:
                    with open(f'{path}/{periode+1}_{1}.pdf', 'wb') as f:
                        f.write(r.content)
                    session = 1
                    periode += 1
                    while True:
                        url = alternative_url.format(periode, periode, transform_session(session), day_str, month_str, year)
                        r = requests.get(url, stream=True)
                        if r.status_code != 404 and r.status_code != 403:
                            with open(f'{path}/{periode}_{session}.pdf', 'wb') as f:
                                f.write(r.content)
                            session += 1
                        else:
                            break
        print(month)
# </editor-fold>

# <editor-fold desc="Berlin">
path = Path(f"{start_path}/Berlin")
path.mkdir(parents=True, exist_ok=True)
for periode in range(19, (19+ceil((max_year-2022)/4))):
    for session in range(300):
        if session < 10:
            url = "https://www.parlament-berlin.de/ados/{}/IIIPlen/protokoll/plen{}-00{}-pp.pdf".format(periode, periode, session)
        elif session < 100:
            url = "https://www.parlament-berlin.de/ados/{}/IIIPlen/protokoll/plen{}-0{}-pp.pdf".format(periode, periode, session)
        else:
            url = "https://www.parlament-berlin.de/ados/{}/IIIPlen/protokoll/plen{}-{}-pp.pdf".format(periode, periode, session)
        r = requests.get(url, stream=True)
        if r.status_code != 404:
            with open(f'{path}/{periode}_{session}.pdf', 'wb') as f:
                f.write(r.content)
# </editor-fold>

# <editor-fold desc="#Brandenburg">
url = "https://www.landtag.nrw.de/portal/WWW/dokumentenarchiv/Dokument/ERP{}-{}.pdf"
get_pdfs(url, "Brandenburg", False)
path = Path(f"{start_path}/Brandenburg")
path.mkdir(parents=True, exist_ok=True)
alternative_url = "https://www.parlamentsdokumentation.brandenburg.de/starweb/LBB/ELVIS/parladoku/w{}/plpr/{}.pdf"
for periode in range(7, 7+ceil((max_year-2022)/4)):
    for session in range(300):
        url = alternative_url.format(periode, session)
        r = requests.get(url, stream=True)
        if r.status_code != 404 and r.status_code != 403:
            with open(f'{path}/{periode}_{session}.pdf', 'wb') as f:
                f.write(r.content)

# </editor-fold>

# <editor-fold desc="Bremen">
path = Path(f"{start_path}/Bremen")
path.mkdir(parents=True, exist_ok=True)

alternative_url = "https://www.bremische-buergerschaft.de/dokumente/wp{}/land/protokoll/P{}L0{}.pdf"
for periode in range(20, (20+ceil((max_year-2022)/4))):
    for session in range(200):
        if session < 10:
            session_str = "00" + str(session)
        elif session < 100:
            session_str = "0" + str(session)
        else:
            session_str = str(session)
        url = alternative_url.format(periode, periode, session_str)
        r = requests.get(url, stream=True)
        if r.status_code != 404 and r.status_code != 403:
            with open(f'{path}/{periode}_{session}.pdf', 'wb') as f:
                f.write(r.content)
# </editor-fold>

# <editor-fold desc="Hamburg">
print("Weiss noch nicht, wie man Hamburg automatisiert scrapet")
# </editor-fold>

# <editor-fold desc="Hessen">
#      https://starweb.hessen.de/cache/PLPR/01/0/00010.pdf
url = "https://starweb.hessen.de/cache/PLPR/{}/{}/00{}.pdf"
get_pdfs(url, "Hessen", True, start_period=20)
# </editor-fold>

# <editor-fold desc="Mecklenburg-Vorpommern">
path = Path(f"{start_path}/Mecklenburg-Vorpommern")
path.mkdir(parents=True, exist_ok=True)
alternative_url = "https://www.landtag-mv.de/fileadmin/media/Dokumente/Parlamentsdokumente/Plenarprotokolle/{}_Wahlperiode/PlPr{}-0{}.pdf"
for periode in range(8, (8+ceil((max_year-2022)/4))):
    for session in range(300):
        if session < 10:
            session_str = "00" + str(session)
        elif session < 100:
            session_str = "0" + str(session)
        else:
            session_str = str(session)
        url = alternative_url.format(periode, "0" + str(periode), session_str)
        r = requests.get(url, stream=True)
        if r.status_code != 404 and r.status_code != 403:
            with open(f'{path}/0{periode}_{session}.pdf', 'wb') as f:
                f.write(r.content)

# </editor-fold>

# <editor-fold desc="Niedersachsen">
path = Path(f"{start_path}/Niedersachsen")
path.mkdir(parents=True, exist_ok=True)
alternative_url = "https://www.landtag-niedersachsen.de/parlamentsdokumente/steno/{}_wp/endber{}.pdf"
for periode in range(18, (18+ceil((max_year-2022)/4))):
    for session in range(300):
        if session < 10:
            session_str = "00" + str(session)
        elif session < 100:
            session_str = "0" + str(session)
        else:
            session_str = str(session)
        url = alternative_url.format(periode, session_str)
        r = requests.get(url, stream=True)
        if r.status_code != 404 and r.status_code != 403:
            with open(f'{path}/{periode}_{session}.pdf', 'wb') as f:
                f.write(r.content)

# </editor-fold>

# <editor-fold desc="Rheinland-Pfalz">
path = Path(f"{start_path}/Rheinland-Pfalz")
path.mkdir(parents=True, exist_ok=True)
alternative_url = "https://dokumente.landtag.rlp.de/landtag/plenarprotokolle/{}-P-{}.pdf"
alternative_url = "https://dokumente.landtag.rlp.de/landtag/plenarprotokolle/PLPR-Sitzung-{}-{}.pdf"
alternative_url = "https://dokumente.landtag.rlp.de/landtag/plenarprotokolle/{}-P-{}.pdf"
#get_pdfs(url, "RLP", False)
for periode in range(18, (18+ceil((max_year-2022)/4))):
    for session in range(300):
        url = alternative_url.format(session, periode)
        r = requests.get(url, stream=True)
        if r.status_code != 404 and r.status_code != 403 and len(r.content) > 26865:
            with open(f'{path}/{periode}_{session}.pdf', 'wb') as f:
                f.write(r.content)
# </editor-fold>

# <editor-fold desc="Saarland">
path = Path(f"{start_path}/Saarland")
path.mkdir(parents=True, exist_ok=True)
alternative_url = "https://www.landtag-saar.de/Downloadfile.ashx?FileId={}&FileName=PlPr{}_{}.pdf"
counter = 45450
for periode in range(17, (17+ceil((max_year-2022)/4))):
    for session in range(1, 300):
        if session < 10:
            session_str = "00" + str(session)
        elif session < 100:
            session_str = "0" + str(session)
        else:
            session_str = str(session)
        while True:
            url = alternative_url.format(counter, periode, session_str)
            r = requests.get(url, stream=True)
            if r.status_code != 404 and r.status_code != 403 and len(
                    r.content) > 50117:
                with open(f'{path}/{periode}_{session}.pdf', 'wb') as f:
                    f.write(r.content)
                    counter += 1
                    break
            else:
                counter += 1
# </editor-fold>

# <editor-fold desc="Sachsen">
print("Sachsen funktioniert nur auf Windows mit Ueberwachung des Downloads")
from selenium import webdriver
from selenium.webdriver import ActionChains
import pyautogui
wd = webdriver.Chrome("C:/Users/kalange/Documents/Webscraping/chromedriver.exe")
action = ActionChains(wd)
path = Path(f"{start_path}/Sachsen")
path.mkdir(parents=True, exist_ok=True)
aux_url = "https://edas.landtag.sachsen.de/viewer.aspx?dok_nr={}&dok_art=PlPr&leg_per={}&pos_dok={}&dok_id="
alternative_url = "https://ws.landtag.sachsen.de/images/{}_PlPr_{}_{}_1_1_.pdf"
for periode in range(7, (7+ceil((max_year-2022)/4))):
    for session in range(53, 300):
        for x in [202]:#, 101, 201]:#range(1, 300):
            url = alternative_url.format(periode, session, x)
            web_url = aux_url.format(session, periode, x)
            wd.get(web_url)
            time.sleep(5)
            pyautogui.moveTo(2500, 500, duration=0.2)
            pyautogui.rightClick()
            pyautogui.moveTo(2520, 520, duration=0.2)
            pyautogui.leftClick()
            time.sleep(3)
            pyautogui.write(f'{path}\\0{periode}_{session}.pdf')
            pyautogui.press("enter")
# </editor-fold>

# <editor-fold desc="Sachsen-Anhalt">
path = Path(f"{start_path}/Sachsen-Anhalt")
path.mkdir(parents=True, exist_ok=True)
alternative_url = "https://padoka.landtag.sachsen-anhalt.de/files/plenum/wp{}/{}stzg.pdf"
for periode in range(8, (8+ceil((max_year-2022)/4))):
    for session in range(1, 300):
        if session < 10:
            session_str = "00" + str(session)
        elif session < 100:
            session_str = "0" + str(session)
        else:
            session_str = str(session)
        url = alternative_url.format(periode, session_str)
        r = requests.get(url, stream=True)
        if r.status_code != 404 and r.status_code != 403:
            with open(f'{path}/0{periode}_{session}.pdf', 'wb') as f:
                f.write(r.content)
# </editor-fold>

# <editor-fold desc="Schleswig-Holstein">
path = Path(f"{start_path}/Schleswig-Holstein")
path.mkdir(parents=True, exist_ok=True)
alternative_url = "https://www.landtag.ltsh.de/export/sites/ltsh/infothek/wahl{}/plenum/plenprot/{}/{}-{}_{}-{}.pdf"
month = 6
year = 2022
session = 1
for periode in range(20, (20+ceil((max_year-2022)/4))):
    while session < 300:
        url = alternative_url.format(periode, year, periode, transform_session(session), transform_month(month), str(year)[2:4])
        r = requests.get(url, stream=True)
        if r.status_code != 404 and r.status_code != 403:
            with open(f'{path}/{periode}_{session}.pdf', 'wb') as f:
                f.write(r.content)
            session += 1
        else:
            month += 1
            if month > 12:
                month = 0
                year += 1
                print(year)
# </editor-fold>

# <editor-fold desc="Thueringen">
print("Thueringen funktioniert nur auf Windows mit Ueberwachung des Downloads")
path = Path(f"{start_path}/Thueringen")
path.mkdir(parents=True, exist_ok=True)
from selenium.webdriver.common.by import By
import pyautogui
import urllib
wd = webdriver.Chrome("C:/Users/kalange/Documents/Webscraping/chromedriver.exe")
for wp in range(7, (7+ceil((max_year-2022)/4))):
    for doc_number in range(1, 200):
        wd.get("https://parldok.thueringer-landtag.de/ParlDok/dokumentennummer")
        time.sleep(1)
        drop_down = wd.find_element(By.ID, "LegislaturperiodenList-button")
        drop_down.click()
        wd.find_elements(By.CLASS_NAME, "ui-menu-item")[8-wp].click()
        pyautogui.scroll(500)
        wd.find_elements(By.CLASS_NAME, "form-check-label")[2].click()
        pyautogui.scroll(-500)
        element = wd.find_element(By.CLASS_NAME, "btn-primary")
        wd.execute_script("return arguments[0].scrollIntoView(true);", element)
        wd.find_element(By.ID, "DokumentenNummer").clear()
        wd.find_element(By.ID, "DokumentenNummer").send_keys(str(doc_number))
        element.click()
        time.sleep(0.5)
        try:
            wd.find_element(By.CLASS_NAME, "col-12").click()
            time.sleep(2)
            response = urllib.request.urlopen(wd.current_url)
            with open(f'{path}/{wp}_{doc_number}.pdf', 'wb') as f:
                f.write(response.read())
        except:
            break
# </editor-fold>
