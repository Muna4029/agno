import json
from os import getenv
from typing import Any, Dict, List, Optional

from agno.tools import Toolkit
from agno.utils.log import logger

try:
    from firecrawl import FirecrawlApp  # type: ignore[attr-defined]
    try:
        # older versions
        from firecrawl import ScrapeOptions  # type: ignore[attr-defined]
    except ImportError:
        # newer versions
        from firecrawl import V1ScrapeOptions as ScrapeOptions  # type: ignore[attr-defined]
except ImportError as e:
    raise ImportError(
        "`firecrawl-py` is required. Install with `pip install firecrawl-py` "
        "and ensure the installed version matches the SDK API."
    ) from e


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
        api_key: Optional[str] = None,
        formats: Optional[List[str]] = None,
        limit: int = 10,
        poll_interval: int = 30,
        scrape: bool = True,
        crawl: bool = False,
        mapping: bool = False,
        search: bool = False,
        search_params: Optional[Dict[str, Any]] = None,
        api_url: Optional[str] = "https://api.firecrawl.dev",
        **kwargs,
    ):
        self.api_key: Optional[str] = api_key or getenv("FIRECRAWL_API_KEY")
        if not self.api_key:
            logger.error("FIRECRAWL_API_KEY not set. Please set the FIRECRAWL_API_KEY environment variable.")

        self.formats: Optional[List[str]] = formats
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

        tools: List[Any] = []
        if scrape:
            tools.append(self.scrape_website)
        if crawl:
            tools.append(self.crawl_website)
        if mapping:
            tools.append(self.map_website)
        if search:
            tools.append(self.search)

        super().__init__(name="firecrawl_tools", tools=tools, **kwargs)

    def scrape_website(self, url: str) -> str:
        """Use this function to scrape a website using Firecrawl.

        Args:
            url (str): The URL to scrape.
        """
        params: Dict[str, Any] = {}
        if self.formats:
            params["formats"] = self.formats

        scrape_result = self.app.scrape_url(url, **params)
        return json.dumps(scrape_result.model_dump(), cls=CustomJSONEncoder)

    def crawl_website(self, url: str, limit: Optional[int] = None) -> str:
        """Use this function to crawl a website using Firecrawl.

        Args:
            url (str): The URL to crawl.
            limit (Optional[int]): The maximum number of pages to crawl.

        Returns:
            str: JSON string containing the crawl results.
        """
        params: Dict[str, Any] = {}

        effective_limit = limit if limit is not None else self.limit
        if effective_limit is not None:
            params["limit"] = effective_limit

        if self.formats:
            params["scrape_options"] = ScrapeOptions(formats=self.formats)  # type: ignore

        params["poll_interval"] = self.poll_interval

        crawl_result = self.app.crawl_url(url, **params)
        return json.dumps(crawl_result.model_dump(), cls=CustomJSONEncoder)

    def map_website(self, url: str) -> str:
        """Use this function to map a website using Firecrawl.

        Args:
            url (str): The URL to map.
        """
        map_result = self.app.map_url(url)
        return json.dumps(map_result.model_dump(), cls=CustomJSONEncoder)

    def search(self, query: str, limit: Optional[int] = None) -> str:
        """Use this function to search the web using Firecrawl.

        Args:
            query (str): The query to search for.
            limit (Optional[int]): The maximum number of results to return.

        Returns:
            str: JSON string containing search results or an error message.
        """
        params: Dict[str, Any] = {}

        effective_limit = limit if limit is not None else self.limit
        if effective_limit is not None:
            params["limit"] = effective_limit

        if self.formats:
            params["scrape_options"] = ScrapeOptions(formats=self.formats)  # type: ignore
        if self.search_params:
            params.update(self.search_params)

        search_result = self.app.search(query, **params)
        if search_result.success:
            return json.dumps(search_result.data, cls=CustomJSONEncoder)
        return "Error searching with the Firecrawl tool: " + search_result.error
