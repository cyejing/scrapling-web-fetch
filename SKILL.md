---
name: scrapling-web-fetch
description: 使用 Scrapling 获取现代网页正文内容，适合抓取博客、新闻、网站、微信公众号文章及许多普通 web_fetch 不稳定、存在反爬或动态渲染干扰的网页。支持噪音清洗，结构化输出适合大模型理解。
---

# Scrapling Web Fetch

当用户要获取网页内容、正文提取、把网页转成 markdown/text、抓取文章主体时，优先使用此技能。

## 用法

### 基础用法
```bash
uv run scripts/scrapling_fetch.py <url> 10000
```

### JSON 结构化输出
```bash
uv run scripts/scrapling_fetch.py <url> 10000 --json
```

### 批量抓取
```bash
uv run scrapling_fetch.py --batch urls.txt 20000 --json
```

### 自定义选择器
```bash
uv run scrapling_fetch.py <url> --selector "article" --text-only
```

### 纯文本输出
```bash
uv run scrapling_fetch.py <url> 10000 --text-only
```

## 输出格式

### 文本模式（默认）
```
[fetch_mode] stealth
[selector] #js_content
[title] 文章标题
[quality] 15
[noise_cleaned] true
正文内容...
```

### JSON 模式
```json
{
  "ok": true,
  "url": "https://example.com",
  "final_url": "https://example.com/article",
  "title": "文章标题",
  "selector": "#js_content",
  "content_length": 5000,
  "quality_score": 15,
  "fetch_mode": "stealth",
  "noise_cleaned": true,
  "content": "正文内容..."
}
```

## 命令行参数

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `url` | 要抓取的 URL | 必填 |
| `max_chars` | 最大输出字符数 | 30000 |
| `--json` | JSON 结构化输出 | false |
| `--batch FILE` | 批量抓取 URL 文件 | - |
| `--text-only` | 仅返回纯文本 | false |
| `--selector CSS` | 指定 CSS 选择器（覆盖网站默认） | - |

## 依赖

优先检查：
- `scrapling`
- `html2text`

若缺失，可安装：
```bash
uv pip install scrapling html2text
```

## 附加资源
- 用法参考：`references/usage.md`
- 网站配置：`scripts/site_configs.py`
- 统一入口：`scripts/scrapling_fetch.py`

## 何时用这个技能
- 获取文章正文
- 抓博客/新闻/公告正文
- 将网页转成 Markdown 供后续总结
- 常规 web_fetch 效果差，希望提升现代网页抓取稳定性
- 需要绕过 Cloudflare 等反爬机制
- 需要清理国内媒体网站噪音

## 何时不用
- 需要完整浏览器交互、点击、登录、翻页时：改用浏览器自动化
- 只是简单获取 API JSON：直接请求 API 更合适
