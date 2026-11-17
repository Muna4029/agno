from __future__ import annotations

import json
from os import getenv
from typing import Any

from agno.tools import Toolkit
from agno.utils.log import logger

try:
    from firecrawl import FirecrawlApp  # type: ignore[attr-defined]

    try:
        from firecrawl import ScrapeOptions  # type: ignore[attr-defined]
    except ImportError:
        # For newer versions of firecrawl-py, ScrapeOptions has been renamed to V1ScrapeOptions
        from firecrawl import V1ScrapeOptions as ScrapeOptions  # type: ignore[attr-defined]
except ImportError:
    raise ImportError("`firecrawl-py` not installed. Please install using `pip install firecrawl-py`")


class CustomJSONEncoder(json.JSONEncoder):
    """Custom JSON encoder that handles non-serializable types by converting them to strings."""

    def default(self, obj):
        try:
            return super().default(obj)
        except TypeError:
            return str(obj)


class FirecrawlTools(Toolkit):
    """
    Firecrawl is a tool for scraping and crawling websites.
    Args:
        api_key (Optional[str]): The API key to use for the Firecrawl app.
        formats (Optional[List[str]]): The formats to use for the Firecrawl app.
        limit (int): The maximum number of pages to crawl.
        scrape (bool): Whether to scrape the website.
        crawl (bool): Whether to crawl the website.
        mapping (bool): Whether to map the website.
        api_url (Optional[str]): The API URL to use for the Firecrawl app.
    """

    def __init__(
        self,
        api_key: str | None = None,
        formats: list[str] | None = None,
        limit: int = 10,
        poll_interval: int = 30,
        scrape: bool = True,
        crawl: bool = False,
        mapping: bool = False,
        search: bool = False,
        search_params: dict[str, Any] | None = None,
        api_url: str | None = "https://api.firecrawl.dev",
        **kwargs,
    ):
        self.api_key: str | None = api_key or getenv("FIRECRAWL_API_KEY")
        if not self.api_key:
            logger.error("FIRECRAWL_API_KEY not set. Please set the FIRECRAWL_API_KEY environment variable.")

        self.formats: list[str] | None = formats
        self.limit: int = limit
        self.poll_interval: int = poll_interval
        self.app: FirecrawlApp = FirecrawlApp(api_key=self.api_key, api_url=api_url)
        self.search_params = search_params

        # Start with scrape by default. But if crawl is set, then set scrape to False.
        if crawl:
            scrape = False
            mapping = False
        elif not scrape:
            crawl = True

        tools: list[Any] = []
        if scrape:
            tools.append(self.scrape_website)
        if crawl:
            tools.append(self.crawl_website)
        if mapping:
            tools.append(self.map_website)
        if search:
            tools.append(self.search)

        super().__init__(name="firecrawl_tools", tools=tools, **kwargs)

    def _call_firecrawl_method(self, old_method_name: str, new_method_name: str, *args: Any, **kwargs: Any) -> Any:
        method = getattr(self.app, old_method_name, None)
        if method is None:
            method = getattr(self.app, new_method_name)
        return method(*args, **kwargs)

    def _dump_response(self, response: Any) -> str:
        if hasattr(response, "model_dump"):
            response = response.model_dump()
        return json.dumps(response, cls=CustomJSONEncoder)

    def scrape_website(self, url: str) -> str:
        """Use this function to scrape a website using Firecrawl.

        Args:
            url (str): The URL to scrape.
        """
        params = {}
        if self.formats:
            params["formats"] = self.formats

        scrape_result = self._call_firecrawl_method("scrape_url", "scrape", url, **params)
        return self._dump_response(scrape_result)

    def crawl_website(self, url: str, limit: int | None = None) -> str:
        """Use this function to Crawls a website using Firecrawl.

        Args:
            url (str): The URL to crawl.
            limit (int): The maximum number of pages to crawl

        Returns:
            The results of the crawling.
        """
        params: dict[str, Any] = {}
        if self.limit or limit:
            params["limit"] = self.limit or limit
        if self.formats:
            params["scrape_options"] = ScrapeOptions(formats=self.formats)  # type: ignore

        params["poll_interval"] = self.poll_interval

        crawl_result = self._call_firecrawl_method("crawl_url", "crawl", url, **params)
        return self._dump_response(crawl_result)

    def map_website(self, url: str) -> str:
        """Use this function to Map a website using Firecrawl.

        Args:
            url (str): The URL to map.

        """
        map_result = self._call_firecrawl_method("map_url", "map", url)
        return self._dump_response(map_result)

    def search(self, query: str, limit: int | None = None):
        """Use this function to search for the web using Firecrawl.

        Args:
            query (str): The query to search for.
            limit (int): The maximum number of results to return.
        """
        params: dict[str, Any] = {}
        if self.limit or limit:
            params["limit"] = self.limit or limit
        if self.formats:
            params["scrape_options"] = ScrapeOptions(formats=self.formats)  # type: ignore
        if self.search_params:
            params.update(self.search_params)

        search_result = self.app.search(query, **params)
        if search_result.success:
            return json.dumps(search_result.data, cls=CustomJSONEncoder)
        else:
            return "Error searching with the Firecrawl tool: " + search_result.error
