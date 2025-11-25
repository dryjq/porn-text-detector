"""网页抓取与文本抽取工具。"""
from __future__ import annotations

import logging
import re
from dataclasses import dataclass
from typing import Optional

import requests
from bs4 import BeautifulSoup

import config

logger = logging.getLogger(__name__)


@dataclass
class FetchResult:
    url: str
    success: bool
    text: str
    error: Optional[str] = None
    status_code: Optional[int] = None


class URLFetcher:
    def __init__(self, timeout: int = config.REQUEST_TIMEOUT):
        self.timeout = timeout

    def fetch(self, url: str) -> FetchResult:
        try:
            resp = requests.get(url, timeout=self.timeout, headers=config.default_headers)
            status = resp.status_code
            if status >= 400:
                return FetchResult(url=url, success=False, text="", error=f"HTTP {status}", status_code=status)
            content = self._extract_text(resp.text)
            return FetchResult(url=url, success=True, text=content, status_code=status)
        except requests.RequestException as exc:  # noqa: BLE001
            logger.exception("访问失败: %s", url)
            return FetchResult(url=url, success=False, text="", error=str(exc))

    @staticmethod
    def _extract_text(html: str) -> str:
        soup = BeautifulSoup(html, "html.parser")
        for tag in soup(["script", "style", "noscript"]):
            tag.extract()
        text = soup.get_text(separator=" ")
        text = re.sub(r"\s+", " ", text)
        return text.strip()
