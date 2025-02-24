import scrapy
from apps.crawler_app.models import Product, Category
from config.settings import logger
from asgiref.sync import sync_to_async


class ProductSpider(scrapy.Spider):
    name = "products"
    allowed_domains = ["esmerdis.com"]
    start_urls = ["https://www.esmerdis.com/shop/page/1"]

    def parse(self, response):
        try:
            for product in response.css("div.wd-product"):
                try:
                    # Extract product ID
                    site_id = product.attrib.get("data-id", "N/A")
                    # Extract product name
                    title = product.css("h3.wd-entities-title a::text").get()
                    # Extract product link
                    product_url = product.css(
                        "h3.wd-entities-title a::attr(href)"
                    ).get()
                    images = product.css(
                        ".wd-product-grid-slide::attr(data-image-url)"
                    ).getall()
                    if not all([title, product_url]):
                        logger.warning(
                            f"⚠️ Skipping product due to missing data: {response.url}",
                            f"Title: {title}",
                            f"Product URL: {product_url}",
                        )
                        continue

                    yield scrapy.Request(
                        url=response.urljoin(product_url),
                        callback=self.parse_product,
                        meta={
                            "site_id": site_id,
                            "title": title,
                            "url": response.urljoin(product_url),
                            "images": images,
                        },
                    )

                except Exception as e:
                    logger.error(f"❌ Error processing product on {response.url}: {e}")

            # Handle pagination
            next_page = response.css("link[rel=next]::attr(href)").get()
            logger.info(f"🔍 Next page: {next_page}")
            if next_page:
                yield response.follow(next_page, callback=self.parse)

        except Exception as e:
            logger.critical(f"🔥 Fatal error in parsing {response.url}: {e}")
            return

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

    def get_price(self, response) -> tuple[int, int, bool]:
        """
        Extracts price information from the product page.

        Parameters
        ----------
        response : scrapy.http.Response
            The response object containing the product page HTML.

        Returns
        -------
        original_price : int
            The original price of the product.
        discount_price : int
            The discounted price of the product.
        availability : bool
            The availability status of the product.
        """
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

        return original_price, discount_price, availability

    def get_info(self, response):
        """
        Extracts product information from the product page.

        Parameters
        ----------
        response : scrapy.http.Response
            The response object containing the product page HTML.

        Returns
        -------
        description : str
            The product description.
        specs : dict
            The product specifications.
        category : str
            The product category.
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

        return description_text, specs, product_category

    async def parse_product(self, response):
        """Extracts full product details including description, images, specifications, and category."""
        try:
            # Extract prices
            original_price, discount_price, availability = self.get_price(response)
            # Extract product information
            description_text, specs, product_category = self.get_info(response)
            if product_category.endswith("/"):
                product_category = product_category[:-1]
            # Retrieve or create category
            category, _ = await sync_to_async(Category.objects.get_or_create)(
                slug=product_category.strip("/").split("/")[
                    -1
                ],  # Use the last part of the path as slug
                defaults={
                    "name": product_category.replace("product-category/", "").replace(
                        "/", ">"
                    )
                },
            )

            # Retrieve metadata from the previous request
            product_data = response.meta
            product_data.update(
                {
                    "original_price": original_price,
                    "discount_price": discount_price,
                    "availability": availability,
                    "description": description_text,
                    "specifications": specs,
                    "category": category,
                }
            )

            # Use sync_to_async to save the product data to the database
            await sync_to_async(Product.objects.update_or_create)(
                site_id=product_data["site_id"],
                defaults={
                    "title": product_data["title"],
                    "category": product_data["category"],
                    "original_price": product_data["original_price"],
                    "discount_price": product_data["discount_price"],
                    "availability": product_data["availability"],
                    "description": product_data["description"],
                    "specifications": product_data["specifications"],
                    "url": product_data["url"],
                    "images": product_data["images"],
                },
            )

            logger.info(
                f"✅ Scraped product: {product_data['title']} | Category: {product_category}"
            )

            yield product_data

        except Exception as e:
            logger.error(f"❌ Error processing product page {response.url}: {e}")
