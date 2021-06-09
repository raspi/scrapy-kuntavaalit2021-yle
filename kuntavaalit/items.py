from dataclasses import dataclass


@dataclass
class Item:
    url: str
    data: dict


@dataclass
class Municipality(Item):
    pass


@dataclass
class ItemWithMunicipality(Item):
    municipality: int


@dataclass
class Party(ItemWithMunicipality):
    pass


@dataclass
class Question(ItemWithMunicipality):
    pass


@dataclass
class Answer(ItemWithMunicipality):
    candidateid: int
