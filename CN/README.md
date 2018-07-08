## 准备工作****

### 安装依赖

进入项目路径，执行下面代码安装依赖

```bash
pip3 install requests
```

### 创建数据库

脚本使用 mysql 数据库进行持久化，以便脚本中断后上次提醒的数据还在

你可以运行 [`db_update.sql`](../db_update.sql)中的脚本来创建数据库，其中可以修改想要提醒的货币内容。

### 注册创建IFTTT活动

本脚本通过 [IFTTT](https://ifttt.com/) 进行提醒，用了才知道方便好用！

1. 打开 [IFTTT](https://ifttt.com) 官网，注册账号
1. 登陆并[创建新的 Applet](https://ifttt.com/create)
1. 点击大大的蓝色的「+THIS」
1. 搜索「Webhooks」服务，然后选择「Receive a web request」触发
1. 重命名 event 为你想要的名称，例如 `ico_price_emergency`
1. 然后点击大大的蓝色的「+that」按钮
1. 搜索「notifications」服务，然后选择「send a notification from the IFTTT app」
1. 改变 Title 为`{{Value1}}`，Message 为 `{{Value2}}`，Link URL 为 `{{Value3}}`
1. 点击 "Finish" 按钮，完成
1. 打开 [IFTTT webhooks](https://ifttt.com/maker_webhooks)，点击右上角的「Documentation」按钮
1. Documentation 页有你的 Webhooks 的 URL，包括 Event 和 key，代码中会用到

## 使用方式

### 修改基本设置

编辑 [PriceReminder.py](../PriceReminder.py) 将顶部的变量改为你自己的信息：IFTTT Key、MySql 数据库、提醒百分点和点击提醒后跳转的页面。

```python
# IFTTT 设置
KEY = "d_l8Cin64gVvWJrpJuZMDs" # 你的 IFTTT Key
IFTTT_WEBHOOKS_URL = 'https://maker.ifttt.com/trigger/{}/with/key/%s' % KEY # 这个不需要改
# Database information
DB_HOST = "你的数据库地址"
DB_USER = "数据库用户名"
DB_PWD = "数据库密码"
DB_NAME = "ICO"
DB_CHARSET = "utf8mb4" # 数据库编码
# Other Setting
REMINDER_POINT = 0.05 # 提醒的百分点
# TODO 改为点击通知打开交易 app
ICO_API_URL = 'https://api.coinmarketcap.com/v1/ticker/' # 点击通知后跳转的页面
```

### 设置定时任务

```bash
crontab -e # 编辑定时任务
# 在定时任务中添加一行如下代码后保存退出
*/2 * * * * python3.6 PriceReminder.py
crontab -l # 查看当前的定时任务列表
service crond start && service crond status # 开启定时任务并查看状态
```

>定时任务格式
>    ```bash
>    *   *　 *　 *　 *　　命令
>    # 分钟(0-59)　小时(0-23)　日期(1-31)　月份(1-12)　星期(0-6,0代表星期天)　 命令
>    # 第1列表示分钟1～59 每分钟用*或者 */1表示
>    # 第2列表示小时1～23（0表示0点）
>    # 第3列表示日期1～31
>    # 第4列表示月份1～12
>    # 第5列标识号星期0～6（0表示星期天）
>    ```

以上，完成之后就可以等他每两分钟运行一次脚本啦！

## 代码分析

### 获取当前汇率

使用 `get_curr_rate` 方法可以从 [ip138](http://qq.ip138.com/hl.asp?from=USD&to=CNY&q=1) 网站抓取当前汇率信息

默认为 1 美元兑换人民币的汇率，可以自行修改

### 获取当前货币价格

调用 `get_latest_ico_price` 方法，通过 [https://api.coinmarketcap.com](https://api.coinmarketcap.com/v1/ticker/) 提供的 api 可以获取当前各个货币的信息，也可以在结尾添加货币名称查询指定货币的信息，其中价格信息则是我们需要的

```
https://api.coinmarketcap.com/v1/ticker/ 
https://api.coinmarketcap.com/v1/ticker/eos
```

你会获得类似下面的数据：

```json
[
    {
        "id": "eos",
        "name": "EOS",
        "symbol": "EOS",
        "rank": "5",
        "price_usd": "8.98341",
        "price_btc": "0.0013345",
        "24h_volume_usd": "529859000.0",
        "market_cap_usd": "8050478309.0",
        "available_supply": "896149492.0",
        "total_supply": "900000000.0",
        "max_supply": "1000000000.0",
        "percent_change_1h": "-0.53",
        "percent_change_24h": "3.61",
        "percent_change_7d": "11.65",
        "last_updated": "1531030333"
    },
    ...
]
```

### 发送 IFTTT Webhook 请求

`post_ifttt_webhook_link` 方法会向我们在 [IFTTT](#注册创建IFTTT活动) 上创建的 Applet 发送请求，IFTTT 则会将内容推送到手机端

因为我们在 IFTTT 上标题、信息和连接都写的是变量，所以我们向 IFTTT 发送请求前需要自行把信息拼接好

>其中 `link_url` 为用户点击推送消息时跳转的网页

### 更新数据库提醒记录

每次提醒时通过 `update_db_prices` 将本次提醒的价格存入数据库，方便下次提醒时作对比

### 从数据库查询上一次提醒的价格

通过 `query_db_prices` 方法可以从数据库中查询出上次提醒的价格，通过对比当前价格判断是否给用户推送消息，若超过配置的提醒百分比则推送消息并更新数据库