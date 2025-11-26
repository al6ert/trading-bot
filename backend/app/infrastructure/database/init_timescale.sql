-- Enable TimescaleDB extension
CREATE EXTENSION IF NOT EXISTS timescaledb;

-- Convert tables to Hypertables
-- We use 'if_not_exists => TRUE' to avoid errors on restart

SELECT create_hypertable('portfolio_snapshots', 'time', if_not_exists => TRUE);
SELECT create_hypertable('trade_logs', 'time', if_not_exists => TRUE);
SELECT create_hypertable('market_candles', 'time', if_not_exists => TRUE);
