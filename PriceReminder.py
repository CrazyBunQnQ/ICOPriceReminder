# coding:utf-8
import requests
import urllib.request
import re
import pymysql
from datetime import datetime
from decimal import getcontext, Decimal
from huobi import RequestClient
from huobi.model import *
from huobi.base.printobject import PrintMix

# IFTTT Info
KEY = "your_ifttt_key"
IFTTT_WEBHOOKS_URL = 'https://maker.ifttt.com/trigger/{}/with/key/%s' % KEY
EVENT_NAME = "your_event_name"
PHONE_EVENT_NAME = "your_event_name"

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
# TODO 每个币种一个限制，存数据库中
TOTAL_SPAND_RMB = 20000


# TODO 添加点击通知打开交易 app

def get_curr_huobi_rate(scur="USDT", amount="1"):
    requests.get()


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


def create_market_order(symbol_name, side, amount):
    """
    下市价单并查询订单交易详情
    amount 市价买单时表示买多少钱, 市价卖单时表示卖多少币
    """
    print("开始下单：")
    # TODO 不同货币保留小数不同
    order_id = HUOBI_CLIENT.create_order(symbol=symbol_name,
                                         account_type=AccountType.SPOT,
                                         order_type=side + "-market",
                                         # price=price,
                                         # client_order_id=client_order_id_test,
                                         # stop_price=12,
                                         # operator="gte",
                                         amount=amount)
    # print("create new order id : " + (str(order_id)) + " with client id " + client_order_id_test)
    print("下单成功 : " + (str(order_id)))
    print("\n\n")

    print("获取订单详情: " + (str(order_id)))
    # 订单完成后返回订单详情
    orderObj = HUOBI_CLIENT.get_order(symbol=symbol_name, order_id=order_id)
    orderState = getattr(orderObj, 'state')
    while orderState == 'filled':
        orderObj = HUOBI_CLIENT.get_order(symbol=symbol_name, order_id=order_id)
        orderState = getattr(orderObj, 'state')
    PrintMix.print_data(orderObj)
    return orderObj


def post_ifttt_webhook_link(event, title, message, link_url):
    # The payload that will be sent to IFTTT service
    if IS_TEST:
        title = "测试：" + title
    data = {'value1': title, 'value2': message, 'value3': link_url}
    # inserts our desired event
    ifttt_event_url = IFTTT_WEBHOOKS_URL.format(event)
    # Sends a HTTP POST request to the webhook URL
    requests.post(ifttt_event_url, json=data)


def post_ifttt_webhook_call_my_phone(title, message, img_url):
    # The payload that will be sent to IFTTT service
    if IS_TEST:
        title = "Test：" + title
    data = {'value1': title, 'value2': message, 'value3': img_url}
    # inserts our desired event
    ifttt_event_url = IFTTT_WEBHOOKS_URL.format(PHONE_EVENT_NAME)
    # Sends a HTTP POST request to the webhook URL
    return requests.post(ifttt_event_url, json=data)


def query_db_account(platform="huobi"):
    account = {}
    try:
        db_connect = pymysql.connect(host=DB_HOST, user=DB_USER, passwd=DB_PWD, db=DB_NAME, charset=DB_CHARSET)
        cursor = db_connect.cursor()
        sql = "select t.* from autotrade.account t where t.platform = '" + platform + "'"
        cursor.execute(sql)
        row = cursor.fetchone()
        db_connect.close()
        account['id'] = row[0]
        account['platform'] = row[1]
        account['usdt'] = float(str(row[2]))
        account['usdt_locked'] = float(str(row[3]))
        account['btc'] = float(str(row[4]))
        account['btc_locked'] = float(str(row[5]))
        account['eth'] = float(str(row[6]))
        account['eth_locked'] = float(str(row[7]))
        account['bnb'] = float(str(row[8]))
        account['bnb_locked'] = float(str(row[9]))
        account['eos'] = float(str(row[10]))
        account['eos_locked'] = float(str(row[11]))
        account['xrp'] = float(str(row[12]))
        account['xrp_locked'] = float(str(row[13]))
        account['cur_profit'] = float(str(row[14]))
    except Exception as e:
        print(datetime.now().strftime('%Y-%m-%d %H:%M:%S') + " " + str(e))
        post_ifttt_webhook_link(EVENT_NAME, "价格提醒脚本出错啦！", "数据库查询账户出错！有空记得检查一下哟！" + str(e), "")
    return account


