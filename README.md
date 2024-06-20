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