import pytest

from download.fetch import cer_links, save_raw


def test_only_correct_product_and_measure():
    base = "https://cer.gov.au/"
    names = ["sgu-solar-installations-2001-to-2010.csv", "sgu-solar-installations-2011-to-present-and-totals.csv",
             "swh-solar-installations-2001-to-2010.csv", "sgu-solar-capacity-2001-to-2010.csv"]
    html = "".join(f'<a href="/{n}">{n}</a>' for n in names)
    links = cer_links(html, base)
    assert len(links) == 2
    assert all("sgu-solar-installations" in url for url in links.values())


def test_existing_raw_never_overwritten(tmp_path):
    path = tmp_path / "raw.csv"
    path.write_bytes(b"immutable")
    with pytest.raises(FileExistsError):
        save_raw("https://cer.gov.au/test.csv", path, {"files": {}})
    assert path.read_bytes() == b"immutable"


def test_unknown_size_never_downloads(monkeypatch, tmp_path):
    monkeypatch.setattr("download.fetch.head", lambda _: {"size_bytes": None})
    with pytest.raises(RuntimeError, match="researcher"):
        save_raw("https://cer.gov.au/test.csv", tmp_path / "new.csv", {"files": {}})
    assert not (tmp_path / "new.csv").exists()


def test_cer_document_download_routes():
    html = '<a href="/document/sgu-solar-installations-2001-to-2010">SGU-Solar Installations (CSV)</a><a href="/document/sgu-solar-installations-2011-to-present-and-totals">SGU-Solar Installations (CSV)</a>'
    links = cer_links(html, "https://cer.gov.au/")
    assert set(links) == {"early", "recent"}
