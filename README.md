# Jade Astrology website

Only the website lives here: pages, styles, scripts, images and data. No keys, no deploy scripts.

Each droplet pulls this repo when it is created and again every hour, then builds the pages with
`python3 build.py --config site.json --out <folder>`. Push a change here and every site has it within the hour.

Preview on your Mac:

```
echo '{"domain":"localhost","site_id":"localhost","brain_url":"test"}' > /tmp/site.json
python3 build.py --config /tmp/site.json --out /tmp/jade-preview
cd /tmp/jade-preview && python3 -m http.server 8000
```

Then open http://localhost:8000. `/blog` is left free for WordPress.
