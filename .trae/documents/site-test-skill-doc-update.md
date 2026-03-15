# 更新 site-test SKILL.md 命令参数文档

## 任务目标

1. 更新 `scripts/site_test.py` 代码，修改 `save-result` 命令参数
2. 更新 `.trae/skills/site-test/SKILL.md` 文档，完善三个命令的参数说明

## 实施步骤

### 步骤 1：修改 site\_test.py

修改 `save-result` 命令参数，所有参数改为必填，新增 `--suggestion` 参数：

| 参数                 | 说明                                   |
| ------------------ | ------------------------------------ |
| `--id`             | 用例编号（必填）                             |
| `--status`         | 状态：passed/failed/timeout/pending（必填） |
| `--score`          | 质量评分 0-100（必填）                       |
| `--comment`        | 质量评价（必填）                             |
| `--fetch-mode`     | 抓取模式（必填）                             |
| `--parser`         | 解析器（必填）                              |
| `--content-length` | 文本长度（必填）                             |
| `--total-duration` | 总耗时（必填）                              |
| `--title`          | 文章标题（必填）                             |
| `--suggestion`     | 优化建议（必填）                             |

更新输出文件模板，包含所有字段。

### 步骤 2：更新 SKILL.md 文档

添加三个命令的参数表格：

#### fetch 命令参数表

| 参数      | 必填 | 说明               |
| ------- | -- | ---------------- |
| `--id`  | 否  | 指定测试用例编号，多个用逗号分隔 |
| `--all` | 否  | 测试所有用例，包括已通过的    |

#### save-result 命令参数表

| 参数                 | 必填 | 说明                               |
| ------------------ | -- | -------------------------------- |
| `--id`             | 是  | 用例编号                             |
| `--status`         | 是  | 状态：passed/failed/timeout/pending |
| `--score`          | 是  | 质量评分（0-100）                      |
| `--comment`        | 是  | 质量评价                             |
| `--fetch-mode`     | 是  | 抓取模式：stealth/fetcher/urllib      |
| `--parser`         | 是  | 解析器：trafilatura/scrapling        |
| `--content-length` | 是  | 文本长度                             |
| `--total-duration` | 是  | 总耗时（秒）                           |
| `--title`          | 是  | 文章标题                             |
| `--suggestion`     | 是  | 优化建议                             |

#### update-case 命令参数表

| 参数          | 必填 | 说明                               |
| ----------- | -- | -------------------------------- |
| `--id`      | 是  | 用例编号                             |
| `--status`  | 是  | 状态：passed/failed/timeout/pending |
| `--score`   | 是  | 质量评分（0-100）                      |
| `--comment` | 是  | 质量评价                             |

### 步骤 3：更新示例命令

更新 `save-result` 命令示例，展示完整参数用法。

## 文件修改清单

1. `/Users/chenyejing/aiproject/scrapling-news-boost/scripts/site_test.py`

   * 修改 `save_parser` 参数定义，全部改为必填

   * 添加 `--total-duration`、`--title`、`--suggestion` 参数

   * 更新 `cmd_save_result` 函数输出模板

2. `/Users/chenyejing/aiproject/scrapling-news-boost/.trae/skills/site-test/SKILL.md`

   * 添加三个命令的参数表格

   * 更新示例命令

