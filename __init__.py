from scraper import Scraper

years = range(2006, 2014)
scraper = Scraper("config.yml")
scraper.scrape_ocf_csv_by_years(years)