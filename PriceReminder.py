# coding:utf-8
import requests
import time
import urllib.request
import re
from datetime import datetime

# your IFTTT key
KEY = ""
ICO_API_URL = 'https://api.coinmarketcap.com/v1/ticker/'
IFTTT_WEBHOOKS_URL = 'https://maker.ifttt.com/trigger/{}/with/key/%s' % KEY
EOS_PRICE_THRESHOLD = 80  # Set this to whatever you like


def get_curr_rate(scur="USD", tcur="CNY", amount="1"):
    rex = r'(<table class="rate">.*\n.*\n *<tr><td>(\d+)</td><td>(\d+\.\d+)</td><td>(\d+\.\d+)</td>.*</table>)'
    rate_url = "http://qq.ip138.com/hl.asp?from=%s&to=%s&q=%s" % (scur, tcur, amount)
    response = urllib.request.urlopen(rate_url, timeout=10)
    html = response.read().decode('gb2312')
    # print(html)
    lists = re.findall(rex, html)
    if len(lists) > 0:
        return float(lists[0][2])
    return 0


def get_latest_ico_price(name="eos"):
    response = requests.get(ICO_API_URL + name)
    response_json = response.json()
    # Convert the price to a floating point number
    return float(response_json[0]['price_usd'])


def post_ifttt_webhook(event, name, price, rise_and_fall):
    # The payload that will be sent to IFTTT service
    data = {'value1': name, 'value2': price, 'value3': rise_and_fall}
    # inserts our desired event
    ifttt_event_url = IFTTT_WEBHOOKS_URL.format(event)
    # Sends a HTTP POST request to the webhook URL
    requests.post(ifttt_event_url, json=data)


def format_ico_history(ico_history):
    rows = []
    for ico_price in ico_history:
        # Formats the date into a string: '2018-05-27 15:09'
        date = ico_price['date'].strftime('%Y-%m-%d %H:%M')
        price = ico_price['price']
        # <b> (bold) tag creates bolded text
        # 2018-05-27 15:09: <b>10123.4</b> RMB
        row = '{}: <b>{}</b> RMB'.format(date, price)
        rows.append(row)

    # Use a <br> (break) tag to create a new line
    # Join the rows delimited by <br> tag: row1<br>row2<br>row3
    return '<br>'.join(rows)


def main():
    dic = {}
    # bitcoin, eos...
    # bitcoin_dic = {'prices': [90, 100, 110, 120, 130, 140, 150, 160, 170, 180, 190],
    #                'i': 6,
    #                'history': []}
    eos_dic = {'prices': [10, 20, 30, 40, 50, 60, 70, 80, 90, 100, 110, 120, 130, 140, 150, 160, 170, 180, 190, 200],
               'i': 6,
               'history': []}
    dic['eos'] = eos_dic
    # dic['bitcoin'] = bitcoin_dic

    rate = 0
    while True:
        tmp = get_curr_rate()
        if tmp != 0:
            rate = tmp
        if rate == 0:
            continue

        for ico in dic:
            price = round(get_latest_ico_price(ico) * rate, 2)
            print("现在 %s 的价格为 %s 元" % (ico, price))
            ico_dic = dic[ico]
            i = ico_dic['i']
            if i >= len(ico_dic['prices']):
                i = len(ico_dic['prices']) - 1
            if i < 1:
                i = 1
            if ico_dic['prices'][i] > price > ico_dic['prices'][i - 1]:
                print('not change')
            elif price > ico_dic['prices'][i]:
                dic[ico]['i'] = i + 1
                # print(price)
                # Send an emergency notification
                post_ifttt_webhook('ico_price_emergency', ico, price, "涨")

            elif price < ico_dic['prices'][i - 1]:
                dic[ico]['i'] = i - 1
                # print(price)
                # Send an emergency notification
                post_ifttt_webhook('ico_price_emergency', ico, price, "跌")

            # Send a Telegram notification
            date = datetime.now()
            dic[ico]['history'].append({'date': date, 'price': price})
            # Once we have 5 items in our ico history send an update
            if len(dic[ico]['history']) == 5:
                post_ifttt_webhook('ico_price_update', ico, format_ico_history(dic[ico]['history']), "")
                # Reset the history
                dic[ico]['history'] = []

        # Sleep for 5 minutes
        # (For testing purposes you can set it to a lower number)
        time.sleep(5 * 60)


if __name__ == '__main__':
    main()
