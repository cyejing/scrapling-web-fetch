# 前 5 条网站测试计划

## 测试目标

针对 site-test.md 中前 5 条网站进行抓取测试，验证 `scrapling_fetch.py` 的抓取能力和噪音清理效果。

## 测试列表

| 编号 | 网站域名 | URL |
|------|----------|-----|
| 01 | mp.weixin.qq.com | https://mp.weixin.qq.com/s/FrWhkYKonLX3ZuD6nDhXpw |
| 02 | finance.sina.com.cn | https://finance.sina.com.cn/roll/2025-09-19/doc-infrchxs4006271.shtml |
| 04 | xueqiu.com | https://xueqiu.com/S/TSLA |
| 05 | www.msn.cn | https://www.msn.cn/zh-cn/news/other/李连杰竟成-陌路人-吴京谢霆锋成最后一代功夫巨星-江湖谁来接棒/ar-AA1YB1E3 |
| 06 | www.sohu.com | https://www.sohu.com/a/996235269_121608032 |

## 实施步骤

### 步骤 1：创建输出目录
- 创建 `output/` 目录用于保存测试结果

### 步骤 2：执行抓取测试
- 依次对 5 个 URL 执行 `scrapling_fetch.py` 脚本
- 使用 `--json` 参数获取结构化输出
- 设置 `max_chars` 为 10000（默认值）

### 步骤 3：保存测试结果
- 每个测试结果保存为 `output/{编号}_{域名}.md`
- 文件内容包括：
  - 测试元信息（编号、URL、状态、选择器等）
  - 完整的抓取内容

### 步骤 4：生成测试报告
- 汇总所有测试结果
- 生成测试报告表格，包含：
  - 编号、原始 URL、抓取状态、选择器、文本长度、噪音清理、质量评分
- 评估噪音清理效果，必要时提出优化建议

## 测试命令

```bash
cd /Users/chenyejing/aiproject/scrapling-news-boost/scripts

# 测试 01: 微信公众号
uv run scrapling_fetch.py "https://mp.weixin.qq.com/s/FrWhkYKonLX3ZuD6nDhXpw" 10000 --json

# 测试 02: 新浪财经
uv run scrapling_fetch.py "https://finance.sina.com.cn/roll/2025-09-19/doc-infrchxs4006271.shtml" 10000 --json

# 测试 04: 雪球
uv run scrapling_fetch.py "https://xueqiu.com/S/TSLA" 10000 --json

# 测试 05: MSN
uv run scrapling_fetch.py "https://www.msn.cn/zh-cn/news/other/李连杰竟成-陌路人-吴京谢霆锋成最后一代功夫巨星-江湖谁来接棒/ar-AA1YB1E3" 10000 --json

# 测试 06: 搜狐
uv run scrapling_fetch.py "https://www.sohu.com/a/996235269_121608032" 10000 --json
```

## 预期输出

1. 5 个测试结果文件保存在 `output/` 目录
2. 测试报告汇总表格
3. 如发现噪音清理问题，提出针对性优化建议
