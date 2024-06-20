# Projekt 3 - Engeto Online Python Akademie

## Overview

`projekt_3.py` is a Python script designed to scrape election data from a specified URL and save the extracted data 
into a CSV file. This script is intended for educational purposes, specifically as a project for the Engeto Online 
Python Academy. The script uses web scraping techniques to gather data from a main URL and subsequent URLs, then 
processes and writes the data into a structured CSV file.

## Author

- **Name:** Anetta Martináková
- **Email:** martinakova.anetta@gmail.com
- **Discord:** Anetta M.#5044 (or originally known as zrzavahlava#5044)

## Requirements

The script requires the following Python libraries:

- `requests`
- `csv`
- `click`
- `validators`
- `sys`
- `structlog`
- `beautifulsoup4`

Ensure you have these libraries installed before running the script. You can install them using `pip`:

```commandline
pip install requests click validators structlog beautifulsoup4
```

## Usage

To run the script, use the following command:

```commandline
python projekt_3.py <main_url> <output_filename>
```
- <main_url>: The URL to start scraping from
- <output_filename>: The name of the CSV file to save scraped results

### Example
```commandline
python project3.py 'https://volby.cz/pls/ps2017nss/ps32?xjazyk=CZ&xkraj=12&xnumnuts=7103' 'elections_results.csv'
```

## Functions

### scrape_main_url(main_url: str) -> Dict[str, Any]
Scrape the main URL to extract city codes, city names, and the list of URLs for further scraping.

- Args:

 - main_url (str): The main URL to scrape.

- Returns:

 - Dict[str, Any]: A dictionary containing city codes, city names, and a list of URLs for further scraping.

### fetch_page(url: str) -> requests.Response
Fetch a page and return the response object.

- Args:

 - url (str): The URL of the page to fetch.

- Returns:

 - requests.Response: The response object containing the fetched page.

- Raises:

 - requests.exceptions.HTTPError: If an HTTP error occurs.
 - Exception: For other exceptions during the fetch process.

### extract_href_values(soup: BeautifulSoup) -> List[str]
Extract href values from the main URL's soup object.

- Args:

 - soup (BeautifulSoup): The BeautifulSoup object of the main URL.

- Returns:

 - List[str]: A list of href values extracted from the soup object.

### scrape_data(codes: ResultSet, locations: ResultSet, urls: List[str]) -> Dict[str, Any]
Scrape data from the list of URLs.

- Args:

 - codes (ResultSet): The ResultSet containing city codes.
 - locations (ResultSet): The ResultSet containing city names.
 - urls (List[str]): The list of URLs to scrape further.

- Returns:

 - Dict[str, Any]: A dictionary containing combined data and fieldnames.

### scraped_data_cleanup(cities_locations_data: List[Dict[str, Any]], votes_data: List[Dict[str, Any]]) -> Dict[str, Any]
Clean up the scraped data and combine city and vote data.

- Args:

 - cities_locations_data (List[Dict[str, Any]]: The list containing city codes and names.
 - votes_data (List[Dict[str, Any]]: The list containing vote data.
 - 
- Returns:

 - Dict[str, Any]: A dictionary containing combined data and fieldnames.

### write_data_into_csv(combined_data: List[Dict[str, Any]], fieldnames: List[str], filename: str) -> None
Write scraped data into a CSV file.

- Args:
 - combined_data (List[Dict[str, Any]]: The combined data to write into the CSV file.
 - fieldnames (List[str]): The fieldnames for the CSV file.
 - filename (str): The name of the CSV file.

### clean_data(text: str) -> str
Clean data by replacing non-breaking space characters with regular spaces.

- Args:

 - text (str): The text to clean.

- Returns:

 - str: The cleaned text.

### main(main_url, output_filename)
Main function to run the script with command-line arguments.

- Args:
 - main_url (str): The main URL to scrape.
 - output_filename (str): The name of the output CSV file.

## Logging
The script uses structlog for logging various stages of the execution. Logs are output to the standard output in JSON 
format with timestamps, which can be useful for debugging and tracking the script's progress.

## Error Handling
The script includes basic error handling to manage exceptions that may occur during the execution, such as HTTP errors 
or invalid inputs. If an error occurs, the script will log the error and exit gracefully.