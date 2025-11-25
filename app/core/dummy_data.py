import random
from datetime import datetime, timedelta
from typing import List, Dict, Any

class DummyDataManager:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DummyDataManager, cls).__new__(cls)
            cls._instance._initialize_data()
        return cls._instance
    
    def _initialize_data(self):
        # Core Portfolio State
        self.total_equity = 12450.00
        self.crypto_pct = 60
        self.stable_pct = 40
        
        # Bags
        self.short_term = {
            "value_usd": 5000.00,
            "available_usdt": 3000.00,
            "assigned_btc": 0.05,
            "pnl_24h": 120.00,
            "active_strategy": "Mean Reversion"
        }
        
        self.long_term = {
            "value_btc": 0.15,
            "value_usd": 7450.00, # Approx 0.15 * 49666
            "accumulated_btc": 0.12,
            "reserved_usdt": 1980.00,
            "total_yield_btc": 0.02,
            "active_strategy": "Trend Following"
        }
        
        # Analytics Data Generation
        self._generate_history()
        self._generate_candles()
        self._generate_trade_markers()
        
        # Logs
        self.logs = self._generate_logs()

    def _calculate_dca(self, day_index, current_btc_price_proxy):
        # Mock DCA: Assuming we bought equal amounts every 30 days
        # This is a simplified mock. 
        # For a smoother line that looks like DCA, we can just make it less volatile than Buy & Hold
        # but trending up similarly if the asset trends up.
        # Let's mock it as a dampened version of the benchmark + some steady growth
        
        # Initial capital
        initial = 10000
        
        # If day_index is 0, it's just initial
        if day_index == 0:
            return initial
            
        # Dampen the volatility of the benchmark (Buy & Hold)
        # DCA usually has lower drawdown but captures average price
        
        # We can approximate DCA performance by averaging the entry price over time
        # But since we are mocking, let's just make it a smoother curve between start and end
        # with some correlation to price.
        
        # Benchmark return
        bench_return = current_btc_price_proxy / 10000
        
        # DCA return is typically roughly half of the lump sum return in a bull market (mathematically)
        # if price goes straight up.
        # Let's approximate it:
        
        dca_return = 1 + (bench_return - 1) * 0.6 # Capture 60% of the upside/downside volatility
        
        return initial * dca_return

    def _generate_history(self):
        # Generate 6 months of data
        dates = []
        today = datetime.now()
        for i in range(180):
            dates.append((today - timedelta(days=180-i)).strftime("%Y-%m-%d"))
            
        # Equity Curve
        self.equity_series = []
        self.composition_series = []
        self.short_term_pnl_history = []
        self.long_term_growth_history = []
        
        current_equity = 10000
        benchmark_equity = 10000
        accumulated_btc = 0.0
        
        for i, date in enumerate(dates):
            # Random walk for equity
            change = random.uniform(-0.02, 0.025) # Slightly positive bias
            current_equity *= (1 + change)
            
            # Benchmark (BTC) - more volatile
            bench_change = random.uniform(-0.04, 0.045)
            benchmark_equity *= (1 + bench_change)
            
            self.equity_series.append({
                "date": date,
                "equity": round(current_equity, 2),
                "benchmark": round(benchmark_equity, 2),
                "dca_benchmark": round(self._calculate_dca(i, benchmark_equity), 2)
            })
            
            # Composition (Oscillating)
            stable = 40 + random.uniform(-5, 5)
            short = 30 + random.uniform(-5, 5)
            long_ = 100 - stable - short
            
            self.composition_series.append({
                "date": date,
                "stable": round(stable, 1),
                "short_term": round(short, 1),
                "long_term": round(long_, 1)
            })
            
            # Short Term PnL (Cumulative)
            pnl_daily = random.uniform(-50, 80)
            self.short_term_pnl_history.append({
                "date": date,
                "pnl": round(pnl_daily, 2) # This should be cumulative in a real chart usually, but let's keep it daily or cumulative? 
                                           # The chart in reference looks cumulative.
            })
            
            # Long Term Growth (Step function-ish)
            if random.random() > 0.95:
                accumulated_btc += random.uniform(0.001, 0.005)
            
            self.long_term_growth_history.append({
                "date": date,
                "btc": round(accumulated_btc, 4)
            })
            
        # Sync final values
        self.total_equity = round(current_equity, 2)
        self.long_term["accumulated_btc"] = round(accumulated_btc, 4)

    def _generate_candles(self):
        # 1. Generate Master 15m Data (10 years)
        self.candles = {}
        master_tf = "15m"
        master_minutes = 15
        days_history = 365 * 10
        
        end_time = datetime.now()
        start_time = end_time - timedelta(days=days_history)
        
        # Align start_time to nearest 15m
        start_timestamp = int(start_time.timestamp())
        start_timestamp -= start_timestamp % (master_minutes * 60)
        current_time = datetime.fromtimestamp(start_timestamp)
        
        master_candles = []
        current_price = 5000.0 # Starting price 10 years ago
        
        # Generate 15m candles
        while current_time <= end_time:
            # Random walk
            change = random.uniform(-0.005, 0.005) * (master_minutes / 60) # Scale volatility
            close = current_price * (1 + change)
            high = max(current_price, close) * (1 + random.uniform(0, 0.002))
            low = min(current_price, close) * (1 - random.uniform(0, 0.002))
            
            master_candles.append({
                "time": int(current_time.timestamp()),
                "open": round(current_price, 2),
                "high": round(high, 2),
                "low": round(low, 2),
                "close": round(close, 2)
            })
            
            current_price = close
            current_time += timedelta(minutes=master_minutes)
            
        self.candles["15m"] = master_candles
        
        # 2. Aggregate for other timeframes
        self.candles["1h"] = self._aggregate_candles(master_candles, 60)
        self.candles["4h"] = self._aggregate_candles(master_candles, 240)
        self.candles["1d"] = self._aggregate_candles(master_candles, 1440)
        self.candles["1w"] = self._aggregate_candles(master_candles, 10080)
        self.candles["1M"] = self._aggregate_candles(master_candles, 43200)

    def _aggregate_candles(self, source_candles, target_minutes):
        if not source_candles:
            return []
            
        aggregated = []
        target_seconds = target_minutes * 60
        
        # Align first candle
        first_time = source_candles[0]["time"]
        current_bucket_start = first_time - (first_time % target_seconds)
        
        current_candle = None
        
        for candle in source_candles:
            candle_time = candle["time"]
            
            # Determine which bucket this candle belongs to
            bucket_start = candle_time - (candle_time % target_seconds)
            
            if current_candle and bucket_start != current_bucket_start:
                # Close current candle and start new one
                aggregated.append(current_candle)
                current_candle = None
                current_bucket_start = bucket_start
            
            if current_candle is None:
                current_candle = {
                    "time": bucket_start,
                    "open": candle["open"],
                    "high": candle["high"],
                    "low": candle["low"],
                    "close": candle["close"]
                }
            else:
                # Update current candle
                current_candle["high"] = max(current_candle["high"], candle["high"])
                current_candle["low"] = min(current_candle["low"], candle["low"])
                current_candle["close"] = candle["close"]
                
        if current_candle:
            aggregated.append(current_candle)
            
        return aggregated

    def get_candles(self, timeframe="1h", start: int = None, end: int = None):
        # For simplicity in this mock, we won't implement complex live aggregation on every request.
        # We will just return the pre-generated aggregated data.
        # Live updates would ideally append to 15m and then re-aggregate or update the last candle of each timeframe.
        
        # To support live updates properly with aggregation:
        # 1. Get master 15m candles (including any new live ones)
        # 2. If we want to be perfect, we'd re-aggregate the last portion.
        # For now, let's just return the static generated data to ensure consistency, 
        # as the user specifically asked for consistency check.
        
        # If we want "Live" updates, we should update self.candles["15m"] and then update the others.
        # But let's stick to the requested "Consistency" first.
        
        all_candles = self.candles.get(timeframe, [])
        
        # Pagination
        filtered_candles = all_candles
        
        if start:
            filtered_candles = [c for c in filtered_candles if c["time"] >= start]
        
        if end:
            filtered_candles = [c for c in filtered_candles if c["time"] <= end]
            
        if not start and not end:
            return filtered_candles[-1000:]
            
        return filtered_candles

    def _generate_trade_markers(self):
        self.trade_markers = []
        # Generate some dummy trades
        for i in range(10):
            self.trade_markers.append({
                "time": int((datetime.now() - timedelta(days=i)).timestamp()),
                "position": "belowBar" if i % 2 == 0 else "aboveBar",
                "color": "#10b981" if i % 2 == 0 else "#ef4444",
                "shape": "arrowUp" if i % 2 == 0 else "arrowDown",
                "text": f"{'BUY' if i % 2 == 0 else 'SELL'} @ {50000 + i*100}"
            })

    def get_trade_markers(self):
        return self.trade_markers

    def _generate_logs(self):
        return [
            {"time": datetime.now().isoformat(), "type": "INFO", "message": "System initialized"},
            {"time": (datetime.now() - timedelta(minutes=5)).isoformat(), "type": "TRADE", "message": "Executed BUY BTC @ 55000"}
        ]

    def get_logs(self, limit=50):
        return self.logs[:limit]
    
    def get_summary(self):
        """Portfolio summary"""
        return {
            "total_equity": self.total_equity,
            "crypto_pct": self.crypto_pct,
            "stable_pct": self.stable_pct,
            "short_term_value": self.short_term["value_usd"],
            "long_term_value": self.long_term["value_usd"]
        }
    
    def get_bags(self):
        """Returns short term and long term bags"""
        return {
            "short_term": self.short_term,
            "long_term": self.long_term
        }
    
    def get_equity_curve(self):
        """Returns historical equity data"""
        return self.equity_series
    
    def get_composition(self):
        """Returns portfolio composition over time"""
        return self.composition_series
    
    def get_short_term_performance(self):
        """Returns short term PnL history"""
        return self.short_term_pnl_history
    
    def get_long_term_performance(self):
        """Returns long term growth history"""
        return self.long_term_growth_history

