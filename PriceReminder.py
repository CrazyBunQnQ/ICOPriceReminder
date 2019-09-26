# coding:utf-8
import requests
import urllib.request
import re
import pymysql
from datetime import datetime
from decimal import getcontext, Decimal

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
LIAN_XU_TIMES = 3
HUO_BI_API_BASE_URL = 'https://api.huobi.pro'
getcontext().prec = 10


# TODO 添加点击通知打开交易 app


def get_curr_rate(scur="USD", tcur="CNY", amount="1"):
    rex = r'(<tr><td><p>(\d)+[<>trdp/]+(\d+\.\d+)[<>trdp/]+(\d+\.\d+)</p></td></tr></table>)'
    rate_url = "http://qq.ip138.com/hl.asp?from=%s&to=%s&q=%s" % (scur, tcur, amount)
    try:
        response = urllib.request.urlopen(rate_url, timeout=10)
        html = response.read()
        html = html.decode('utf-8')
        # print(datetime.now().strftime('%Y-%m-%d %H:%M:%S') + " " + html)
        lists = re.findall(rex, html)
        if len(lists) > 0:
            return Decimal(lists[0][2])
        return 0
    except Exception as e:
        print(datetime.now().strftime('%Y-%m-%d %H:%M:%S') + " get rate error: " + str(e))
        return 0


def get_latest_ico_price(name="btc", fiat="usdt"):
    url = HUO_BI_API_BASE_URL + "/market/trade?symbol=" + name + fiat
    try:
        response = requests.get(url)
        response_json = response.json()
        # Convert the price to a floating point number
        return Decimal(response_json['tick']['data'][0]['price'])
    except Exception as e:
        print(datetime.now().strftime('%Y-%m-%d %H:%M:%S') + " get last price error: " + str(e))
        return 0


# except:
#     print(datetime.now().strftime('%Y-%m-%d %H:%M:%S') + " get price error")
#     return 0


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


def send_notice_link(ico, price, reminder_point, times, is_img):
    title = ico + " 价格变动"
    rise_or_fall = "涨"
    buy_or_sell = "脱手"
    if times < 0:
        rise_or_fall = "跌"
        buy_or_sell = "买入"
    message = ico + " 现在" + rise_or_fall + "到 " + str(price) + " 元啦！相对于上次提醒的价格" + rise_or_fall + "了 " + str(
        reminder_point * 100) + "% ！"
    if abs(times) >= 2:
        point = round(abs(times) * reminder_point * 100, 1)
        message += "已连续" + rise_or_fall + "了 " + str(point) + "% 啦!!!~ "
    message += "你要趁现在" + buy_or_sell + "吗？"
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
        # sql = "select t.id, t.sample_name, t.price, t.lian_xu from Coin t"
        sql = "select t.id, t.symbol, t.coin_name, t.platform, t.max_price, t.min_price, t.reminder_point, t.count_in_a_row, t.trade_avg_price " \
              "from autotrade.strategy_low_buy_high_sell_max t where t.enabled is true"
        cursor.execute(sql)
        rows = cursor.fetchall()
        db_connect.close()
        for row in rows:
            ico = {}
            ico['id'] = row[0]
            ico['symbol'] = row[1]
            ico['coin_name'] = row[2]
            ico['platform'] = row[3]
            ico['max_price'] = row[4]
            ico['min_price'] = row[5]
            ico['reminder_point'] = float(row[6])
            ico['count_in_a_row'] = row[7]
            ico['trade_avg_price'] = row[8]
            dic[row[2] + "_" + row[3]] = ico
    except Exception as e:
        post_ifttt_webhook_link(EVENT_NAME, "价格提醒脚本出错啦！", "数据库查询出错！有空记得检查一下哟！" + e, "")
    return dic


def update_db_prices(symbol_id, last_price, max_price, min_price, times):
    try:
        db_connect = pymysql.connect(host=DB_HOST, user=DB_USER, passwd=DB_PWD, db=DB_NAME, charset=DB_CHARSET)
        cursor = db_connect.cursor()
        sql = "update autotrade.strategy_low_buy_high_sell_max set trade_avg_price = " + str(last_price) + ", max_price = " + str(max_price) + ", min_price = " + \
              str(min_price) + ", count_in_a_row = " + str(times) + " where id = " + str(symbol_id)
        print(datetime.now().strftime('%Y-%m-%d %H:%M:%S') + " " + sql)
        cursor.execute(sql)
        db_connect.commit()
        db_connect.close()
    except Exception as e:
        post_ifttt_webhook_link(EVENT_NAME, "价格提醒脚本出错啦！", "数据库更新出错！有空记得检查一下哟！" + e, "")


