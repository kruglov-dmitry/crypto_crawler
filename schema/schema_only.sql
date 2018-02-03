--
-- PostgreSQL database dump
--

-- Dumped from database version 9.6.4
-- Dumped by pg_dump version 9.6.4

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SET check_function_bodies = false;
SET client_min_messages = warning;
SET row_security = off;

--
-- Name: postgres; Type: COMMENT; Schema: -; Owner: postgres
--

COMMENT ON DATABASE postgres IS 'default administrative connection database';


--
-- Name: plpgsql; Type: EXTENSION; Schema: -; Owner: 
--

CREATE EXTENSION IF NOT EXISTS plpgsql WITH SCHEMA pg_catalog;


--
-- Name: EXTENSION plpgsql; Type: COMMENT; Schema: -; Owner: 
--

COMMENT ON EXTENSION plpgsql IS 'PL/pgSQL procedural language';


SET search_path = public, pg_catalog;

SET default_tablespace = '';

SET default_with_oids = false;

--
-- Name: alarms; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE alarms (
    id integer NOT NULL,
    src_exchange_id integer,
    dst_exchange_id integer,
    src_pair_id integer,
    dst_pair_id integer,
    src_ask_price double precision,
    dst_bid_price double precision,
    timest bigint,
    date_time timestamp without time zone
);


ALTER TABLE alarms OWNER TO postgres;

--
-- Name: TABLE alarms; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON TABLE alarms IS 'not really normalized table. to be adapted.';


--
-- Name: alarms_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE alarms_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE alarms_id_seq OWNER TO postgres;

--
-- Name: alarms_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE alarms_id_seq OWNED BY alarms.id;


--
-- Name: candle; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE candle (
    id integer NOT NULL,
    pair_id integer NOT NULL,
    exchange_id integer NOT NULL,
    open double precision,
    close double precision,
    high double precision,
    low double precision,
    timest bigint,
    date_time timestamp without time zone
);


ALTER TABLE candle OWNER TO postgres;

--
-- Name: candle_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE candle_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE candle_id_seq OWNER TO postgres;

--
-- Name: candle_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE candle_id_seq OWNED BY candle.id;


--
-- Name: deal_type; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE deal_type (
    id integer NOT NULL,
    name character varying NOT NULL
);


ALTER TABLE deal_type OWNER TO postgres;

--
-- Name: deal_type_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE deal_type_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE deal_type_id_seq OWNER TO postgres;

--
-- Name: deal_type_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE deal_type_id_seq OWNED BY deal_type.id;


--
-- Name: exchange; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE exchange (
    id integer NOT NULL,
    name character varying
);


ALTER TABLE exchange OWNER TO postgres;

--
-- Name: exchange_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE exchange_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE exchange_id_seq OWNER TO postgres;

--
-- Name: exchange_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE exchange_id_seq OWNED BY exchange.id;


--
-- Name: order_book; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE order_book (
    id integer NOT NULL,
    pair_id integer NOT NULL,
    exchange_id integer NOT NULL,
    timest bigint,
    date_time timestamp without time zone
);


ALTER TABLE order_book OWNER TO postgres;

--
-- Name: order_book_ask; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE order_book_ask (
    id integer NOT NULL,
    order_book_id integer,
    price double precision,
    volume double precision
);


ALTER TABLE order_book_ask OWNER TO postgres;

--
-- Name: order_book_ask_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE order_book_ask_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE order_book_ask_id_seq OWNER TO postgres;

--
-- Name: order_book_ask_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE order_book_ask_id_seq OWNED BY order_book_ask.id;


--
-- Name: order_book_bid; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE order_book_bid (
    id integer NOT NULL,
    order_book_id integer,
    price double precision,
    volume double precision
);


ALTER TABLE order_book_bid OWNER TO postgres;

--
-- Name: order_book_bid_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE order_book_bid_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE order_book_bid_id_seq OWNER TO postgres;

--
-- Name: order_book_bid_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE order_book_bid_id_seq OWNED BY order_book_bid.id;


--
-- Name: order_book_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE order_book_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE order_book_id_seq OWNER TO postgres;

--
-- Name: order_book_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE order_book_id_seq OWNED BY order_book.id;


