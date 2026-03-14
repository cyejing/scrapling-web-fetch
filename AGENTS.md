# Scrapling News Boost 项目规则

## 项目概述

本项目是一个通用技能（Skill），用于使用 Scrapling 抓取国内主流新闻网页信息，提取主要文本内容，输出结构化内容供大模型理解。核心目标是清除噪音，只保留主要内容信息，减少大模型的 token 消耗。

## 项目结构

```
scrapling-news-boost/
├── SKILL.md              # 技能入口描述文件，供大模型理解技能用途和使用方法
├── scripts/
│   └── scrapling_fetch.py # 核心脚本：网页抓取与噪音处理
├── references/
│   └── usage.md          # 用法参考文档
├── site-test.md          # 测试网站列表（仅在明确要求全局测试时执行）
└── Agents.md             # 本文件：项目规则文档
```

## 核心脚本说明

### scrapling_fetch.py

主要逻辑流程：
1. **网页抓取**：使用 Scrapling 的三级回退机制
   - `StealthyFetcher`（stealth 模式）：最佳反爬绕过能力
   - `Fetcher`（fetcher 模式）：基础抓取，带隐蔽请求头
   - `urllib`（urllib 模式）：纯 Python 回退方案

2. **内容提取**：通过 CSS 选择器定位正文区域

3. **噪音去除**：多层级噪音清理策略

4. **输出格式化**：支持文本模式和 JSON 模式

## 噪音去除策略

### 三种噪音处理方式

1. **selectors（选择器）**
   - 用途：定位正文内容的 CSS 选择器列表
   - 优先级：按列表顺序依次尝试，使用第一个匹配成功的选择器
   - 示例：`['#js_content', 'article', 'main']`

2. **noise_patterns（噪音模式）**
   - 用途：正则表达式列表，匹配需要删除的噪音行
   - 匹配到的行会被完全移除
   - 示例：`[r'推荐阅读.*', r'责任编辑.*', r'\[广告\].*']`

3. **truncate_markers（截断标记）**
   - 用途：文本截断标记，遇到该标记后截断后续所有内容
   - 优先级高于 noise_patterns，先执行截断再执行行过滤
   - 示例：`['推荐阅读', '返回搜狐', '责任编辑']`

### 通用默认策略

对于未在 `SITE_CONFIGS` 中配置的网站，使用以下默认策略：

```python
DEFAULT_SELECTORS = [
    'article',
    'main',
    '.post-content',
    '[class*="body"]',
    'body',
]
```

默认不应用 noise_patterns 和 truncate_markers，仅依赖选择器定位正文。

### 已配置的网站

当前已为以下网站配置专门的噪音处理规则：

| 网站域名 | 主要选择器 | 特殊处理 |
|---------|-----------|---------|
| mp.weixin.qq.com | #js_article, #js_content | 微信公众号尾部噪音清理 |
| www.sohu.com / news.sohu.com | article | 搜狐推荐、广告清理 |
| www.163.com / news.163.com | .post_body | 网易新闻尾部清理 |
| www.sina.com.cn / news.sina.com.cn | article | 新浪新闻相关推荐清理 |
| www.toutiao.com | article | 今日头条客户端推广清理 |
| www.thepaper.cn | .news_txt | 澎湃新闻客户端推广清理 |
| www.guancha.cn | .content | 观察者网编辑信息清理 |
| www.cctv.com / news.cctv.com | .content_area | 央视网来源信息清理 |
| www.people.com.cn / news.people.com.cn | .box_con | 人民网编辑信息清理 |
| www.xinhuanet.com / www.news.cn | .article | 新华网编辑信息清理 |
| www.chinanews.com | .content | 中国新闻网编辑信息清理 |
| www.ifeng.com / news.ifeng.com | .yc_con | 凤凰网客户端推广清理 |
| www.zhihu.com / zhuanlan.zhihu.com | .Post-RichText | 知乎 App 推广清理 |
| www.bilibili.com | .article-content | B站客户端推广清理 |
| www.36kr.com | .article-content | 36氪 App 推广清理 |
| www.huxiu.com | .article-content | 虎嗅 App 推广清理 |

## 添加新网站配置

当需要为新网站添加专门配置时，在 `SITE_CONFIGS` 字典中添加：

```python
'example.com': {
    'selectors': ['.article-body', 'article'] + DEFAULT_SELECTORS,
    'noise_patterns': [
        r'相关推荐.*',
        r'广告.*',
    ],
    'truncate_markers': [
        '相关推荐',
        '热门评论',
    ],
},
```

## 测试规则

### 测试文件

`site-test.md` 包含测试网站列表和测试要求。

### 测试触发条件

- **仅在用户明确要求"全局测试"时执行** site-test.md 中的所有测试网站
- 单个网站测试可随时执行
- 测试过程中发现通用噪音去除不满足要求时，需针对特殊网站添加专门配置

### 测试输出要求

1. JSON 结构明确
2. 所有字段正确填充
3. content 内容仅包含正文，无 HTML 脚本、图片标签等噪音
4. 标题、作者、发布时间、正文内容完整准确

## 代码修改规范

### 噪音处理优化

如果发现更好的噪音去除方式，应先提出方案讨论，再进行实现。可能的优化方向：

1. **基于内容密度的正文提取**：分析文本密度自动定位正文区域
2. **基于机器学习的噪音识别**：训练模型识别噪音内容
3. **DOM 结构分析**：利用 HTML 结构特征识别正文
4. **视觉块分析**：模拟浏览器渲染，基于视觉特征提取正文

### 代码风格

- 保持与现有代码风格一致
- 新增网站配置应放在 `SITE_CONFIGS` 字典中
- 噪音模式使用正则表达式，注意转义特殊字符

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
| `max_chars` | 最大输出字符数 | 10000 |
| `--json` | JSON 结构化输出 | false |
| `--batch FILE` | 批量抓取 URL 文件 | - |
| `--text-only` | 仅返回纯文本 | false |
| `--selector CSS` | 指定 CSS 选择器（覆盖网站默认） | - |

## 依赖

- `scrapling`：核心抓取库
- `html2text`：HTML 转 Markdown

安装命令：
```bash
uv pip install scrapling html2text
```
