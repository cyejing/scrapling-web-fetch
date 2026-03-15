# Checklist

## 架构设计

- [x] 解析器抽象层设计清晰，接口定义简洁
- [x] 代码分层合理：fetcher -> parser -> output
- [x] 模块职责单一，易于理解和维护

## 功能实现

- [x] Jina Reader 解析器正确调用 API 并解析响应
- [x] Trafilatura 解析器正确提取网页正文
- [x] 降级策略正确实现：Jina Reader 限流时自动切换 Trafilatura
- [x] Scrapling 抓取保留三级回退机制

## 输出格式

- [x] JSON 输出包含 url、title、content、content_length、quality_score 字段
- [x] Markdown 输出格式清晰，利于大模型理解
- [x] quality_score 计算逻辑合理

## 命令行接口

- [x] 支持 `url` 位置参数
- [x] 支持 `max_chars` 可选参数（默认 10000）
- [x] 支持 `--json` 标志参数
- [x] 移除 `--batch`、`--text-only`、`--selector` 参数

## 代码清理

- [x] 删除 `scripts/site_configs.py`
- [x] 更新 `SKILL.md` 文档反映新用法
- [x] 无遗留的死代码或未使用的导入

## 依赖管理

- [x] 添加 `trafilatura` 到项目依赖
- [x] `scrapling` 依赖保留
- [x] 移除 `html2text` 依赖（如不再需要）

## 测试对比

- [x] 重构后脚本能成功抓取基准测试 URL
- [x] 重构后输出内容与基准结果对比，正文提取质量相当或更好
- [x] 标题提取功能正常工作（基准测试中标题为空，重构后应能正确提取）
- [x] 输出格式符合规范（JSON 和 Markdown 两种模式）
