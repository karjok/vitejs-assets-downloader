import argparse
import sys
import re
from . import ViteJsAssetsDownloader
from . import __version__


def banner():
    banner_text = f"""
\033[1;35m⡀⢀ ⠄ ⣰⡀ ⢀⡀   \033[0m⢀⣸ ⡇
\033[1;35m⠱⠃ ⠇ ⠘⠤ ⠣⠭   \033[0m⠣⠼ ⠣
\033[1;30mv{__version__}\033[0m
"""
    print(banner_text)


def colorize(msg: str) -> str:
    # c = "\033[1;35m"
    c = ""
    r = "\033[0m"
    msg = re.sub(r"(\[\d+/\d+\])", rf"{c}\1{r}", msg)
    msg = re.sub(r"(\[FAILED\])", rf"{c}\1{r}", msg)
    msg = re.sub(r"\b(downloaded|beautifying)\b", rf"{c}\1{r}", msg)
    msg = re.sub(r"(Download complete:)", rf"{c}\1{r}", msg)
    msg = re.sub(r"(All files saved to)", rf"{c}\1{r}", msg)
    return msg


def main():
    banner()
    parser = argparse.ArgumentParser(
        description="Download JS assets from a Vite.js powered website"
    )
    parser.add_argument("url", help="Target website URL")
    parser.add_argument("-o", "--output-dir", default=None,
                        help="Output directory name (default: auto from hostname)")
    parser.add_argument("-b", "--beautify", action="store_true", default=False,
                        help="Beautify JS output")
    args = parser.parse_args()

    with ViteJsAssetsDownloader(args.url) as dl:
        dl.download_js_files(
            output_dir=args.output_dir,
            beautify=args.beautify,
            log_func=lambda msg: print(colorize(msg))
        )


if __name__ == "__main__":
    main()
