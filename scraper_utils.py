"""
Utility functions for scraping election data from HTML pages.
Provides helpers for requesting, extracting, and processing
election results.
"""

from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup as bs
from bs4.element import Tag


def request_data(url: str) -> bs:
    """
    Get HTML content from a URL and return a BeautifulSoup object.

    Args:
        url (str): The URL to fetch.

    Returns:
        BeautifulSoup: Parsed HTML content.

    Raises:
        requests.RequestException: If the request fails.
    """
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        return bs(response.text, 'html.parser')
    except requests.RequestException as e:
        raise requests.RequestException(f'Request failed: {e}')


def extract_data(soup: bs, locator: tuple[str, dict]) -> list[str]:
    """
    Extract text content from selected HTML elements.

    Args:
        soup (BeautifulSoup): Parsed HTML content.
        locator (tuple[str, dict]): Tag and attribute dictionary
            for selection.

    Returns:
        list[str]: List of extracted text values.
    """
    elements = soup.find_all(*locator)
    extracted_values = []
    for element in elements:
        extracted_values.append(
            element.get_text(strip=True).replace('\xa0', ' ')
        )
    return extracted_values


def extract_links(soup: bs, url: str, locator: tuple[str, dict]) -> list[str]:
    """
    Find and build full URLs from selected HTML elements.

    Args:
        soup (BeautifulSoup): Parsed HTML content.
        url (str): Base URL for joining relative links.
        locator (tuple[str, dict]): Tag and attribute dictionary
            for selection.

    Returns:
        list[str]: List of full URLs extracted from anchor tags.
    """
    parsed = urlparse(url)
    base_path = parsed.path.rsplit('/', 1)[0]
    base_url = f"{parsed.scheme}://{parsed.netloc}{base_path}/"
    elements = soup.find_all(*locator)
    links = []
    for td in elements:
        if isinstance(td, Tag):
            link_tag = td.find('a')
            if isinstance(link_tag, Tag):
                href = link_tag.get('href')
                if isinstance(href, str):
                    full_link = urljoin(base_url, href)
                    links.append(full_link)
    return links


def extract_csv_fieldnames(
        base_headers: list[str],
        soup: bs,
        party_locator: tuple[str, dict]
) -> list[str]:
    """
    Add party names to base CSV headers.

    Args:
        base_headers (list[str]): Initial CSV column headers.
        soup (BeautifulSoup): Parsed HTML content.
        party_locator (tuple[str, dict]): Tag and attribute dictionary
            for party name selection.

    Returns:
        list[str]: Extended list of CSV column headers including
            party names.
    """
    extended_headers = base_headers.copy()
    party_names = extract_data(soup, party_locator)
    for name in party_names:
        if name not in extended_headers:
            extended_headers.append(name)
    return extended_headers


def extract_district_data(
    link: str,
    votes_table1_locator: tuple[str, dict],
    votes_table2_locator: tuple[str, dict],
    registered_voters_locator: tuple[str, dict],
    envelopes_issued_locator: tuple[str, dict],
    valid_votes_locator: tuple[str, dict],
    csv_headers: list[str],
    party_name_locator: tuple[str, dict]
) -> tuple[list[str], list[str], list[str], list[str], list[str]]:
    """
    Extract all relevant data for a district from its detail page.

    Args:
        link (str): URL to the district detail page.
        votes_table1_locator, votes_table2_locator: Locators for
            vote tables.
        registered_voters_locator, envelopes_issued_locator,
            valid_votes_locator: Locators for summary fields.
        csv_headers (list[str]): Base CSV headers.
        party_name_locator: Locator for party names.

    Returns:
        tuple: (party_votes, reg_voters, issued_envelopes,
            valid_votes, party_names)
    """
    soup = request_data(link)
    party_votes =(
        extract_data(soup, votes_table1_locator)
        + extract_data(soup, votes_table2_locator)
    )
    reg_voters = extract_data(soup, registered_voters_locator)
    issued_envelopes = extract_data(soup, envelopes_issued_locator)
    valid_votes = extract_data(soup, valid_votes_locator)
    party_names = extract_csv_fieldnames(
        csv_headers, soup, party_name_locator
    )
    return party_votes, reg_voters, issued_envelopes, valid_votes, party_names


def process_election_results(
    district_links: list[str],
    votes_table1_locator: tuple[str, dict],
    votes_table2_locator: tuple[str, dict],
    registered_voters_locator: tuple[str, dict],
    envelopes_issued_locator: tuple[str, dict],
    valid_votes_locator: tuple[str, dict],
    csv_headers: list[str],
    party_name_locator: tuple[str, dict],
    district_codes: list[str],
    district_names: list[str]
) -> tuple[list[dict], list[str]]:
    """
    Process election results for all districts and return final
    results and fieldnames.

    Args:
        district_links (list[str]): List of URLs to district detail
            pages.
        votes_table1_locator (tuple[str, dict]): Locator for first
            vote table.
        votes_table2_locator (tuple[str, dict]): Locator for second
            vote table.
        registered_voters_locator (tuple[str, dict]): Locator for
            registered voters field.
        envelopes_issued_locator (tuple[str, dict]): Locator for
            issued envelopes field.
        valid_votes_locator (tuple[str, dict]): Locator for valid
            votes field.
        csv_headers (list[str]): Base CSV column headers.
        party_name_locator (tuple[str, dict]): Locator for party
            names.
        district_codes (list[str]): List of district codes.
        district_names (list[str]): List of district names.

    Returns:
        tuple[list[dict], list[str]]: Final results as list of dicts
            and CSV fieldnames.

    Raises:
        ValueError: If no CSV fieldnames are extracted.
    """
    party_vote_counts = []
    all_fieldnames = []
    reg_voters = []
    issued_envelopes = []
    valid_votes_count = []

    for link in district_links:
        party_votes, reg, envelopes, valid_votes, party_names = (
            extract_district_data(
            link,
            votes_table1_locator,
            votes_table2_locator,
            registered_voters_locator,
            envelopes_issued_locator,
            valid_votes_locator,
            csv_headers,
            party_name_locator
            )
        )
        if not party_votes:
            print(f'Warning: No party votes found for {link}')
        party_vote_counts.append(party_votes)
        reg_voters += reg
        issued_envelopes += envelopes
        valid_votes_count += valid_votes
        if not all_fieldnames:
            all_fieldnames = party_names
    if not all_fieldnames:
        raise ValueError('No CSV fieldnames extracted.')

    party_votes_dict = []
    for vote_row in party_vote_counts:
        vote_mapping = dict(zip(all_fieldnames[5:], vote_row))
        party_votes_dict.append(vote_mapping)

    final_results = []
    for code, name, voters, envelopes, valid, party_votes in zip(
        district_codes,
        district_names,
        reg_voters,
        issued_envelopes,
        valid_votes_count,
        party_votes_dict
    ):
        row = {
            'Kód': code,
            'Obec': name,
            'Voliči v seznamu': voters,
            'Vydané obálky': envelopes,
            'Platné hlasy': valid
        }
        row.update(party_votes)
        final_results.append(row)

    return final_results, all_fieldnames
