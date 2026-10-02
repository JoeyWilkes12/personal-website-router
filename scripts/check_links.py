#!/usr/bin/env python3
"""Check generated Pages content and every navigational destination."""

import argparse
import hashlib
import json
from html.parser import HTMLParser
from pathlib import Path
import re
from urllib.parse import urljoin
from urllib.request import HTTPRedirectHandler, Request, build_opener
import xml.etree.ElementTree as ET


ROOT = Path(__file__).resolve().parents[1]
PUBLIC_URL = "https://joeywilkes12.github.io/personal-website-router/"
REPOSITORY_URL = "https://github.com/JoeyWilkes12/personal-website-router"


class Redirects(HTTPRedirectHandler):
    def redirect_request(self, request, response, code, message, headers, url):
        print(f"  HTTP {code}: {request.full_url} -> {url}")
        return super().redirect_request(request, response, code, message, headers, url)


class PageLinks(HTMLParser):
    def __init__(self):
        super().__init__()
        self.destinations = []
        self.refresh = None

    def handle_starttag(self, tag, attributes):
        attrs = dict(attributes)
        if tag == "a" or (tag == "link" and attrs.get("rel") == "canonical"):
            self.destinations.append(attrs["href"])
        if tag == "meta" and attrs.get("http-equiv", "").lower() == "refresh":
            self.refresh = attrs.get("content")


def require(condition, message):
    if not condition:
        raise ValueError(message)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--site-url", default=PUBLIC_URL)
    args = parser.parse_args()
    base = args.site_url.rstrip("/") + "/"
    source = (ROOT / "index.html").read_text()
    setting = re.search(r'^redirect_url:\s*("[^\n]+")\s*$', source, re.M)
    require(setting is not None, "Missing redirect_url setting in index.html")
    target = json.loads(setting.group(1))
    require(target.startswith("https://"), "Use an absolute HTTPS destination")
    opener = build_opener(Redirects())
    cache = {}

    def fetch(url):
        if url not in cache:
            request = Request(url, headers={"User-Agent": "PersonalWebsiteRouterLinkCheck/1.0"})
            with opener.open(request, timeout=30) as response:
                require(200 <= response.status < 300, f"HTTP {response.status}: {url}")
                cache[url] = response.read()
                print(f"PASS HTTP {response.status}: {url}")
        return cache[url]

    html = fetch(base).decode("utf-8")
    require("{{" not in html and "{%" not in html, "Unrendered Liquid template")
    require("<h1>Joey Wilkes</h1>" in html, "Missing expected page content")
    links = PageLinks()
    links.feed(html)
    require(links.destinations == [target, target], "Canonical and fallback URLs differ")
    require(links.refresh == f"0; url={target}", "HTML refresh URL differs")
    javascript = re.search(r'window\.location\.replace\((".*?")\);', html)
    require(javascript is not None, "Missing JavaScript redirect")
    require(json.loads(javascript.group(1)) == target, "JavaScript URL differs")
    metadata = re.search(r'<script type="application/ld\+json">(.*?)</script>', html, re.S)
    require(metadata is not None, "Missing structured metadata")
    require(json.loads(metadata.group(1))["url"] == target, "Metadata URL differs")
    for url in set(links.destinations + [REPOSITORY_URL]):
        fetch(url)

    robots = fetch(urljoin(base, "robots.txt")).decode("utf-8")
    require("User-agent: *\nAllow: /" in robots, "Robots file must allow public content")
    require(f"Sitemap: {PUBLIC_URL}sitemap.xml" in robots, "Incorrect sitemap reference")
    sitemap = ET.fromstring(fetch(urljoin(base, "sitemap.xml")))
    locations = [node.text for node in sitemap.findall(".//{*}loc")]
    require(locations == [PUBLIC_URL], "Unexpected sitemap destinations")
    # A local preview checks its equivalent route; a public check follows every sitemap URL.
    for url in locations:
        fetch(base if base != PUBLIC_URL and url == PUBLIC_URL else url)

    png = fetch(urljoin(base, "personal-website-router-qr.png"))
    local_png = (ROOT / "personal-website-router-qr.png").read_bytes()
    require(png.startswith(b"\x89PNG\r\n\x1a\n"), "QR response is not a PNG")
    require(hashlib.sha256(png).digest() == hashlib.sha256(local_png).digest(), "QR bytes differ")
    print("PASS all redirect, hyperlink, metadata, sitemap, robots, and PNG checks")


if __name__ == "__main__":
    try:
        main()
    except Exception as error:
        raise SystemExit(f"FAIL: {error}") from error
