"""
Run this file to download data from Dryad and unzip the zip files. Downloaded files end
up in this repostitory's data/ directory.

First create the b2txt25 conda environment. Then in a Terminal, at this repository's
top-level directory (nejm-brain-to-text/), run:

conda activate b2txt25
python download_data.py
"""

import sys
import os
import urllib.request
import json
import zipfile


########################################################################################
#
# Helpers.
#
########################################################################################


def display_progress_bar(block_num, block_size, total_size, message=""):
    """"""
    bytes_downloaded_so_far = block_num * block_size
    MB_downloaded_so_far = bytes_downloaded_so_far / 1e6
    MB_total = total_size / 1e6
    sys.stdout.write(
        f"\r{message}\t\t{MB_downloaded_so_far:.1f} MB / {MB_total:.1f} MB"
    )
    sys.stdout.flush()


# top: pip install requests
import time, requests
from requests.adapters import HTTPAdapter, Retry

CHUNK = 8 * 1024 * 1024  # 8 MiB
PRINT_EVERY_BYTES = 100 * 1024 * 1024  # 100 MiB

def download_with_resume(url, dest, expected_size=None, max_retries=8):
    os.makedirs(os.path.dirname(dest) or ".", exist_ok=True)
    s = requests.Session()
    retries = Retry(total=max_retries, backoff_factor=1.5,
                    status_forcelist=[429,500,502,503,504],
                    allowed_methods=["GET","HEAD"])
    s.mount("http://", HTTPAdapter(max_retries=retries))
    s.mount("https://", HTTPAdapter(max_retries=retries))

    existing = os.path.getsize(dest) if os.path.exists(dest) else 0
    head = s.head(url, timeout=30)
    head.raise_for_status()
    total = int(head.headers.get("Content-Length", expected_size or 0)) or None
    supports_range = head.headers.get("Accept-Ranges","").lower() == "bytes"

    headers = {"Range": f"bytes={existing}-"} if (supports_range and existing) else {}
    mode = "ab" if headers else "wb"
    downloaded = existing
    last_print = existing

    with s.get(url, headers=headers, stream=True, timeout=60) as r, open(dest, mode) as f:
        if headers and r.status_code == 200:
            # server ignored Range; restart
            f.close()
            os.remove(dest)
            return download_with_resume(url, dest, expected_size, max_retries)
        r.raise_for_status()
        start = time.time()
        for chunk in r.iter_content(chunk_size=CHUNK):
            if not chunk:
                continue
            f.write(chunk)
            downloaded += len(chunk)
            if downloaded - last_print >= PRINT_EVERY_BYTES or (time.time()-start) > 1.0:
                if total:
                    pct = 100.0 * downloaded / total
                    print(f"\rDownloading {os.path.basename(dest)}: {downloaded/1e6:.1f} / {total/1e6:.1f} MB ({pct:.1f}%)", end="")
                else:
                    print(f"\rDownloading {os.path.basename(dest)}: {downloaded/1e6:.1f} MB", end="")
                last_print = downloaded
                start = time.time()
    print()
    if total and downloaded != total:
        raise IOError(f"Download incomplete: got {downloaded} of {total} bytes")



########################################################################################
#
# Main function.
#
########################################################################################


def main():
    """"""
    DRYAD_DOI = "10.5061/dryad.dncjsxm85"

    ## Make sure the command is being run from the right place and we can see the data/
    ## directory.

    DATA_DIR = "data/"
    data_dirpath = os.path.abspath(DATA_DIR)
    assert os.getcwd().endswith(
        "brain-to-text-25"
    ), f"Please run the download command from the brain-to-text-25 (instead of {os.getcwd()})"
    assert os.path.exists(
        data_dirpath
    ), "Cannot find the data directory to download into."

    ## Get the list of files from the latest version on Dryad.

    DRYAD_ROOT = "https://datadryad.org"
    urlified_doi = DRYAD_DOI.replace("/", "%2F")

    versions_url = f"{DRYAD_ROOT}/api/v2/datasets/doi:{urlified_doi}/versions"
    with urllib.request.urlopen(versions_url) as response:
        versions_info = json.loads(response.read().decode())

    files_url_path = versions_info["_embedded"]["stash:versions"][-1]["_links"][
        "stash:files"
    ]["href"]
    files_url = f"{DRYAD_ROOT}{files_url_path}"
    with urllib.request.urlopen(files_url) as response:
        files_info = json.loads(response.read().decode())

    file_infos = files_info["_embedded"]["stash:files"]

    ## Download each file into the data directory (and unzip for certain files).

    for file_info in file_infos:
        filename = file_info["path"]

        if filename == "README.md":
            continue

        download_path = file_info["_links"]["stash:download"]["href"]
        download_url = f"{DRYAD_ROOT}{download_path}"

        download_to_filepath = os.path.join(data_dirpath, filename)

        download_with_resume(download_url, download_to_filepath)
        sys.stdout.write("\n")

        # If this file is a zip file, unzip it into the data directory.

        if file_info["mimeType"] == "application/zip":
            print(f"Extracting files from {filename} ...")
            with zipfile.ZipFile(download_to_filepath, "r") as zf:
                zf.extractall(data_dirpath)

    print(f"\nDownload complete. See data files in {data_dirpath}\n")


if __name__ == "__main__":
    main()