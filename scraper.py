from simple_bucket import SimpleBucket
import yaml
from ocf_scraper import OCFScraper


class Scraper:
    def __init__(self, config_file):
        config_file = open(config_file, 'r')
        config = yaml.safe_load(config_file)
        config_file.close()

        self.bucket = SimpleBucket(config['aws']['s3']['aws_key_id'],
                                   config['aws']['s3']['aws_secret_key'],
                                   config['aws']['s3']['bucket_name'])

    def scrape_ocf_csv_by_years(self, years):
        ocf_scraper = OCFScraper()

        for year in years:
            start_date = '01/01/' + str(year)
            end_date = '12/31/' + str(year)

            print("Fetching ocf information for year: ", str(year))
            try:
                contributions_expenditures = ocf_scraper.scrape_all(start_date, end_date)
            except TypeError:
                print("Unable to process year: ", str(year))
                continue

            print("Saving ocf-contributions and ocf expenditures to S3 now...")
            self.bucket.save(["csv", "ocf-contributions-" + str(year) + ".csv"],
                             contributions_expenditures["contributions"].csv)
            self.bucket.save(["csv", "ocf-expenditures-" + str(year) + ".csv"],
                             contributions_expenditures["expenditures"].csv)