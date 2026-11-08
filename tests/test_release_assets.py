from release_assets import linux_download_url


def test_selects_only_matching_linux_artifacts():
    release = {"assets": [
        {"name": "unrelated-2.0.tar.gz", "browser_download_url": "unrelated"},
        {"name": "VerseFlow-linux-aarch64-2.0.tar.gz", "browser_download_url": "arm"},
        {"name": "VerseFlow-linux-x86_64-2.0.tar.gz", "browser_download_url": "linux"},
    ]}
    assert linux_download_url(release, "amd64") == "linux"
    assert linux_download_url(release, "arm64") == "arm"
    assert linux_download_url(release, "riscv64") is None
    assert linux_download_url({"assets": release["assets"][:1]}, "x86_64") is None
