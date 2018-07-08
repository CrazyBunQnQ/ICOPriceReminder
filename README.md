## Preparatory Work

### Install Requirements

```bash
pip3 install requests
```

### Create Database

This program uses a MySql database. You can run the [`db_update.sql`](db_update.sql) to create the table that the program needs.

### Register [IFTTT](https://ifttt.com) and [create an activity](https://ifttt.com/create)

1. [Create your applet](https://ifttt.com/create) after signing up for [IFTTT].
1. Click the big blue「+This」button.
1. Search for the「Webhooks」service, then select「Receive a web request」.
1. Rename the「event」for you want to name, for example `ico_price_emergency`
1. Then click the big blue「+That」button.
1. Search the「notifications」service and select「send a notification from the IFTTT app」.
1. Change the「Title」to `{{Value1}}`,「Message」to `{{Value2}}`, the「Link URL」to `{{Value3}}`.
1. Click the「Finish」button to complete.
1. Open the [IFTTT webhooks](https://ifttt.com/maker_webhooks) and click the「Documentation」button in the upper right corner.
1. The Documentation page has your `Webhooks URL`, including `Event Name` and `key`, which is used in the python code.

## How to Use

### Modify configuration information

Edit [PriceReminder.py](PriceReminder.py), Change the top variable to your own information: `KEY`, MySql Database info and `REMINDER_POINT`.

```python
# IFTTT Info
KEY = "your_ifttt key"
IFTTT_WEBHOOKS_URL = 'https://maker.ifttt.com/trigger/{}/with/key/%s' % KEY
EVENT_NAME = "your_event_name"
# Database information
DB_HOST = "localhost"
DB_USER = "your_db_user_name"
DB_PWD = "your_db_password"
DB_NAME = "ICO"
DB_CHARSET = "utf8mb4"
# Other Setting
REMINDER_POINT = 0.05
ICO_API_URL = 'https://api.coinmarketcap.com/v1/ticker/'
```

### Set timing tasks

Set the timer task in CentOS using `crontab`.

```bash
crontab -e # Edit timing task
# Save and exit by adding a line of the following code to the timed task
*/2 * * * * python3.6 PriceReminder.py
crontab -l # View the current list of timed tasks
service crond start && service crond status # Start the timer task and check the status
```

>crontab configuration format
>    ```bash
>    *   *　 *　 *　 *　　command
>    # minute(0-59)　hour(0-23)　day(1-31)　month(1-12)　week(0-6, 0 is Sunday) command
>    # Column 1 represents minutes 1 to 59, '*' or '*/1' is every minute.
>    # Column 2 represents hours 1 to 23（0 is zero）
>    # Column 3 represents dates 1 to 31
>    # Column 4 represents months 1 through 12
>    # Column 5 marks week 0 ~ 6（0 is Sunday）
>    ```

After completing the above steps, you can wait for it to run the script every two minutes!