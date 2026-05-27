<div align="center">
  <br>
  <p>
    <picture>
      <source media="(prefers-color-scheme: dark)" srcset="https://img.shields.io/badge/vitejs--assets--downloader-v0.1.0-%23c084fc?style=for-the-badge&labelColor=%23333333">
      <img src="https://img.shields.io/badge/vitejs--assets--downloader-v0.1.0-%23933ea2?style=for-the-badge&labelColor=%23f3e8ff" alt="vitejs-assets-downloader">
    </picture>
  </p>
  <p>
    <img src="https://img.shields.io/badge/python-%3E%3D3.10-%23933ea2?style=flat-square&logo=python&logoColor=white" alt="python">
    <img src="https://img.shields.io/badge/license-MIT-%23933ea2?style=flat-square" alt="license">
    <img src="https://img.shields.io/github/last-commit/karjok/vitejs-assets-downloader?style=flat-square&color=%23933ea2" alt="last commit">
  </p>
</div>

<br>

# ViteJS Assets Downloader

Download all JavaScript chunk assets from Vite.js powered websites. Scrapes the `__vite__mapDeps` array embedded in the main entry script to discover and download every lazy-loaded JS chunk.
<img width="611" height="314" alt="image" src="https://github.com/user-attachments/assets/2d60b5c9-3684-4bc6-849f-ded3411ec63f" />
## Installation

```bash
# via pip (git)
pip install git+https://github.com/karjok/vitejs-assets-downloader.git

# via uv
uv pip install git+https://github.com/karjok/vitejs-assets-downloader.git

# or locally (editable)
uv pip install -e .
```

## CLI Usage

```bash
vitedl <url> [-o <dir>] [-b]
```

### Options

| Flag | Description |
|---|---|
| `url` | Target website URL (positional) |
| `-o`, `--output-dir` | Output subdirectory name (default: auto from hostname) |
| `-b`, `--beautify` | Beautify JS output with `jsbeautifier` |

### Examples

```bash
# Basic download
vitedl https://example.com

# Custom output directory
vitedl https://example.com -o myproject

# Beautify output
vitedl https://example.com -b

# Combined
vitedl https://example.com -o myproject -b
```

All files are saved under `vitedl-output/<dir>/`.

## Python Module Usage

```python
from vitedl import ViteJsAssetsDownloader

# Sync context manager
with ViteJsAssetsDownloader("https://example.com") as dl:
    dl.download_js_files(
        output_dir="myproject",
        beautify=True,
        max_concurrency=20,
        log_func=print
    )

# Async context manager
async with ViteJsAssetsDownloader("https://example.com") as dl:
    await dl.download_js_files_async(
        output_dir="myproject",
        beautify=True,
        max_concurrency=20,
        log_func=print
    )
```

### API

#### `ViteJsAssetsDownloader(target_url)`

| Method | Description |
|---|---|
| `download_js_files(output_dir, beautify, max_concurrency, log_func)` | Sync entry point — wraps async version with `asyncio.run()` |
| `download_js_files_async(output_dir, beautify, max_concurrency, log_func)` | Async download — fetches HTML, parses `__vite__mapDeps`, downloads all chunks concurrently |

**Parameters:**
- `output_dir` — subdirectory name inside `vitedl-output/` (default: hostname)
- `beautify` — beautify JS using `jsbeautifier` after all downloads complete (default: `False`)
- `max_concurrency` — max concurrent downloads (default: `20`)
- `log_func` — callable `(msg: str) -> None` for progress messages (default: no-op)

## How It Works

1. Fetches the target page HTML
2. Finds the Vite entry script (`<script src="...index-xxx.js">`)
3. Fetches the entry script and extracts the `__vite__mapDeps` array
4. Resolves all chunk URLs from the array
5. Downloads all chunks concurrently (synchronized by semaphore)
6. Optionally beautifies all files after download completes
7. Saves everything to `vitedl-output/<hostname>/`

## Dependencies

- `bs4` — HTML parsing
- `curl-cffi` — async HTTP with TLS fingerprint impersonation
- `jsbeautifier` — JavaScript beautification

## Development

```bash
git clone https://github.com/karjok/vitejs-assets-downloader.git
cd vitejs-assets-downloader
uv sync
```

Then start coding. Use `uv run` to execute:

```bash
uv run vitedl https://example.com -b
uv run python main.py https://example.com -b
```

### Bumping version

```bash
uv run bump-my-version bump patch   # 0.1.0 → 0.1.1
uv run bump-my-version bump minor   # 0.1.0 → 0.2.0
uv run bump-my-version bump major   # 0.1.0 → 1.0.0
```

Auto-updates version in `pyproject.toml` and `vitedl/__init__.py`.

## License

MIT
