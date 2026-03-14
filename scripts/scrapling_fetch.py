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

from site_configs import DEFAULT_SELECTORS, SITE_CONFIGS


def fail(msg, code=1, as_json=False):
    """输出错误信息并退出程序
    
    Args:
        msg: 错误信息
        code: 退出码，默认 1
        as_json: 是否以 JSON 格式输出
    """
    if as_json:
        print(json.dumps({'ok': False, 'error': msg}, ensure_ascii=False))
    else:
        print(f'[error] {msg}', file=sys.stderr)
    sys.exit(code)


def get_site_config(url):
    """根据 URL 获取网站的噪音处理配置
    
    Args:
        url: 目标 URL
        
    Returns:
        dict: 网站配置字典，包含 selectors、noise_patterns、truncate_markers
    """
    host = urlparse(url).hostname or ''
    return SITE_CONFIGS.get(host, {})


def get_selectors(url, custom_selector=None):
    """获取用于提取正文内容的 CSS 选择器列表
    
    Args:
        url: 目标 URL
        custom_selector: 自定义选择器，若提供则覆盖默认配置
        
    Returns:
        list: CSS 选择器列表
    """
    if custom_selector:
        return [custom_selector]
    config = get_site_config(url)
    return config.get('selectors', DEFAULT_SELECTORS)


def score_markdown(md):
    """评估 Markdown 内容的质量分数
    
    根据内容长度、结构特征等指标计算质量分数，用于判断抓取结果的有效性。
    分数范围 0-15，分数越高表示内容质量越好。
    
    评分规则：
    - 内容长度：每 500 字符加 1 分，最高 10 分
    - 换行符：有换行加 2 分（表示有段落结构）
    - Markdown 标记：有 # 或 - 加 1 分（表示有标题或列表）
    - 单词数量：超过 80 个单词加 2 分
    
    Args:
        md: Markdown 文本内容
        
    Returns:
        int: 质量分数，范围 0-15
    """
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
    """清理 Markdown 内容中的噪音
    
    根据网站配置执行两级噪音清理：
    1. 截断清理：遇到截断标记后删除后续所有内容
    2. 行过滤：删除匹配噪音模式的行
    
    Args:
        markdown: 原始 Markdown 内容
        url: 目标 URL，用于获取网站特定配置
        
    Returns:
        tuple: (清理后的内容, 是否执行了清理)
    """
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
    """使用 urllib 作为最后的回退方案抓取网页
    
    当 Scrapling 不可用或失败时，使用纯 Python 的 urllib 进行抓取。
    
    Args:
        url: 目标 URL
        
    Returns:
        tuple: (HTML 内容, 抓取模式名称)
        
    Raises:
        RuntimeError: 抓取失败时抛出
    """
    try:
        req = urllib.request.Request(
            url,
            headers={"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"}
        )
        with urllib.request.urlopen(req, timeout=15) as r:
            return r.read().decode("utf-8", errors="replace"), "urllib"
    except Exception as e:
        raise RuntimeError(f"urllib fallback failed: {e}")


STEALTHY_FETCHER_CONFIG = {
    'headless': True,           # 无头模式，隐藏浏览器窗口
    'network_idle': True,       # 等待网络空闲（500ms 内无请求）
    'disable_resources': True,  # 屏蔽图片、视频、字体、样式表等资源，加速加载
    'hide_canvas': True,        # 添加随机噪声防止 Canvas 指纹识别
    'block_webrtc': True,       # 阻止 WebRTC 泄露本地 IP
    'google_search': True,      # 设置 Google Referer 头，模拟从搜索进入
    'solve_cloudflare': True,   # 自动解决 Cloudflare 验证码
}

FETCHER_CONFIG = {
    'stealthy_headers': True,   # 使用真实浏览器请求头
}


def scrapling_fetch(url, selectors, text_only=False):
    """使用 Scrapling 抓取网页内容
    
    采用三级回退机制：
    1. StealthyFetcher：浏览器级隐身抓取，最佳反爬能力
    2. Fetcher：HTTP 级抓取，带隐蔽请求头
    3. urllib：纯 Python 回退方案
    
    Args:
        url: 目标 URL
        selectors: CSS 选择器列表，按优先级尝试
        text_only: 是否仅返回纯文本（不转换 Markdown）
        
    Returns:
        tuple: (内容, page对象, 使用的选择器, 抓取模式)
    """
    try:
        from scrapling.fetchers import StealthyFetcher
        page = StealthyFetcher.fetch(url, **STEALTHY_FETCHER_CONFIG)
        
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
        fetcher = Fetcher()
        page = fetcher.get(url, **FETCHER_CONFIG)
        
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
    """抓取单个 URL 并返回结构化结果
    
    执行完整的抓取流程：URL 验证 -> 抓取 -> HTML 转 Markdown -> 噪音清理 -> 结果封装
    
    Args:
        url: 目标 URL
        max_chars: 最大输出字符数
        as_json: 是否以 JSON 格式输出
        custom_selector: 自定义 CSS 选择器
        text_only: 是否仅返回纯文本
        
    Returns:
        dict: 抓取结果，包含 ok、url、title、content 等字段
    """
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
    """命令行入口函数
    
    解析命令行参数，执行抓取任务，输出结果。
    支持单个 URL 抓取和批量抓取。
    """
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