def is_rebound_rise(cur_usd, max_price, min_price):
    return max_price - cur_usd > cur_usd - min_price


def main():
    dic = query_db_prices()
    rate = 0
    while rate == 0:
        # rate = get_curr_rate()
        rate = Decimal(7.123300)
        if rate == 0:
            continue

        for ico in dic:
            coin = dic[ico]
            usd = 0
            while usd == 0:
                usd = get_latest_ico_price(coin['coin_name'])

            print(datetime.now().strftime('%Y-%m-%d %H:%M:%S') + " 现在 %s 的价格为 %s 元" % (ico, usd * rate))

            last_price = coin['trade_avg_price']
            count_in_a_row = coin['count_in_a_row']
            last_count_in_a_row = coin['count_in_a_row']
            max_price = coin['max_price']
            min_price = coin['min_price']
            reminder_point = coin['reminder_point']
            is_rebound = False

            cur_point = reminder_point - reminder_point
            if usd > max_price:
                max_price = usd
                cur_point = float(((usd - min_price) / min_price) if last_price == 0 else ((usd - last_price) / last_price))
                count_in_a_row = int(cur_point / reminder_point)
                update_db_prices(coin['id'], last_price, max_price, min_price, count_in_a_row)
            elif usd < min_price:
                min_price = usd
                cur_point = float(((usd - max_price) / max_price) if last_price == 0 else ((usd - last_price) / last_price))
                count_in_a_row = int(cur_point / reminder_point)
                update_db_prices(coin['id'], last_price, max_price, min_price, count_in_a_row)
            else:
                is_rebound = True

            if abs(cur_point) > reminder_point:
                # coin['price'] = usd
                if count_in_a_row / cur_point > 0:
                    count_in_a_row = count_in_a_row + int(cur_point / abs(cur_point))
                else:
                    count_in_a_row = int(cur_point / abs(cur_point))
                if usd != 0:
                    update_db_prices(coin['id'], last_price, usd, usd, count_in_a_row)
                    send_notice_link(coin['coin_name'], usd * rate, reminder_point, count_in_a_row, False)
            elif is_rebound:
                # 是否反弹, 若反弹判断为提醒百分比的 1/3
                reminder_point = reminder_point * 1 / 3
                if last_price == 0:
                    isReboundRise = is_rebound_rise(usd, max_price, min_price)
                    if isReboundRise:
                        cur_point = float((usd - min_price) / min_price)
                    else:
                        cur_point = float((max_price - usd) / max_price)
                else:
                    # TODO 根据上次交易价格获取涨跌幅度
                    print()

                if abs(cur_point) <= reminder_point:
                    print("cur_point: " + str(cur_point))
                    continue

                if last_price == 0:
                    title = coin['coin_name'] + "价格反弹了!"
                    # TODO 打开 火币 app 的 url
                    url = ""
                    if isReboundRise:
                        message = "近期从 " + str(max_price * rate) + " 元跌到 " + str(min_price * rate) + " 元后反涨了 " + str(cur_point) + "(" + str(usd * rate) + " 元)"
                        # TODO 进行交易, 获取实际交易金额
                        # TODO 余额不足电话提醒
                        update_db_prices(coin['id'], last_price, usd, usd, 0)
                    else:
                        message = "近期从 " + str(min_price * rate) + " 元涨到 " + str(max_price) + " 元后反跌了 " + str(cur_point * rate) + "(" + str(usd * rate) + " 元)"
                        # TODO 进行交易, 获取实际交易金额
                        # TODO 余额不足电话提醒
                        update_db_prices(coin['id'], last_price, usd, usd, 0)
                    print(message)
                    post_ifttt_webhook_img(EVENT_NAME, title, message, url)
                else:
                    # TODO 能赚才交易
                    print()


if __name__ == '__main__':
    # main()
    while True:
        main()
