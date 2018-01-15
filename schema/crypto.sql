CREATE TABLE trades (
    id integer NOT NULL,
    arbitrage_id integer NOT NULL,
    exchange_id integer NOT NULL,
    trade_type integer NOT NULL,
    pair_id integer NOT NULL,
    price double precision NOT NULL,
    volume double precision NOT NULL,
    executed_volume double precision,
    deal_id character varying,
    order_book_time bigint,
    create_time bigint NOT NULL,
    execute_time bigint,
    execute_time_date timestamp without time zone
);

CREATE SEQUENCE trade_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE trade_id_seq OWNER TO postgres;

CREATE UNIQUE INDEX trade_id_uindex ON trades USING btree (id);
ALTER TABLE ONLY trades ALTER COLUMN id SET DEFAULT nextval('trade_id_seq'::regclass);

CREATE SEQUENCE trade_arbitrage_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;

ALTER TABLE trade_arbitrage_id_seq OWNER TO postgres;

CREATE UNIQUE INDEX trade_arbitrage_id_uindex ON trades USING btree (arbitrage_id);
ALTER TABLE ONLY trades ALTER COLUMN arbitrage_id SET DEFAULT nextval('trade_arbitrage_id_seq'::regclass);

--
-- Name: candle_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE candle_id_seq OWNED BY candle.id;

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
INSERT INTO public.exchange (id, name) VALUES (4, 'binance');

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
INSERT INTO public.pair (id, pair) VALUES (16, 'BTC_TO_DCR');

INSERT INTO public.pair (id, pair) VALUES (17, 'BTC_TO_NEO');
INSERT INTO public.pair (id, pair) VALUES (18, 'BTC_TO_QTUM');
INSERT INTO public.pair (id, pair) VALUES (19, 'BTC_TO_EOS');
INSERT INTO public.pair (id, pair) VALUES (20, 'BTC_TO_IOTA');
INSERT INTO public.pair (id, pair) VALUES (21, 'BTC_TO_BTG');
INSERT INTO public.pair (id, pair) VALUES (22, 'BTC_TO_WTC');
INSERT INTO public.pair (id, pair) VALUES (23, 'BTC_TO_KNC');
INSERT INTO public.pair (id, pair) VALUES (24, 'BTC_TO_BAT');
INSERT INTO public.pair (id, pair) VALUES (25, 'BTC_TO_ZRX');
INSERT INTO public.pair (id, pair) VALUES (26, 'BTC_TO_RDN');
INSERT INTO public.pair (id, pair) VALUES (27, 'BTC_TO_GAS');
INSERT INTO public.pair (id, pair) VALUES (28, 'BTC_TO_ADA');
INSERT INTO public.pair (id, pair) VALUES (29, 'BTC_TO_RCN');
INSERT INTO public.pair (id, pair) VALUES (30, 'BTC_TO_QSP');
INSERT INTO public.pair (id, pair) VALUES (31, 'BTC_TO_XBY');
INSERT INTO public.pair (id, pair) VALUES (32, 'BTC_TO_PAC');
INSERT INTO public.pair (id, pair) VALUES (33, 'BTC_TO_RDD');
INSERT INTO public.pair (id, pair) VALUES (34, 'BTC_TO_ICX');
INSERT INTO public.pair (id, pair) VALUES (35, 'BTC_TO_WABI');
INSERT INTO public.pair (id, pair) VALUES (36, 'BTC_TO_XLM');
INSERT INTO public.pair (id, pair) VALUES (37, 'BTC_TO_TRX');
INSERT INTO public.pair (id, pair) VALUES (38, 'BTC_TO_AION');
INSERT INTO public.pair (id, pair) VALUES (39, 'BTC_TO_ITC');

