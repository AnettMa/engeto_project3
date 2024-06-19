"""
projekt_3.py: třetí projekt do Engeto Online Python Akademie
author: Anetta Martináková
email: martinakova.anetta@gmail.com
discord: Anetta M.#5044 (or originally known as zrzavahlava#5044)
"""

import requests
import csv
import click
import validators
import sys
import structlog
from bs4 import BeautifulSoup


structlog.configure(
    processors=[
        structlog.processors.TimeStamper(fmt='iso'),
        structlog.processors.JSONRenderer()
    ],
    logger_factory=structlog.PrintLoggerFactory(file=sys.stdout)
)

logger = structlog.get_logger()


def scrape_main_url(main_url, output_filename):
    """Scrape URL from user - save code and name of the city + create list of URLs that should be scraped further."""
    response_from_main_url = fetch_page(main_url)
    main_url_soup = BeautifulSoup(response_from_main_url.text, 'html.parser')

    codes = main_url_soup.find_all(class_='cislo')
    locations = main_url_soup.find_all('td', class_='overflow_name')
    href_values = extract_href_values(main_url_soup)

    urls = []
    for href_value in href_values:
        urls.append(f'https://www.volby.cz/pls/ps2017nss/{href_value}')

    scrape_data(codes, locations, urls, output_filename)


def fetch_page(url):
    """Fetch a page and return the response object."""
    logger.info('Requesting page.', extra={'url': url})
    try:
        response = requests.get(url)
        response.raise_for_status()
        logger.info('Page retrieved.', extra={'url': url, 'status_code': response.status_code})
        return response
    except requests.exceptions.HTTPError as e:
        logger.error('HTTP error occurred while retrieving page.', extra={'url': url, 'error': str(e)})
        raise e
    except Exception as e:
        logger.error(f'An error occurred while retrieving page: {e}', extra={'url': url, 'error': str(e)})
        raise e


def extract_href_values(soup):
    """Extract href values from the soup object."""
    headers_to_check = {'t1sa1', 't2sa1', 't3sa1'}
    return [
        a_tag['href']
        for td in soup.find_all('td', {'class': 'cislo'})
        if any(header in td.get('headers', '') for header in headers_to_check)
        if (a_tag := td.find('a')) and 'href' in a_tag.attrs
    ]


def scrape_data(codes, locations, urls, output_filename):
    cities_locations_data = []
    votes_data = []
    for code, location in zip(codes, locations):
        code_text = code.text.strip()
        location_text = location.text.strip()
        cities_locations_data.append({'Code': code_text, 'Location': location_text})

    for url in urls:
        logger.info('Requesting page.', url=url)
        response_from_url = fetch_page(url)
        districts_url_soup = BeautifulSoup(response_from_url.text, 'html.parser')
        registered = districts_url_soup.find('td', class_='cislo', headers='sa2').text
        envelopes = districts_url_soup.find('td', class_='cislo', headers='sa3').text
        valid_votes = districts_url_soup.find('td', class_='cislo', headers='sa6').text

        cleaned_registered = clean_data(registered)
        cleaned_envelopes = clean_data(envelopes)
        cleaned_valid_votes = clean_data(valid_votes)

        party_details = {}
        for table_idx, parties_div in enumerate(districts_url_soup.find_all('div', class_='t2_470'), start=1):
            for party_row in parties_div.find_all('tr'):
                # Skip header and empty row
                if party_row.find('th') or \
                        party_row.find('td', class_='hidden_td', headers=f't{table_idx}sa1 t{table_idx}sb1'):
                    continue

                party_name = party_row.find('td', class_='overflow_name').text
                party_count = party_row.find('td', class_='cislo', headers=f't{table_idx}sa2 t{table_idx}sb3').text

                cleaned_party_name = clean_data(party_name)
                cleaned_party_count = clean_data(party_count)
                party_details[cleaned_party_name] = cleaned_party_count

        votes_data.append({
            'Registered': cleaned_registered,
            'Envelopes': cleaned_envelopes,
            'Valid': cleaned_valid_votes,
            'party_details': party_details
        })

    scraped_data_cleanup(cities_locations_data, votes_data, output_filename)


def scraped_data_cleanup(cities_locations_data, votes_data, output_filename):
    party_names = list(votes_data[0]['party_details'].keys())
    fieldnames = ['Code', 'Location', 'Registered', 'Envelopes', 'Valid'] + party_names

    for data in votes_data:
        party_details = data.pop('party_details', None)
        if not party_details:
            continue
        data.update(**party_details)

    combined_data = []
    for city, vote in zip(cities_locations_data, votes_data):
        combined_entry = {**city, **vote}
        combined_data.append(combined_entry)

    write_data_into_csv(combined_data, fieldnames, output_filename)


def write_data_into_csv(combined_data, fieldnames, filename):
    """Write scraped data into a CSV file."""

    with open(filename, mode='w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)

        writer.writeheader()
        for data in combined_data:
            writer.writerow(data)


def clean_data(text):
    """Clean data by replacing non-breaking space characters with regular spaces."""
    return text.replace('\xa0', ' ')


@click.command()
@click.argument('main_url')
@click.argument('output_filename')
def main(main_url, output_filename):
    """To run this script please use 2 arguments separated by space:

    URL in format: 'https://volby.cz/pls/ps2017nss/ps311?xjazyk=CZ&xkraj=2&xnumnuts=2101'

    and name of CSV file in format: 'name.csv'"""
    if not validators.url(main_url):
        sys.exit('Invalid URL. Please provide valid URL.')
    if not output_filename.endswith('.csv'):
        sys.exit('Invalid filename. Output filename must end with .csv')
    try:
        scrape_main_url(main_url, output_filename)
    except Exception as e:
        sys.exit(e)


if __name__ == '__main__':
    main()


# example url = 'https://volby.cz/pls/ps2017nss/ps32?xjazyk=CZ&xkraj=12&xnumnuts=7103'
