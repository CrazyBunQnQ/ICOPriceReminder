# coding:utf-8
import requests
import time
import urllib.request
import re
import pymysql
from datetime import datetime

# IFTTT Info
KEY = "your_ifttt_key"
IFTTT_WEBHOOKS_URL = 'https://maker.ifttt.com/trigger/{}/with/key/%s' % KEY
# Database information
DB_HOST = "localhost"
DB_USER = "root"
DB_PWD = "your_db_password"
DB_NAME = "ICO"
DB_CHARSET = "utf8mb4"
# Other Setting
REMINDER_POINT = 0.1
ICO_API_URL = 'https://api.coinmarketcap.com/v1/ticker/'


def get_curr_rate(scur="USD", tcur="CNY", amount="1"):
    rex = r'(<table class="rate">.*\n.*\n *<tr><td>(\d+)</td><td>(\d+\.\d+)</td><td>(\d+\.\d+)</td>.*</table>)'
    rate_url = "http://qq.ip138.com/hl.asp?from=%s&to=%s&q=%s" % (scur, tcur, amount)
    try:
        response = urllib.request.urlopen(rate_url, timeout=10)
        html = response.read().decode('gb2312')
        # print(html)
        lists = re.findall(rex, html)
        if len(lists) > 0:
            return float(lists[0][2])
        return 0
    except:
        print("get rate error")
        return 0
    return 0


def get_latest_ico_price(name="eos"):
    try:
        response = requests.get(ICO_API_URL + name)
        response_json = response.json()
        # Convert the price to a floating point number
        return float(response_json[0]['price_usd'])
    except:
        print("get price error")
        return 0


def post_ifttt_webhook(event, name, price, rise_and_fall):
    # The payload that will be sent to IFTTT service
    data = {'value1': name, 'value2': price, 'value3': rise_and_fall}
    # inserts our desired event
    ifttt_event_url = IFTTT_WEBHOOKS_URL.format(event)
    # Sends a HTTP POST request to the webhook URL
    requests.post(ifttt_event_url, json=data)


def query_db_prices():
    dic = {}
    db_connect = pymysql.connect(host=DB_HOST, user=DB_USER, passwd=DB_PWD, db=DB_NAME, charset=DB_CHARSET)
    cursor = db_connect.cursor()
    sql = "select t.name, t.price from Coin t"
    cursor.execute(sql)
    rows = cursor.fetchall()
    db_connect.close()
    for row in rows:
        dic[row[0]] = row[1]
    return dic


def update_db_prices(price):
    db_connect = pymysql.connect(host=DB_HOST, user=DB_USER, passwd=DB_PWD, db=DB_NAME, charset=DB_CHARSET)
    cursor = db_connect.cursor()
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    sql = "update Coin t set t.price = " + str(price) + ", t.update_time = '" + now + "'"
    print(sql)
    cursor.execute(sql)
    db_connect.commit()
    db_connect.close()


def main():
    dic = query_db_prices()

    rate = 0
    price = 0
    while True:
        tmp = get_curr_rate()
        if tmp != 0:
            rate = tmp
        if rate == 0:
            continue

        for ico in dic:
            usd = get_latest_ico_price(ico)
            if usd != 0:
                price = round(usd * rate, 2)
            print("现在 %s 的价格为 %s 元" % (ico, price))

            cur_point = (usd - dic[ico]) / dic[ico]
            if abs(cur_point) > REMINDER_POINT:
                dic[ico] = usd
                update_db_prices(usd)
                if cur_point > 0:
                    post_ifttt_webhook('ico_price_emergency', ico, price, "涨")
                else:
                    post_ifttt_webhook('ico_price_emergency', ico, price, "跌")

        # Sleep for 5 minutes
        # (For testing purposes you can set it to a lower number)
        time.sleep(5 * 60)


if __name__ == '__main__':
    main()
