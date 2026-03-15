---
name: scrapling-web-fetch
description: 使用 Scrapling 抓取网页，Trafilatura 解析正文内容，适合抓取博客、新闻、网站、微信公众号文章及许多普通 web_fetch 不稳定、存在反爬或动态渲染干扰的网页。输出结构化内容适合大模型理解。
---

# Scrapling Web Fetch

当用户要获取网页内容、正文提取、把网页转成 markdown、抓取文章主体时，优先使用此技能。

## 用法

### 基础用法（Markdown 输出）
```bash
uv run scripts/scrapling_fetch.py <url>
```

### 指定最大字符数
```bash
uv run scripts/scrapling_fetch.py <url> 10000
```

### JSON 结构化输出
```bash
uv run scripts/scrapling_fetch.py <url> 10000 --json
```

### 指定解析器
```bash
uv run scripts/scrapling_fetch.py <url> 10000 --parser auto
uv run scripts/scrapling_fetch.py <url> 10000 --parser scrapling
uv run scripts/scrapling_fetch.py <url> 10000 --parser trafilatura
```

## 输出格式

### Markdown 模式（默认）
```markdown
# 文章标题

> URL: https://example.com
> 最终URL: https://example.com/article
> 内容长度: 5000 字符
> 质量评分: 15
> 抓取模式: stealth
> 解析器: trafilatura
> 耗时: 抓取 4.89s + 解析 0.67s = 总计 5.56s

---

正文内容...
```

### JSON 模式
```json
{
  "ok": true,
  "url": "https://example.com",
  "final_url": "https://example.com/article",
  "title": "文章标题",
  "content_length": 5000,
  "quality_score": 15,
  "fetch_mode": "stealth",
  "parser": "trafilatura",
  "fetch_duration": 4.89,
  "parse_duration": 0.67,
  "total_duration": 5.56,
  "content": "正文内容..."
}
```

## 命令行参数

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `url` | 要抓取的 URL | 必填 |
| `max_chars` | 最大输出字符数 | 10000 |
| `--json` | JSON 结构化输出 | false |
| `--parser` | 解析器选择 | auto |

## 解析器选项

| 选项 | 说明 |
|------|------|
| `auto` | 默认，优先 Trafilatura，失败时降级到 Scrapling |
| `trafilatura` | 仅使用 Trafilatura 本地解析 |
| `scrapling` | 仅使用 Scrapling 原生解析 |

## 内容解析策略

系统使用两级解析策略：

1. **Trafilatura**（主要）：智能正文识别，噪音清理更好
2. **Scrapling**（降级）：原生 `get_all_text()` 方法，当 Trafilatura 失败时自动降级

## 依赖

优先检查：
- `scrapling` - 网页抓取
- `trafilatura` - 内容解析

若缺失，可安装：
```bash
uv pip install scrapling trafilatura
```

## 项目结构

```
scripts/
├── scrapling_fetch.py    # 主入口脚本
├── fetcher/              # 抓取模块
│   └── scrapling_fetcher.py
├── parsers/              # 解析模块
│   ├── base.py           # 解析器基类
│   ├── trafilatura_parser.py
│   ├── scrapling_parser.py
│   └── manager.py
└── output/               # 输出模块
    └── formatters.py
```

## 何时用这个技能
- 获取文章正文
- 抓博客/新闻/公告正文
- 将网页转成 Markdown 供后续总结
- 常规 web_fetch 效果差，希望提升现代网页抓取稳定性
- 需要绕过 Cloudflare 等反爬机制

## 何时不用
- 需要完整浏览器交互、点击、登录、翻页时：改用浏览器自动化
- 只是简单获取 API JSON：直接请求 API 更合适
