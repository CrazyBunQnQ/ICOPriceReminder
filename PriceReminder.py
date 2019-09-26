# coding:utf-8
import requests
import urllib.request
import re
import pymysql
from datetime import datetime
from decimal import getcontext, Decimal
from huobi import RequestClient
from huobi.model import *

# IFTTT Info
KEY = "your_ifttt_key"
IFTTT_WEBHOOKS_URL = 'https://maker.ifttt.com/trigger/{}/with/key/%s' % KEY
EVENT_NAME = "your_event_name"
# Database information
DB_HOST = "localhost"
DB_NAME = "autotrade"
DB_USER = "root"
DB_PWD = "your_db_password"
DB_CHARSET = "utf8mb4"

# Huobi
API_KEY = "your huobi api key"
SECRET_KEY = "your huobi secret key"
HUO_BI_API_BASE_URL = 'https://api.huobi.pro'
# TODO 打开 火币 app 的 url
APP_URL = ""

# Other Setting
LIAN_XU_TIMES = 3
getcontext().prec = 10
SHOW_SQL = False
IS_TEST = True
HUOBI_CLIENT = RequestClient(api_key=API_KEY, secret_key=SECRET_KEY)


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
            return float(lists[0][2])
        return 0
    except Exception as e:
        print(datetime.now().strftime('%Y-%m-%d %H:%M:%S') + " get rate error: " + str(e))
        return 0


def get_latest_ico_price(name="btc", fiat="usdt"):
    trades = HUOBI_CLIENT.get_market_trade(symbol=name + fiat)
    obj = trades[0]
    return getattr(obj, 'price')


def post_ifttt_webhook_link(event, title, message, link_url):
    # The payload that will be sent to IFTTT service
    if IS_TEST:
        title = "测试：" + title
    data = {'value1': title, 'value2': message, 'value3': link_url}
    # inserts our desired event
    ifttt_event_url = IFTTT_WEBHOOKS_URL.format(event)
    # Sends a HTTP POST request to the webhook URL
    requests.post(ifttt_event_url, json=data)


def post_ifttt_webhook_img(event, title, message, img_url):
    # The payload that will be sent to IFTTT service
    if IS_TEST:
        title = "测试：" + title
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


def update_db_account(platform="huobi"):
    usdt = 0.0
    usdt_locked = 0.0
    btc = 0.0
    btc_locked = 0.0
    eth = 0.0
    eth_locked = 0.0
    eos = 0.0
    eos_locked = 0.0
    xrp = 0.0
    xrp_locked = 0.0
    spot_balance = HUOBI_CLIENT.get_account_balance_by_account_type(AccountType.SPOT)
    balances = getattr(spot_balance, 'balances')
    for i, coin in enumerate(balances):
        currency = getattr(coin, 'currency')
        balance_type = getattr(coin, 'balance_type')
        balance = getattr(coin, 'balance')
        if currency == 'usdt':
            if balance_type == 'trade':
                usdt = balance
            else:
                usdt_locked = balance
        if currency == 'btc':
            if balance_type == 'trade':
                btc = balance
            else:
                btc_locked = balance
        if currency == 'eth':
            if balance_type == 'trade':
                eth = balance
            else:
                eth_locked = balance
        if currency == 'eos':
            if balance_type == 'trade':
                eos = balance
            else:
                eos_locked = balance
        if currency == 'xrp':
            if balance_type == 'trade':
                xrp = balance
            else:
                xrp_locked = balance
    try:
        db_connect = pymysql.connect(host=DB_HOST, user=DB_USER, passwd=DB_PWD, db=DB_NAME, charset=DB_CHARSET)
        cursor = db_connect.cursor()
        # language=MySQL
        sql = "update autotrade.account set usdt = {:f}, usdt_locked = {:f}, btc = {:f}, btc_locked = {:f}, eth = {:f}, eth_locked = {:f}, eos = {:f}, eos_locked = {:f}, xrp = {:f}, xrp_locked = {:f} where platform = '{:s}'".format(
            usdt, usdt_locked, btc, btc_locked, eth, eth_locked, eos, eos_locked, xrp, xrp_locked, platform)
        if SHOW_SQL:
            print(datetime.now().strftime('%Y-%m-%d %H:%M:%S') + " " + sql)
        cursor.execute(sql)
        db_connect.commit()
        db_connect.close()
    except Exception as e:
        print(datetime.now().strftime('%Y-%m-%d %H:%M:%S') + " " + str(e))
        post_ifttt_webhook_link(EVENT_NAME, "价格提醒脚本出错啦！", "数据库更新余额出错！有空记得检查一下哟！" + str(e), "")


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
            ico['max_price'] = float(row[4])
            ico['min_price'] = float(row[5])
            ico['reminder_point'] = float(row[6])
            ico['count_in_a_row'] = row[7]
            ico['trade_avg_price'] = float(row[8])
            dic[row[2] + "_" + row[3]] = ico
    except Exception as e:
        print(datetime.now().strftime('%Y-%m-%d %H:%M:%S') + " " + str(e))
        post_ifttt_webhook_link(EVENT_NAME, "价格提醒脚本出错啦！", "数据库查询出错！有空记得检查一下哟！" + str(e), "")
    return dic


