#!/usr/bin/env python3

from typing import Optional, List
from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
import logging

from fp.fp import FreeProxy
from fp.errors import FreeProxyException

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Proxy Manager API",
    description="REST API for getting free working proxies with various filtering options",
    version="1.0.0"
)


# Pydantic models
class ProxyResponse(BaseModel):
    proxy: str
    schema: str
    country: Optional[str] = None


class ProxyListResponse(BaseModel):
    proxies: List[str]
    count: int
    country: Optional[str] = None


class ProxyConfigResponse(BaseModel):
    proxy_url: str
    requests: dict
    playwright: dict


# Health check endpoint
@app.get("/health", tags=["Health"])
async def health_check():
    """Check if the service is running"""
    return {"status": "ok"}


# Get single proxy endpoint
@app.get("/proxy", response_model=ProxyResponse, tags=["Proxy"])
async def get_proxy(
    country: Optional[str] = Query(None, description="Country code (e.g., 'US', 'GB', 'BR')"),
    timeout: float = Query(1.0, gt=0, description="Timeout for proxy validation in seconds (default: 1.0s)"),
    random: bool = Query(False, description="Randomize proxy selection"),
    anonymous: bool = Query(False, description="Only return anonymous proxies"),
    elite: bool = Query(False, description="Only return elite proxies"),
    https: bool = Query(False, description="Only return HTTPS proxies"),
    google: Optional[bool] = Query(None, description="Filter by Google compatibility")
):
    """
    Get a single working proxy with specified filters.

    **Parameters:**
    - **country**: Country code filter (e.g., 'US', 'GB')
    - **timeout**: Proxy validation timeout (default: 0.5s)
    - **random**: Randomize proxy selection order
    - **anonymous**: Only anonymous proxies
    - **elite**: Only elite proxies
    - **https**: Only HTTPS proxies
    - **google**: Filter by Google compatibility
    """
    try:
        country_list = [country] if country else None

        proxy_handler = FreeProxy(
            country_id=country_list,
            timeout=timeout,
            rand=random,
            anonym=anonymous,
            elite=elite,
            google=google,
            https=https
        )

        proxy_url = proxy_handler.get()
        schema = 'https' if https else 'http'

        return ProxyResponse(
            proxy=proxy_url,
            schema=schema,
            country=country
        )
    except FreeProxyException as e:
        logger.error(f"Failed to get proxy: {str(e)}")
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


# Get proxy configuration endpoint
@app.get("/proxy/config", response_model=ProxyConfigResponse, tags=["Proxy"])
async def get_proxy_config(
    country: Optional[str] = Query(None, description="Country code (e.g., 'US', 'GB')"),
    timeout: float = Query(1.0, gt=0, description="Timeout for proxy validation in seconds (default: 1.0s)"),
    random: bool = Query(False, description="Randomize proxy selection"),
    anonymous: bool = Query(False, description="Only return anonymous proxies"),
    elite: bool = Query(False, description="Only return elite proxies"),
    https: bool = Query(False, description="Only return HTTPS proxies"),
    google: Optional[bool] = Query(None, description="Filter by Google compatibility")
):
    """
    Get a single working proxy as formatted configuration objects for different libraries.

    Returns proxy in formats ready for:
    - requests library
    - Playwright (JavaScript)
    """
    try:
        country_list = [country] if country else None
        schema = 'https' if https else 'http'

        proxy_handler = FreeProxy(
            country_id=country_list,
            timeout=timeout,
            rand=random,
            anonym=anonymous,
            elite=elite,
            google=google,
            https=https
        )

        proxy_url = proxy_handler.get()

        # proxy_url comes as 'http://IP:PORT' so we use it directly for requests
        # For Playwright, use the same format
        return ProxyConfigResponse(
            proxy_url=proxy_url,
            requests={schema: proxy_url},
            playwright={'server': proxy_url}
        )
    except FreeProxyException as e:
        logger.error(f"Failed to get proxy config: {str(e)}")
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


