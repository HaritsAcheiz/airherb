import asyncio
import aiohttp
from selectolax.parser import HTMLParser
from dataclasses import dataclass, field
from typing import List
from random import choice

@dataclass
class AirHerb:
    useragent: str = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'

    # useragent: List[str] = field(default_factory=lambda: [
    #     'Mozilla/5.0 (Wayland; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.137 Safari/537.36 Ubuntu/22.04 (5.0.2497.35-1) Vivaldi/5.0.2497.35',
    #     'Mozilla/5.0 (Wayland; Linux x86_64; System76 Galago Pro (galp2)) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.175 Safari/537.36 Ubuntu/22.04 (5.0.2497.48-1) Vivaldi/5.0.2497.48',
    #     'Mozilla/5.0 (Wayland; Linux x86_64; System76 Galago Pro (galp2)) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.175 Safari/537.36 Ubuntu/22.04 (5.0.2497.51-1) Vivaldi/5.0.2497.51,',
    #     'Mozilla/5.0 (Wayland; Linux x86_64; System76) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.133 Safari/537.36 Ubuntu/22.04 (5.2.2623.34-1) Vivaldi/5.2.2623.39',
    #     'Mozilla/5.0 (Wayland; Linux x86_64; System76) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.92 Safari/537.36 Ubuntu/22.04 (5.2.2623.34-1) Vivaldi/5.2.2623.34'
    # ])

    # proxies: List[str] = field(default_factory=lambda: ['154.12.112.208:8800', '192.126.194.95:8800', '154.38.156.187:8800',
    #                                                     '192.126.196.137:8800', '154.12.112.163:8800', '192.126.194.135:8800',
    #                                                     '192.126.196.93:8800', '154.38.156.14:8800', '154.12.113.202:8800',
    #                                                     '154.38.156.188:8800'])


    async def fetch(self, client, url, proxies, headers):
        async with client.get(url, proxy=proxies, headers=headers) as r:
            if r.status != 200:
                r.raise_for_status()
            return await r.text()


    async def extract(self):
        urls = []
        for page in range(1, 3):
            url = f'https://www.iherb.com/specials?sr=3&p={page}'
            urls.append(url)

        async with aiohttp.ClientSession() as client:
            tasks = []

            for url in urls:
                # proxy = choice(self.proxies)
                # proxies = f"http://{proxy}"

                ua = choice(self.useragent)

                headers = {
                    'user-agent': self.useragent
                }

                task = asyncio.create_task(self.fetch(
                    client=client,
                    url=url,
                    # proxies=proxies,
                    headers=headers))

                tasks.append(task)

            results = await asyncio.gather(*tasks)

        return results


    def get_detail_links(self, htmls):
        results = []
        for html in htmls:
            tree = HTMLParser(html)
            product_list = tree.css('div.products.product-cells.clearfix > div')
            products = []
            for product in product_list:
                product_temp = {'product_id': '', 'price': '', 'out_of_stock': 'True', 'link': ''}
                product_temp['product_id'] = product.css_first('a.absolute-link.product-link').attributes.get('data-product-id', '')
                product_temp['price'] = product.css_first('a.absolute-link.product-link').attributes.get('data-ga-discount-price', '')
                product_temp['out_of_stock'] = product.css_first('a.absolute-link.product-link').attributes.get('data-ga-is-out-of-stock', 'True')
                product_temp['link'] = product.css_first('a.absolute-link.product-link').attributes.get('href', '')
                products.append(product_temp)

            results.extend(products)

        return results


    def run(self):
        htmls = asyncio.run(self.extract())
        detail_links = self.get_detail_links(htmls)
        print(detail_links)

if __name__ == '__main__':
    scraper = AirHerb()
    scraper.run()