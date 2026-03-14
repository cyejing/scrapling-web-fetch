# Usage

## Basic
```bash
uv run scripts/scrapling_fetch.py <url> 10000
```

## JSON output
```bash
uv run scripts/scrapling_fetch.py <url> 10000 --json
```

## Batch mode
```bash
uv run scripts/scrapling_fetch.py --batch urls.txt 20000 --json
```

## Text only (strip HTML)
```bash
uv run scripts/scrapling_fetch.py <url> 10000 --text-only
```

## Raw HTML output
```bash
uv run scripts/scrapling_fetch.py <url> 10000 --html
```

## Custom CSS selector
```bash
uv run scripts/scrapling_fetch.py <url> 10000 --selector "article.content"
```

## Combined options
```bash
uv run scripts/scrapling_fetch.py <url> 5000 --selector "main" --text-only --json
```

## Fetch Modes

The script uses a three-tier fallback chain:

1. **stealth** - StealthyFetcher with Playwright (best for Cloudflare bypass)
2. **fetcher** - Basic Scrapling Fetcher with stealthy headers
3. **urllib** - Pure Python urllib fallback

Check the `[fetch_mode]` in stderr output to see which method was used.
