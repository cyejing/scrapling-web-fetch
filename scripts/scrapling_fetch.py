#!/usr/bin/env python3
"""
Cloudflare-bypassing web fetcher built on Scrapling, with urllib fallback.

Usage:
  uv run scrapling_fetch.py <url> [max_chars] [options]

Options:
  --json              Output as JSON
  --batch FILE        Read URLs from file (one per line)
  --text-only         Strip HTML tags, return plain text
  --selector CSS      Target a specific CSS element

Exit codes:
  0  Success
  1  No URL provided or argument error
  2  Dependency import failed
  3  Fetch failed

Examples:
  uv run scrapling_fetch.py "https://example.com" 10000
  uv run scrapling_fetch.py "https://example.com" 10000 --json
  uv run scrapling_fetch.py --batch urls.txt 20000 --json
  uv run scrapling_fetch.py "https://example.com" --selector "article" --text-only
"""

import argparse
import json
import re
import sys
import urllib.request
from pathlib import Path
from urllib.parse import urlparse

DEFAULT_SELECTORS = [
    'article',
    'main',
    '.post-content',
    '[class*="body"]',
    'body',
]

SITE_CONFIGS = {
    'mp.weixin.qq.com': {
        'selectors': ['#js_article', '#js_content'] + DEFAULT_SELECTORS,
        'noise_patterns': [
            r'预览时标签不可点.*',
            r'Scan to Follow.*',
            r'继续滑动看下一个.*',
            r'轻触阅读原文.*',
            r'微信扫一扫可打开此内容.*',
            r'使用完整服务.*',
            r'Scan with Weixin to.*',
            r'use this Mini Program.*',
            r'Video Mini Program Like.*',
            r'轻点两下取消赞.*',
            r'轻点两下取消在看.*',
            r'Share Comment Favorite.*',
            r'哎咆科技.*向上滑动看下一个.*',
            r'\[Got It\].*',
            r'\[Cancel\].*\[Allow\].*',
            r'× 分析.*',
            r'!\[跳转二维码\]\(\)',
            r'!\[作者头像\]\([^\)]*\)',
            r'!\[Image\].*',
            r'!\[cover_image\].*',
            r'在小说阅读器中沉浸阅读.*',
            r'^_\d{4}年\d{1,2}月\d{1,2}日.*_$',
            r'^_.*_$',
            r'\[javascript:void\(0\);?\]',
            r'\[.*\]\(javascript:.*\)',
            r'!\[.*\]\(data:image.*\)',
            r'!\[.*\]\(.*svg.*\)',
        ],
        'truncate_markers': [
            '预览时标签不可点',
            'Scan to Follow',
            '继续滑动看下一个',
            '轻触阅读原文',
            '微信扫一扫可打开此内容',
            'Scan with Weixin to',
            'use this Mini Program',
            '× 分析',
        ],
    },
    'www.sohu.com': {
        'selectors': ['article'] + DEFAULT_SELECTORS,
        'noise_patterns': [
            r'推荐阅读.*',
            r'相关阅读.*',
            r'搜狐号.*',
            r'小编推荐.*',
            r'返回搜狐.*',
            r'查看更多.*',
            r'热点推荐.*',
            r'猜你喜欢.*',
            r'\[广告\].*',
        ],
        'truncate_markers': [
            '推荐阅读',
            '相关阅读',
            '返回搜狐',
            '小编推荐',
        ],
    },
    'news.sohu.com': {
        'selectors': ['article'] + DEFAULT_SELECTORS,
        'noise_patterns': [
            r'推荐阅读.*',
            r'相关阅读.*',
            r'搜狐号.*',
            r'小编推荐.*',
            r'返回搜狐.*',
            r'查看更多.*',
            r'热点推荐.*',
            r'猜你喜欢.*',
            r'\[广告\].*',
        ],
        'truncate_markers': [
            '推荐阅读',
            '相关阅读',
            '返回搜狐',
            '小编推荐',
        ],
    },
    'www.163.com': {
        'selectors': ['.post_body'] + DEFAULT_SELECTORS,
        'noise_patterns': [
            r'网易新闻.*',
            r'责任编辑.*',
            r'本文来源.*',
            r'更多精彩.*',
            r'扫码下载.*',
            r'打开网易新闻.*',
            r'\[广告\].*',
            r'热点推荐.*',
        ],
        'truncate_markers': [
            '责任编辑',
            '本文来源',
            '更多精彩',
            '打开网易新闻',
        ],
    },
    'news.163.com': {
        'selectors': ['.post_body'] + DEFAULT_SELECTORS,
        'noise_patterns': [
            r'网易新闻.*',
            r'责任编辑.*',
            r'本文来源.*',
            r'更多精彩.*',
            r'扫码下载.*',
            r'打开网易新闻.*',
            r'\[广告\].*',
            r'热点推荐.*',
        ],
        'truncate_markers': [
            '责任编辑',
            '本文来源',
            '更多精彩',
            '打开网易新闻',
        ],
    },
    'www.sina.com.cn': {
        'selectors': ['article'] + DEFAULT_SELECTORS,
        'noise_patterns': [
            r'新浪新闻.*',
            r'责任编辑.*',
            r'本文来源.*',
            r'更多精彩.*',
            r'扫码下载.*',
            r'新浪客户端.*',
            r'\[广告\].*',
            r'热点推荐.*',
            r'相关新闻.*',
        ],
        'truncate_markers': [
            '责任编辑',
            '本文来源',
            '更多精彩',
            '新浪客户端',
        ],
    },
    'news.sina.com.cn': {
        'selectors': ['article'] + DEFAULT_SELECTORS,
        'noise_patterns': [
            r'新浪新闻.*',
            r'责任编辑.*',
            r'本文来源.*',
            r'更多精彩.*',
            r'扫码下载.*',
            r'新浪客户端.*',
            r'\[广告\].*',
            r'热点推荐.*',
            r'相关新闻.*',
        ],
        'truncate_markers': [
            '责任编辑',
            '本文来源',
            '更多精彩',
            '新浪客户端',
        ],
    },
    'www.toutiao.com': {
        'selectors': ['article'] + DEFAULT_SELECTORS,
        'noise_patterns': [
            r'今日头条.*',
            r'下载客户端.*',
            r'扫码下载.*',
            r'更多精彩.*',
            r'相关推荐.*',
            r'猜你喜欢.*',
            r'\[广告\].*',
            r'热点推荐.*',
        ],
        'truncate_markers': [
            '下载客户端',
            '更多精彩',
            '相关推荐',
        ],
    },
    'www.thepaper.cn': {
        'selectors': ['.news_txt'] + DEFAULT_SELECTORS,
        'noise_patterns': [
            r'澎湃新闻.*',
            r'责任编辑.*',
            r'扫码下载.*',
            r'澎湃客户端.*',
            r'更多精彩.*',
            r'\[广告\].*',
        ],
        'truncate_markers': [
            '责任编辑',
            '澎湃客户端',
            '更多精彩',
        ],
    },
    'www.guancha.cn': {
        'selectors': ['.content'] + DEFAULT_SELECTORS,
        'noise_patterns': [
            r'观察者网.*',
            r'责任编辑.*',
            r'扫码下载.*',
            r'更多精彩.*',
            r'\[广告\].*',
        ],
        'truncate_markers': [
            '责任编辑',
            '更多精彩',
        ],
    },
    'www.cctv.com': {
        'selectors': ['.content_area'] + DEFAULT_SELECTORS,
        'noise_patterns': [
            r'央视网.*',
            r'责任编辑.*',
            r'本文来源.*',
            r'更多精彩.*',
            r'\[广告\].*',
        ],
        'truncate_markers': [
            '责任编辑',
            '本文来源',
        ],
    },
    'news.cctv.com': {
        'selectors': ['.content_area'] + DEFAULT_SELECTORS,
        'noise_patterns': [
            r'央视网.*',
            r'责任编辑.*',
            r'本文来源.*',
            r'更多精彩.*',
            r'\[广告\].*',
        ],
        'truncate_markers': [
            '责任编辑',
            '本文来源',
        ],
    },
    'www.people.com.cn': {
        'selectors': ['.box_con'] + DEFAULT_SELECTORS,
        'noise_patterns': [
            r'人民网.*',
            r'责任编辑.*',
            r'本文来源.*',
            r'更多精彩.*',
            r'\[广告\].*',
        ],
        'truncate_markers': [
            '责任编辑',
            '本文来源',
        ],
    },
    'news.people.com.cn': {
        'selectors': ['.box_con'] + DEFAULT_SELECTORS,
        'noise_patterns': [
            r'人民网.*',
            r'责任编辑.*',
            r'本文来源.*',
            r'更多精彩.*',
            r'\[广告\].*',
        ],
        'truncate_markers': [
            '责任编辑',
            '本文来源',
        ],
    },
    'www.xinhuanet.com': {
        'selectors': ['.article'] + DEFAULT_SELECTORS,
        'noise_patterns': [
            r'新华网.*',
            r'责任编辑.*',
            r'本文来源.*',
            r'更多精彩.*',
            r'\[广告\].*',
        ],
        'truncate_markers': [
            '责任编辑',
            '本文来源',
        ],
    },
    'www.news.cn': {
        'selectors': ['.article'] + DEFAULT_SELECTORS,
        'noise_patterns': [
            r'新华网.*',
            r'责任编辑.*',
            r'本文来源.*',
            r'更多精彩.*',
            r'\[广告\].*',
        ],
        'truncate_markers': [
            '责任编辑',
            '本文来源',
        ],
    },
    'www.chinanews.com': {
        'selectors': ['.content'] + DEFAULT_SELECTORS,
        'noise_patterns': [
            r'中国新闻网.*',
            r'责任编辑.*',
            r'本文来源.*',
            r'更多精彩.*',
            r'\[广告\].*',
        ],
        'truncate_markers': [
            '责任编辑',
            '本文来源',
        ],
    },
    'www.ifeng.com': {
        'selectors': ['.yc_con'] + DEFAULT_SELECTORS,
        'noise_patterns': [
            r'凤凰网.*',
            r'责任编辑.*',
            r'本文来源.*',
            r'更多精彩.*',
            r'扫码下载.*',
            r'凤凰客户端.*',
            r'\[广告\].*',
        ],
        'truncate_markers': [
            '责任编辑',
            '本文来源',
            '凤凰客户端',
        ],
    },
    'news.ifeng.com': {
        'selectors': ['.yc_con'] + DEFAULT_SELECTORS,
        'noise_patterns': [
            r'凤凰网.*',
            r'责任编辑.*',
            r'本文来源.*',
            r'更多精彩.*',
            r'扫码下载.*',
            r'凤凰客户端.*',
            r'\[广告\].*',
        ],
        'truncate_markers': [
            '责任编辑',
            '本文来源',
            '凤凰客户端',
        ],
    },
    'www.zhihu.com': {
        'selectors': ['.Post-RichText'] + DEFAULT_SELECTORS,
        'noise_patterns': [
            r'知乎.*',
            r'扫码下载.*',
            r'知乎App.*',
            r'\[广告\].*',
            r'相关推荐.*',
        ],
        'truncate_markers': [
            '扫码下载',
            '知乎App',
        ],
    },
    'zhuanlan.zhihu.com': {
        'selectors': ['.Post-RichText'] + DEFAULT_SELECTORS,
        'noise_patterns': [
            r'知乎.*',
            r'扫码下载.*',
            r'知乎App.*',
            r'\[广告\].*',
            r'相关推荐.*',
        ],
        'truncate_markers': [
            '扫码下载',
            '知乎App',
        ],
    },
    'www.bilibili.com': {
        'selectors': ['.article-content'] + DEFAULT_SELECTORS,
        'noise_patterns': [
            r'哔哩哔哩.*',
            r'扫码下载.*',
            r'B站客户端.*',
            r'\[广告\].*',
            r'相关推荐.*',
        ],
        'truncate_markers': [
            '扫码下载',
            'B站客户端',
        ],
    },
    'www.36kr.com': {
        'selectors': ['.article-content'] + DEFAULT_SELECTORS,
        'noise_patterns': [
            r'36氪.*',
            r'扫码下载.*',
            r'36氪App.*',
            r'\[广告\].*',
            r'相关推荐.*',
        ],
        'truncate_markers': [
            '扫码下载',
            '36氪App',
        ],
    },
    'www.huxiu.com': {
        'selectors': ['.article-content'] + DEFAULT_SELECTORS,
        'noise_patterns': [
            r'虎嗅.*',
            r'扫码下载.*',
            r'虎嗅App.*',
            r'\[广告\].*',
            r'相关推荐.*',
        ],
        'truncate_markers': [
            '扫码下载',
            '虎嗅App',
        ],
    },
}


