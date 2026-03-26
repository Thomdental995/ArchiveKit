#!/usr/bin/env python3
"""
Web Archive Downloader
Made by MikePinku

Download a website snapshot from the Internet Archive Wayback Machine.
Supports Linux and Windows only.
"""

from __future__ import annotations

import argparse
import hashlib
import os
import platform
import re
from collections import deque
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup

WAYBACK_CDX_API = "https://web.archive.org/cdx/search/cdx"
WAYBACK_WEB_PREFIX = "https://web.archive.org/web"
SUPPORTED_PLATFORMS = {"Windows", "Linux"}
PROGRAM_VERSION = "1.0-rc1"


@dataclass
class Snapshot:
    timestamp: str
    original_url: str

    @property
    def page_url(self) -> str:
        return f"{WAYBACK_WEB_PREFIX}/{self.timestamp}id_/{self.original_url}"


class WaybackError(Exception):
    """Raised when Wayback API or download operations fail."""


class WaybackDownloader:
    def __init__(self, output_dir: Path, timeout: int = 30) -> None:
        self.output_dir = output_dir
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update(
            {
                "User-Agent": (
                    "WebArchiveDownloader/1.0 (Made by MikePinku; "
                    "+https://web.archive.org/)"
                )
            }
        )

    def resolve_snapshot(self, url: str, timestamp: str | None = None) -> Snapshot:
        direct = self._parse_wayback_url(url)
        if direct:
            return direct

        params = {
            "url": url,
            "output": "json",
            "fl": "timestamp,original,statuscode",
            "filter": "statuscode:200",
            "limit": "1",
        }
        if timestamp:
            params["closest"] = timestamp

        response = self.session.get(WAYBACK_CDX_API, params=params, timeout=self.timeout)
        response.raise_for_status()

        rows = response.json()
        if len(rows) < 2:
            raise WaybackError("No archived snapshot found for this URL.")

        timestamp_value = rows[1][0]
        original = rows[1][1]
        return Snapshot(timestamp=timestamp_value, original_url=original)

    @staticmethod
    def _parse_wayback_url(url: str) -> Snapshot | None:
        match = re.match(
            r"^https?://web\.archive\.org/web/(\d{14})(?:[^/]*)/(https?://.+)$",
            url,
        )
        if not match:
            return None
        return Snapshot(timestamp=match.group(1), original_url=match.group(2))

    def download_site(
        self,
        target_url: str,
        timestamp: str | None = None,
        depth: int = 0,
    ) -> Path:
        snapshot = self.resolve_snapshot(target_url, timestamp=timestamp)
        site_root = self._site_root(snapshot)
        site_root.mkdir(parents=True, exist_ok=True)

        start = snapshot.page_url
        target_host = urlparse(snapshot.original_url).netloc

        queue: deque[tuple[str, int]] = deque([(start, 0)])
        visited_pages: set[str] = set()
        downloaded_assets: set[str] = set()

        while queue:
            page_url, level = queue.popleft()
            if page_url in visited_pages:
                continue
            visited_pages.add(page_url)

            html = self._get_text(page_url)
            soup = BeautifulSoup(html, "html.parser")

            if level < depth:
                for candidate in self._extract_page_links(soup, page_url, snapshot.timestamp, target_host):
                    if candidate not in visited_pages:
                        queue.append((candidate, level + 1))

            self._download_assets(soup, page_url, snapshot.timestamp, downloaded_assets, site_root)
            self._rewrite_page_links(soup, page_url, snapshot.timestamp, target_host, site_root)

            page_path = self._local_page_path(site_root, page_url)
            page_path.parent.mkdir(parents=True, exist_ok=True)
            page_path.write_text(str(soup), encoding="utf-8")

        return site_root

    def _site_root(self, snapshot: Snapshot) -> Path:
        parsed = urlparse(snapshot.original_url)
        clean_host = parsed.netloc.replace(":", "_")
        return self.output_dir / f"{clean_host}_{snapshot.timestamp}"

    def _get_text(self, url: str) -> str:
        response = self.session.get(url, timeout=self.timeout)
        response.raise_for_status()
        current_encoding = (response.encoding or "").lower()
        if not current_encoding or current_encoding in {"iso-8859-1", "latin-1", "latin1"}:
            detected = response.apparent_encoding
            if detected:
                response.encoding = detected
            else:
                response.encoding = "utf-8"
        return response.text

    def _download_binary(self, url: str) -> bytes:
        response = self.session.get(url, timeout=self.timeout)
        response.raise_for_status()
        return response.content

    def _download_assets(
        self,
        soup: BeautifulSoup,
        page_url: str,
        timestamp: str,
        downloaded_assets: set[str],
        site_root: Path,
    ) -> None:
        for tag, attr in self._asset_selectors():
            for node in soup.find_all(tag):
                source = node.get(attr)
                if not source:
                    continue
                normalized = self._normalize_asset_url(source, page_url, timestamp)
                if not normalized:
                    continue
                if normalized not in downloaded_assets:
                    try:
                        data = self._download_binary(normalized)
                    except requests.RequestException:
                        # Some archived asset URLs are missing; skip them and continue.
                        continue
                    local_path = self._local_asset_path(site_root, normalized)
                    local_path.parent.mkdir(parents=True, exist_ok=True)
                    local_path.write_bytes(data)
                    downloaded_assets.add(normalized)
                node[attr] = self._relative_link(site_root, self._local_page_path(site_root, page_url), self._local_asset_path(site_root, normalized))

    def _rewrite_page_links(
        self,
        soup: BeautifulSoup,
        page_url: str,
        timestamp: str,
        target_host: str,
        site_root: Path,
    ) -> None:
        page_local = self._local_page_path(site_root, page_url)
        for node in soup.find_all("a"):
            href = node.get("href")
            if not href:
                continue
            normalized = self._normalize_page_url(href, page_url, timestamp, target_host)
            if not normalized:
                continue
            linked_local = self._local_page_path(site_root, normalized)
            node["href"] = os.path.relpath(linked_local, start=page_local.parent).replace("\\", "/")

    def _extract_page_links(
        self,
        soup: BeautifulSoup,
        page_url: str,
        timestamp: str,
        target_host: str,
    ) -> Iterable[str]:
        for node in soup.find_all("a"):
            href = node.get("href")
            if not href:
                continue
            normalized = self._normalize_page_url(href, page_url, timestamp, target_host)
            if normalized:
                yield normalized

    def _normalize_page_url(self, href: str, page_url: str, timestamp: str, target_host: str) -> str | None:
        if href.startswith(("#", "javascript:", "mailto:", "tel:")):
            return None

        absolute = urljoin(page_url, href)
        parsed = urlparse(absolute)

        if parsed.netloc == "web.archive.org":
            return absolute

        if parsed.netloc != target_host:
            return None

        return f"{WAYBACK_WEB_PREFIX}/{timestamp}id_/{absolute}"

    def _normalize_asset_url(self, src: str, page_url: str, timestamp: str) -> str | None:
        if src.startswith(("data:", "javascript:", "mailto:", "tel:", "#")):
            return None

        absolute = urljoin(page_url, src)
        parsed = urlparse(absolute)

        if parsed.netloc == "web.archive.org":
            return absolute

        return f"{WAYBACK_WEB_PREFIX}/{timestamp}id_/{absolute}"

    def _local_page_path(self, site_root: Path, page_url: str) -> Path:
        parsed = urlparse(page_url)
        raw = parsed.path.strip("/")
        if not raw or raw.endswith("/"):
            raw = f"{raw}index.html" if raw else "index.html"
        if not raw.endswith(".html"):
            raw = f"{raw}.html"

        safe = self._safe_path(raw)
        if parsed.query:
            digest = hashlib.sha1(parsed.query.encode("utf-8")).hexdigest()[:8]
            base, ext = os.path.splitext(safe)
            safe = f"{base}_{digest}{ext}"
        return site_root / "pages" / safe

    def _local_asset_path(self, site_root: Path, asset_url: str) -> Path:
        parsed = urlparse(asset_url)
        raw_path = parsed.path.strip("/") or "asset.bin"
        safe_path = self._safe_path(raw_path)
        if parsed.query:
            digest = hashlib.sha1(parsed.query.encode("utf-8")).hexdigest()[:8]
            base, ext = os.path.splitext(safe_path)
            safe_path = f"{base}_{digest}{ext or '.bin'}"
        return site_root / "assets" / parsed.netloc / safe_path

    @staticmethod
    def _relative_link(site_root: Path, page_path: Path, asset_path: Path) -> str:
        _ = site_root
        return os.path.relpath(asset_path, start=page_path.parent).replace("\\", "/")

    @staticmethod
    def _asset_selectors() -> list[tuple[str, str]]:
        return [
            ("img", "src"),
            ("script", "src"),
            ("link", "href"),
            ("source", "src"),
            ("video", "poster"),
            ("audio", "src"),
        ]

    @staticmethod
    def _safe_path(path_value: str) -> str:
        cleaned = re.sub(r"[<>:\\|?*\x00-\x1F]", "_", path_value)
        return cleaned.replace("//", "/")


