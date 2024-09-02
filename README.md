# python-backtesting-template
Trading strategy template that uses Python `backtesting` library. It lets you focus on improving your price forecasts and reduces the time and effort spent on auxiliary tasks.

# Understanding the Benefits of This Repo

Just like with the original Python `backtesting` package, you can obtain and use `stats`, `trades`, and interactive charts in HTML files. In addition, this repository solves many problems that the `backtesting` library does not solve.

1. You can easily run backtests of your strategy for several (or several dozen) tickers simultaneously. The results of these backtests are combined and saved in the `output.xlsx` file. For details, explore files in the `strategy` folder.

2. The `run_backtest_for_ticker` function returns not only `stats` and `trades` but also `last_day_result` dict. It allows you to send notifications if the trading signal is detected. For details, see the `utils/strategy_exec/last_day.py` file and `next` function.

3. The system updates trailing stop-loss daily using the Average True Range (ATR) multiplied by 2.5. If a volatility outbreak (`tr_delta` high value) is detected, the stop loss is tightened. You can customize this behavior in `utils/strategy_exec/stop_loss.py` file.

4. If it's possible to close half of the active position and make the remaining half risk-free, the system will do so. See the file `utils/strategy_exec/partial_close.py` for details. You can easily change or disable this behavior if you wish.

5. In addition to partial closures, the system handles many other special situations. For details, see the `utils/strategy_exec/special_situations.py` file. You are encouraged to modify the list of special situations, change the order of their processing, and add your custom special situations.

6. You can set the maximum duration for long and short trades. See the `process_max_duration` function for details.

7. You can analyze trades in many different ways. The system adds tags to many trades that explain their fate. Each trade can contain several tags. For details, explore the `add_tag_to_trades_and_close_position` function code and where it is called. See also the functions `add_feature_to_trades` and `get_stat_and_trades_for_ticker`. 

8. You can optimize different parameters of your strategy. See the variable `strategy_params`, its filling in `run_strategy_main.py` and its usage in the `get_desired_current_position_size` function. 

# Quick Start

The system currently uses [Alpha Vantage](https://www.alphavantage.co/) as its main source of OHLC data. If you want to change it, modify the `import_ohlc_daily` function. 

First of all, you need to register on the Alpha Vantage site to receive a free API key. Write this key to your environment variables. At the start of the run, the system will retrieve it `ALPHA_VANTAGE_API_KEY = os.environ.get("alpha_vantage_key")` and use it. 

To avoid requesting data from Alpha Vantage every time, the system saves copies of the data as Excel files in the `/tmp/` folder. For example, `single_SPY.xlsx`. To make the system access Alpha Vantage again, you need to manually delete these files. You can modify the destination folder in the `constants.py` file.

Once you have received the API key from Alpha Vantage and given the system access to it, follow these steps.

1. Create some forecast in the `forecast` folder. See `forecast_bb.py` file for example.
2. Add its `get_forecast_***` function to the `utils/prepare_df.py` file.
3. Specify your forecast in the `init` function of the trading strategy in `strategy/run_backtest_for_ticker.py` file.
4. Code the rules for determining the desired position size in the `get_desired_current_position_size` function in `get_position_size_main.py` file.
5. Review and, if desired, change the `tickers_all` list in the `constants.py` file.
6. Run the `run_strategy_main.py` file. When the script finishes running, view the `output.xlsx` file, as well as logs in the `app_run.log` file.

Note 1. The file `output.xlsx` is created only if the number of tickers is more than one.

Note 2. If you wish, you can use several different forecasts at the same time, as well as additional features for filtering trades. In real life, you will most likely do so.

Invention of forecasts and rules for determining the desired position size are the steps where you create value.

# Output.xlsx File Overview and Explanations

Your `output.xlsx`file may look like the following:
![Python backtesting output file](./img/output.PNG)

If you are a trader, you probably understand the meaning of its rows. The only row that requires explanation is `SQN_modified`. 

System Quality Number (SQN) is a popular indicator of the trading system's quality developed by Dr. Van Tharp. Its classic formula has a drawback: it tends to produce overly optimistic results when analyzing more than 100 trades, particularly when the number of trades exceeds 150-200. 

`SQN_modified` is devoid of this drawback. It is simply the average of trade profits divided by the standard deviation of profits. A trading system is considered not bad if its `SQN_modified` has a positive value of at least 0.1. Systems whose `SQN_modified` value exceeds 0.2 are deemed decent or even good. By looking through the `output.xlsx` file, you can easily calculate the average  `SQN_modified` for all tickers.

# Optimization of Strategy Parameters

You can determine the best values for one or more numerical parameters in your trading strategy. These are the parameters the `get_desired_current_position_size` function uses to calculate the desired position size.

A script `optimize_params.py` can help you in finding the optimal parameter values. After it runs, you'll have a file `parameter_values.xlsx` with the results. It will look like this.

![trading strategy parameters optimization results](./img/optimization_res.PNG)

It's a good sign when the charts of backtest results depending on parameter values resemble Gaussian curves. Little deviations from the optimal parameter value should ​​only cause slight deterioration in backtest results. If the backtest results fluctuate wildly and chaotically, something went wrong.

# Analyzing Close-Close Returns

This repository could assist you in analyzing the likely direction of stock prices over the next few days. Some days, you can predict it with a fair amount of confidence based on today's value of some features. These features may be discrete or continuous. The script `run_analysis.py` demonstrates how to do it. It runs the functions that are in the `analysis/fwd_returns` folder.

## Discrete Feature Example

As a tutorial example of using a discrete feature, see `bb_cooling`. It is a rudimentary indicator suggesting that overbought or oversold conditions are beginning to stabilize. See details in the function `add_bb_cooling_to_ohlc`. It adds this feature as a column to the OHLC data.

The `analyze_fwd_ret_by_bb_cooling` function performs the analysis and saves the results in an Excel file. The `run_analysis.py` script calls this function for stocks, precious metals, and commodities.

![Analyzing commodities prices](./img/bb_cooling_cmd.PNG)

Getting long commodities when oversold conditions stabilize (`LOW_TO_HIGHER` group) could be a promising strategy. 

Theoretically, taking a short position in commodities when market excitement starts to cool should be profitable. This situation is indicated by stabilizing overbought conditions, the `HIGH_TO_LOWER` group. However, the current version of the `bb_cooling` feature does not support this assumption. 

Please note that the `bb_cooling` feature is rudimentary. You would better not use it for real-world trading without substantial enhancements.

## Continuous Feature Example

The `add_bb_forecast` function adds a `forecast_bb` column to the data, serving as a rudimentary trend strength indicator. Typically, folks plot Bollinger Bands where the absolute value of this indicator exceeds 2.0 or 2.2. A price crossing above the upper Bollinger Band signals overbought conditions. Also, a price crossing below the lower Bollinger Band signals oversold conditions.