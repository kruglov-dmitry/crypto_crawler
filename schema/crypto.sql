--
-- refactor schema data etc
--

CREATE TABLE public.candle
(
    id integer DEFAULT nextval('candle_id_seq'::regclass) PRIMARY KEY NOT NULL,
    pair_id integer NOT NULL,
    exchange_id integer NOT NULL,
    open double precision,
    close double precision,
    high double precision,
    low double precision,
    timest bigint,
    date_time timestamp,
    CONSTRAINT candle_pair_id_fk FOREIGN KEY (pair_id) REFERENCES pair (id),
    CONSTRAINT candle_exchange_id_fk FOREIGN KEY (exchange_id) REFERENCES exchange (id)
);
CREATE UNIQUE INDEX candle_id_uindex ON public.candle (id);

CREATE TABLE public.deal_type
(
    id integer DEFAULT nextval('deal_type_id_seq'::regclass) PRIMARY KEY NOT NULL,
    name varchar NOT NULL
);
INSERT INTO public.deal_type (id, name) VALUES (1, 'sell');
INSERT INTO public.deal_type (id, name) VALUES (2, 'buy');

CREATE TABLE public.exchange
(
    id integer DEFAULT nextval('exchange_id_seq'::regclass) PRIMARY KEY NOT NULL,
    name varchar
);
CREATE UNIQUE INDEX exchange_id_uindex ON public.exchange (id);
INSERT INTO public.exchange (id, name) VALUES (1, 'poloniex');
INSERT INTO public.exchange (id, name) VALUES (2, 'kraken');
INSERT INTO public.exchange (id, name) VALUES (3, 'bittrex');

CREATE TABLE public.order_book
(
    id integer DEFAULT nextval('order_book_id_seq'::regclass) PRIMARY KEY NOT NULL,
    pair_id integer NOT NULL,
    exchange_id integer NOT NULL,
    timest bigint,
    date_time timestamp,
    CONSTRAINT order_book_pair_id_fk FOREIGN KEY (pair_id) REFERENCES pair (id),
    CONSTRAINT order_book_exchange_id_fk FOREIGN KEY (exchange_id) REFERENCES exchange (id)
);
CREATE UNIQUE INDEX order_book_id_uindex ON public.order_book (id);

CREATE TABLE public.order_book_ask
(
    id integer DEFAULT nextval('order_book_ask_id_seq'::regclass) PRIMARY KEY NOT NULL,
    order_book_id integer,
    price double precision,
    volume double precision,
    CONSTRAINT order_book_ask_order_book_id_fk FOREIGN KEY (order_book_id) REFERENCES order_book (id)
);
CREATE UNIQUE INDEX order_book_ask_id_uindex ON public.order_book_ask (id);

CREATE TABLE public.order_book_bid
(
    id integer DEFAULT nextval('order_book_bid_id_seq'::regclass) PRIMARY KEY NOT NULL,
    order_book_id integer,
    price double precision,
    volume double precision,
    CONSTRAINT order_book_bid_order_book_id_fk FOREIGN KEY (order_book_id) REFERENCES order_book (id)
);
CREATE UNIQUE INDEX order_book_bid_id_uindex ON public.order_book_bid (id);

CREATE TABLE public.order_history
(
    id integer DEFAULT nextval('order_history_id_seq'::regclass) PRIMARY KEY NOT NULL,
    pair_id integer NOT NULL,
    exchange_id integer NOT NULL,
    deal_type integer,
    price double precision NOT NULL,
    amount double precision,
    total double precision,
    timest bigint,
    date_time timestamp,
    CONSTRAINT order_history_pair_id___fk FOREIGN KEY (pair_id) REFERENCES pair (id),
    CONSTRAINT order_history_exchange_id__fk FOREIGN KEY (exchange_id) REFERENCES exchange (id),
    CONSTRAINT order_history_deal_type_id_fk FOREIGN KEY (deal_type) REFERENCES deal_type (id)
);
CREATE UNIQUE INDEX order_history_id_uindex ON public.order_history (id);