# Get proxy list endpoint
@app.get("/proxies", response_model=ProxyListResponse, tags=["Proxy"])
async def get_proxy_list(
    country: Optional[str] = Query(None, description="Country code (e.g., 'US', 'GB')"),
    timeout: float = Query(1.0, gt=0, description="Timeout for proxy validation in seconds (default: 1.0s)"),
    random: bool = Query(False, description="Randomize proxy selection"),
    anonymous: bool = Query(False, description="Only return anonymous proxies"),
    elite: bool = Query(False, description="Only return elite proxies"),
    https: bool = Query(False, description="Only return HTTPS proxies"),
    google: Optional[bool] = Query(None, description="Filter by Google compatibility"),
    limit: int = Query(10, ge=1, le=100, description="Maximum number of proxies to return")
):
    """
    Get a list of working proxies with specified filters.

    This endpoint returns multiple proxies that match the criteria. Note that
    this may take longer as each proxy needs to be validated.
    """
    try:
        country_list = [country] if country else None

        proxy_handler = FreeProxy(
            country_id=country_list,
            timeout=timeout,
            rand=random,
            anonym=anonymous,
            elite=elite,
            google=google,
            https=https
        )

        # Get proxy list without validation
        proxy_list = proxy_handler.get_proxy_list(repeat=False)

        # Limit results
        limited_proxies = proxy_list[:limit]

        if not limited_proxies:
            raise FreeProxyException("No proxies found matching the criteria")

        return ProxyListResponse(
            proxies=limited_proxies,
            count=len(limited_proxies),
            country=country
        )
    except FreeProxyException as e:
        logger.error(f"Failed to get proxy list: {str(e)}")
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


# Root endpoint
@app.get("/", tags=["Info"])
async def root():
    """API documentation and info"""
    return {
        "name": "Proxy Manager API",
        "version": "1.0.0",
        "description": "Free proxy service with filtering capabilities",
        "docs": "/docs",
        "endpoints": {
            "health": {
                "method": "GET",
                "path": "/health",
                "description": "Check service health status"
            },
            "get_single_proxy": {
                "method": "GET",
                "path": "/proxy",
                "description": "Get a single working proxy",
                "parameters": {
                    "country": "Country code (e.g., 'US', 'GB', 'BR')",
                    "timeout": "Proxy validation timeout in seconds (default: 1.0)",
                    "random": "Randomize selection (default: false)",
                    "anonymous": "Only anonymous proxies (default: false)",
                    "elite": "Only elite proxies (default: false)",
                    "https": "Only HTTPS proxies (default: false)",
                    "google": "Filter by Google compatibility (default: null)"
                },
                "example": "/proxy?country=US&elite=true"
            },
            "get_proxy_config": {
                "method": "GET",
                "path": "/proxy/config",
                "description": "Get proxy in requests/playwright formats",
                "parameters": {
                    "country": "Country code (e.g., 'US', 'GB', 'BR')",
                    "timeout": "Proxy validation timeout in seconds (default: 1.0)",
                    "random": "Randomize selection (default: false)",
                    "anonymous": "Only anonymous proxies (default: false)",
                    "elite": "Only elite proxies (default: false)",
                    "https": "Only HTTPS proxies (default: false)",
                    "google": "Filter by Google compatibility (default: null)"
                },
                "example": "/proxy/config?country=US",
                "response_example": {
                    "proxy_url": "113.160.218.14:8888",
                    "requests": {"http": "http://113.160.218.14:8888"},
                    "playwright": {"server": "http://113.160.218.14:8888"}
                }
            },
            "get_proxy_list": {
                "method": "GET",
                "path": "/proxies",
                "description": "Get a list of working proxies",
                "parameters": {
                    "country": "Country code (e.g., 'US', 'GB')",
                    "timeout": "Proxy validation timeout in seconds (default: 1.0)",
                    "random": "Randomize selection (default: false)",
                    "anonymous": "Only anonymous proxies (default: false)",
                    "elite": "Only elite proxies (default: false)",
                    "https": "Only HTTPS proxies (default: false)",
                    "google": "Filter by Google compatibility (default: null)",
                    "limit": "Max results to return (1-100, default: 10)"
                },
                "example": "/proxies?country=US&elite=true&limit=5"
            }
        },
        "common_filters": {
            "web_scraping": "?elite=true&anonymous=true&timeout=1.0",
            "fast_operations": "?timeout=0.3&random=true",
            "privacy_sensitive": "?elite=true&anonymous=true&https=true",
            "us_traffic": "?country=US&elite=true&google=true"
        },
        "usage_examples": {
            "python_requests": "requests.get(url, proxies=requests_config)",
            "javascript_playwright": "browser.newContext({ proxy: playwright_config })",
            "curl": "curl 'http://localhost:8000/proxy?country=US'"
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
