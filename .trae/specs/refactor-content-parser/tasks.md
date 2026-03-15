# Tasks

- [x] Task 1: 设计并实现内容解析器抽象层
  - [x] SubTask 1.1: 创建 `parsers/base.py` 定义解析器基类和结果类型
  - [x] SubTask 1.2: 定义 `ParseResult` 数据类，包含 url、title、content 字段

- [x] Task 2: 实现 Jina Reader 解析器
  - [x] SubTask 2.1: 创建 `parsers/jina_reader.py` 实现 Jina Reader API 调用
  - [x] SubTask 2.2: 实现限流检测和错误处理逻辑
  - [x] SubTask 2.3: 解析 Jina Reader 返回的 Markdown 内容

- [x] Task 3: 实现 Trafilatura 解析器
  - [x] SubTask 3.1: 创建 `parsers/trafilatura_parser.py` 实现本地解析
  - [x] SubTask 3.2: 配置 Trafilatura 提取参数以优化输出质量

- [x] Task 4: 实现解析器管理器
  - [x] SubTask 4.1: 创建 `parsers/manager.py` 实现解析器选择和降级逻辑
  - [x] SubTask 4.2: 实现默认降级策略（Jina Reader -> Trafilatura）

- [x] Task 5: 重构网页抓取模块
  - [x] SubTask 5.1: 创建 `fetcher/scrapling_fetcher.py` 封装 Scrapling 抓取逻辑
  - [x] SubTask 5.2: 简化抓取配置，移除选择器相关逻辑
  - [x] SubTask 5.3: 保留三级回退机制（StealthyFetcher -> Fetcher -> urllib）

- [x] Task 6: 实现输出格式化模块
  - [x] SubTask 6.1: 创建 `output/formatters.py` 实现 JSON 和 Markdown 格式化
  - [x] SubTask 6.2: 实现 `quality_score` 计算逻辑
  - [x] SubTask 6.3: 设计利于大模型理解的 Markdown 输出格式

- [x] Task 7: 重构主入口脚本
  - [x] SubTask 7.1: 简化命令行参数解析
  - [x] SubTask 7.2: 整合抓取、解析、输出流程
  - [x] SubTask 7.3: 移除 site_configs 依赖

- [x] Task 8: 清理旧代码
  - [x] SubTask 8.1: 删除 `scripts/site_configs.py`
  - [x] SubTask 8.2: 更新 `SKILL.md` 文档

- [x] Task 9: 测试对比验证
  - [x] SubTask 9.1: 使用重构后的脚本测试基准 URL `https://mp.weixin.qq.com/s/FrWhkYKonLX3ZuD6nDhXpw`
  - [x] SubTask 9.2: 对比重构前后输出结果，验证内容提取质量
  - [x] SubTask 9.3: 记录对比结果，确保重构效果达标

# Task Dependencies

- [Task 2] depends on [Task 1]
- [Task 3] depends on [Task 1]
- [Task 4] depends on [Task 2, Task 3]
- [Task 6] depends on [Task 1]
- [Task 7] depends on [Task 4, Task 5, Task 6]
- [Task 8] depends on [Task 7]
