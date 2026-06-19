# Dataset reference

Tessera serves **gold** datasets — deduplicated, quality-checked, backtest-ready Parquet built
from raw Hyperliquid trade data. Each dataset is partitioned by `coin` and `month` (`YYYY-MM`),
covers **October 2025 onward**, and every row carries a `time` (UTC `Datetime`) and `coin` column.

| Dataset | Granularity | Tier | Contents |
| --- | --- | --- | --- |
| `gold_ohlcv_1m` | 1 minute | Free + Pro | Order-flow-enriched OHLCV candles |
| `gold_funding_1h` | 1 hour | Pro | Funding rates |
| `gold_positioning_1h` | 1 hour | Pro | Open-interest / positioning analytics |

**Free tier** covers BTC, ETH, SOL, HYPE. **Pro** unlocks every coin — 250+ symbols including
HIP-3 markets and `xyz:`-prefixed equity/commodity perps (e.g. `xyz:NVDA`, `xyz:GOLD`) — plus the
funding and positioning datasets. See [pricing](https://tesseralytics.dev).

## `gold_ohlcv_1m`

Minute candles enriched with order-flow microstructure.

| Column | Type | Meaning |
| --- | --- | --- |
| `time` | datetime | Bar start (UTC) |
| `coin` | str | Coin symbol |
| `open` / `high` / `low` / `close` | f64 | OHLC price |
| `volume` | f64 | Traded volume |
| `buy_vol` / `sell_vol` | f64 | Aggressor buy / sell volume |
| `aggressor_delta` | f64 | `buy_vol − sell_vol` for the bar |
| `cvd` | f64 | Cumulative volume delta |
| `trade_count` | u32 | Number of trades |
| `unique_takers` | u32 | Distinct taker accounts |
| `vwap` | f64 | Volume-weighted average price |
| `total_fees` / `taker_fees` / `maker_fees` | f64 | Fees attributed to the bar |
| `taker_open_long_vol` / `taker_open_short_vol` | f64 | Taker volume opening longs / shorts |
| `taker_close_long_vol` / `taker_close_short_vol` | f64 | Taker volume closing longs / shorts |
| `closed_pnl_long` / `closed_pnl_short` | f64 | Realised PnL from closed longs / shorts |
| `funding_rate` | f64 | Funding rate in effect |
| `bootstrap_source` | str | Provenance of the bar |

## `gold_funding_1h`

| Column | Type | Meaning |
| --- | --- | --- |
| `time` | datetime | Hour (UTC) |
| `coin` | str | Coin symbol |
| `funding_rate` | f64 | Hourly funding rate |
| `annualized` | f64 | Annualised funding rate |
| `cum_funding` | f64 | Cumulative funding |
| `bootstrap_source` | str | Provenance |

## `gold_positioning_1h`

Open-interest and crowd-positioning analytics (selected columns):

| Column | Type | Meaning |
| --- | --- | --- |
| `time` | datetime | Hour (UTC) |
| `coin` | str | Coin symbol |
| `open_interest` / `d_open_interest` | f64 | Open interest and its hourly change |
| `n_long_positions` / `n_short_positions` | u32 | Open long / short positions |
| `account_ls_ratio` | f64 | Account long/short ratio |
| `top10_long_share` / `top10_short_share` | f64 | Share of OI held by the top 10 accounts |
| `concentration_skew` / `hhi_gross` | f64 | Concentration metrics |
| `whale_net_position` / `whale_long_account_share` / `n_whale_accounts` | f64 / f64 / u32 | Whale positioning |
| `n_new_longs` / `n_new_shorts` / `n_closed_longs` / `n_closed_shorts` | u32 | Position open/close counts |
| `n_flipped_l2s` / `n_flipped_s2l` | u32 | Long→short / short→long flips |
| `aggressor_delta_1h` / `net_taker_open_1h` | f64 | Hourly order-flow aggregates |

!!! tip
    Schemas evolve. Inspect the live column set without downloading data:
    `client.scan("gold_ohlcv_1m", "BTC", "<month>").collect_schema()`.

## Discovering coverage

```python
client.partitions("gold_ohlcv_1m", coin="BTC")   # which months exist for BTC?
client.datasets()                                  # coins + month range per dataset
```
