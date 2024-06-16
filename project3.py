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


def write_data_into_csv(scraped_data, filename):
    """Write scraped data into a CSV file."""
    party_names = list(scraped_data[0]['party_details'].keys())
    fieldnames = ['Code', 'Location', 'Envelopes', 'Registered', 'Valid'] + party_names

    # transform scraped_data list -> remove party_details dict and unpack it
    for data in scraped_data:
        party_details = data.pop('party_details', None)
        if not party_details:
            continue
        data.update(**party_details)
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(scraped_data)


def clean_data(text):
    """Clean data by replacing non-breaking space characters with regular spaces."""
    return text.replace('\xa0', ' ')


def scrape_main_url(main_url, output_filename):
    """Scrape URL from user - save code and name of the city + create list of URLs that should be scraped further."""
    logger.info('Requesting page.', url=main_url)
    try:
        response_from_main_url = requests.get(main_url)
        response_from_main_url.raise_for_status()
        logger.info('Page retrieved.', url=main_url, status_code=response_from_main_url.status_code)
    except requests.exceptions.HTTPError as e:
        logger.info('HTTP error occurred while retrieving page.', url=main_url, error=str(e))
        raise e
    except Exception as e:
        logger.error(f'An error occurred while retrieving page: {e}', url=main_url, error=str(e))
        raise e
    main_url_soup = BeautifulSoup(response_from_main_url.text, 'html.parser')
    codes = main_url_soup.find_all(class_='cislo')
    locations = main_url_soup.find_all('td', class_='overflow_name')
    href_values = []
    td_elements = main_url_soup.find_all('td', {'class': 'center', 'headers': 't1sa2'})
    for td in td_elements:
        a_tag = td.find('a')
        if a_tag and 'href' in a_tag.attrs:
            href_values.append(a_tag['href'])
    urls = []
    for value in href_values:
        if 'xvyber' not in value:
            okrsek_url = f'https://www.volby.cz/pls/ps2017nss/{value}'
            logger.info('Requesting page.', url=okrsek_url)
            try:
                response_from_okrsek_url = requests.get(okrsek_url)
                response_from_okrsek_url.raise_for_status()
            except requests.exceptions.HTTPError as e:
                logger.info('HTTP error occurred while retrieving page.', url=okrsek_url, error=str(e))
                raise e
            except Exception as e:
                logger.error(f'An error occurred while retrieving page: {e}', url=main_url, error=str(e))
                raise e
            okrsek_url_soup = BeautifulSoup(response_from_okrsek_url.text, 'html.parser')
            okrsek_href = [i['href'] for i in okrsek_url_soup.find_all('a', href=True)]
            for okrsek in okrsek_href:
                if 'okrsek' not in okrsek:
                    continue
                else:
                    new_url = f'https://www.volby.cz/pls/ps2017nss/{okrsek}'
                    urls.append(new_url)
        else:
            new_url = f'https://www.volby.cz/pls/ps2017nss/{value}'
            urls.append(new_url)

    flattened_url_list = [item for sublist in urls for item in (sublist if isinstance(sublist, list) else [sublist])]
    scrape_data(codes, locations, flattened_url_list, output_filename)


def scrape_data(codes, locations, flattened_url_list, output_filename):
    scraped_data = []
    for code, location in zip(codes, locations):
        code_text = code.text.strip()
        location_text = location.text.strip()
        for url in flattened_url_list:
            logger.info('Requesting page.', url=url)
            try:
                response_from_url = requests.get(url)
                response_from_url.raise_for_status()
                logger.info('Page retrieved.', url=url, status_code=response_from_url.status_code)
            except requests.exceptions.HTTPError as e:
                logger.info('HTTP error occurred while retrieving page.', url=url, error=str(e))
                raise e
            except Exception as e:
                logger.error(f'An error occurred while retrieving page: {e}', url=url, error=str(e))
                raise e

            districts_url_soup = BeautifulSoup(response_from_url.text, 'html.parser')
            envelopes = districts_url_soup.find('td', class_='cislo', headers='sa3').text
            registered = districts_url_soup.find('td', class_='cislo', headers='sa2').text
            valid_votes = districts_url_soup.find('td', class_='cislo', headers='sa6').text

            cleaned_envelopes = clean_data(envelopes)
            cleaned_registered = clean_data(registered)
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

                    party_details[party_name] = party_count

            scraped_data.append({
                'Code': code_text,
                'Location': location_text,
                'Envelopes': cleaned_envelopes,
                'Registered': cleaned_registered,
                'Valid': cleaned_valid_votes,
                'party_details': party_details
            })
    write_data_into_csv(scraped_data, output_filename)


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