INSERT INTO public.pair (id, pair) VALUES (40, 'BTC_TO_ARK');
INSERT INTO public.pair (id, pair) VALUES (41, 'BTC_TO_STRAT');

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
INSERT INTO public.pair (id, pair) VALUES (1015, 'ETH_TO_NEO');
INSERT INTO public.pair (id, pair) VALUES (1016, 'ETH_TO_QTUM');
INSERT INTO public.pair (id, pair) VALUES (1017, 'ETH_TO_EOS');
INSERT INTO public.pair (id, pair) VALUES (1018, 'ETH_TO_IOTA');
INSERT INTO public.pair (id, pair) VALUES (1019, 'ETH_TO_BTG');
INSERT INTO public.pair (id, pair) VALUES (1020, 'ETH_TO_WTC');
INSERT INTO public.pair (id, pair) VALUES (1021, 'ETH_TO_KNC');
INSERT INTO public.pair (id, pair) VALUES (1022, 'ETH_TO_BAT');
INSERT INTO public.pair (id, pair) VALUES (1023, 'ETH_TO_ZRX');
INSERT INTO public.pair (id, pair) VALUES (1024, 'ETH_TO_RDN');
INSERT INTO public.pair (id, pair) VALUES (1025, 'ETH_TO_GAS');
INSERT INTO public.pair (id, pair) VALUES (1026, 'ETH_TO_ADA');
INSERT INTO public.pair (id, pair) VALUES (1027, 'ETH_TO_RCN');
INSERT INTO public.pair (id, pair) VALUES (1028, 'ETH_TO_QSP');
INSERT INTO public.pair (id, pair) VALUES (1029, 'ETH_TO_XBY');
INSERT INTO public.pair (id, pair) VALUES (1030, 'ETH_TO_PAC');
INSERT INTO public.pair (id, pair) VALUES (1031, 'ETH_TO_RDD');
INSERT INTO public.pair (id, pair) VALUES (1032, 'ETH_TO_ICX');
INSERT INTO public.pair (id, pair) VALUES (1033, 'ETH_TO_WABI');
INSERT INTO public.pair (id, pair) VALUES (1034, 'ETH_TO_XLM');
INSERT INTO public.pair (id, pair) VALUES (1035, 'ETH_TO_TRX');
INSERT INTO public.pair (id, pair) VALUES (1036, 'ETH_TO_AION');
INSERT INTO public.pair (id, pair) VALUES (1037, 'ETH_TO_ITC');

INSERT INTO public.pair (id, pair) VALUES (1038, 'ETH_TO_ARK');
INSERT INTO public.pair (id, pair) VALUES (1039, 'ETH_TO_STRAT');

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
INSERT INTO public.pair (id, pair) VALUES (3015, 'USDT_TO_NEO');
INSERT INTO public.pair (id, pair) VALUES (3016, 'USDT_TO_QTUM');
INSERT INTO public.pair (id, pair) VALUES (3017, 'USDT_TO_EOS');
INSERT INTO public.pair (id, pair) VALUES (3018, 'USDT_TO_IOTA');
INSERT INTO public.pair (id, pair) VALUES (3019, 'USDT_TO_BTG');
INSERT INTO public.pair (id, pair) VALUES (3020, 'USDT_TO_WTC');
INSERT INTO public.pair (id, pair) VALUES (3021, 'USDT_TO_KNC');
INSERT INTO public.pair (id, pair) VALUES (3022, 'USDT_TO_BAT');
INSERT INTO public.pair (id, pair) VALUES (3023, 'USDT_TO_ZRX');
INSERT INTO public.pair (id, pair) VALUES (3024, 'USDT_TO_RDN');
INSERT INTO public.pair (id, pair) VALUES (3025, 'USDT_TO_GAS');
INSERT INTO public.pair (id, pair) VALUES (3026, 'USDT_TO_ADA');
INSERT INTO public.pair (id, pair) VALUES (3027, 'USDT_TO_RCN');
INSERT INTO public.pair (id, pair) VALUES (3028, 'USDT_TO_QSP');
INSERT INTO public.pair (id, pair) VALUES (3029, 'USDT_TO_XBY');
INSERT INTO public.pair (id, pair) VALUES (3030, 'USDT_TO_PAC');
INSERT INTO public.pair (id, pair) VALUES (3031, 'USDT_TO_RDD');
INSERT INTO public.pair (id, pair) VALUES (3032, 'USDT_TO_ICX');
INSERT INTO public.pair (id, pair) VALUES (3033, 'USDT_TO_WABI');
INSERT INTO public.pair (id, pair) VALUES (3034, 'USDT_TO_XLM');
INSERT INTO public.pair (id, pair) VALUES (3035, 'USDT_TO_TRX');
INSERT INTO public.pair (id, pair) VALUES (3036, 'USDT_TO_AION');
INSERT INTO public.pair (id, pair) VALUES (3037, 'USDT_TO_ITC');
INSERT INTO public.pair (id, pair) VALUES (4000, 'USD_TO_USDT');


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