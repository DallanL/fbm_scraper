import requests
from lxml import html

def pcpp_list_scraper(url):
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:58.0) Gecko/20100101 Firefox/58.0'}
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        raise Exception(f"Failed to fetch URL: {url} {response.status_code}")
    
    tree = html.fromstring(response.content)
    components_list = {}
    
    rows = tree.xpath('//*[@id="partlist"]/div[2]/section[2]/div/div[2]/table/tbody/tr[contains(@class, "tr__product")]')


    for row in rows:
        try:
            # Get the component type and name
            component_type = row.xpath('.//td[@class="td__component"]//a/text() | .//td[@class="td__component"]//p/text()')[0].strip()
            component_name = row.xpath('.//td[@class="td__name"]/a/text()')[0].strip()
            if component_type in components_list:
                components_list[component_type].append(component_name)
            else:
                components_list[component_type] = [component_name]
        except IndexError:
            continue

    return components_list