def update_db_account(platform="huobi", update_profit=False):
    account = {}
    spot_balance = HUOBI_CLIENT.get_account_balance_by_account_type(AccountType.SPOT)
    balances = getattr(spot_balance, 'balances')
    for i, coin in enumerate(balances):
        currency = getattr(coin, 'currency')
        balance_type = getattr(coin, 'balance_type')
        balance = getattr(coin, 'balance')
        if currency == 'usdt':
            if balance_type == 'trade':
                account['usdt'] = balance
            else:
                account['usdt_locked'] = balance
        if currency == 'btc':
            if balance_type == 'trade':
                account['btc'] = balance
            else:
                account['btc_locked'] = balance
        if currency == 'eth':
            if balance_type == 'trade':
                account['eth'] = balance
            else:
                account['eth_locked'] = balance
        if currency == 'eos':
            if balance_type == 'trade':
                account['eos'] = balance
            else:
                account['eos_locked'] = balance
        if currency == 'xrp':
            if balance_type == 'trade':
                account['xrp'] = balance
            else:
                account['xrp_locked'] = balance
    try:
        db_connect = pymysql.connect(host=DB_HOST, user=DB_USER, passwd=DB_PWD, db=DB_NAME, charset=DB_CHARSET)
        cursor = db_connect.cursor()
        sql = "update autotrade.account set usdt = {:f}, usdt_locked = {:f}, btc = {:f}, btc_locked = {:f}, eth = {:f}, eth_locked = {:f}, eos = {:f}, eos_locked = {:f}, xrp = {:f}, xrp_locked = {:f} where platform = '{:s}'".format(
            account['usdt'], account['usdt_locked'], account['btc'], account['btc_locked'], account['eth'], account['eth_locked'], account['eos'], account['eos_locked'], account['xrp'],
            account['xrp_locked'], platform)
        if SHOW_SQL:
            print(datetime.now().strftime('%Y-%m-%d %H:%M:%S') + " " + sql)
        cursor.execute(sql)
        db_connect.commit()
        db_connect.close()
        return account
    except Exception as e:
        print(datetime.now().strftime('%Y-%m-%d %H:%M:%S') + " " + str(e))
        post_ifttt_webhook_link(EVENT_NAME, "价格提醒脚本出错啦！", "数据库更新余额出错！有空记得检查一下哟！" + str(e), "")
        return {}


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
            ico['id'] = float(str(row[0]))
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
    """是否持续下跌后反涨"""
    if last_price == 0:
        return max_price - cur_usd > cur_usd - min_price
    else:
        return cur_usd < last_price


def getProfitAmount(account={}, rate=7.1, coin_name='btc', coin_price=0):
    """获取盈利金额
    盈利金额 = (USDT 余额*汇率 + BTC余额*价格*汇率 + ...) - 投入金额(2w RMB)
    """
    return (account['usdt'] + account['usdt_locked']) * rate + (account[coin_name] + account[coin_name + '_locked']) * coin_price * rate - TOTAL_SPAND_RMB


def main():
    dic = query_db_prices()
    rate = 0
    while rate == 0:
        rate = get_curr_rate()
        # rate = 7.123300
        print("当前 usdt/cny 汇率：{:f}".format(rate))
        if rate == 0:
            continue

        for ico in dic:
            coin = dic[ico]
            # 当前价格
            usd = 0
            while usd == 0:
                usd = get_latest_ico_price(coin['coin_name'])

            print(datetime.now().strftime('%Y-%m-%d %H:%M:%S') + " 现在 %s 的价格为 %.6f 元" % (ico, usd * rate))

            # TODO 取最后连续购买的平均价, 空则设为 0
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
                    #  购买时比最后连续购买的平均低
                    #  出售时盈利金额提升即为赚, 盈利金额 = (USDT 余额*汇率 + BTC余额*价格*汇率 + ...) - 投入金额(2w RMB)
                    account = query_db_account()
                    # 当前盈利
                    profit = getProfitAmount(account, rate, coin['coin_name'], usd)
                    cur_actual_point = (usd - last_price) / last_price
                    if abs(cur_actual_point) > reminder_point * 2:
                        side = "sell" if cur_actual_point > 0 else "buy"
                        print("当前价格相比上次交易价格: {:.2f}%, 开始交易...{:s}".format(cur_actual_point * 100, side))
                        # TODO 买入时，跌的越多买的越多，封顶上次交易金额的 2 倍, 并更新盈利金额
                        # TODO 进行市价交易, 获取实际交易金额
                        # TODO 余额不足电话提醒
                        # TODO 交易成功才重制数据库
                        if side == "sell":
                            print("")
                        else:
                            print("当前价格相比上次交易价格: {:.2f}%, 开始交易...{:s}".format(cur_actual_point * 100, side))



if __name__ == '__main__':
    # test
    # print("当前价格相比上次交易价格: {:.1f}, 开始交易...{:s}".format(0.123 * 100, "2"))
    # 电话测试
    # while True:
    # test = post_ifttt_webhook_call_my_phone("Hello", "Test if you can make phone calls in Chinese", "Your balance does not seem to be enough, please recharge it!")

    # orders = HUOBI_CLIENT.get_historical_orders(symbol='btcusdt', order_state='filled', order_type='sell-market', start_date='2019-08-14')
    # PrintMix.print_data(orders)

    # orderObj = HUOBI_CLIENT.get_order(symbol='btcusdt', order_id=49453854888)
    # print("获取订单详情: " + (str(49453854888)))
    # PrintMix.print_data(orderObj)

    # acc = update_db_account()
    account = query_db_account()
    profit = getProfitAmount(account=account, rate=7.073, coin_price=7490.0)

    # main()
    while True:
        main()
