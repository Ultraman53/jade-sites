#!/usr/bin/env python3
"""Build the Jade Astrology site into plain HTML files.

Runs on every droplet (at first boot and then hourly), and on your Mac for a preview:

    python3 site/build.py --config site/site.example.json --out build/

Only the Python standard library is used. Content that changes (daily, tomorrow and
weekly horoscopes, compatibility texts) comes from the AWS brain's public content
address. If the brain can't be reached, the last good copy is reused; with no copy
yet (or brain_url "test") sample text is used, clearly marked as sample.
"""
import argparse
import datetime as dt
import html
import json
import os
import shutil
import sys
import tempfile
import urllib.request
from zoneinfo import ZoneInfo

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import pages  # noqa: E402  (the page definitions live in site/pages.py)

TZ = ZoneInfo("America/New_York")


def load_json(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def fetch_content(brain, name, cache_dir):
    """Content JSON from the brain, else the cached copy, else None."""
    cache = os.path.join(cache_dir, name + ".json")
    if brain and brain != "test":
        url = brain.rstrip("/") + "/v1/content/" + name
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "jade-site-build/1"})
            with urllib.request.urlopen(req, timeout=20) as r:
                data = json.loads(r.read().decode("utf-8"))
            os.makedirs(cache_dir, exist_ok=True)
            tmp = cache + ".tmp"
            with open(tmp, "w", encoding="utf-8") as f:
                json.dump(data, f)
            os.replace(tmp, cache)
            return data
        except Exception as e:  # keep the site up with the last good copy
            print(f"warning: could not fetch {name} from the brain ({e}); using the cached copy", file=sys.stderr)
    if os.path.exists(cache):
        try:
            return load_json(cache)
        except Exception:
            pass
    return None


def write_tree(files, out):
    """Write all files into a fresh folder, then swap it in so visitors never see a half-built site."""
    out = os.path.abspath(out.rstrip("/"))
    parent = os.path.dirname(out)
    os.makedirs(parent, exist_ok=True)
    stage = tempfile.mkdtemp(prefix=".jade-build-", dir=parent)
    for rel, content in files.items():
        path = os.path.join(stage, rel)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        mode = "wb" if isinstance(content, bytes) else "w"
        with open(path, mode, **({} if mode == "wb" else {"encoding": "utf-8"})) as f:
            f.write(content)
    # copy static assets
    shutil.copytree(os.path.join(HERE, "assets"), os.path.join(stage, "assets"), dirs_exist_ok=True)
    os.chmod(stage, 0o755)
    for root, dirs, fs in os.walk(stage):
        for d in dirs:
            os.chmod(os.path.join(root, d), 0o755)
        for f in fs:
            os.chmod(os.path.join(root, f), 0o644)
    if os.path.isdir(out) and os.listdir(out):
        old = out + ".old"
        shutil.rmtree(old, ignore_errors=True)
        # Keep the folder itself (the web server points at it); swap its contents.
        os.rename(out, old)
        os.rename(stage, out)
        shutil.rmtree(old, ignore_errors=True)
    else:
        if os.path.isdir(out):
            os.rmdir(out)
        os.rename(stage, out)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", required=True, help="site.json with domain, site_id, brain_url")
    ap.add_argument("--out", required=True, help="output folder")
    ap.add_argument("--cache", default=None, help="folder for the last good content (default: next to --config)")
    ap.add_argument("--now", default=None, help="pretend it is this time (YYYY-MM-DDTHH:MM), for previews")
    a = ap.parse_args()

    cfg = load_json(a.config)
    for k in ("domain", "site_id", "brain_url"):
        if not cfg.get(k):
            sys.exit(f"config is missing '{k}'")
    cache_dir = a.cache or os.path.join(os.path.dirname(os.path.abspath(a.config)), "content-cache")
    now = dt.datetime.fromisoformat(a.now).replace(tzinfo=TZ) if a.now else dt.datetime.now(TZ)

    ref = load_json(os.path.join(HERE, "data", "reference.json"))
    copy = load_json(os.path.join(HERE, "data", "funnel-copy.json"))
    horoscopes = fetch_content(cfg["brain_url"], "horoscopes", cache_dir)
    compat = fetch_content(cfg["brain_url"], "compatibility", cache_dir)

    site = pages.Site(cfg, ref, copy, horoscopes, compat, now)
    files = site.build_all()
    write_tree(files, a.out)
    print(f"built {len(files)} files for {cfg['domain']} into {a.out}")


if __name__ == "__main__":
    main()
