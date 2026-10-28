"""Run with python -m download.fetch {headers,cer,abs}.

The abs subcommand is for the researcher only. Existing raw files are never
overwritten. Metadata is recorded only after a successful complete transfer.
"""
import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urljoin, urlparse
from urllib.request import Request, urlopen

import yaml
from bs4 import BeautifulSoup

CONFIG = Path("configs/sources.yaml")


def request(url, method="GET"):
    host = urlparse(url).hostname or ""
    if host not in {"cer.gov.au", "www.cer.gov.au", "www.abs.gov.au", "abs.gov.au"}:
        raise ValueError(f"Unapproved host: {host}")
    response = urlopen(Request(url, method=method, headers={"User-Agent": "BE-GNN-data-audit/0.1"}), timeout=45)
    if urlparse(response.url).hostname not in {"cer.gov.au", "www.cer.gov.au", "www.abs.gov.au", "abs.gov.au"}:
        response.close()
        raise ValueError("Redirect outside approved hosts")
    return response


def head(url):
    with request(url, "HEAD") as response:
        size = response.headers.get("Content-Length")
        return {"url": url, "checked_at": datetime.now(timezone.utc).isoformat(),
                "size_bytes": int(size) if size else None,
                "headers": dict(response.headers)}


def save_raw(url, path, config, allow_large=False):
    path = Path(path)
    if path.exists():
        raise FileExistsError(f"Raw file exists; no replacement allowed: {path}")
    metadata = head(url)
    size = metadata["size_bytes"]
    if not allow_large and (size is None or size >= 50_000_000):
        raise RuntimeError("Unknown or large size: researcher must run the download")
    path.parent.mkdir(parents=True, exist_ok=True)
    digest = hashlib.sha256()
    total = 0
    # Exclusive creation prevents accidental replacement even during concurrent use.
    # Interrupted transfers are kept and require researcher review, never deleted.
    with request(url) as response, path.open("xb") as output:
        while chunk := response.read(1024 * 1024):
            total += len(chunk)
            if not allow_large and total >= 50_000_000:
                raise RuntimeError("Transfer exceeded size limit; partial raw file retained")
            output.write(chunk)
            digest.update(chunk)
    if size is not None and total != size:
        raise RuntimeError("Incomplete transfer; raw file retained for review")
    config["files"][path.as_posix()] = {
        "url": url, "retrieved_at": datetime.now(timezone.utc).isoformat(),
        "size_bytes": total, "sha256": digest.hexdigest(),
    }
    CONFIG.write_text(yaml.safe_dump(config, sort_keys=False), encoding="utf-8")
    print(json.dumps(config["files"][path.as_posix()]))


def cer_links(html, base):
    links = {}
    for link in BeautifulSoup(html, "html.parser").find_all("a", href=True):
        url = urljoin(base, link["href"])
        name = urlparse(url).path.lower()
        is_csv = name.endswith(".csv") or (name.startswith("/document/") and "CSV" in link.get_text(" "))
        if "sgu-solar" in name and "installations" in name and is_csv:
            period = "early" if "2001-to-2010" in name else "recent" if "2011-to-present" in name else None
            if period:
                if period in links and links[period] != url:
                    raise ValueError(f"Ambiguous SGU Solar download for {period}")
                links[period] = url
    if set(links) != {"early", "recent"}:
        raise ValueError("Could not uniquely identify both SGU Solar installation CSVs")
    return links


def main():
    parser = argparse.ArgumentParser(__doc__)
    parser.add_argument("action", choices=["headers", "cer-headers", "cer", "abs"])
    parser.add_argument("--researcher-download", action="store_true", help="Researcher only: permit unknown/large CER transfer sizes")
    args = parser.parse_args()
    config = yaml.safe_load(CONFIG.read_text(encoding="utf-8"))
    if args.action == "headers":
        result = head(config["abs_url"])
        Path("reports/audit/abs_header.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
        print(json.dumps(result, indent=2))
    elif args.action == "abs":
        save_raw(config["abs_url"], "data/raw/abs_ed3_non_abs.zip", config, allow_large=True)
    else:
        with request(config["cer_page"]) as response:
            html = response.read(5_000_001)
        if len(html) > 5_000_000:
            raise RuntimeError("Unexpectedly large CER page")
        # Check both sizes before making any new raw file.
        links = cer_links(html, config["cer_page"])
        sizes = {period: head(url) for period, url in links.items()}
        Path("reports/audit/cer_headers.json").write_text(json.dumps(sizes, indent=2), encoding="utf-8")
        print(json.dumps(sizes, indent=2))
        if args.action == "cer-headers":
            return
        for metadata in sizes.values():
            if not args.researcher_download and (metadata["size_bytes"] is None or metadata["size_bytes"] >= 50_000_000):
                raise RuntimeError("CER size unknown/large; hand over to researcher")
        snapshot = Path("data/raw/cer_page.html")
        with snapshot.open("xb") as output:
            output.write(html)
        config["files"][snapshot.as_posix()] = {
            "url": config["cer_page"], "retrieved_at": datetime.now(timezone.utc).isoformat(),
            "size_bytes": len(html), "sha256": hashlib.sha256(html).hexdigest()}
        CONFIG.write_text(yaml.safe_dump(config, sort_keys=False), encoding="utf-8")
        for period, url in links.items():
            save_raw(url, f"data/raw/sgu_solar_{period}.csv", config, allow_large=args.researcher_download)


if __name__ == "__main__":
    main()
