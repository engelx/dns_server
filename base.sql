-- Dumped from database version 9.6.3
-- Dumped by pg_dump version 9.6.3

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SET check_function_bodies = false;
SET client_min_messages = warning;
SET row_security = off;

CREATE EXTENSION IF NOT EXISTS plpgsql WITH SCHEMA pg_catalog;

COMMENT ON EXTENSION plpgsql IS 'PL/pgSQL procedural language';

SET search_path = public, pg_catalog;

SET default_tablespace = '';

SET default_with_oids = false;


CREATE USER minidns WITH PASSWORD 'minidns';
CREATE DATABASE minidns;
GRANT ALL ON DATABASE minidns TO minidns;
\c minidns

CREATE TABLE blacklist (
    host character varying(255) NOT NULL UNIQUE,
    category character varying(255) NOT NULL
);

CREATE TABLE cache (
    host character varying(2044) NOT NULL UNIQUE,
    ip character varying(2044) NOT NULL,
    fixed character varying(6) NOT NULL,
    expire integer NOT NULL
);

CREATE TABLE configuration (
    name character varying(50) NOT NULL,
    value character varying(50) NOT NULL
);


CREATE TABLE exceptions (
    ip character varying(20) NOT NULL,
    host character varying(255) NOT NULL
);

CREATE TABLE logs (
    ip character varying(2044) NOT NULL,
    date character varying(2044) NOT NULL,
    host character varying(2044) NOT NULL,
    id integer NOT NULL,
    answer character varying(200) NOT NULL
);

CREATE TABLE users (
    ip character varying(2044) NOT NULL UNIQUE,
    name character varying(2044) NOT NULL,
    "group" character varying(2044) NOT NULL
);

ALTER TABLE blacklist OWNER TO minidns;
ALTER TABLE cache OWNER TO minidns;
ALTER TABLE configuration OWNER TO minidns;
ALTER TABLE exceptions OWNER TO minidns;
ALTER TABLE logs OWNER TO minidns;
ALTER TABLE users OWNER TO minidns;

INSERT INTO "configuration" ("name", "value") VALUES ('cache_expiration', '600');
INSERT INTO "configuration" ("name", "value") VALUES ('use_block', 'True');
INSERT INTO "configuration" ("name", "value") VALUES ('redirect_blocked_ip', '10.16.100.100');
INSERT INTO "configuration" ("name", "value") VALUES ('primary_dns', '8.8.8.8');
INSERT INTO "configuration" ("name", "value") VALUES ('secondary_dns', '8.8.4.4');
INSERT INTO "configuration" ("name", "value") VALUES ('secondary_dns', '200.44.32.12');
INSERT INTO "configuration" ("name", "value") VALUES ('log_file', '/var/log/dns_server');
INSERT INTO "configuration" ("name", "value") VALUES ('debug', 'False');
INSERT INTO "configuration" ("name", "value") VALUES ('use_log', 'False');
INSERT INTO "configuration" ("name", "value") VALUES ('data_display', '1');
