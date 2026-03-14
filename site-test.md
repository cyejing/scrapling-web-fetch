# 网页抓取测试文档

## 测试目标

验证 `scrapling_fetch.py` 脚本对各主流新闻网站的抓取能力，确保：
- 文章内容包含标题、正文内容
- 结果输出准确，避免缺失或错误信息
- 结构化内容输出，便于大模型理解
- 清除无用噪音，减少 token 消耗
- 绕过网站反爬机制，避免被封 IP

## 测试要求

- 测试过程中，如果通用噪音去除方式不能满足要求，需针对特殊网站添加专门的噪音处理配置
- 仅在用户明确要求"全局测试"时执行全部测试列表

## 测试结果保存

- 测试结果保存在 `output/` 目录下
- 文件命名格式：`{编号}_{域名}.json`（如 `01_mp.weixin.qq.com.json`）
- 对比测试时，根据编号和域名查找上一次测试结果

## 测试输出格式

### JSON 输出示例

```json
{
    "ok": true,
    "url": "https://mp.weixin.qq.com/s/xxxxx",
    "final_url": "https://mp.weixin.qq.com/s/xxxxx",
    "title": "文章标题",
    "selector": "#js_article",
    "content_length": 5427,
    "quality_score": 15,
    "fetch_mode": "stealth",
    "noise_cleaned": true,
    "content": "正文内容..."
}
```

### 测试报告表格

| 编号 | 原始 URL | 抓取状态 | 选择器 | 文本长度 | 噪音清理 | 质量评分 | 变化 | 优化质量 |
|------|----------|----------|--------|----------|----------|----------|------------|----------------|
| 01 | https://... | 成功/失败 | #js_content | 5000 | 是/否 | 0-100 | 是/否 | -10 |


**质量评分标准（0-100分）：**
- 90-100：内容完整，噪音清除干净
- 70-89：内容基本完整，有少量噪音
- 50-69：内容有缺失或噪音较多
- 0-49：抓取失败或内容严重缺失

**变化**
  - 相较于上一次测试结果是否有变化
**优化质量百分比（-100-100分）：**
  - 相较于上一次测试结果是否有优化，正优化或者负优化的

## 测试网站列表

| 编号 | 网站域名 | URL |
|------|----------|-----|
| 01 | mp.weixin.qq.com | https://mp.weixin.qq.com/s/FrWhkYKonLX3ZuD6nDhXpw |
| 02 | finance.sina.com.cn | https://finance.sina.com.cn/roll/2025-09-19/doc-infrchxs4006271.shtml |
| 03 | cn.investing.com | https://cn.investing.com/equities/tesla-motors-news |
| 04 | xueqiu.com | https://xueqiu.com/S/TSLA |
| 05 | www.msn.cn | https://www.msn.cn/zh-cn/news/other/... |
| 06 | www.sohu.com | https://www.sohu.com/a/996235269_121608032 |
| 07 | news.qq.com | https://news.qq.com/rain/a/20260313A08DDL00 |
| 08 | sports.huanqiu.com | https://sports.huanqiu.com/article/4QjG4cQdz1v |
| 09 | www.guancha.cn | https://www.guancha.cn/sports/2026_03_13_809919.shtml |
| 10 | news.bjd.com.cn | https://news.bjd.com.cn/2026/03/13/11628598.shtml |
| 11 | news.sina.cn | https://news.sina.cn/gn/2026-03-13/detail-inhqvhtn4169536.d.html?vt=4 |
| 12 | www.globalpeople.com.cn | https://www.globalpeople.com.cn/n4/2026/0314/c305917-21644941.html |
| 13 | www.chinanews.com.cn | https://www.chinanews.com.cn/ty/2026/03-13/10586350.shtml |
| 14 | www.36kr.com | https://www.36kr.com/p/2984752225886082 |
| 15 | www.nbd.com.cn | https://www.nbd.com.cn/articles/2025-10-17/4095107.html |
| 16 | news.qq.com | https://news.qq.com/rain/a/20260312A04DDQ00 |
| 17 | mp.weixin.qq.com | https://mp.weixin.qq.com/s?src=11&timestamp=1773504861... |
| 18 | mp.weixin.qq.com | https://mp.weixin.qq.com/s?src=11&timestamp=1773504861... |
| 19 | baijiahao.baidu.com | https://baijiahao.baidu.com/s?id=1859359368585426709&wfr=spider&for=pc |
| 20 | baijiahao.baidu.com | https://baijiahao.baidu.com/s?id=1856155636617175508&wfr=spider&for=pc |
| 21 | www.toutiao.com | https://www.toutiao.com/article/7617049061619581480/ |
| 22 | news.mydrivers.com | https://news.mydrivers.com/1/1108/1108180.htm |
| 23 | news.cctv.com | https://news.cctv.com/2026/03/14/ARTIKOxmS8y08Ezdt89y2I2z260314.shtml |
| 24 | news.sina.com.cn | https://news.sina.com.cn/zx/gj/2026-03-14/doc-inhqwuuu3714268.shtml |
| 25 | www.thepaper.cn | https://www.thepaper.cn/newsDetail_forward_32769323 |
| 26 | military.people.com.cn | http://military.people.com.cn/n1/2025/1225/c1011-40631976.html |
| 27 | www.news.cn | https://www.news.cn/fortune/20260314/b04b8abad1b040f6ae04bb8623e00e50/c.html |
| 28 | www.chinanews.com.cn | https://www.chinanews.com.cn/sh/2026/03-14/10586622.shtml |
| 29 | news.ifeng.com | https://news.ifeng.com/c/8rUozrIUp80 |
| 30 | www.bilibili.com | https://www.bilibili.com/opus/1175833574604013571 |
| 31 | www.huxiu.com | https://www.huxiu.com/article/4842060.html |