def validate_platform() -> None:
    current = platform.system()
    if current not in SUPPORTED_PLATFORMS:
        raise SystemExit(
            "This tool is only available for Linux and Windows users. "
            f"Current platform: {current}"
        )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Web Archive Downloader (Made by MikePinku)",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"Web Archive Downloader {PROGRAM_VERSION}",
    )
    parser.add_argument("url", help="Target website URL to download from Wayback")
    parser.add_argument(
        "-t",
        "--timestamp",
        help="Preferred archive timestamp in YYYYMMDDhhmmss",
    )
    parser.add_argument(
        "-d",
        "--depth",
        type=int,
        default=0,
        help="Page crawl depth inside same host (default: 0)",
    )
    parser.add_argument(
        "-o",
        "--output",
        default="downloads",
        help="Output directory (default: downloads)",
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=30,
        help="HTTP timeout in seconds (default: 30)",
    )
    return parser.parse_args()


def print_welcome_screen() -> None:
    print("=" * 58)
    print("Welcome to Web Archive Downloader")
    print("Made by MikePinku")
    print("This tool downloads archived web pages from Wayback Machine.")
    print("Supported platforms: Windows and Linux")
    print("=" * 58)


def main() -> None:
    validate_platform()
    args = parse_args()
    print_welcome_screen()

    if args.depth < 0:
        print("an error has occurred. please try again!")
        raise SystemExit(1)

    output_dir = Path(args.output)
    downloader = WaybackDownloader(output_dir=output_dir, timeout=args.timeout)

    try:
        print("downloading archive page, please wait...")
        saved_to = downloader.download_site(
            target_url=args.url,
            timestamp=args.timestamp,
            depth=args.depth,
        )
    except (requests.RequestException, WaybackError, Exception):
        print("an error has occurred. please try again!")
        raise SystemExit(1)

    print("the page has benn successfully archived. thank you for using my service!")
    print(f"Saved to: {saved_to}")


if __name__ == "__main__":
    main()