--
-- Name: order_history.py.py; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE order_history (
    id integer NOT NULL,
    pair_id integer NOT NULL,
    exchange_id integer NOT NULL,
    deal_type integer,
    price double precision NOT NULL,
    amount double precision,
    total double precision,
    timest bigint,
    date_time timestamp without time zone
);


ALTER TABLE order_history OWNER TO postgres;

--
-- Name: order_history_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE order_history_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE order_history_id_seq OWNER TO postgres;

--
-- Name: order_history_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE order_history_id_seq OWNED BY order_history.id;


--
-- Name: pair; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE pair (
    id integer NOT NULL,
    pair character varying NOT NULL
);


ALTER TABLE pair OWNER TO postgres;

--
-- Name: pair_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE pair_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE pair_id_seq OWNER TO postgres;

--
-- Name: pair_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE pair_id_seq OWNED BY pair.id;


--
-- Name: tickers; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE tickers (
    id integer NOT NULL,
    exchange_id integer NOT NULL,
    pair_id integer NOT NULL,
    lowest_ask double precision NOT NULL,
    highest_bid double precision NOT NULL,
    timest bigint NOT NULL,
    date_time timestamp without time zone
);


ALTER TABLE tickers OWNER TO postgres;

--
-- Name: tickers_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE tickers_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE tickers_id_seq OWNER TO postgres;

--
-- Name: tickers_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE tickers_id_seq OWNED BY tickers.id;


--
-- Name: alarms id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY alarms ALTER COLUMN id SET DEFAULT nextval('alarms_id_seq'::regclass);


--
-- Name: candle id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY candle ALTER COLUMN id SET DEFAULT nextval('candle_id_seq'::regclass);


--
-- Name: deal_type id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY deal_type ALTER COLUMN id SET DEFAULT nextval('deal_type_id_seq'::regclass);


--
-- Name: exchange id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY exchange ALTER COLUMN id SET DEFAULT nextval('exchange_id_seq'::regclass);


--
-- Name: order_book id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY order_book ALTER COLUMN id SET DEFAULT nextval('order_book_id_seq'::regclass);


--
-- Name: order_book_ask id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY order_book_ask ALTER COLUMN id SET DEFAULT nextval('order_book_ask_id_seq'::regclass);


--
-- Name: order_book_bid id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY order_book_bid ALTER COLUMN id SET DEFAULT nextval('order_book_bid_id_seq'::regclass);


--
-- Name: order_history.py.py id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY order_history ALTER COLUMN id SET DEFAULT nextval('order_history_id_seq'::regclass);


--
-- Name: pair id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY pair ALTER COLUMN id SET DEFAULT nextval('pair_id_seq'::regclass);


--
-- Name: tickers id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY tickers ALTER COLUMN id SET DEFAULT nextval('tickers_id_seq'::regclass);


--
-- Name: alarms alarms_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY alarms
    ADD CONSTRAINT alarms_pkey PRIMARY KEY (id);


--
-- Name: candle candle_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY candle
    ADD CONSTRAINT candle_pkey PRIMARY KEY (id);


--
-- Name: deal_type deal_type_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY deal_type
    ADD CONSTRAINT deal_type_pkey PRIMARY KEY (id);


--
-- Name: exchange exchange_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY exchange
    ADD CONSTRAINT exchange_pkey PRIMARY KEY (id);


--
-- Name: order_book_ask order_book_ask_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY order_book_ask
    ADD CONSTRAINT order_book_ask_pkey PRIMARY KEY (id);


--
-- Name: order_book_bid order_book_bid_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY order_book_bid
    ADD CONSTRAINT order_book_bid_pkey PRIMARY KEY (id);


--
-- Name: order_book order_book_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY order_book
    ADD CONSTRAINT order_book_pkey PRIMARY KEY (id);


--
-- Name: order_history.py.py order_history_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY order_history
    ADD CONSTRAINT order_history_pkey PRIMARY KEY (id);


--
-- Name: pair pair_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY pair
    ADD CONSTRAINT pair_pkey PRIMARY KEY (id);


