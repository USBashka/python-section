import re
from datetime import date, datetime
from typing import Iterable
from urllib.parse import urljoin

from bs4 import BeautifulSoup

_LINK_PATTERN = re.compile(
    r"/upload/reports/oil_xls/oil_xls_(\d{8})[^/]*\.(?:xls|xlsx)$",
    re.IGNORECASE,
)

def _iter_candidate_hrefs(html: str) -> Iterable[str]:
    soup = BeautifulSoup(html, "html.parser")
    # TODO: Возможно, в будущем придётся ослабить селектор классов
    for a in soup.select("a.accordeon-inner__item-title.link.xls"):
        href = a.get("href")
        if not href:
            continue
        yield href.split("?", 1)[0]

def _extract_file_date(href: str) -> date | None:
    m = _LINK_PATTERN.search(href)
    if not m:
        return None
    ymd = m.group(1)
    try:
        return datetime.strptime(ymd, "%Y%m%d").date()
    except ValueError:
        return None

def parse_page_links(html: str, start_date: date, end_date: date, url: str, logger=None):
    """
    Парсит ссылки на бюллетени на странице и возвращает список (absolute_url, file_date)
    Фильтрует по диапазону дат [start_date, end_date]
    """
    if start_date > end_date:
        raise ValueError("start_date must not be after end_date")

    results: list[tuple[str, date]] = []
    seen: set[tuple[str, date]] = set()

    for href in _iter_candidate_hrefs(html):
        file_date = _extract_file_date(href)
        if file_date is None:
            msg = f"Не удалось извлечь дату из ссылки {href}"
            if logger: logger.warning(msg)
            else: print(msg)
            continue

        if not (start_date <= file_date <= end_date):
            msg = f"Ссылка {href} вне диапазона дат"
            if logger: logger.debug(msg)
            else: print(msg)
            continue

        absolute = urljoin(url, href)
        key = (absolute, file_date)
        if key in seen:
            continue
        seen.add(key)
        results.append(key)

    results.sort(key=lambda t: t[1])
    return results



def main():
    html = """
    <a class="accordeon-inner__item-title link xls" href="/upload/reports/oil_xls/oil_xls_20250101_test.xls?utm=1">link1</a>
    <a class="accordeon-inner__item-title link xls" href="/upload/reports/oil_xls/oil_xls_20250115.xlsx">link2</a>
    <a class="accordeon-inner__item-title link xls" href="/wrong/path/oil_xls_20250101.xls">bad</a>
    """
    out = parse_page_links(html, date(2025, 1, 1), date(2025, 1, 10), "https://spimex.com")
    print(out)

if __name__ == "__main__":
    main()
