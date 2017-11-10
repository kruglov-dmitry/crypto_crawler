How to kill all processes:
ps -ef | grep arbitrage | awk '{print $2}' | xargs kill -9 $1

Postgres related stuff:
pg_dump -h 192.168.1.106 -p 5432 -U postgres -F c -b -v -f "/home/dima/full_DDMMYYYY"
pg_dump -h 192.168.1.106 -p 5432 -U postgres -s public

select last_value from order_book_ask_id_seq;
260411979
select last_value from order_book_bid_id_seq;
69942433
select last_value from order_book_id_seq;
191289

1. Moving BIDS to ASKS for Poloniex
WITH moved_rows AS (
    DELETE FROM order_book_bid a
    USING order_book b
    WHERE b.exchange_id = 1 and -- poloniex
	a.order_book_id = b.id and
	a.id < 69942433 and b.id < 191289
    RETURNING a.* -- or specify columns
)
INSERT INTO order_book_ask (order_book_id, price, volume) --specify columns if necessary
SELECT order_book_id, price, volume FROM moved_rows;

2. Moving ASKS to BIDS for Poloniex
WITH moved_rows AS (
    DELETE FROM order_book_ask a
    USING order_book b
    WHERE b.exchange_id = 1 and -- poloniex
	a.order_book_id = b.id and
	a.id < 260411979 and b.id < 191289
    RETURNING a.* -- or specify columns
)
INSERT INTO order_book_bid (order_book_id, price, volume) --specify columns if necessary
SELECT order_book_id, price, volume FROM moved_rows;

3. Moving BIDS to ASKS for Kraken
WITH moved_rows AS (
    DELETE FROM order_book_bid a
    USING order_book b
    WHERE b.exchange_id = 2 and -- kraken
	a.order_book_id = b.id and
	a.id < 69942433 and b.id < 191289
    RETURNING a.* -- or specify columns
)
INSERT INTO order_book_ask (order_book_id, price, volume) --specify columns if necessary
SELECT order_book_id, price, volume FROM moved_rows;

4. Moving ASKS to BIDS for Poloniex
WITH moved_rows AS (
    DELETE FROM order_book_ask a
    USING order_book b
    WHERE b.exchange_id = 2 and -- poloniex
	a.order_book_id = b.id and
	a.id < 260411979 and b.id < 191289
    RETURNING a.* -- or specify columns
)
INSERT INTO order_book_bid (order_book_id, price, volume) --specify columns if necessary
SELECT order_book_id, price, volume FROM moved_rows;



"""
How to check what the fuck is happening with the bot:
https://api.telegram.org/bot438844686:AAE8lS3VyMsNgtytR4I1uWy4DLUaot2e5hU/getUpdates

"""

# https://github.com/toorop/go-bittrex/blob/master/bittrex.go
