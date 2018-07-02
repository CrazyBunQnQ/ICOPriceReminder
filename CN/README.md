## 准备工作

### 安装依赖

进入项目路径，执行下面代码安装依赖

```bash
pip3 install requests
```

### 创建数据库

脚本使用 mysql 数据库进行持久化，以便脚本中断后上次提醒的数据还在

你可以运行 [`db_update.sql`](db_update.sql)中的脚本来创建数据库，其中可以修改想要提醒的货币内容。

### 注册创建 IFTTT 活动

本脚本通过 [IFTTT](https://ifttt.com/) 进行提醒，用了才知道方便好用！

睡觉咯！有空再补充！

## 使用方式

编辑 [PriceReminder.py]() 将顶部的变量改为你自己的信息：IFTTT Key、MySql 数据库、提醒百分点和点击提醒后跳转的页面。

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

以上，改好之后就可以运行脚本啦！

```bash
python3 PriceReminder.py
```