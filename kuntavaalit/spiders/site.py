from urllib.parse import urlsplit, SplitResult

import scrapy

from kuntavaalit.items import *


class SiteSpider(scrapy.Spider):
    """
    Base spider (not called directly)
    """

    allowed_domains = [
        'vaalikone.yle.fi',
    ]
    start_urls = [
        'http://vaalikone.yle.fi/kuntavaalit2021/api/public/constituencies',
    ]

    def parse(self, response: scrapy.http.Response):
        raise NotImplemented

    def load_questions(self, response: scrapy.http.TextResponse):
        url: SplitResult = urlsplit(response.url)
        p = url.path.strip('/').split('/')
        municipality = int(p[4])

        yield Question(
            url=response.url,
            data=response.json(),
            municipality=municipality,
        )

    def load_candidates(self, response: scrapy.http.TextResponse):
        url: SplitResult = urlsplit(response.url)
        p = url.path.strip('/').split('/')
        municipality = p[4]

        for i in response.json():
            yield scrapy.Request(
                response.urljoin(
                    f"/kuntavaalit2021/api/public/constituencies/{municipality}/candidates/{i['id']}"
                ),
                callback=self.load_candidate_answers,
            )

    def load_parties(self, response: scrapy.http.TextResponse):
        url: SplitResult = urlsplit(response.url)
        p = url.path.strip('/').split('/')
        municipality = int(p[4])

        yield Party(
            url=response.url,
            data=response.json(),
            municipality=municipality,
        )

    def load_candidate_answers(self, response: scrapy.http.TextResponse):
        data = response.json()

        url: SplitResult = urlsplit(response.url)
        p = url.path.strip('/').split('/')
        municipality = int(p[4])

        yield Answer(
            url=response.url,
            data=data,
            municipality=municipality,
            candidateid=data['election_number'],
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

        yield Municipality(
            url=response.url,
            data=response.json(),
        )

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
        data = response.json()

        yield Municipality(
            url=response.url,
            data=data,
        )

        for i in data:
            yield scrapy.Request(
                response.urljoin(f"/kuntavaalit2021/api/public/constituencies/{i['id']}/questions"),
                callback=self.load_questions,
            )

            yield scrapy.Request(
                response.urljoin(f"/kuntavaalit2021/api/public/constituencies/{i['id']}/candidates"),
                callback=self.load_candidates,
            )

            yield scrapy.Request(
                response.urljoin(f"/kuntavaalit2021/api/public/constituencies/{i['id']}/parties"),
                callback=self.load_parties,
            )
