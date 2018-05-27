# coding:utf-8
import requests
import time
import urllib.request
import re
from datetime import datetime

ICO_API_URL = 'https://api.coinmarketcap.com/v1/ticker/'
IFTTT_WEBHOOKS_URL = 'https://maker.ifttt.com/trigger/{}/with/key/{}'
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


def post_ifttt_webhook(event, key, name, price):
    # The payload that will be sent to IFTTT service
    data = {'value1': name, 'value2': price}
    # inserts our desired event
    ifttt_event_url = IFTTT_WEBHOOKS_URL.format(event, key)
    # Sends a HTTP POST request to the webhook URL
    requests.post(ifttt_event_url, json=data)


def format_ico_history(ico_history):
    rows = []
    for ico_price in ico_history:
        # Formats the date into a string: '24.02.2018 15:09'
        date = ico_price['date'].strftime('%d.%m.%Y %H:%M')
        price = ico_price['price']
        # <b> (bold) tag creates bolded text
        # 27.05.2018 15:09: <b>10123.4</b> RMB
        row = '{}: <b>{}</b> RMB'.format(date, price)
        rows.append(row)

    # Use a <br> (break) tag to create a new line
    # Join the rows delimited by <br> tag: row1<br>row2<br>row3
    return '<br>'.join(rows)


def main():
    ico_history = []
    # bitcoin, eos...
    ico = "eos"
    key = ""
    # ico_list = {'eos': 80}
    last = 2 ** 31
    rate = 0
    while True:
        tmp = get_curr_rate()
        if tmp != 0:
            rate = tmp
        if rate == 0:
            continue
        price = round(get_latest_ico_price() * rate, 2)
        date = datetime.now()
        ico_history.append({'date': date, 'price': price})

        # Send an emergency notification
        if price > EOS_PRICE_THRESHOLD:
            last = 2 ** 31
        if price < EOS_PRICE_THRESHOLD < last:
            post_ifttt_webhook('ico_price_emergency', key, ico, price)
            last = price

        # Send a Telegram notification
        # Once we have 5 items in our ico_history send an update
        if len(ico_history) == 5:
            post_ifttt_webhook('ico_price_update', key, ico,
                               format_ico_history(ico_history))
            # Reset the history
            ico_history = []

        # Sleep for 5 minutes
        # (For testing purposes you can set it to a lower number)
        time.sleep(5 * 60)


if __name__ == '__main__':
    main()
