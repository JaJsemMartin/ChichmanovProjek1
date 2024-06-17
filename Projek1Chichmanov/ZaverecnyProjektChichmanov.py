# Projekt: project_3
# Autor: Martin Chichmanov
# Email: chichtium@gmail.com
# Discord: martymcgold

import requests
from bs4 import BeautifulSoup
import csv
import sys
import argparse

def odstranit_po_posledni_lomitko(url):
    posledni_lomitko_index = url.rfind('/')
    if posledni_lomitko_index != -1:
        return url[:posledni_lomitko_index]
    return url

def stahni_vysledky_voleb(url, vystupni_soubor):
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        rows = soup.find_all('tr')

        data = []

        for row in rows:
            cells = row.find_all("td")
            if len(cells) >= 2:
                cell1 = cells.pop(0)
                cell2 = cells.pop(0)
                odkazy = cell1.find_all("a")
                if len(odkazy) >= 1:
                    odkaz1 = odkazy.pop(0)
                    href = odkaz1.get("href")
                    url2 = odstranit_po_posledni_lomitko(url) + "/" + href

                    radek_data = [cell1.get_text(strip=True), cell2.get_text(strip=True)]
                    ziskej_podrobne_vysledky(url2, data, radek_data)

        with open(vystupni_soubor, 'w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file, delimiter=";")
            writer.writerows(data)

        print(f"Výsledky byly uloženy do souboru {vystupni_soubor}")
    except requests.RequestException as e:
        print(f"Chyba při stahování dat: {e}")
    except Exception as e:
        print(f"Došlo k chybě: {e}")

def ziskej_podrobne_vysledky(url, excel_radky, radek_data):
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        rows = soup.find_all('tr')
        hlavicky = []

        for row in rows:
            cells = row.find_all("td")
            if len(cells) == 9:
                cell1 = cells.pop(3)
                cell2 = cells.pop(3)
                platne_hlasy = cells.pop(5)
                radek_data.extend([cell1.get_text(strip=True), cell2.get_text(strip=True), platne_hlasy.get_text(strip=True)])
            elif len(cells) == 5:
                nazev_strany = cells.pop(1).get_text(strip=True)
                celkem_hlas = cells.pop(1).get_text(strip=True)
                radek_data.append(celkem_hlas)
                hlavicky.append(nazev_strany)
        
        if len(excel_radky) == 0:
            hlavicky = ['kod_obce', 'nazev_obce', 'volici', 'obalky', 'hlasy'] + hlavicky
            excel_radky.append(hlavicky)
        excel_radky.append(radek_data)
    except requests.RequestException as e:
        print(f"Chyba při stahování dat: {e}")
    except Exception as e:
        print(f"Došlo k chybě: {e}")

def main(url, vystupni_soubor):
    stahni_vysledky_voleb(url, vystupni_soubor)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Web scraping script')
    parser.add_argument('url', type=str, help='URL stránky, kterou chcete stáhnout')
    parser.add_argument('vystupni_soubor', type=str, help='Název výstupního souboru')
    args = parser.parse_args()

    if not args.url or not args.vystupni_soubor:
        print("Chyba: Musíte zadat oba argumenty: URL a název výstupního souboru.")
    else:
        main(args.url, args.vystupni_soubor)
