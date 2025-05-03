"""
main.py: třetí projekt do Engeto Online Python Akademie

author: Radek Jíša
email: radek.jisa@gmail.com

!!! VYTVORIT NOVY REPOZITAR !!!
"""


import csv
import sys
import requests
from bs4 import BeautifulSoup as bs


# HTML selectors for extracting data
DISTRICT_CODE_SELECTOR = ('td', {'class': 'cislo'})
DISTRICT_NAME_SELECTOR = ('td', {'class': 'overflow_name'})
REG_VOTERS_SELECTOR = ('td', {'class': 'cislo', 'headers': 'sa2'})
ISSUED_ENVELOPES_SELECTOR = ('td', {'class': 'cislo', 'headers': 'sa3'})
VALID_VOTES_SELECTOR = ('td', {'class': 'cislo', 'headers': 'sa6'})
VOTES_T1_SELECTOR = ('td', {'class': 'cislo', 'headers': 't1sa2 t1sb3'})
VOTES_T2_SELECTOR = ('td', {'class': 'cislo', 'headers': 't2sa2 t2sb3'})
PARTY_NAME_SELECTOR = ('td', {'class': 'overflow_name'})

# Base CSV column headers
CSV_HEADERS = ['Kód', 'Obec', 'Voliči v seznamu', 'Vydané obálky', 'Platné hlasy']


def request_data(url: str) -> bs:
    '''Get HTML content and return BeautifulSoup object'''

    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        return bs(response.text, 'html.parser')
    except requests.exceptions.RequestException as e:
        print(f'Request failed: {e}')
        sys.exit()


def extract_data(parsed_html: bs, selector: tuple[str, dict]) -> list[str]:
    '''Extract text from selected HTML'''

    elements_html = parsed_html.find_all(*selector)
    extracted_values = []
    for element in elements_html:
        extracted_values.append(element.get_text(strip=True).replace('\xa0', ' '))
    return extracted_values


def extract_links(parsed_html: bs, selector: tuple[str, dict]) -> list[str]:
    '''Find and build full URLs from selected HTML'''

    links_html = parsed_html.find_all(*selector)
    links = []
    for td in links_html:
        link = td.find('a')
        if link and link.get('href'):
            full_link = 'https://www.volby.cz/pls/ps2017nss/' + link['href']
            links.append(full_link)
    return links


def extract_csv_fieldnames(
        base_headers: list,
        parsed_html: bs,
        party_selector: tuple[str, dict]
        ) -> list[str]:
    '''Add party names to CSV headers'''

    extended_headers = base_headers.copy()
    party_names = extract_data(parsed_html, party_selector)
    for name in party_names:
        if name not in extended_headers:
            extended_headers.append(name)
    return extended_headers


def extract_votes(
        parsed_html: bs,
        selector_1: tuple[str, dict],
        selector_2: tuple[str, dict]
        ) -> list[str]:
    '''Extract all vote counts from both vote tables'''

    list_of_votes = extract_data(parsed_html, selector_1)
    list_of_votes += extract_data(parsed_html, selector_2)
    return list_of_votes


def save_csv(data: list[dict], headers: list[str], filename: str) -> None:
    '''Save list of dictionaries to a CSV file'''

    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, headers)
        writer.writeheader()
        writer.writerows(data)


def main(
        url: str,
        csv_filename: str,
        district_code_select: tuple[str, dict],
        district_name_select: tuple[str, dict],
        reg_voters_select: tuple[str, dict],
        issued_envelopes_select: tuple[str, dict],
        valid_votes_select: tuple[str, dict],
        votes_t1_select: tuple[str, dict],
        votes_t2_select: tuple[str, dict],
        party_name_select: tuple[str, dict],
        csv_headers: list[str]
        ) -> None:
    '''Main logic to scrape data and export to CSV'''

    #Load main page
    print(f'Connecting to {url}')
    soup = request_data(url)

    #Extract info and links from main page
    district_codes = extract_data(soup, district_code_select)
    district_names = extract_data(soup, district_name_select)
    district_links = extract_links(soup, district_code_select)

    #Prepare variables
    party_vote_counts = []
    all_fieldnames = []
    reg_voters = []
    issued_envelopes = []
    valid_votes_count = []

    #Scrape detail pages
    print('Processing data...')
    for link in district_links:
        inner_soup = request_data(link)
        party_vote_counts.append(extract_votes(inner_soup, votes_t1_select, votes_t2_select))
        reg_voters += extract_data(inner_soup, reg_voters_select)
        issued_envelopes += extract_data(inner_soup, issued_envelopes_select)
        valid_votes_count += extract_data(inner_soup, valid_votes_select)
        if not all_fieldnames:
            all_fieldnames = extract_csv_fieldnames(csv_headers, inner_soup, party_name_select)

    #Pair votes with names
    party_votes_dict = []
    for vote_row in party_vote_counts:
        vote_mapping = dict(zip(all_fieldnames[5:], vote_row))
        party_votes_dict.append(vote_mapping)

    #Merge data
    final_results = []
    for i, _ in enumerate(district_links):
        row = {
            'Kód': district_codes[i],
            'Obec': district_names[i],
            'Voliči v seznamu': reg_voters[i],
            'Vydané obálky': issued_envelopes[i],
            'Platné hlasy': valid_votes_count[i]
        }
        row.update(party_votes_dict[i])
        final_results.append(row)

    #Export to CSV
    save_csv(final_results, all_fieldnames, csv_filename)
    print(f'File {csv_filename} exported')


if __name__ == '__main__':
    if len(sys.argv) != 3:
        print('Wrong input. Type: python main.py \'<URL>\' csv_name')
        sys.exit()

    Url_arg = sys.argv[1]
    Filename_arg = sys.argv[2]

    main(Url_arg,
        Filename_arg,
        DISTRICT_CODE_SELECTOR,
        DISTRICT_NAME_SELECTOR,
        REG_VOTERS_SELECTOR,
        ISSUED_ENVELOPES_SELECTOR,
        VALID_VOTES_SELECTOR,
        VOTES_T1_SELECTOR,
        VOTES_T2_SELECTOR,
        PARTY_NAME_SELECTOR,
        CSV_HEADERS
        )

#url = 'https://www.volby.cz/pls/ps2017nss/ps32?xjazyk=CZ&xkraj=9&xnumnuts=5303'