--
-- Name: tickers tickers_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY tickers
    ADD CONSTRAINT tickers_pkey PRIMARY KEY (id);


--
-- Name: alarms_id_uindex; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX alarms_id_uindex ON alarms USING btree (id);


--
-- Name: candle_id_uindex; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX candle_id_uindex ON candle USING btree (id);


--
-- Name: exchange_id_uindex; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX exchange_id_uindex ON exchange USING btree (id);


--
-- Name: order_book_ask_id_uindex; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX order_book_ask_id_uindex ON order_book_ask USING btree (id);


--
-- Name: order_book_bid_id_uindex; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX order_book_bid_id_uindex ON order_book_bid USING btree (id);


--
-- Name: order_book_id_uindex; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX order_book_id_uindex ON order_book USING btree (id);


--
-- Name: order_history_id_uindex; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX order_history_id_uindex ON order_history USING btree (id);


--
-- Name: tickers_id_uindex; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX tickers_id_uindex ON tickers USING btree (id);


--
-- Name: alarms alarms_dst_exchange_id_fk; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY alarms
    ADD CONSTRAINT alarms_dst_exchange_id_fk FOREIGN KEY (dst_exchange_id) REFERENCES exchange(id);


--
-- Name: alarms alarms_dst_pair_id_fk; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY alarms
    ADD CONSTRAINT alarms_dst_pair_id_fk FOREIGN KEY (dst_pair_id) REFERENCES pair(id);


--
-- Name: alarms alarms_src_exchange_id_fk; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY alarms
    ADD CONSTRAINT alarms_src_exchange_id_fk FOREIGN KEY (src_exchange_id) REFERENCES exchange(id);


--
-- Name: alarms alarms_src_pair_id_fk; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY alarms
    ADD CONSTRAINT alarms_src_pair_id_fk FOREIGN KEY (src_pair_id) REFERENCES pair(id);


--
-- Name: candle candle_exchange_id_fk; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY candle
    ADD CONSTRAINT candle_exchange_id_fk FOREIGN KEY (exchange_id) REFERENCES exchange(id);


--
-- Name: candle candle_pair_id_fk; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY candle
    ADD CONSTRAINT candle_pair_id_fk FOREIGN KEY (pair_id) REFERENCES pair(id);


--
-- Name: tickers exchange_id_fk; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY tickers
    ADD CONSTRAINT exchange_id_fk FOREIGN KEY (exchange_id) REFERENCES exchange(id);


--
-- Name: order_book_ask order_book_ask_order_book_id_fk; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY order_book_ask
    ADD CONSTRAINT order_book_ask_order_book_id_fk FOREIGN KEY (order_book_id) REFERENCES order_book(id);


--
-- Name: order_book_bid order_book_bid_order_book_id_fk; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY order_book_bid
    ADD CONSTRAINT order_book_bid_order_book_id_fk FOREIGN KEY (order_book_id) REFERENCES order_book(id);


--
-- Name: order_book order_book_exchange_id_fk; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY order_book
    ADD CONSTRAINT order_book_exchange_id_fk FOREIGN KEY (exchange_id) REFERENCES exchange(id);


--
-- Name: order_book order_book_pair_id_fk; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY order_book
    ADD CONSTRAINT order_book_pair_id_fk FOREIGN KEY (pair_id) REFERENCES pair(id);


--
-- Name: order_history.py.py order_history_deal_type_id_fk; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY order_history
    ADD CONSTRAINT order_history_deal_type_id_fk FOREIGN KEY (deal_type) REFERENCES deal_type(id);


--
-- Name: order_history.py.py order_history_exchange_id__fk; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY order_history
    ADD CONSTRAINT order_history_exchange_id__fk FOREIGN KEY (exchange_id) REFERENCES exchange(id);


--
-- Name: order_history.py.py order_history_pair_id___fk; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY order_history
    ADD CONSTRAINT order_history_pair_id___fk FOREIGN KEY (pair_id) REFERENCES pair(id);


--
-- Name: tickers pair_id___fk; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY tickers
    ADD CONSTRAINT pair_id___fk FOREIGN KEY (pair_id) REFERENCES pair(id);


--
-- PostgreSQL database dump complete
--

