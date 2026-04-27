import requests

try:
    from .html_parser import extract_start_list_pdf_urls, fetch_page
    from .pdf_parser import parse_start_list_pdf_from_url
except ImportError:
    from kulup_mobile.parsers.html_parser import extract_start_list_pdf_urls, fetch_page
    from kulup_mobile.parsers.pdf_parser import parse_start_list_pdf_from_url



def get_start_list_from_pdf_url(event_url: str) -> list[dict]:
    """
    Verilen bir start listesi PDF URL'sinden start listesi verilerini çıkarır.

    Örnek: get_start_list_from_pdf_url("https://canli.tyf.gov.tr/ankara/cs-1005292/")
    """
    soup = fetch_page(event_url)
    if soup is None:
        return []

    start_list_urls = extract_start_list_pdf_urls(soup, event_url)
    if not start_list_urls:
        print("Start listesi PDF URL'si bulunamadı.")
        return []

    start_list_total = []
    for url in start_list_urls:
        start_list = parse_start_list_pdf_from_url(url)
        if start_list:
            start_list_total.extend(start_list)

    return start_list_total


def send_parsed_start_list_to_api(
    event_url: str,
    api_url: str,
    token: str | None = None,
    replace_existing: bool = False,
    timeout: int = 30,
) -> dict:
    """
    Event URL'den start list verisini parse eder ve API'ye gönderir.

    API payload:
      {
        "parsed_entries": [...],
        "replace_existing": false
      }
    """
    parsed_entries = get_start_list_from_pdf_url(event_url)

    payload = {
        "parsed_entries": parsed_entries,
        "replace_existing": replace_existing,
        "event_url": event_url,
    }

    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"

    response = requests.post(api_url, json=payload, headers=headers, timeout=timeout)
    response.raise_for_status()
    return response.json()


if __name__ == "__main__":
    startlist = get_start_list_from_pdf_url("https://canli.tyf.gov.tr/ankara/cs-1005292")
    if not startlist:
        print("Start listesi verisi cikarilamadi.")


startlist=get_start_list_from_pdf_url("https://canli.tyf.gov.tr/ankara/cs-1005292")
if not startlist:
        print("Start listesi verisi çıkarılamadı.")
        