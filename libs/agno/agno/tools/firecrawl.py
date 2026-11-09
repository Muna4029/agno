import json
from os import getenv
from typing import Any, Dict, List, Optional

from agno.tools import Toolkit
from agno.utils.log import logger

try:
    from firecrawl import FirecrawlApp  # type: ignore[attr-defined]
except ImportError:
    raise ImportError("`firecrawl-py` not installed. Please install using `pip install firecrawl-py`")

try:
    from firecrawl import ScrapeOptions as FirecrawlScrapeOptions  # type: ignore[attr-defined]
except ImportError:
    try:
        from firecrawl import V1ScrapeOptions as FirecrawlScrapeOptions  # type: ignore[attr-defined]
    except ImportError:
        FirecrawlScrapeOptions = None


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

    def _get_scrape_options(self) -> Any:
        if FirecrawlScrapeOptions is None:
            return {"formats": self.formats}
        return FirecrawlScrapeOptions(formats=self.formats)

    @staticmethod
    def _get_firecrawl_v1_client(app: Any) -> Optional[Any]:
        app_dict = getattr(app, "__dict__", None)
        if not isinstance(app_dict, dict):
            return None
        return app_dict.get("v1")

    def _scrape(self, url: str, params: Dict[str, Any]) -> Any:
        if hasattr(self.app, "scrape_url"):
            return self.app.scrape_url(url, **params)
        app = self._get_firecrawl_v1_client(self.app)
        if app is not None and hasattr(app, "scrape_url"):
            return app.scrape_url(url, **params)
        return self.app.scrape(url, **params)

    def _crawl(self, url: str, params: Dict[str, Any]) -> Any:
        if hasattr(self.app, "crawl_url"):
            return self.app.crawl_url(url, **params)
        app = self._get_firecrawl_v1_client(self.app)
        if app is not None and hasattr(app, "crawl_url"):
            return app.crawl_url(url, **params)
        return self.app.crawl(url, **params)

    def _map(self, url: str) -> Any:
        if hasattr(self.app, "map_url"):
            return self.app.map_url(url)
        app = self._get_firecrawl_v1_client(self.app)
        if app is not None and hasattr(app, "map_url"):
            return app.map_url(url)
        return self.app.map(url)

    def scrape_website(self, url: str) -> str:
        """Use this function to scrape a website using Firecrawl.

        Args:
            url (str): The URL to scrape.
        """
        params = {}
        if self.formats:
            params["formats"] = self.formats

        scrape_result = self._scrape(url, params)
        return json.dumps(scrape_result.model_dump(), cls=CustomJSONEncoder)

    def crawl_website(self, url: str, limit: Optional[int] = None) -> str:
        """Use this function to Crawls a website using Firecrawl.

        Args:
            url (str): The URL to crawl.
            limit (int): The maximum number of pages to crawl

        Returns:
            The results of the crawling.
        """
        params: Dict[str, Any] = {}
        if self.limit or limit:
            params["limit"] = self.limit or limit
        if self.formats:
            params["scrape_options"] = self._get_scrape_options()

        params["poll_interval"] = self.poll_interval

        crawl_result = self._crawl(url, params)
        return json.dumps(crawl_result.model_dump(), cls=CustomJSONEncoder)

    def map_website(self, url: str) -> str:
        """Use this function to Map a website using Firecrawl.

        Args:
            url (str): The URL to map.

        """
        map_result = self._map(url)
        return json.dumps(map_result.model_dump(), cls=CustomJSONEncoder)

    def search(self, query: str, limit: Optional[int] = None):
        """Use this function to search for the web using Firecrawl.

        Args:
            query (str): The query to search for.
            limit (int): The maximum number of results to return.
        """
        params: Dict[str, Any] = {}
        if self.limit or limit:
            params["limit"] = self.limit or limit
        if self.formats:
            params["scrape_options"] = self._get_scrape_options()
        if self.search_params:
            params.update(self.search_params)

        search_result = self.app.search(query, **params)
        if search_result.success:
            return json.dumps(search_result.data, cls=CustomJSONEncoder)
        else:
            return "Error searching with the Firecrawl tool: " + search_result.error
