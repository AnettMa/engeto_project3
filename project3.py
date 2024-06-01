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
    fieldnames = ['Code', 'Location', 'Envelopes', 'Registered', 'Valid']
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(scraped_data)


def clean_data(text):
    """Clean data by replacing non-breaking space characters with regular spaces."""
    return text.replace('\xa0', ' ')


def scrape_main_url(main_url, output_filename):
    """Scrape districts code and name of the city."""
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
    scrape_districts_data(codes, locations, output_filename)


def scrape_districts_data(codes, locations, output_filename):
    """Scrape elections result from each district."""
    scraped_data = []
    for code, location in zip(codes, locations):
        code_text = code.text.strip()
        location_text = location.text.strip()
        districts_url = f'https://volby.cz/pls/ps2017nss/ps311?xjazyk=CZ&xkraj=12&xobec={code_text}&xvyber=7103'
        try:
            response_from_districts_url = requests.get(districts_url)
            response_from_districts_url.raise_for_status()
            logger.info('Page retrieved.', url=districts_url, status_code=response_from_districts_url.status_code)
        except requests.exceptions.HTTPError as e:
            logger.error(f'HTTP error occurred for code {code_text}:', url=districts_url, error=str(e))
            raise e
        except Exception as e:
            logger.error(f'Other error occurred for code {code_text}: {e}', url=districts_url, error=str(e))
            continue
        districts_url_soup = BeautifulSoup(response_from_districts_url.text, 'html.parser')
        try:
            envelopes = districts_url_soup.find('td', class_='cislo', headers='sa3').text
            registered = districts_url_soup.find('td', class_='cislo', headers='sa2').text
            valid = districts_url_soup.find('td', class_='cislo', headers='sa6').text

            # Cleaning the extracted values from NBSC
            cleaned_envelopes = clean_data(envelopes)
            cleaned_registered = clean_data(registered)
            cleaned_valid = clean_data(valid)
            scraped_data.append({'Code': code_text, 'Location': location_text, 'Envelopes': cleaned_envelopes,
                                 'Registered': cleaned_registered, 'Valid': cleaned_valid})
        except AttributeError as e:
            logger.error(f'Failed to fetch data for code {code_text}: {e}')
            continue

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
