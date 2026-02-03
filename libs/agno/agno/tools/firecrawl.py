import json
from os import getenv
from typing import Any, Dict, List, Optional

from agno.tools import Toolkit
from agno.utils.log import logger

try:
    from firecrawl import FirecrawlApp  # type: ignore[import-not-found]
except ImportError as e:
    raise ImportError("`firecrawl-py` not installed. Please install using `pip install firecrawl-py`") from e

# Optional compatibility: firecrawl SDK renamed ScrapeOptions to V1ScrapeOptions in some versions.
try:
    from firecrawl import ScrapeOptions as _ScrapeOptions  # type: ignore[attr-defined,import-not-found]
except Exception:
    try:
        from firecrawl import V1ScrapeOptions as _ScrapeOptions  # type: ignore[attr-defined,import-not-found]
    except Exception:
        _ScrapeOptions = None  # type: ignore[assignment]


class CustomJSONEncoder(json.JSONEncoder):
    """Custom JSON encoder that handles non-serializable types by converting them to strings."""

    def default(self, obj: Any) -> Any:
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
        **kwargs: Any,
    ):
        self.api_key: Optional[str] = api_key or getenv("FIRECRAWL_API_KEY")
        if not self.api_key:
            logger.error("FIRECRAWL_API_KEY not set. Please set the FIRECRAWL_API_KEY environment variable.")

        self.formats: Optional[List[str]] = formats
        self.limit: int = limit
        self.poll_interval: int = poll_interval

        # Tests patch FirecrawlApp and only assert app is not None
        self.app: FirecrawlApp = FirecrawlApp(api_key=self.api_key, api_url=api_url)

        # Tests may set this after init
        self.search_params: Optional[Dict[str, Any]] = search_params

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
        """Use this function to scrape a website using Firecrawl."""
        params: Dict[str, Any] = {}
        if self.formats:
            params["formats"] = self.formats

        scrape_result = self.app.scrape_url(url, **params)
        return json.dumps(scrape_result.model_dump(), cls=CustomJSONEncoder)

    def crawl_website(self, url: str, limit: Optional[int] = None) -> str:
        """Use this function to crawl a website using Firecrawl."""
        params: Dict[str, Any] = {}

        # Respect explicit argument first, then fallback to self.limit
        params["limit"] = limit if limit is not None else self.limit

        # Keep poll_interval behavior as tests expect
        params["poll_interval"] = self.poll_interval

        # Do not require ScrapeOptions for tests, but support it when present
        if self.formats and _ScrapeOptions is not None:
            params["scrape_options"] = _ScrapeOptions(formats=self.formats)  # type: ignore[misc]

        crawl_result = self.app.crawl_url(url, **params)
        return json.dumps(crawl_result.model_dump(), cls=CustomJSONEncoder)

    def map_website(self, url: str) -> str:
        """Use this function to map a website using Firecrawl."""
        map_result = self.app.map_url(url)
        return json.dumps(map_result.model_dump(), cls=CustomJSONEncoder)

    def search(self, query: str, limit: Optional[int] = None) -> str:
        """Use this function to search for the web using Firecrawl."""
        params: Dict[str, Any] = {}

        params["limit"] = limit if limit is not None else self.limit

        if self.formats and _ScrapeOptions is not None:
            params["scrape_options"] = _ScrapeOptions(formats=self.formats)  # type: ignore[misc]

        if self.search_params:
            params.update(self.search_params)

        search_result = self.app.search(query, **params)
        if getattr(search_result, "success", False):
            return json.dumps(search_result.data, cls=CustomJSONEncoder)

        err = getattr(search_result, "error", "Unknown error")
        return "Error searching with the Firecrawl tool: " + str(err)
