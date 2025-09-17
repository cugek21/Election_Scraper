"""
Entry point for the election scraper project.
Handles argument parsing, version check, and orchestrates
scraping and CSV export.

author: Radek Jíša
email: radek.jisa@gmail.com
"""

import sys

from csv_utils import save_csv
from scraper_utils import (
    request_data,
    extract_data,
    extract_links,
    process_election_results
)

DISTRICT_CODE_LOCATOR = ('td', {'class': 'cislo'})
DISTRICT_NAME_LOCATOR = ('td', {'class': 'overflow_name'})
REG_VOTERS_LOCATOR = ('td', {'class': 'cislo', 'headers': 'sa2'})
ISSUED_ENVELOPES_LOCATOR = ('td', {'class': 'cislo', 'headers': 'sa3'})
VALID_VOTES_LOCATOR = ('td', {'class': 'cislo', 'headers': 'sa6'})
VOTES_T1_LOCATOR = ('td', {'class': 'cislo', 'headers': 't1sa2 t1sb3'})
VOTES_T2_LOCATOR = ('td', {'class': 'cislo', 'headers': 't2sa2 t2sb3'})
PARTY_NAME_LOCATOR = ('td', {'class': 'overflow_name'})
CSV_HEADERS = [
    'Kód',
    'Obec',
    'Voliči v seznamu',
    'Vydané obálky',
    'Platné hlasy'
]


def check_python_version(required=(3, 10)):
    """
    Raises an error if the Python version is below the required.
    
    Args:
        required (tuple): Required Python version as (major, minor).

    Raises:
        RuntimeError: If current version is lower than required.
    """
    current = sys.version_info
    if current[:2] < required:
        raise RuntimeError(
        f'Requires Python {required[0]}.{required[1]}+, '
        f'but found {current.major}.{current.minor}'
        )


def main(
    url: str,
    csv_filename: str,
    district_code_locator: tuple[str, dict],
    district_name_locator: tuple[str, dict],
    registered_voters_locator: tuple[str, dict],
    envelopes_issued_locator: tuple[str, dict],
    valid_votes_locator: tuple[str, dict],
    votes_table1_locator: tuple[str, dict],
    votes_table2_locator: tuple[str, dict],
    party_name_locator: tuple[str, dict],
    csv_headers: list[str]
) -> None:
    """
    Scrape election data from the given URL and export to CSV.

    Args:
        url (str): The URL to scrape.
        csv_filename (str): Output CSV filename.
        district_code_locator (tuple[str, dict]):
            Locator for district codes.
        district_name_locator (tuple[str, dict]):
            Locator for district names.
        registered_voters_locator (tuple[str, dict]):
            Locator for registered voters.
        envelopes_issued_locator (tuple[str, dict]):
            Locator for issued envelopes.
        valid_votes_locator (tuple[str, dict]):
            Locator for valid votes.
        votes_table1_locator (tuple[str, dict]):
            Locator for first vote table.
        votes_table2_locator (tuple[str, dict]):
            Locator for second vote table.
        party_name_locator (tuple[str, dict]): Locator for party names.
        csv_headers (list[str]): List of CSV column headers.

    Returns:
        None

    Raises:
        ValueError: If required data cannot be extracted or saved.
    """

    print(f'Connecting to {url}')
    soup = request_data(url)
    district_codes = extract_data(soup, district_code_locator)
    district_names = extract_data(soup, district_name_locator)
    district_links = extract_links(soup, url, district_code_locator)
    if not (district_codes and district_names and district_links):
        raise ValueError('Failed to extract district codes, names, or links.')

    all_fieldnames = []
    print('Processing data...')
    final_results, all_fieldnames = process_election_results(
        district_links,
        votes_table1_locator,
        votes_table2_locator,
        registered_voters_locator,
        envelopes_issued_locator,
        valid_votes_locator,
        csv_headers,
        party_name_locator,
        district_codes,
        district_names
    )
    if not final_results:
        raise ValueError('No results to save.')

    save_csv(final_results, all_fieldnames, csv_filename)


if __name__ == '__main__':
    if len(sys.argv) != 3:
        print('Wrong input. Type: python main.py \'<URL>\' csv_name')
        sys.exit()
    url_arg = sys.argv[1]
    filename_arg = sys.argv[2]

    check_python_version((3,10))
    main(
        url_arg,
        filename_arg,
        DISTRICT_CODE_LOCATOR,
        DISTRICT_NAME_LOCATOR,
        REG_VOTERS_LOCATOR,
        ISSUED_ENVELOPES_LOCATOR,
        VALID_VOTES_LOCATOR,
        VOTES_T1_LOCATOR,
        VOTES_T2_LOCATOR,
        PARTY_NAME_LOCATOR,
        CSV_HEADERS
    )
