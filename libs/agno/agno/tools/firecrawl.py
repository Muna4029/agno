import json
from os import getenv
from typing import Any, Dict, List, Optional

# The firecrawl package has changed its exported symbols in some versions.
# Try to import the expected names and fall back to V1ScrapeOptions if available;
# finally, provide a small fallback ScrapeOptions-compatible placeholder so
# the rest of the module can operate in environments without the newer package.
try:
    from firecrawl import FirecrawlApp, ScrapeOptions
except Exception:  # pragma: no cover - handle different installed versions
    try:
        from firecrawl import FirecrawlApp, V1ScrapeOptions as ScrapeOptions
    except Exception:  # pragma: no cover
        # Minimal placeholder to preserve runtime behavior when firecrawl isn't available
        from dataclasses import dataclass, field
        from typing import List as _List, Optional as _Optional

        @dataclass
        class ScrapeOptions:
            formats: _Optional[_List[str]] = field(default=None)

        # Provide a lightweight stub for FirecrawlApp to avoid NameError during import
        class FirecrawlApp:  # pragma: no cover - fallback stub
            def __init__(self, api_key=None, api_url=None):
                self.api_key = api_key
                self.api_url = api_url

            def scrape_url(self, url, **kwargs):
                raise RuntimeError("Firecrawl is not installed; cannot call scrape_url")

            def crawl_url(self, url, **kwargs):
                raise RuntimeError("Firecrawl is not installed; cannot call crawl_url")

            def map_url(self, url, **kwargs):
                raise RuntimeError("Firecrawl is not installed; cannot call map_url")

            def search(self, query, **kwargs):
                raise RuntimeError("Firecrawl is not installed; cannot call search")

from agno.tools import Toolkit
from agno.utils.log import logger

try:
    from firecrawl import FirecrawlApp, ScrapeOptions  # type: ignore[attr-defined]
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
        params = {}
        if self.formats:
            params["formats"] = self.formats

        scrape_result = self.app.scrape_url(url, **params)
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
            # Some versions of firecrawl expose a model class for ScrapeOptions
            # while others may expect a plain dict. Be resilient and try to
            # construct the ScrapeOptions object, falling back to a dict.
            try:
                params["scrape_options"] = ScrapeOptions(formats=self.formats)  # type: ignore
            except Exception:
                params["scrape_options"] = {"formats": self.formats}

        params["poll_interval"] = self.poll_interval

        crawl_result = self.app.crawl_url(url, **params)
        return json.dumps(crawl_result.model_dump(), cls=CustomJSONEncoder)

    def map_website(self, url: str) -> str:
        """Use this function to Map a website using Firecrawl.

        Args:
            url (str): The URL to map.

        """
        map_result = self.app.map_url(url)
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
            try:
                params["scrape_options"] = ScrapeOptions(formats=self.formats)  # type: ignore
            except Exception:
                params["scrape_options"] = {"formats": self.formats}
        if self.search_params:
            params.update(self.search_params)

        search_result = self.app.search(query, **params)
        if search_result.success:
            return json.dumps(search_result.data, cls=CustomJSONEncoder)
        else:
            return "Error searching with the Firecrawl tool: " + search_result.error
