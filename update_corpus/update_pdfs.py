import os
import re

import requests
import pathlib
import time
from pathlib import Path
from math import ceil
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium import webdriver
from selenium.webdriver import ChromeOptions
import selenium
from selenium.webdriver import ActionChains
import pyautogui
from selenium.webdriver.common.by import By
import pyautogui
import urllib
from selenium.webdriver.support.ui import Select


def get_landtag_pdf(name, initial_year, max_year, initial_period, initial_session, start_path, max_period=None):
    if max_period is None:
        max_period = initial_period + 2

    def get_pdfs(orig_url, kuerzel, additional_zeroes=True, double=False, switch=False):
        path = pathlib.Path(f'{start_path}/{kuerzel}')
        path.mkdir(parents=True, exist_ok=True)
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:66.0) Gecko/20100101 Firefox/66.0",
            "Accept-Encoding": "*",
            "Connection": "keep-alive"
        }
        for period in range(initial_period, (initial_period + ceil((max_year - initial_year) / 4))):
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
                    #print(url)
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

    if name == "Baden-Württemberg":
        # <editor-fold desc="Baden-Württemberg">
        path = Path(f"{start_path}/Baden-Württemberg")
        path.mkdir(parents=True, exist_ok=True)
        alternative_url = "https://www.landtag-bw.de/files/live/sites/LTBW/files/dokumente/WP{}/Plp/{}_0{}_{}{}{}.pdf"
        periode = initial_period
        session = initial_session
        for year in range(initial_year, max_year):
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
    elif name == "Bayern":
        # <editor-fold desc="Bayern">
        print("For Bayern, you have to enter and download each period separately. Please enter the website to download the pdfs from:\n")
        website = input("Enter website: ")
        website = website.strip() if website else "https://www.bayern.landtag.de/webangebot3/views/protokolle/protokollsuche.xhtml?datum=30.10.2023&gremium=PL&sCalledURL=https%3A%2F%2Fwww.bayern.landtag.de%2Fparlament%2Fdokumente%2Fprotokolle%2F"
        path = Path(f"{start_path}/Bayern")
        path.mkdir(parents=True, exist_ok=True)
        wd = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
        params = {'cmd': 'Page.setDownloadBehavior', 'params': {'behavior': 'allow', 'downloadPath': os.path.abspath(path)}}
        wd.command_executor._commands["send_command"] = ("POST", '/session/$sessionId/chromium/send_command')
        wd.execute("send_command", params)
        wd.get(website)
        time.sleep(1)
        wd.find_element(By.ID, "mcc-deny").click()
        time.sleep(1)
        for x in range(1, 302):
            try:
                wd.find_element(By.XPATH, f"/html/body/div[1]/main/div[2]/div[2]/div/div[1]/div/div/div/div[1]/div[1]/div[4]/form/div[2]/div[2]/div[3]/div/table/tbody/tr[{x}]/td[3]/a[1]").click()
                time.sleep(5)
            except selenium.common.exceptions.NoSuchElementException:
                pass
        # </editor-fold>
    elif name == "Berlin":
        # <editor-fold desc="Berlin">
        path = Path(f"{start_path}/Berlin")
        path.mkdir(parents=True, exist_ok=True)
        for periode in range(initial_period, max_period):
            start = initial_session if periode == initial_period else 1
            for session in range(start, 300):
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
    elif name == "Brandenburg":
        # <editor-fold desc="#Brandenburg">
        url = "https://www.landtag.nrw.de/portal/WWW/dokumentenarchiv/Dokument/ERP{}-{}.pdf"
        get_pdfs(url, "Brandenburg", False)
        path = Path(f"{start_path}/Brandenburg")
        path.mkdir(parents=True, exist_ok=True)
        alternative_url = "https://www.parlamentsdokumentation.brandenburg.de/starweb/LBB/ELVIS/parladoku/w{}/plpr/{}.pdf"
        for periode in range(initial_period, max_period):
            start = initial_session if periode == initial_period else 1
            for session in range(start, 300):
                url = alternative_url.format(periode, session)
                r = requests.get(url, stream=True)
                if r.status_code != 404 and r.status_code != 403:
                    with open(f'{path}/{periode}_{session}.pdf', 'wb') as f:
                        f.write(r.content)

        # </editor-fold>
    elif name == "Bremen":
        # <editor-fold desc="Bremen">
        path = Path(f"{start_path}/Bremen")
        path.mkdir(parents=True, exist_ok=True)

        alternative_url = "https://www.bremische-buergerschaft.de/dokumente/wp{}/land/protokoll/P{}L0{}.pdf"
        for periode in range(initial_period, max_period):
            start = initial_session if periode == initial_period else 1
            for session in range(start, 300):
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
    elif name == "Hamburg":
        # <editor-fold desc="Hamburg">
        print("For Hamburg, you have to enter and download each period separately.")
        path = Path(f"{start_path}/Hamburg")
        path.mkdir(parents=True, exist_ok=True)
        wd = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
        params = {'cmd': 'Page.setDownloadBehavior', 'params': {'behavior': 'allow', 'downloadPath': os.path.abspath(path)}}
        wd.command_executor._commands["send_command"] = ("POST", '/session/$sessionId/chromium/send_command')
        wd.execute("send_command", params)
        for periode in range(initial_period, max_period):
            wd.get("https://www.buergerschaft-hh.de/parldok/formalkriterien")
            time.sleep(5)
            wd.find_element(By.CLASS_NAME, "cookiebtn").click()
            dropdown = wd.find_element(By.ID, "LegislaturperiodenList")
            dropdown.click()
            Select(dropdown).select_by_value(str(periode))
            dropdown.click()
            time.sleep(1)
            type = wd.find_element(By.ID, "DokumententypId")
            Select(type).select_by_visible_text("Plenarprotokoll")
            time.sleep(1)
            wd.find_element(By.XPATH, "/html/body/div[4]/div[2]/div/form/fieldset/table/tbody/tr[8]/td[2]/input").click()
            time.sleep(5)
            for x in range(1, 31):
                if x > 0:
                    wd.get(f"https://www.buergerschaft-hh.de/parldok/formalkriterien/{x}")
                for y in range(10):
                    try:
                        time.sleep(1)
                        wd.find_element(By.XPATH, f"/html/body/div[4]/div[2]/div/table/tbody/tr[{(y+1) * 5 + 1}]/td[2]/a").click()
                        protocol_name = wd.current_url
                        reg = re.match(r".*/plenarprotokoll_(\d+)_(\d+).pdf", protocol_name)
                        if int(reg.group(1)) <= initial_period and int(reg.group(2)) <= initial_session:
                            break
                        time.sleep(1)
                        r = requests.get(wd.current_url, stream=True)
                        with open(f'{path}/{reg.group(1)}_{reg.group(2)}.pdf', 'wb') as f:
                            f.write(r.content)
                        wd.get(f"https://www.buergerschaft-hh.de/parldok/formalkriterien/{x}")
                    except selenium.common.exceptions.NoSuchElementException:
                        break
                if y < 9:
                    break
        # </editor-fold>
    elif name == "Hessen":
        # <editor-fold desc="Hessen">
        #      https://starweb.hessen.de/cache/PLPR/01/0/00010.pdf
        url = "https://starweb.hessen.de/cache/PLPR/{}/{}/00{}.pdf"
        get_pdfs(url, "Hessen", True)
        # </editor-fold>
    elif name == "Mecklenburg-Vorpommern":
        # <editor-fold desc="Mecklenburg-Vorpommern">
        path = Path(f"{start_path}/Mecklenburg-Vorpommern")
        path.mkdir(parents=True, exist_ok=True)
        alternative_url = "https://www.landtag-mv.de/fileadmin/media/Dokumente/Parlamentsdokumente/Plenarprotokolle/{}_Wahlperiode/PlPr{}-0{}.pdf"
        for periode in range(initial_period, max_period):
            start = initial_session if periode == initial_period else 1
            for session in range(start, 300):
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
    elif name == "Niedersachsen":
        # <editor-fold desc="Niedersachsen">
        path = Path(f"{start_path}/Niedersachsen")
        path.mkdir(parents=True, exist_ok=True)
        alternative_url = "https://www.landtag-niedersachsen.de/parlamentsdokumente/steno/{}_wp/endber{}.pdf"
        for periode in range(initial_period, max_period):
            start = initial_session if periode == initial_period else 1
            for session in range(start, 300):
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
    elif name == "Nordrhein-Westfalen":
        # <editor-fold desc="Nordrhein Westfahlen">
        path = Path(f"{start_path}/Nordrhein-Westfalen")
        path.mkdir(parents=True, exist_ok=True)
        for periode in range(initial_period, max_period):
            start = initial_session if periode == initial_period else 1
            for session in range(start, 360):
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
    elif name == "Rheinland-Pfalz":
        # <editor-fold desc="Rheinland-Pfalz">
        path = Path(f"{start_path}/Rheinland-Pfalz")
        path.mkdir(parents=True, exist_ok=True)
        alternative_url = "https://dokumente.landtag.rlp.de/landtag/plenarprotokolle/{}-P-{}.pdf"
        alternative_url = "https://dokumente.landtag.rlp.de/landtag/plenarprotokolle/PLPR-Sitzung-{}-{}.pdf"
        alternative_url = "https://dokumente.landtag.rlp.de/landtag/plenarprotokolle/{}-P-{}.pdf"
        #get_pdfs(url, "RLP", False)
        for periode in range(initial_period, max_period):
            start = initial_session if periode == initial_period else 1
            for session in range(start, 300):
                url = alternative_url.format(session, periode)
                r = requests.get(url, stream=True)
                if r.status_code != 404 and r.status_code != 403 and len(r.content) > 26865 and r.url != 'https://landtag-rlp.de':
                    with open(f'{path}/{periode}_{session}.pdf', 'wb') as f:
                        f.write(r.content)
        # </editor-fold>
    elif name == "Saarland":
        # <editor-fold desc="Saarland">
        path = Path(f"{start_path}/Saarland")
        path.mkdir(parents=True, exist_ok=True)
        alternative_url = "https://www.landtag-saar.de/Downloadfile.ashx?FileId={}&FileName=PlPr{}_{}.pdf"
        counter = 45450
        for periode in range(initial_period, max_period):
            start = initial_session if periode == initial_period else 1
            for session in range(start, 300):
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
    elif name == "Sachsen":
        # <editor-fold desc="Sachsen">
        path = Path(f"{start_path}/Sachsen")
        path.mkdir(parents=True, exist_ok=True)
        print("Sachsen only works when having the browser window open at all times")
        wd = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
        params = {'cmd': 'Page.setDownloadBehavior', 'params': {'behavior': 'allow', 'downloadPath': os.path.abspath(path)}}
        wd.command_executor._commands["send_command"] = ("POST", '/session/$sessionId/chromium/send_command')
        wd.execute("send_command", params)
        action = ActionChains(wd)
        aux_url = "https://edas.landtag.sachsen.de/viewer.aspx?dok_nr={}&dok_art=PlPr&leg_per={}&pos_dok={}&dok_id="
        alternative_url = "https://ws.landtag.sachsen.de/images/{}_PlPr_{}_{}_1_1_.pdf"
        for periode in range(initial_period, max_period):
            start = initial_session if periode == initial_period else 1
            for session in range(start, 200):
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
    elif name == "Sachsen-Anhalt":
        # <editor-fold desc="Sachsen-Anhalt">
        path = Path(f"{start_path}/Sachsen-Anhalt")
        path.mkdir(parents=True, exist_ok=True)
        alternative_url = "https://padoka.landtag.sachsen-anhalt.de/files/plenum/wp{}/{}stzg.pdf"
        for periode in range(initial_period, max_period):
            start = initial_session if periode == initial_period else 1
            for session in range(start, 300):
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
    elif name == "Schleswig-Holstein":
        # <editor-fold desc="Schleswig-Holstein">
        path = Path(f"{start_path}/Schleswig-Holstein")
        path.mkdir(parents=True, exist_ok=True)
        alternative_url = "https://www.landtag.ltsh.de/export/sites/ltsh/infothek/wahl{}/plenum/plenprot/{}/{}-{}_{}-{}.pdf"
        month = 1
        year = initial_year
        session = initial_session
        for periode in range(initial_period, max_period):
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
                    if year >= max_year:
                        break
        # </editor-fold>
    elif name == "Thüringen":
        # <editor-fold desc="Thueringen">
        print("Thüringen only works when having the browser window open at all times")
        path = Path(f"{start_path}/Thüringen")
        path.mkdir(parents=True, exist_ok=True)
        wd = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
        params = {'cmd': 'Page.setDownloadBehavior', 'params': {'behavior': 'allow', 'downloadPath': os.path.abspath(path)}}
        wd.command_executor._commands["send_command"] = ("POST", '/session/$sessionId/chromium/send_command')
        wd.execute("send_command", params)
        action = ActionChains(wd)
        for wp in range(initial_period, max_period):
            start = initial_session if wp == initial_period else 1
            for doc_number in range(start, 200):
                wd.get("https://parldok.thueringer-landtag.de/ParlDok/dokumentennummer")
                time.sleep(1)
                try:
                    action.move_to_element_with_offset(wd.find_element(By.CLASS_NAME, "grt-cookie-button"), 5, 5)
                    action.click()
                    action.perform()
                    wd.get("https://parldok.thueringer-landtag.de/ParlDok/dokumentennummer")
                    #wd.execute_script("document.body.style.zoom='50%'")
                except:
                    pass
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
                    r = requests.get(wd.current_url, stream=True)
                    with open(f'{path}/{wp}_{doc_number}.pdf', 'wb') as f:
                        f.write(r.content)
                    #response = urllib.request.urlopen(wd.current_url)
                    #with open(f'{path}/{wp}_{doc_number}.pdf', 'wb') as f:
                    #    f.write(response.read())
                except:
                    break
        # </editor-fold>
    else:
        raise Exception("Landtag not found")

import argparse
argParser = argparse.ArgumentParser()
argParser.add_argument("-n", "--name", help="Name of the Landtag", type=str)
argParser.add_argument("-iy", "--inityear", help="Initial year", default=2023, type=int)
argParser.add_argument("-my", "--maxyear", help="Maximum year", default=2024, type=int)
argParser.add_argument("-ip", "--initperiod", help="Initial period", default=19, type=int)
argParser.add_argument("-mp", "--maxperiod", help="Maximum period", default="pdfs", type=str)
argParser.add_argument("-is", "--initsession", help="Initial session - only needed for Baden-Württemberg", default=82, type=int)
argParser.add_argument("-p", "--path", help="Path to save all Landtag files in", default="pdfs", type=str)
if __name__ == '__main__':
    get_landtag_pdf(argParser.parse_args().name, argParser.parse_args().inityear, argParser.parse_args().maxyear+1, argParser.parse_args().initperiod,
                    argParser.parse_args().path, argParser.parse_args().max_period+1)