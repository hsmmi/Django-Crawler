import asyncio
import scrapy
from apps.crawler_app.models import Product, Category
from config.settings import logger
from asgiref.sync import sync_to_async
from dataclasses import dataclass


@dataclass
class ProductItem:
    site_id: str = None
    title: str = None
    url: str = None
    images: list[str] = None
    original_price: int = None
    discount_price: int = None
    availability: bool = None
    description: str = None
    specifications: dict = None
    category: Category = None


class ProductSpider(scrapy.Spider):
    name = "products"
    allowed_domains = ["esmerdis.com"]
    start_urls = ["https://www.esmerdis.com/shop/page/1"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.products_to_process: list[ProductItem] = []

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        """Creates a spider instance and connects the `spider_closed` signal."""
        spider = super(ProductSpider, cls).from_crawler(crawler, *args, **kwargs)
        crawler.signals.connect(
            spider.spider_closed, signal=scrapy.signals.spider_closed
        )
        return spider

    def parse(self, response):
        try:
            logger.info(f"🔍 Parsing page: {response.url}")
            for product in response.css("div.wd-product"):
                try:
                    product_info = ProductItem()
                    product_info = self.product_info_in_menu(product, product_info)

                    yield scrapy.Request(
                        url=response.urljoin(product_info.url),
                        callback=self.product_info_in_product_page,
                        cb_kwargs={"product_info": product_info},
                    )

                except Exception as e:
                    logger.error(
                        f"❌ Error processing product on {response.url}: {e}",
                        exc_info=True,
                    )

            # Handle pagination
            next_page = response.css("link[rel=next]::attr(href)").get()
            logger.info(f"🔍 Next page: {next_page}")
            if next_page:
                yield response.follow(next_page, callback=self.parse)
            else:
                logger.info("🛑 No more pages to parse!")

        except Exception as e:
            logger.critical(f"🔥 Fatal error in parsing {response.url}: {e}")
            return

    def product_info_in_menu(
        self, response: scrapy.http.Response, product_info: ProductItem = None
    ) -> ProductItem:
        """
        Extracts product information from the product menu.

        Returns
        -------
        product_info : ProductItem
            The site ID, title, URL, and images of the product.
        """
        if not product_info:
            product_info = ProductItem()
        # Extract product ID
        site_id = response.attrib.get("data-id", "N/A")
        # Extract product name
        title = response.css("h3.wd-entities-title a::text").get()
        # Extract product link
        product_url = response.css("h3.wd-entities-title a::attr(href)").get()
        # Extract product images
        images = response.css(".wd-product-grid-slide::attr(data-image-url)").getall()
        product_info.site_id = site_id
        product_info.title = title
        product_info.url = product_url
        product_info.images = images
        return product_info

    def get_price(
        self, response: scrapy.http.Response, product_info: ProductItem = None
    ) -> ProductItem:
        """
        Extracts price information from the product page.

        Returns
        -------
        product_info : ProductItem
            The original price, discount price, and availability of the product.
        """
        if not product_info:
            product_info = ProductItem()
        # Extract prices
        original_price = response.css(
            ".price del .woocommerce-Price-amount bdi::text"
        ).get()
        discount_price = response.css(
            ".price ins .woocommerce-Price-amount bdi::text"
        ).get()
        if not original_price:
            logger.warning("No original price found")
            original_price = 0
        if not discount_price:
            logger.warning("No discount price found")
            discount_price = original_price
        original_price = self.convert_persian_number(original_price)
        discount_price = self.convert_persian_number(discount_price)

        # Extract availability
        if response.css('meta[name="twitter:data2"]::attr(content)').get() == "موجود":
            availability = True
        else:
            availability = False

        product_info.original_price = original_price
        product_info.discount_price = discount_price
        product_info.availability = availability
        return product_info

    async def product_info_in_product_page(
        self, response: scrapy.http.Response, product_info: ProductItem = None
    ) -> ProductItem:
        """ """
        if not product_info:
            product_info = ProductItem()
        # Extract product price
        product_info = self.get_price(response, product_info)
        # Extract product information
        product_info = await self.get_info(response, product_info)

        self.products_to_process.append(product_info)

    def spider_closed(self, spider):
        """Runs `process_products` after crawling is complete."""
        logger.info("✅ Crawling finished - Running process_products()")
        asyncio.create_task(self.process_products())

    async def process_products(self):
        """Processes products in bulk: fetches existing, updates, and inserts new products."""
        try:
            logger.info("🔄 Processing products in bulk...")
            existing_products = await sync_to_async(
                lambda: {
                    p.site_id: p
                    for p in Product.objects.filter(
                        site_id__in=[p.site_id for p in self.products_to_process]
                    )
                }
            )()

            products_to_insert = []
            products_to_update = []

            for product_data in self.products_to_process:
                product_data = product_data.__dict__
                if product_data["site_id"] in existing_products:
                    existing_product = existing_products[product_data["site_id"]]
                    for key, value in product_data.items():
                        setattr(existing_product, key, value)
                    products_to_update.append(existing_product)
                else:
                    products_to_insert.append(Product(**product_data))

            if products_to_insert:
                await sync_to_async(Product.objects.bulk_create)(
                    products_to_insert, ignore_conflicts=True
                )

            if products_to_update:
                await sync_to_async(Product.objects.bulk_update)(
                    products_to_update, ["title", "url", "images"]
                )

            logger.info(
                f"✅ Processed {len(self.products_to_process)} products in bulk!"
                f"Inserted: {len(products_to_insert)} | Updated: {len(products_to_update)}"
            )

        except Exception as e:
            logger.error(f"🔥 Error in bulk processing: {e}", exc_info=True)

    async def get_or_create_category(self, full_category_path):
        """Creates categories recursively from a hierarchical string (e.g., decoration>bedroom>bed)."""
        if full_category_path.endswith("/"):
            full_category_path = full_category_path[:-1]
        category_names = full_category_path.replace("product-category/", "").split("/")
        parent = None
        current_category = []
        for category_name in category_names:
            current_category += [category_name]
            category, created = await sync_to_async(Category.objects.get_or_create)(
                name=">".join(current_category),
                slug=category_name.lower().replace(" ", "-"),
                parent=parent,
            )
            parent = category

        return category, created

    def convert_persian_number(self, num):
        """
        Converts Persian numbers to English numbers in floats.

        Parameters
        ----------
        num : str
            The Persian number to convert.

        Returns
        -------
        int
            The English number.
        """
        if not num:
            logger.warning("No number provided for conversion")
            return 0
        persian_numbers = "۰۱۲۳۴۵۶۷۸۹"
        english_numbers = "0123456789"
        num = str(num).strip().replace(",", "")
        return float(num.translate(str.maketrans(persian_numbers, english_numbers)))

    async def get_info(self, response, product_info: ProductItem = None) -> ProductItem:
        """
        Extracts product information from the product page.

        Parameters
        ----------
        response : scrapy.http.Response
            The response object containing the product page HTML.

        Returns
        -------
        """
        # Extract product description
        description = response.css(".c-mask.js-mask p span::text").getall()
        description_text = (
            "\n".join(description).strip()
            if description
            else "No description available"
        )
        # Extract product specifications (dimensions, material, etc.)
        specs = {}
        for spec_group in response.css(".dwspecs-product-table-group"):
            group_title = spec_group.css(".group-title::text").get()
            specs[group_title] = {}
            spec_items = spec_group.css("table tr")
            for item in spec_items:
                spec_key = item.css("td:nth-child(1)::text").get().strip()
                spec_value = item.css("td:nth-child(2)::text").get().strip()
                specs[group_title][spec_key] = spec_value
        # Extract product category from breadcrumbs
        category_links = response.css(".wd-breadcrumbs a::attr(href)").getall()[-1]
        product_category = category_links.replace("https://www.esmerdis.com/", "")

        category, _ = await self.get_or_create_category(product_category)

        product_info.description = description_text
        product_info.specifications = specs
        product_info.category = category

        return product_info
