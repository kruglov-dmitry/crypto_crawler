-- How to create indexes:
CREATE INDEX CONCURRENTLY order_history_oha ON order_history (amount);

-- 1. Moving BIDS to ASKS for Poloniex
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

-- 2. Moving ASKS to BIDS for Poloniex
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

-- 3. Moving BIDS to ASKS for Kraken
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

-- 4. Moving ASKS to BIDS for Poloniex
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


-- Removing dubplicate rows:
DELETE FROM tablename
WHERE id IN (SELECT id
    FROM (SELECT id,
    ROW_NUMBER() OVER (partition BY column1, column2, column3 ORDER BY id) AS rnum
    FROM tablename) t
WHERE t.rnum > 1);

-- candle:
-- pair_id | exchange_id |  open   | close  |  high   | low  |   timest
delete from candle WHERE id IN (SELECT id
              FROM (SELECT id,
                             ROW_NUMBER() OVER (partition BY pair_id, exchange_id, open, close, high, low, timest ORDER BY id) AS rnum
                     FROM candle) t
              WHERE t.rnum > 1);


-- clean order history
delete from order_history WHERE id IN (SELECT id
              FROM (SELECT id,
                             ROW_NUMBER() OVER (partition BY pair_id, exchange_id, deal_type, price, amount, timest ORDER BY id) AS rnum
                     FROM order_history) t
              WHERE t.rnum > 1);