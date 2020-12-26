import datetime
import functools
import json
from typing import Any, Dict, Iterable, List, Union
from urllib import parse as urlparse

import dateutil.parser
import scrapy  # type: ignore
from scrapy.http.response import Response  # type: ignore

from build.lib.crib.scraper.spiders.rightmove import _load_page_model
from crib import injection
from crib.domain import Property
from crib.scraper import base
from crib.scraper.items import PropertyItem

PR = Iterable[Union[Dict, scrapy.Request]]


class RightmoveSpider(base.WithInjection, scrapy.Spider):
    name: str = "rightmove"
    property_repository = injection.Dependency()

    def start_requests(self) -> Iterable[scrapy.Request]:
        urls = self.settings.getlist("RIGHTMOVE_SEARCHES") or []
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response: Response) -> PR:
        model = _load_model(response)
        for page in _get_pages(response, model):
            yield scrapy.Request(page, callback=self.parse_page)

        yield from self.parse_propertymodel(response, model)

    def parse_page(self, response: Response) -> PR:
        model = _load_model(response)
        yield from self.parse_propertymodel(response, model)

    def parse_propertymodel(self, response: Response, model: Dict) -> PR:
        properties = model["properties"]
        for data in properties:
            _make_id(data)
            existing = self.property_repository.get(data["id"])
            if existing and existing.banned:
                continue
            callback = functools.partial(self.parse_property, data, existing)
            yield response.follow(data["propertyUrl"], callback=callback)

    def parse_property(self, data, existing, response: Response) -> PR:
        property = _load_page_model(response)["propertyData"]
        data["propertyImages"] = self._get_property_images(property)
        data["floorplanImages"] = self._get_floorplan_images(property)
        data["lettingInformation"] = self._get_letting_information(property)
        data["keyFeatures"] = self._get_key_features(property)
        data["summary"] = self._get_summary(property)
        prop = to_prop(data, existing)
        yield PropertyItem({"prop": prop, "existing": existing})

    def _get_key_features(self, property: Dict) -> List[str]:
        return property["keyFeatures"]

    def _get_letting_information(self, property: Dict) -> Dict[str, str]:
        return property["lettings"]

    def _get_summary(self, property: Dict) -> str:
        return property["text"]["description"]

    def _get_property_images(self, property: Dict) -> List[str]:
        return [img["url"] for img in property["images"]]

    def _get_floorplan_images(self, property: Dict) -> List[str]:
        return [img["url"] for img in property["floorplans"]]


def _load_model(response: Response) -> Dict:
    script = response.xpath("/html/body/script[2]/text()").extract_first()
    jsmodel = script[len("window.jsonModel = ") :]
    model = json.loads(jsmodel)
    return model

def _load_page_model(response: Response) -> Dict:
    script = response.xpath("/html/body/script[1]/text()").extract_first()
    jsmodel = script[len("\n    window.PAGE_MODEL = ") :]
    model = json.loads(jsmodel)
    return model

def _get_pages(response: Response, model: Dict) -> Iterable[str]:
    url = response.url
    pagination = model["pagination"]
    options = pagination["options"]

    qr = urlparse.urlparse(url)
    parsed = list(qr)
    qs = urlparse.parse_qs(qr.query)

    # ignore first page. We only parse pages once, by loading the first page.
    for option in options[1:]:
        newqs = qs.copy()
        newqs["index"] = option["value"]
        newquery = urlparse.urlencode(newqs, doseq=True)
        parsed[4] = newquery
        yield urlparse.urlunparse(parsed)


def _make_id(propmodel: Dict):
    propmodel["id"] = f"RM-{propmodel['id']}"


def to_prop(data, existing=None):
    keys = (
        "bedrooms",
        "displayAddress",
        "featuredProperty",
        "feesApply",
        "feesApplyText",
        "firstVisibleDate",
        "floorplanImages",
        "id",
        "keyFeatures",
        "lettingInformation",
        "location",
        "price",
        "propertyImages",
        "propertySubType",
        "propertyTypeFullDescription",
        "propertyUrl",
        "students",
        "summary",
        "transactionType",
    )

    def identity(x):
        return x

    conversions = {
        "firstVisibleDate": _to_dt,
        "price": _to_price,
        "propertyUrl": lambda x: "https://www.rightmove.co.uk" + x,
        "feesApplyText": lambda x: x or "",
    }

    d = {k: conversions.get(k, identity)(data[k]) for k in keys}
    if existing:
        d["favorite"] = existing.favorite
        if existing.toWork:
            d["toWork"] = existing.toWork.asdict()

    return Property.fromdict(d)


def _to_dt(string: str) -> datetime.datetime:
    return dateutil.parser.parse(string)


def _to_price(data: Dict) -> Dict[str, Any]:
    price = {k: data[k] for k in ("amount", "currencyCode", "frequency")}
    if price["frequency"] == "weekly":
        price["amount"] = int(price["amount"] * 52 / 12)
        price["frequency"] = "monthly"
    return price
