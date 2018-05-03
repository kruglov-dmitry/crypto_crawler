# DEPLOY - HOWTO
## Prerequsities:
* redis in place
* postgres in place with proper schema
FIXME: automate this part as part of ticket https://gitlab.com/crypto_trade/crypto_crawler/issues/23
sudo service docker start
cd ~/deploy
sudo /usr/local/bin/docker-compose -f docker_compose.yml up
/home/ec2-user/crypto_crawler/deploy
python update_nonce_redis.py


## Deploying data retrieval services: order_book, history, tickers and notification
python deploy_data_retrieval

## Deploying arbitrage bots
1. verify settings at config file:
more deploy/deploy.cfg
2. Initiate deployment processes
python deploy_arbitrage_bots.py deploy/deploy.cfg

### How to run dedicated services from subfolder:
``` bash
python -m services.telegram_notifier
```
## Kill ALL processes
``` bash
ps -ef | grep arbitrage | awk '{print $2}' | xargs kill -9 $1
```
or just
``` bash
pkill python
```

## Kill ALL screens with all session MacOs
``` bash
screen -ls | awk '{print $1}' | xargs -I{} screen -S {} -X quit
```
screen -ls | grep -v deploy | awk '{print $1}' | xargs -I{} screen -S {} -X quit
based on  https://stackoverflow.com/questions/1509677/kill-detached-screen-session

``` bash
alias cleanscreen="screen -ls | tail -n +2 | head -n -1|cut -d'.' -f 1 |xargs kill -9 ; screen -wipe"

alias bot_count='ps -ef | grep python | wc -l'
alias bot_kill='pkill python'
alias bot_stop_screen="screen -ls | tail -n +2 | head -n -1|cut -d'.' -f 1 |xargs kill -9 ; screen -wipe"
```

## Rename existing screen session
``` bash
screen -S old_session_name -X sessionname new_session_name
```

### REMOTE_ACCESS:
``` bash
ssh -v -N -L 7777:192.168.1.106:5432 86.97.142.164 -i .ssh/crptdb_sec_openssh -l dima -p 8883
ssh -i .ssh/crptdb_sec_openssh -v dima@86.97.142.164 -p 8883
ssh dima@86.96.108.235 -p 8883
```

### MacOs dependencies:
``` bash
pip install python-telegram-bot --user
```

### redis
type <key>
and depending on the response perform:

https://lzone.de/cheat-sheet/Redis
for "string": get <key>
for "hash": hgetall <key>
for "list": lrange <key> 0 -1
for "set": smembers <key>
for "zset": zrange <key> 0 -1 withscores

### POSTGRES
https://wiki.postgresql.org/wiki/Deleting_duplicates

Postgres backups:
``` bash
pg_dump -h 192.168.1.106 -p 5432 -U postgres -F c -b -v -f "/home/dima/full_DDMMYYYY"
pg_dump -h 192.168.1.106 -p 5432 -U postgres -s public
-- How to do full dump without particular tables
pg_dump -h 192.168.1.106 -p 5432 -U postgres -F c -b -v --exclude-table=alarams --exclude-table=tmp_binance_orders --exclude-table=tmp_history_trades --exclude-table=tmp_trades --exclude-table=trades -f "/home/dima/full_DDMMYYYY"
```

AWS:
``` bash
psql --host=orders.cervsj06c8zw.us-west-1.rds.amazonaws.com --port=5432 --username=postgres --password --dbname=crypto
```


### TELEGRAM BOT
How to get ID of telegram chat:
https://api.telegram.org/bot<YourBOTToken>/getUpdates

"""
How to check what the fuck is happening with the bot:
https://api.telegram.org/bot438844686:AAE8lS3VyMsNgtytR4I1uWy4DLUaot2e5hU/getUpdates

"""


### Get all tradable pairs
https://www.binance.com/api/v1/ticker/allBookTickers
https://bittrex.com/api/v1.1/public/getmarkets

https://api.kraken.com/0/public/Assets
https://api.kraken.com/0/public/AssetPairs

https://poloniex.com/public?command=returnTicker

http://api.huobi.pro/v1/common/symbols


### Rounding rules

https://support.binance.com/hc/en-us/articles/115000594711-Trading-Rule


### Setup balance monitoring from the scratch
``` bash
sudo curl -L https://github.com/docker/compose/releases/download/1.18.0/docker-compose-`uname -s`-`uname -m` -o /usr/local/bin/docker-compose
sudo yum install docker, mc, git
sudo service docker start
sudo /usr/local/bin/docker-compose -f docker_compose.yml up
scp -i wtf.pem -r crypto_crawler/secret_keys/ ec2-user@ec2-54-183-153-123.us-west-1.compute.amazonaws.com:/tmp/
```


### sysops
``` bash
sudo logrotate -s /var/log/logstatus /etc/logrotate.conf
/home/ec2-user/crypto_crawler/logs/*.log {
    size 10M
    compress
    rotate 10
    nodateext
    missingok
    notifempty
}

sudo vim /etc/crontab
*/5 * * * * root logrotate -f /etc/logrotate.conf
```

https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/USER_VPC.Scenarios.html#USER_VPC.Scenario3


### Logs analysis

How to find last modified files recursively:
``` bash
find $1 -type f -print0 | xargs -0 stat --format '%Y :%y %n' | sort -nr | cut -d: -f2- | head
```


### Anaconda profit report How-TO Windows
1. Install https://www.anaconda.com/download/ for 2.7 Python
2. Run  Start->Programs->Anaconda Prompt
3. Install necessary dependencies using pip:
``` bash
    pip install redis tqdm
```
4. Run Start->Programs->Jupiter Notebook
5. Open Notebook from ipython_notebooks/iPython_local_Input.ipynb
6. Adjust following parameters:
* CRYPTO_MODULE
* should_fetch_data
* time_end
* time_start
* api_key_full_path
7. Sequentially execute all sells
8. Profit report should be under your %HOME%/logs folder



### How to setup dynuiuc domain name update
```bash
more /usr/lib/systemd/system/dynuiuc.service
[Unit]
Description=Dynu

[Service]
Type=forking
PIDFile=/var/run/dynuiuc.pid
ExecStart=/usr/bin/dynuiuc --conf_file /etc/dynuiuc/dynuiuc.conf --log_file /var/log/dynuiuc.log --pid_file /var/run/dynuiuc.pid --daemon
ExecReload=/bin/kill -HUP $MAINPID
# DK manually
Restart=always

[Install]
WantedBy=multi-user.target
```
sudo systemctl enable dynuiuc.service
sudo service dynuiuc start