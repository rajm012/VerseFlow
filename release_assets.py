"""Only offer release artifacts built for this Linux architecture."""
import platform


def linux_download_url(release, architecture=None):
    arch = (architecture or platform.machine()).lower()
    arch = {"amd64": "x86_64", "arm64": "aarch64"}.get(arch, arch)
    for asset in release.get("assets", []):
        name = asset.get("name", "").lower()
        if (name.startswith(f"verseflow-linux-{arch}-")
                and name.endswith((".tar.gz", ".appimage"))):
            return asset.get("browser_download_url")
    return None
