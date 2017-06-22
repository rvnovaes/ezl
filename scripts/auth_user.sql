--
-- PostgreSQL database dump
--

SET statement_timeout = 0;
SET lock_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SET check_function_bodies = false;
SET client_min_messages = warning;

SET search_path = public, pg_catalog;

SET default_tablespace = '';

SET default_with_oids = false;

--
-- Name: auth_user; Type: TABLE; Schema: public; Owner: gsnasc; Tablespace: 
--

CREATE TABLE auth_user (
    id integer NOT NULL,
    password character varying(128) NOT NULL,
    last_login timestamp with time zone,
    is_superuser boolean NOT NULL,
    username character varying(150) NOT NULL,
    first_name character varying(30) NOT NULL,
    last_name character varying(30) NOT NULL,
    email character varying(254) NOT NULL,
    is_staff boolean NOT NULL,
    is_active boolean NOT NULL,
    date_joined timestamp with time zone NOT NULL
);


ALTER TABLE auth_user OWNER TO gsnasc;

--
-- Name: auth_user_id_seq; Type: SEQUENCE; Schema: public; Owner: gsnasc
--

CREATE SEQUENCE auth_user_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE auth_user_id_seq OWNER TO gsnasc;

--
-- Name: auth_user_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: gsnasc
--

ALTER SEQUENCE auth_user_id_seq OWNED BY auth_user.id;


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: gsnasc
--

ALTER TABLE ONLY auth_user ALTER COLUMN id SET DEFAULT nextval('auth_user_id_seq'::regclass);


--
-- Data for Name: auth_user; Type: TABLE DATA; Schema: public; Owner: gsnasc
--

COPY auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) FROM stdin;
1	pbkdf2_sha256$36000$0UcZvFKNq3W9$7/0s/p9OKORszWjuUjDLK9SSqixZKnb5OxGpNnvVRM8=	\N	f	john			jlennon@beatles.com	f	t	2017-06-12 12:26:48.176584-03
2	pbkdf2_sha256$36000$YGw6DkdX0gOv$HkxOUkqKoYs/j/9KKf8IyloZZbE2jBfAG20eGB2H0iI=	2017-06-21 14:17:55.16022-03	f	dev			dev@dev.com	f	t	2017-06-12 12:27:24.46849-03
\.


--
-- Name: auth_user_id_seq; Type: SEQUENCE SET; Schema: public; Owner: gsnasc
--

SELECT pg_catalog.setval('auth_user_id_seq', 3, true);


--
-- Name: auth_user_pkey; Type: CONSTRAINT; Schema: public; Owner: gsnasc; Tablespace: 
--

ALTER TABLE ONLY auth_user
    ADD CONSTRAINT auth_user_pkey PRIMARY KEY (id);


--
-- Name: auth_user_username_key; Type: CONSTRAINT; Schema: public; Owner: gsnasc; Tablespace: 
--

ALTER TABLE ONLY auth_user
    ADD CONSTRAINT auth_user_username_key UNIQUE (username);


--
-- Name: auth_user_username_6821ab7c_like; Type: INDEX; Schema: public; Owner: gsnasc; Tablespace: 
--

CREATE INDEX auth_user_username_6821ab7c_like ON auth_user USING btree (username varchar_pattern_ops);


--
-- PostgreSQL database dump complete
--

