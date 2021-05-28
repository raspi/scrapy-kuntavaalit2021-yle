import scrapy

from kuntavaalit.items import *


class SiteSpider(scrapy.Spider):
    allowed_domains = [
        'vaalikone.yle.fi',
    ]
    start_urls = [
        'http://vaalikone.yle.fi/kuntavaalit2021/api/public/constituencies',
    ]

    def parse(self, response: scrapy.http.Response):
        raise NotImplemented

    def load_questions(self, response: scrapy.http.TextResponse):
        yield Item(
            url=response.url,
            data=response.json(),
        )

    def load_candidates(self, response: scrapy.http.TextResponse):
        for i in response.json():
            yield scrapy.Request(
                response.urljoin(
                    f"/kuntavaalit2021/api/public/constituencies/{response.meta['_id']}/candidates/{i['id']}"
                ),
                callback=self.load_candidate_answers,
            )

    def load_parties(self, response: scrapy.http.TextResponse):
        yield Item(
            url=response.url,
            data=response.json(),
        )

    def load_candidate_answers(self, response: scrapy.http.TextResponse):
        yield Item(
            url=response.url,
            data=response.json(),
        )


class KuntaSpider(SiteSpider):
    """
    Fetch all from municipality X
    """

    name = 'kunta'
    id: str = ""

    def __init__(self, id: str = ""):
        if id == "":
            id = None

        if id is None:
            raise ValueError("no id")

        self.id = id

    def parse(self, response: scrapy.http.TextResponse):
        found: bool = False
        for i in response.json():
            if str(i['id']) == self.id:
                found = True
                break

        if not found:
            raise ValueError(f"id {self.id} not found")

        yield scrapy.Request(
            response.urljoin(f"/kuntavaalit2021/api/public/constituencies/{self.id}/parties"),
            callback=self.load_parties,
        )

        yield scrapy.Request(
            response.urljoin(f"/kuntavaalit2021/api/public/constituencies/{self.id}/questions"),
            callback=self.load_questions,
        )

        yield scrapy.Request(
            response.urljoin(f"/kuntavaalit2021/api/public/constituencies/{self.id}/candidates"),
            callback=self.load_candidates,
            meta={
                '_id': self.id,
            },
        )


class KVSpider(SiteSpider):
    """
    Fetch all
    """

    name = 'kaikki'

    def parse(self, response: scrapy.http.TextResponse):
        for i in response.json():
            yield scrapy.Request(
                response.urljoin(f"/kuntavaalit2021/api/public/constituencies/{i['id']}/questions"),
                callback=self.load_questions,
            )

            yield scrapy.Request(
                response.urljoin(f"/kuntavaalit2021/api/public/constituencies/{i['id']}/candidates"),
                callback=self.load_candidates,
                meta={
                    '_id': i['id'],
                },
            )

            yield scrapy.Request(
                response.urljoin(f"/kuntavaalit2021/api/public/constituencies/{i['id']}/parties"),
                callback=self.load_parties,
            )
