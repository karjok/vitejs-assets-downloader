import re
import json
import os
import asyncio
from urllib.parse import urljoin, urlparse
from curl_cffi import AsyncSession
from bs4 import BeautifulSoup
import jsbeautifier

__version__ = "0.1.0"


class ViteJsAssetsDownloader:
    def __init__(self, target_url: str):
        self.target_url = target_url
        self._async_session: AsyncSession | None = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    async def __aenter__(self):
        self._async_session = AsyncSession(impersonate="chrome131")
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self._async_session:
            await self._async_session.close()

    async def _async_fetch(self, url: str) -> str:
        if self._async_session is None:
            async with AsyncSession(impersonate="chrome131") as s:
                response = await s.get(url)
                response.raise_for_status()
                return response.text
        response = await self._async_session.get(url)
        response.raise_for_status()
        return response.text

    @staticmethod
    def _parse_index_src(page_source: str) -> str | None:
        html = BeautifulSoup(page_source, "html.parser")
        script_tags = html.find_all("script")
        script_tags_src = [
            x.get("src") for x in script_tags if hasattr(x, "src") and "index" in x.get("src", "")
        ]
        if not script_tags_src:
            return None
        return script_tags_src[-1] if len(script_tags_src) > 1 else script_tags_src[0]

    @staticmethod
    def _parse_mapDeps(js_code: str) -> str | None:
        match = re.search(r"__vite__mapDeps.*;", js_code)
        return match.group() if match else None

    @staticmethod
    def _extract_js_file_from_mapDeps_assets(mapDeps: str) -> list:
        match = re.search(r"\[\"(.*?)\"\]", mapDeps)
        if not match:
            return []
        return sorted(set(js for js in json.loads(match.group()) if js.endswith(".js")))

    async def _async_find_index_js(self) -> str | None:
        return self._parse_index_src(await self._async_fetch(self.target_url))

    async def _async_get_vite_mapDeps(self) -> str | None:
        index_script = await self._async_find_index_js()
        if not index_script:
            return None
        return self._parse_mapDeps(
            await self._async_fetch(urljoin(self.target_url, index_script))
        )

    async def _async_build_js_file_urls(self) -> list | None:
        index_script = await self._async_find_index_js()
        if not index_script:
            return None
        index_url = urljoin(self.target_url, index_script)
        js_code = await self._async_fetch(index_url)
        mapDeps = self._parse_mapDeps(js_code)
        if not mapDeps:
            return None
        js_files = self._extract_js_file_from_mapDeps_assets(mapDeps)
        chunk_urls = [urljoin(self.target_url, js) for js in js_files]
        return [index_url] + chunk_urls if chunk_urls else None

    def _find_index_js(self) -> str | None:
        return asyncio.run(self._async_find_index_js())

    def _get_vite_mapDeps(self) -> str | None:
        return asyncio.run(self._async_get_vite_mapDeps())

    def _build_js_file_urls(self) -> list | None:
        return asyncio.run(self._async_build_js_file_urls())

    def download_js_files(self, output_dir: str = None, beautify=False, max_concurrency=20, log_func=None):
        asyncio.run(self.download_js_files_async(output_dir, beautify, max_concurrency, log_func))

    async def download_js_files_async(self, output_dir: str = None, beautify=False, max_concurrency=20, log_func=None):
        if not output_dir:
            output_dir = urlparse(self.target_url).netloc
        output_path = os.path.join("vitedl-output", output_dir)
        log = log_func or (lambda _: None)

        own_session = self._async_session is None
        if own_session:
            self._async_session = AsyncSession(impersonate="chrome131")

        try:
            js_file_urls = await self._async_build_js_file_urls() or []
            if not js_file_urls:
                return
            os.makedirs(output_path, exist_ok=True)
            semaphore = asyncio.Semaphore(max_concurrency)
            downloaded = []
            dl_count = 0
            total = len(js_file_urls)

            async def download_one(url: str):
                nonlocal dl_count
                try:
                    async with semaphore:
                        file_name = urlparse(url).path.split("/")[-1]
                        js_code = await self._async_fetch(url)
                    file_path = os.path.join(output_path, file_name)
                    with open(file_path, "w") as file:
                        file.write(js_code)
                    downloaded.append(file_path)
                    dl_count += 1
                    log(f"[{dl_count}/{total}] {file_name} downloaded")
                except Exception as e:
                    log(f"[FAILED] {url} — {e}")

            await asyncio.gather(*[download_one(url) for url in js_file_urls], return_exceptions=True)

            success = len(downloaded)
            log(f"\nDownload complete: {success}/{total} files\n")

            if beautify:
                for i, fp in enumerate(downloaded, 1):
                    name = fp.split("/")[-1]
                    log(f"[{i}/{success}] beautifying {name}")
                    result = await asyncio.to_thread(jsbeautifier.beautify_file, fp)
                    with open(fp, "w") as f:
                        f.write(result)

            log(f"\nAll files saved to {output_path}")
        finally:
            if own_session:
                await self._async_session.close()
                self._async_session = None