CREATE TABLE public.pair
(
    id integer DEFAULT nextval('pair_id_seq'::regclass) PRIMARY KEY NOT NULL,
    pair varchar NOT NULL
);
INSERT INTO public.pair (id, pair) VALUES (1, 'BTC_TO_DASH');
INSERT INTO public.pair (id, pair) VALUES (2, 'BTC_TO_ETH');
INSERT INTO public.pair (id, pair) VALUES (3, 'BTC_TO_LTC');
INSERT INTO public.pair (id, pair) VALUES (4, 'BTC_TO_XRP');
INSERT INTO public.pair (id, pair) VALUES (5, 'BTC_TO_BCC');
INSERT INTO public.pair (id, pair) VALUES (6, 'BTC_TO_ETC');
INSERT INTO public.pair (id, pair) VALUES (7, 'BTC_TO_SC');
INSERT INTO public.pair (id, pair) VALUES (8, 'BTC_TO_DGB');
INSERT INTO public.pair (id, pair) VALUES (9, 'BTC_TO_XEM');
INSERT INTO public.pair (id, pair) VALUES (10, 'BTC_TO_ARDR');
INSERT INTO public.pair (id, pair) VALUES (11, 'BTC_TO_OMG');
INSERT INTO public.pair (id, pair) VALUES (12, 'BTC_TO_ZEC');
INSERT INTO public.pair (id, pair) VALUES (13, 'BTC_TO_REP');
INSERT INTO public.pair (id, pair) VALUES (14, 'BTC_TO_XMR');
INSERT INTO public.pair (id, pair) VALUES (15, 'BTC_TO_DOGE');
INSERT INTO public.pair (id, pair) VALUES (1001, 'ETH_TO_DASH');
INSERT INTO public.pair (id, pair) VALUES (1002, 'ETH_TO_BTC');
INSERT INTO public.pair (id, pair) VALUES (1003, 'ETH_TO_LTC');
INSERT INTO public.pair (id, pair) VALUES (1004, 'ETH_TO_XRP');
INSERT INTO public.pair (id, pair) VALUES (1005, 'ETH_TO_BCC');
INSERT INTO public.pair (id, pair) VALUES (1006, 'ETH_TO_ETC');
INSERT INTO public.pair (id, pair) VALUES (1007, 'ETH_TO_SC');
INSERT INTO public.pair (id, pair) VALUES (1008, 'ETH_TO_DGB');
INSERT INTO public.pair (id, pair) VALUES (1009, 'ETH_TO_XEM');
INSERT INTO public.pair (id, pair) VALUES (1010, 'ETH_TO_ARDR');
INSERT INTO public.pair (id, pair) VALUES (1011, 'ETH_TO_OMG');
INSERT INTO public.pair (id, pair) VALUES (1012, 'ETH_TO_ZEC');
INSERT INTO public.pair (id, pair) VALUES (1013, 'ETH_TO_REP');
INSERT INTO public.pair (id, pair) VALUES (1014, 'ETH_TO_XMR');
INSERT INTO public.pair (id, pair) VALUES (2001, 'USD_TO_DASH');
INSERT INTO public.pair (id, pair) VALUES (2002, 'USD_TO_ETH');
INSERT INTO public.pair (id, pair) VALUES (2003, 'USD_TO_LTC');
INSERT INTO public.pair (id, pair) VALUES (2004, 'USD_TO_XRP');
INSERT INTO public.pair (id, pair) VALUES (2005, 'USD_TO_BCC');
INSERT INTO public.pair (id, pair) VALUES (2006, 'USD_TO_ETC');
INSERT INTO public.pair (id, pair) VALUES (2007, 'USD_TO_SC');
INSERT INTO public.pair (id, pair) VALUES (2008, 'USD_TO_DGB');
INSERT INTO public.pair (id, pair) VALUES (2009, 'USD_TO_XEM');
INSERT INTO public.pair (id, pair) VALUES (2010, 'USD_TO_ARDR');
INSERT INTO public.pair (id, pair) VALUES (2011, 'USD_TO_BTC');
INSERT INTO public.pair (id, pair) VALUES (2012, 'USD_TO_ZEC');
INSERT INTO public.pair (id, pair) VALUES (2013, 'USD_TO_REP');
INSERT INTO public.pair (id, pair) VALUES (2014, 'USD_TO_XMR');
INSERT INTO public.pair (id, pair) VALUES (3001, 'USDT_TO_DASH');
INSERT INTO public.pair (id, pair) VALUES (3002, 'USDT_TO_ETH');
INSERT INTO public.pair (id, pair) VALUES (3003, 'USDT_TO_LTC');
INSERT INTO public.pair (id, pair) VALUES (3004, 'USDT_TO_XRP');
INSERT INTO public.pair (id, pair) VALUES (3005, 'USDT_TO_BCC');
INSERT INTO public.pair (id, pair) VALUES (3006, 'USDT_TO_ETC');
INSERT INTO public.pair (id, pair) VALUES (3007, 'USDT_TO_SC');
INSERT INTO public.pair (id, pair) VALUES (3008, 'USDT_TO_DGB');
INSERT INTO public.pair (id, pair) VALUES (3009, 'USDT_TO_XEM');
INSERT INTO public.pair (id, pair) VALUES (3010, 'USDT_TO_ARDR');
INSERT INTO public.pair (id, pair) VALUES (3011, 'USDT_TO_BTC');
INSERT INTO public.pair (id, pair) VALUES (3012, 'USDT_TO_ZEC');
INSERT INTO public.pair (id, pair) VALUES (3013, 'USDT_TO_REP');
INSERT INTO public.pair (id, pair) VALUES (3014, 'USDT_TO_XMR');


CREATE TABLE public.tickers
(
    id integer DEFAULT nextval('tickers_id_seq'::regclass) PRIMARY KEY NOT NULL,
    exchange_id integer NOT NULL,
    pair_id integer NOT NULL,
    lowest_ask double precision NOT NULL,
    highest_bid double precision NOT NULL,
    timest bigint NOT NULL,
    date_time timestamp,
    CONSTRAINT exchange_id_fk FOREIGN KEY (exchange_id) REFERENCES exchange (id),
    CONSTRAINT pair_id___fk FOREIGN KEY (pair_id) REFERENCES pair (id)
);
CREATE UNIQUE INDEX tickers_id_uindex ON public.tickers (id);

CREATE TABLE public.alarms
(
    id integer DEFAULT nextval('alarms_id_seq'::regclass) PRIMARY KEY NOT NULL,
    src_exchange_id integer,
    dst_exchange_id integer,
    src_pair_id integer,
    dst_pair_id integer,
    src_ask_price double precision,
    dst_bid_price double precision,
    timest bigint,
    date_time timestamp,
    CONSTRAINT alarms_src_exchange_id_fk FOREIGN KEY (src_exchange_id) REFERENCES exchange (id),
    CONSTRAINT alarms_dst_exchange_id_fk FOREIGN KEY (dst_exchange_id) REFERENCES exchange (id),
    CONSTRAINT alarms_src_pair_id_fk FOREIGN KEY (src_pair_id) REFERENCES pair (id),
    CONSTRAINT alarms_dst_pair_id_fk FOREIGN KEY (dst_pair_id) REFERENCES pair (id)
);
CREATE UNIQUE INDEX alarms_id_uindex ON public.alarms (id);