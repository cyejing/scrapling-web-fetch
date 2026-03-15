# Scrapling 原生 Parser 方案研究

## 研究结论

### Scrapling 原生 API 确实有文本提取功能

Scrapling 的 `Selector` 类和 `Response` 类提供以下文本提取方法：

| 方法 | 说明 |
|------|------|
| `page.text` | 获取元素的文本内容属性 |
| `page.get_all_text()` | 获取页面所有文本内容（递归提取） |
| `page.body` | 获取 body 元素的 bytes |

### 测试对比结果

**测试 URL**: `https://mp.weixin.qq.com/s/FrWhkYKonLX3ZuD6nDhXpw`

| 方案 | 文本长度 | 质量 |
|------|---------|------|
| Scrapling `get_all_text()` | 5615 字符 | 较好，但可能包含噪音 |
| Trafilatura | 5348 字符 | 更干净，噪音更少 |

### 结论

1. **Scrapling 原生 `get_all_text()` 可用**，但提取的文本可能包含更多噪音
2. **Trafilatura 更适合正文提取**，噪音清理更好，输出更干净
3. **建议保留 Trafilatura** 作为主要解析方案

## 可选方案

### 方案 A: 仅使用 Scrapling 原生 API

```python
from scrapling.fetchers import StealthyFetcher

page = StealthyFetcher.fetch(url, headless=True, network_idle=True)
text = page.get_all_text()  # 直接获取所有文本
```

**优点**:
- 无需额外依赖
- 代码更简洁

**缺点**:
- 噪音较多，可能包含导航、广告等无关内容
- 无智能正文识别

### 方案 B: 仅使用 Trafilatura（当前方案）

```python
from scrapling.fetchers import StealthyFetcher
import trafilatura

page = StealthyFetcher.fetch(url, headless=True, network_idle=True)
text = trafilatura.extract(page.html_content, output_format='markdown')
```

**优点**:
- 智能正文识别
- 噪音清理更好
- 输出更干净

**缺点**:
- 需要额外依赖

### 方案 C: 混合方案（推荐）

```python
from scrapling.fetchers import StealthyFetcher
import trafilatura

page = StealthyFetcher.fetch(url, headless=True, network_idle=True)

# 优先使用 Trafilatura
text = trafilatura.extract(page.html_content, output_format='markdown')

# 如果 Trafilatura 失败，降级到 Scrapling 原生
if not text:
    text = page.get_all_text()
```

**优点**:
- 结合两者优点
- 更高的成功率

**缺点**:
- 代码稍复杂

## 建议

**保持当前 Trafilatura 方案**，原因：
1. 正文提取质量更高
2. 噪音清理更好
3. 输出更适合大模型理解
4. 当前实现已经稳定工作

如果需要简化依赖，可以考虑：
- 移除 Trafilatura，仅使用 Scrapling 原生 `get_all_text()`
- 但需要接受正文质量可能下降的代价
