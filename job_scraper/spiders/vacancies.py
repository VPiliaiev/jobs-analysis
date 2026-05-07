import scrapy
from scrapy.http import Response
from typing import Generator, Dict, Any

from config import START_URL


class VacanciesSpider(scrapy.Spider):
    name = "vacancies"
    allowed_domains = ["work.ua"]
    start_urls = [START_URL]

    def parse(self, response: Response) -> Generator:
        job_cards = response.css("div.card-hover") or response.css("div.card")
        for job in job_cards:
            link = job.css("h2 a::attr(href)").get()
            if link:
                yield response.follow(link, callback=self.parse_job)
        next_page = response.css("ul.pagination li.active + li a::attr(href)").get()
        if next_page:
            yield response.follow(next_page, callback=self.parse)

    def parse_job(
            self,
            response: Response
    ) -> Generator[Dict[str, Any], None, None]:
        title = response.css("h1::text").get()
        description = " ".join(
            response.css("div#job-description *::text").getall()
        ).strip()
        company = response.css("div.company-info a::text").get()
        yield {
            "title": title,
            "company": company,
            "description": description,
            "url": response.url,
        }
