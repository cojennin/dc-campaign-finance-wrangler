# This file downloads data from the DC Office of Campaign Finance
# and generates various data tables suitable for graphing.
# It uses @sshanabrook's awesome dc_campaign_finance_data package.

from dc_campaign_finance_scraper import scraper

'''
DOWNLOAD CONTRIBUTIONS AND EXPENDITURES DATA.
Even though we only have offices data from 2000 on,
we download contribution and expenditure data from 1999 on for storage and review.
We could eventually enter in the offices data for 1999-2009.
'''


class OCFScraper:
    def scrape_expenditures(self, start_date, end_date):
        return scraper.records_with_office_and_election_year(from_date=start_date, to_date=end_date, report_type='exp')

    def scrape_contributions(self, start_date, end_date):
        return scraper.records_with_office_and_election_year(from_date=start_date, to_date=end_date, report_type='con')

    def scrape_all(self, start_date, end_date):
        return {
            'expenditures' : self.scrape_expenditures(start_date, end_date),
            'contributions' : self.scrape_contributions(start_date, end_date)
        }