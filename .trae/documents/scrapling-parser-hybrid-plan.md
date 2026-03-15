# Scrapling Parser 混合方案实施计划

## 目标

实现混合解析方案：优先使用 Trafilatura，失败时降级到 Scrapling 原生 `get_all_text()`

## 实施步骤

### 1. 更新 TrafilaturaParser

修改 `parsers/trafilatura_parser.py`，添加降级逻辑：
- 优先使用 Trafilatura 提取正文
- 如果 Trafilatura 返回空或失败，降级到 Scrapling 原生 `get_all_text()`

### 2. 更新 ParserManager

修改 `parsers/manager.py`：
- 简化解析器管理逻辑
- 仅使用 TrafilaturaParser（内部已包含降级）

### 3. 更新输出格式

修改 `output/formatters.py`：
- 添加 `parser_fallback` 字段，标记是否使用了降级方案

### 4. 测试验证

测试微信公众号文章，验证混合方案效果

## 代码结构

```
scripts/
├── scrapling_fetch.py      # 主入口
├── fetcher/
│   └── scrapling_fetcher.py # 抓取模块
├── parsers/
│   ├── base.py             # 解析器基类
│   ├── trafilatura_parser.py # 混合解析器（Trafilatura + Scrapling 降级）
│   └── manager.py          # 解析器管理器
└── output/
    └── formatters.py       # 输出格式化
```

## 混合解析逻辑

```python
def parse(html, url):
    # 1. 尝试 Trafilatura
    text = trafilatura.extract(html, ...)
    
    # 2. 如果失败，降级到 Scrapling 原生
    if not text:
        from scrapling.parser import Selector
        page = Selector(html)
        text = page.get_all_text()
        parser_used = "scrapling_native"
    else:
        parser_used = "trafilatura"
    
    return ParseResult(content=text, parser_name=parser_used)
```
