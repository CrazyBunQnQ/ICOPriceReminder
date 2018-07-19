# coding:utf-8
import requests
import urllib.request
import re
import pymysql
from datetime import datetime

# IFTTT Info
KEY = "your_ifttt_key"
IFTTT_WEBHOOKS_URL = 'https://maker.ifttt.com/trigger/{}/with/key/%s' % KEY
EVENT_NAME = "your_event_name"
# Database information
DB_HOST = "localhost"
DB_USER = "root"
DB_PWD = "your_db_password"
DB_NAME = "ICO"
DB_CHARSET = "utf8mb4"
# Other Setting
REMINDER_POINT = 0.05
ICO_API_URL = 'https://api.coinmarketcap.com/v1/ticker/'
# TODO 添加点击通知打开交易 app


def get_curr_rate(scur="USD", tcur="CNY", amount="1"):
    rex = r'(<table class="rate">.*\n.*\n *<tr><td>(\d+)</td><td>(\d+\.\d+)</td><td>(\d+\.\d+)</td>.*</table>)'
    rate_url = "http://qq.ip138.com/hl.asp?from=%s&to=%s&q=%s" % (scur, tcur, amount)
    try:
        response = urllib.request.urlopen(rate_url, timeout=10)
        html = response.read().decode('gb2312')
        # print(datetime.now().strftime('%Y-%m-%d %H:%M:%S') + " " + html)
        lists = re.findall(rex, html)
        if len(lists) > 0:
            return float(lists[0][2])
        return 0
    except:
        print(datetime.now().strftime('%Y-%m-%d %H:%M:%S') + " get rate error")
        return 0
    return 0


def get_latest_ico_price(name="eos"):
    try:
        response = requests.get(ICO_API_URL + name)
        response_json = response.json()
        # Convert the price to a floating point number
        return float(response_json[0]['price_usd'])
    except:
        print(datetime.now().strftime('%Y-%m-%d %H:%M:%S') + " get price error")
        return 0


def post_ifttt_webhook_link(event, title, message, link_url):
    # The payload that will be sent to IFTTT service
    data = {'value1': title, 'value2': message, 'value3': link_url}
    # inserts our desired event
    ifttt_event_url = IFTTT_WEBHOOKS_URL.format(event)
    # Sends a HTTP POST request to the webhook URL
    requests.post(ifttt_event_url, json=data)


def post_ifttt_webhook_img(event, title, message, img_url):
    # The payload that will be sent to IFTTT service
    data = {'value1': title, 'value2': message, 'value3': img_url}
    # inserts our desired event
    ifttt_event_url = IFTTT_WEBHOOKS_URL.format(event)
    # Sends a HTTP POST request to the webhook URL
    requests.post(ifttt_event_url, json=data)


def send_notice_link(ico, price, rise_and_fall, is_img):
    title = ico + " 价格变动"
    rise_or_fall = "涨"
    buy_or_sell = "脱手"
    if rise_and_fall == 0:
        rise_or_fall = "跌"
        buy_or_sell = "买入"
    message = ico + " 现在" + rise_or_fall + "到 " + str(price) + " 元啦！相对于上次提醒的价格" + rise_or_fall + "了 " + str(
        REMINDER_POINT * 100) + "% ！你要趁现在" + buy_or_sell + "吗？"
    if is_img:
        img_url = "https://coinmarketcap.com/currencies/" + ico + "/"
        post_ifttt_webhook_img(EVENT_NAME, title, message, img_url)
    else:
        link_url = "https://coinmarketcap.com/currencies/" + ico + "/"
        post_ifttt_webhook_link(EVENT_NAME, title, message, link_url)
    print(datetime.now().strftime('%Y-%m-%d %H:%M:%S') + " 发送提醒：" + message)


def query_db_prices():
    dic = {}
    try:
        db_connect = pymysql.connect(host=DB_HOST, user=DB_USER, passwd=DB_PWD, db=DB_NAME, charset=DB_CHARSET)
        cursor = db_connect.cursor()
        sql = "select t.id, t.sample_name, t.price from Coin t"
        cursor.execute(sql)
        rows = cursor.fetchall()
        db_connect.close()
        for row in rows:
            ico = {}
            ico['name'] = row[1]
            ico['price'] = row[2]
            dic[row[0]] = ico
    except:
        post_ifttt_webhook_link(EVENT_NAME, "价格提醒脚本出错啦！", "数据库查询出错！有空记得检查一下哟！", "")
    return dic



def update_db_prices(ico, price):
    try:
        db_connect = pymysql.connect(host=DB_HOST, user=DB_USER, passwd=DB_PWD, db=DB_NAME, charset=DB_CHARSET)
        cursor = db_connect.cursor()
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        sql = "update Coin t set t.price = " + str(price) + ", t.update_time = '" + now + "' where t.id = '" + ico + "'"
        # print(datetime.now().strftime('%Y-%m-%d %H:%M:%S') + " " + sql)
        cursor.execute(sql)
        db_connect.commit()
        db_connect.close()
    except:
        post_ifttt_webhook_link(EVENT_NAME, "价格提醒脚本出错啦！", "数据库更新出错！有空记得检查一下哟！", "")



def main():
    dic = query_db_prices()
    rate = 0
    while rate == 0:
        rate = get_curr_rate()
        if rate == 0:
            continue

        for ico in dic:
            usd = 0
            while usd == 0:
                usd = get_latest_ico_price(ico)
            price = round(usd * rate, 2)
            print(datetime.now().strftime('%Y-%m-%d %H:%M:%S') + " 现在 %s 的价格为 %s 元" % (ico, price))

            cur_point = (usd - dic[ico]['price']) / dic[ico]['price']
            if abs(cur_point) > REMINDER_POINT:
                dic[ico]['price'] = usd
                if usd != 0:
                    update_db_prices(ico, usd)
                if cur_point > 0:
                    send_notice_link(dic[ico]['name'], price, 1, False)
                else:
                    send_notice_link(dic[ico]['name'], price, 0, False)


if __name__ == '__main__':
    main()
