## 准备工作

### 安装依赖

进入项目路径，执行下面代码安装依赖

```bash
pip3 install requests
```

### 创建数据库

脚本使用 mysql 数据库进行持久化，以便脚本中断后上次提醒的数据还在

你可以运行 [`db_update.sql`](../db_update.sql)中的脚本来创建数据库，其中可以修改想要提醒的货币内容。

### 注册创建 IFTTT 活动

本脚本通过 [IFTTT](https://ifttt.com/) 进行提醒，用了才知道方便好用！

睡觉咯！有空再补充！

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
