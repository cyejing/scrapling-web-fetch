# Parser 重构计划

## 问题分析

1. **当前实现问题**：TrafilaturaParser 内部混合了两种解析逻辑，职责不清晰
2. **url 参数无用**：parse 方法的 url 参数未被使用，应该移除

## 重构方案

### 1. 抽取独立的 ScraplingNativeParser

创建 `parsers/scrapling_native.py`：
- 独立实现 Scrapling 原生 `get_all_text()` 解析
- 实现 ContentParser 接口

### 2. 简化 TrafilaturaParser

修改 `parsers/trafilatura_parser.py`：
- 只负责 Trafilatura 解析
- 移除内部降级逻辑

### 3. 在 ParserManager 中实现降级逻辑

修改 `parsers/manager.py`：
- 支持参数选择 parser：`auto`、`trafilatura`、`scrapling_native`
- `auto` 模式：优先 Trafilatura，失败降级到 ScraplingNative

### 4. 移除无用的 url 参数

修改所有相关文件：
- `base.py`: `parse(html: str) -> ParseResult`
- `trafilatura_parser.py`: 移除 url 参数
- `scrapling_native.py`: 不需要 url 参数
- `manager.py`: 移除 url 参数
- `scrapling_fetch.py`: 调用时移除 url 参数

## 代码结构

```
parsers/
├── __init__.py
├── base.py              # ParseResult, ContentParser（移除 url 参数）
├── trafilatura_parser.py # Trafilatura 解析器（纯 Trafilatura）
├── scrapling_native.py  # Scrapling 原生解析器（新增）
└── manager.py           # 解析器管理器（降级逻辑）
```

## 接口设计

```python
# base.py
class ContentParser(ABC):
    @abstractmethod
    def parse(self, html: str) -> ParseResult:  # 移除 url 参数
        pass

# manager.py
class ParserManager:
    def parse(self, html: str, parser: str = "auto") -> ParseResult:
        """
        parser 选项：
        - auto: 优先 Trafilatura，失败降级 ScraplingNative
        - trafilatura: 仅使用 Trafilatura
        - scrapling_native: 仅使用 ScraplingNative
        """
```

## 实施步骤

1. 创建 `scrapling_native.py` 实现 ScraplingNativeParser
2. 简化 `trafilatura_parser.py`，移除降级逻辑和 url 参数
3. 更新 `base.py`，移除 url 参数
4. 更新 `manager.py`，实现降级逻辑和 parser 参数
5. 更新 `__init__.py`，导出新的类
6. 更新 `scrapling_fetch.py`，移除 url 参数，添加 --parser 参数
