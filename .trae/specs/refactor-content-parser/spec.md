# 内容解析器重构 Spec

## Why

当前项目使用复杂的 `site_configs.py` 配置文件来处理不同网站的噪音清理，维护成本高且扩展性差。引入专业的网页内容提取工具 Jina Reader 和 Trafilatura，可以自动提取正文内容，无需手动维护网站配置，同时提供更准确的内容提取能力。

## What Changes

- **BREAKING**: 移除 `site_configs.py` 及所有网站特定配置
- **BREAKING**: 移除 CSS 选择器逻辑和噪音清理逻辑
- 引入 Jina Reader API 作为主要内容解析器
- 引入 Trafilatura 作为降级内容解析器
- 重构代码架构，实现清晰的分层设计
- 简化命令行参数，移除 `--batch`、`--text-only`、`--selector` 参数
- 输出格式改为 JSON 和 Markdown 两种模式

## Impact

- Affected specs: 网页内容抓取与解析能力
- Affected code: 
  - `scripts/scrapling_fetch.py` - 完全重构
  - `scripts/site_configs.py` - 删除
  - `SKILL.md` - 需要更新

## ADDED Requirements

### Requirement: 内容解析器抽象

系统 SHALL 提供统一的内容解析器接口，支持多种解析实现。

#### Scenario: 解析器接口定义
- **WHEN** 系统初始化内容解析器
- **THEN** 所有解析器实现统一的 `parse(html: str, url: str) -> ParseResult` 接口

### Requirement: Jina Reader 解析器

系统 SHALL 提供 Jina Reader 解析器实现，通过 Jina Reader API 提取网页正文。

#### Scenario: Jina Reader 成功解析
- **WHEN** 使用 Jina Reader 解析网页内容
- **AND** API 请求成功
- **THEN** 返回包含 title、content 的解析结果

#### Scenario: Jina Reader 限流失败
- **WHEN** Jina Reader API 返回限流错误（HTTP 429）
- **THEN** 自动降级到 Trafilatura 解析器

### Requirement: Trafilatura 解析器

系统 SHALL 提供 Trafilatura 解析器实现，作为本地降级方案。

#### Scenario: Trafilatura 解析
- **WHEN** 使用 Trafilatura 解析网页内容
- **THEN** 返回包含 title、content 的解析结果

### Requirement: 解析器降级策略

系统 SHALL 实现自动降级策略，确保内容解析的可靠性。

#### Scenario: 默认解析流程
- **WHEN** 用户未指定解析器
- **THEN** 默认使用 Jina Reader
- **AND** 如果 Jina Reader 失败（限流或错误），自动降级到 Trafilatura

### Requirement: 输出格式

系统 SHALL 支持 JSON 和 Markdown 两种输出格式。

#### Scenario: JSON 输出
- **WHEN** 用户指定 `--json` 参数
- **THEN** 输出包含 url、title、content、content_length、quality_score 的 JSON 结构

#### Scenario: Markdown 输出
- **WHEN** 用户未指定 `--json` 参数（默认）
- **THEN** 输出格式化的 Markdown 内容，包含元信息头部和正文内容

### Requirement: 命令行接口

系统 SHALL 提供简化的命令行接口。

#### Scenario: 基本用法
- **WHEN** 用户执行 `uv run scrapling_fetch.py <url> [max_chars]`
- **THEN** 抓取并解析网页内容，输出 Markdown 格式

#### Scenario: JSON 输出
- **WHEN** 用户执行 `uv run scrapling_fetch.py <url> [max_chars] --json`
- **THEN** 抓取并解析网页内容，输出 JSON 格式

## MODIFIED Requirements

### Requirement: 网页抓取流程

系统 SHALL 使用 Scrapling 进行网页抓取，然后将 HTML 传递给内容解析器。

#### Scenario: 抓取并解析
- **WHEN** 用户请求抓取 URL
- **THEN** 使用 Scrapling 获取 HTML
- **AND** 将 HTML 传递给内容解析器提取正文

## REMOVED Requirements

### Requirement: 网站特定配置

**Reason**: 使用专业内容提取工具后，不再需要手动维护网站配置

**Migration**: 删除 `scripts/site_configs.py`，移除所有选择器和噪音模式配置

### Requirement: CSS 选择器参数

**Reason**: 内容解析器自动提取正文，无需手动指定选择器

**Migration**: 移除 `--selector` 命令行参数

### Requirement: 批量抓取

**Reason**: 简化功能，专注于单 URL 抓取场景

**Migration**: 移除 `--batch` 命令行参数

### Requirement: 纯文本模式

**Reason**: 内容解析器输出已优化的 Markdown 格式，无需额外纯文本模式

**Migration**: 移除 `--text-only` 命令行参数

## 测试验证

### 基准测试 URL

使用 `https://mp.weixin.qq.com/s/FrWhkYKonLX3ZuD6nDhXpw` 作为基准测试 URL，基准结果保存在 `.trae/specs/refactor-content-parser/baseline_test.json`。

### 验证标准

1. 重构后脚本能成功抓取并解析该 URL
2. 正文内容提取质量与基准结果相当或更好
3. 标题提取功能正常工作（基准测试中标题为空，重构后应能正确提取）
4. 输出格式符合规范