def update_db_prices(symbol_id, last_price, max_price, min_price, times):
    try:
        db_connect = pymysql.connect(host=DB_HOST, user=DB_USER, passwd=DB_PWD, db=DB_NAME, charset=DB_CHARSET)
        cursor = db_connect.cursor()
        sql = "update autotrade.strategy_low_buy_high_sell_max set trade_avg_price = " + str(last_price) + ", max_price = " + str(max_price) + ", min_price = " + \
              str(min_price) + ", count_in_a_row = " + str(times) + " where id = " + str(symbol_id)
        if SHOW_SQL:
            print(datetime.now().strftime('%Y-%m-%d %H:%M:%S') + " " + sql)
        cursor.execute(sql)
        db_connect.commit()
        db_connect.close()
    except Exception as e:
        print(datetime.now().strftime('%Y-%m-%d %H:%M:%S') + " " + str(e))
        post_ifttt_webhook_link(EVENT_NAME, "价格提醒脚本出错啦！", "数据库更新出错！有空记得检查一下哟！" + str(e), "")


def is_rebound_rise(cur_usd, max_price, min_price, last_price):
    '是否持续下跌后反涨'
    if last_price == 0:
        return max_price - cur_usd > cur_usd - min_price
    else:
        return cur_usd < last_price


def main():
    dic = query_db_prices()
    rate = 0
    while rate == 0:
        rate = get_curr_rate()
        # rate = 7.123300
        if rate == 0:
            continue

        for ico in dic:
            coin = dic[ico]
            usd = 0
            while usd == 0:
                usd = get_latest_ico_price(coin['coin_name'])

            print(datetime.now().strftime('%Y-%m-%d %H:%M:%S') + " 现在 %s 的价格为 %.6f 元" % (ico, usd * rate))

            last_price = coin['trade_avg_price']
            count_in_a_row = coin['count_in_a_row']
            last_count_in_a_row = coin['count_in_a_row']
            max_price = coin['max_price']
            min_price = coin['min_price']
            reminder_point = coin['reminder_point']
            is_rebound = False

            cur_point = 0.0
            if usd > max_price:
                max_price = usd
                cur_point = ((usd - min_price) / min_price) if last_price == 0 else ((usd - last_price) / last_price)
                count_in_a_row = int(cur_point / reminder_point)
                update_db_prices(coin['id'], last_price, max_price, min_price, count_in_a_row)
            elif usd < min_price:
                min_price = usd
                cur_point = ((usd - max_price) / max_price) if last_price == 0 else ((usd - last_price) / last_price)
                count_in_a_row = int(cur_point / reminder_point)
                update_db_prices(coin['id'], last_price, max_price, min_price, count_in_a_row)
            else:
                is_rebound = True

            if is_rebound:
                isReboundRise = is_rebound_rise(usd, max_price, min_price, last_price)
                if isReboundRise:
                    cur_point = (usd - min_price) / min_price
                else:
                    cur_point = (max_price - usd) / max_price
                # if last_price == 0:
                # else:

                if abs(cur_point) <= reminder_point:
                    print("cur_point: {:.2f}%".format(cur_point * 100))
                    continue

                if last_price == 0:
                    title = coin['coin_name'] + "价格反弹了!"
                    if isReboundRise:
                        message = "近期从 {:.6f} 元跌到 {:.6f} 元后反涨了 {:.2f}%(当前 {:.6f} 元)".format(max_price * rate, min_price * rate, (cur_point * 100), usd * rate)
                        # TODO 进行市价交易, 获取实际交易金额
                        side = "buy"
                        # TODO 余额不足电话提醒
                        # TODO 交易成功才重制数据库
                        # update_db_prices(coin['id'], last_price, usd, usd, 0)
                    else:
                        message = "近期从 {:.6f} 元涨到 {:.6f} 元后反跌了 {:.2f}%(当前 {:.6f} 元)".format(min_price * rate, max_price * rate, (cur_point * 100), usd * rate)
                        # update_db_prices(coin['id'], last_price, usd, usd, 0)
                    print(title + ", " + message)
                    post_ifttt_webhook_link(EVENT_NAME, title, message, APP_URL)
                else:
                    # TODO 能赚才交易
                    cur_actual_point = (usd - last_price) / last_price
                    if abs(cur_actual_point) > reminder_point * 2:
                        side = "sell" if cur_actual_point > 0 else "buy"
                        print("当前价格相比上次交易价格: {:.2f}%, 开始交易...{:s}".format(cur_actual_point * 100, side))
                        # TODO 买入时，跌的越多买的越多，封顶上次交易金额的 2 倍
                        # TODO 进行市价交易, 获取实际交易金额
                        # TODO 余额不足电话提醒
                        # TODO 交易成功才重制数据库


if __name__ == '__main__':
    # test
    # print("当前价格相比上次交易价格: {:.1f}, 开始交易...{:s}".format(0.123 * 100, "2"))

    update_db_account()
    # main()
    while True:
        main()