def fail(msg, code=1, as_json=False):
    if as_json:
        print(json.dumps({'ok': False, 'error': msg}, ensure_ascii=False))
    else:
        print(f'[error] {msg}', file=sys.stderr)
    sys.exit(code)


def get_site_config(url):
    host = urlparse(url).hostname or ''
    return SITE_CONFIGS.get(host, {})


def get_selectors(url, custom_selector=None):
    if custom_selector:
        return [custom_selector]
    config = get_site_config(url)
    return config.get('selectors', DEFAULT_SELECTORS)


def score_markdown(md):
    text = md.strip()
    if not text:
        return 0
    score = 0
    score += min(len(text) // 500, 10)
    if '\n' in text:
        score += 2
    if '#' in text or '-' in text:
        score += 1
    if len(text.split()) > 80:
        score += 2
    return score


def clean_site_noise(markdown, url):
    config = get_site_config(url)
    patterns = config.get('noise_patterns', [])
    truncate_markers = config.get('truncate_markers', [])
    
    if not patterns and not truncate_markers:
        return markdown, False
    
    original = markdown
    
    for marker in truncate_markers:
        idx = markdown.find(marker)
        if idx != -1:
            markdown = markdown[:idx].rstrip()
            break
    
    lines = []
    for line in markdown.splitlines():
        stripped = line.strip()
        noisy = False
        for pattern in patterns:
            if re.search(pattern, stripped, re.IGNORECASE):
                noisy = True
                break
        if not noisy:
            lines.append(line)
    
    markdown = '\n'.join(lines)
    markdown = re.sub(r'\n{3,}', '\n\n', markdown).strip()
    return markdown, markdown != original


def fallback_fetch(url):
    try:
        req = urllib.request.Request(
            url,
            headers={"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"}
        )
        with urllib.request.urlopen(req, timeout=15) as r:
            return r.read().decode("utf-8", errors="replace"), "urllib"
    except Exception as e:
        raise RuntimeError(f"urllib fallback failed: {e}")


def scrapling_fetch(url, selectors, text_only=False):
    try:
        from scrapling.fetchers import StealthyFetcher
        page = StealthyFetcher.fetch(url, headless=True, network_idle=True)
        
        for selector in selectors:
            els = page.css(selector)
            if els:
                if text_only:
                    return "\n".join(el.text for el in els), page, selector, "stealth"
                return "\n".join(el.html_content for el in els), page, selector, "stealth"
        
        if text_only:
            return page.get_all_text(), page, None, "stealth"
        return page.html_content, page, None, "stealth"
    except ImportError:
        print("WARN: scrapling not installed — falling back to urllib", file=sys.stderr)
    except Exception as e:
        print(f"WARN: StealthyFetcher failed ({e}) — trying Fetcher", file=sys.stderr)
    
    try:
        from scrapling.fetchers import Fetcher
        page = Fetcher().get(url, stealthy_headers=True)
        
        for selector in selectors:
            els = page.css(selector)
            if els:
                if text_only:
                    return "\n".join(el.text for el in els), page, selector, "fetcher"
                return "\n".join(getattr(el, 'html', '') or str(el) for el in els), page, selector, "fetcher"
        
        if text_only:
            return page.get_all_text(), page, None, "fetcher"
        return page.html_content, page, None, "fetcher"
    except ImportError:
        print("WARN: scrapling not installed — falling back to urllib", file=sys.stderr)
    except Exception as e:
        print(f"WARN: Fetcher failed ({e}) — falling back to urllib", file=sys.stderr)
    
    html, mode = fallback_fetch(url)
    if text_only:
        text = re.sub(r"<[^>]+>", " ", html)
        text = re.sub(r"\s+", " ", text).strip()
        return text, None, "raw_html", mode
    return html, None, "raw_html", mode


def fetch_one(url, max_chars, as_json, custom_selector, text_only):
    parts = urlparse(url)
    if parts.scheme not in ('http', 'https'):
        return {'ok': False, 'url': url, 'error': 'url must start with http:// or https://'}

    selectors = get_selectors(url, custom_selector)
    

    html, page, used_selector, fetch_mode = scrapling_fetch(url, selectors, text_only)

    if text_only:
        markdown = html[:max_chars]
        title = getattr(page, 'title', None) or '' if page else ''
        final_url = getattr(page, 'url', None) or url if page else url
        quality = score_markdown(markdown)
        return {
            'ok': True,
            'url': url,
            'final_url': final_url,
            'title': title,
            'selector': used_selector,
            'content_length': len(markdown),
            'quality_score': quality,
            'fetch_mode': fetch_mode,
            'noise_cleaned': False,
            'content': markdown,
        }
    try:
        from html2text import HTML2Text
    except ImportError as e:
        fail(f'html2text import failed: {e}. install with: python3 -m pip install html2text', 2, as_json)
    
    h = HTML2Text()
    h.ignore_links = False
    h.ignore_images = False
    h.body_width = 0
    markdown = h.handle(html).strip()
    
    markdown, noise_cleaned = clean_site_noise(markdown, url)
    markdown = markdown[:max_chars]

    title = ''
    final_url = url
    if page:
        title = getattr(page, 'title', None) or ''
        final_url = getattr(page, 'url', None) or url

    quality = score_markdown(markdown)

    return {
        'ok': True,
        'url': url,
        'final_url': final_url,
        'title': title,
        'selector': used_selector,
        'content_length': len(markdown),
        'quality_score': quality,
        'fetch_mode': fetch_mode,
        'noise_cleaned': noise_cleaned,
        'content': markdown,
    }


def main():
    parser = argparse.ArgumentParser(
        description="Fetch a URL with Cloudflare bypass via Scrapling, urllib fallback. Supports WeChat article cleanup, markdown output, batch fetch."
    )
    parser.add_argument('url', nargs='?', help='URL to fetch')
    parser.add_argument('max_chars', nargs='?', type=int, default=10000, help='Max characters to output (default: 10000)')
    parser.add_argument('--json', action='store_true', help='Output as JSON')
    parser.add_argument('--batch', type=str, default=None, help='Read URLs from file (one per line)')
    parser.add_argument('--text-only', action='store_true', help='Return plain text (strips HTML)')
    parser.add_argument('--selector', type=str, default=None, help='CSS selector to target a specific element')
    
    args = parser.parse_args()
    
    urls = []
    if args.url:
        urls.append(args.url)
    if args.batch:
        batch_path = Path(args.batch)
        if batch_path.exists():
            urls.extend([line.strip() for line in batch_path.read_text(encoding='utf-8').splitlines() if line.strip()])
    
    if not urls:
        fail('no url provided', 1, args.json)

    results = []
    for url in urls:
        try:
            results.append(fetch_one(
                url, args.max_chars, args.json,
                args.selector, args.text_only
            ))
        except Exception as e:
            results.append({'ok': False, 'url': url, 'error': f'fetch failed: {e}'})

    if args.json or len(results) > 1:
        print(json.dumps(results if len(results) > 1 else results[0], ensure_ascii=False))
    else:
        result = results[0]
        if not result.get('ok'):
            fail(result.get('error', 'unknown error'), 3, False)
        print(f"[fetch_mode] {result['fetch_mode']}", file=sys.stderr)
        print(f"[selector] {result['selector']}", file=sys.stderr)
        if result.get('title'):
            print(f"[title] {result['title']}", file=sys.stderr)
        print(f"[quality] {result['quality_score']}", file=sys.stderr)
        if result.get('noise_cleaned'):
            print(f"[noise_cleaned] true", file=sys.stderr)
        print(result['content'])


if __name__ == '__main__':
    main()
