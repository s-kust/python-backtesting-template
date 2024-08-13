# python-backtesting-template
Trading strategy template that uses Python `backtesting` library. It lets you focus on improving your price forecasts and reduces the time and effort spent on auxiliary tasks.

# Quick Start

1. Create some forecast in the `forecast` folder. See `forecast_bb.py` file for example.
2. Add its `get_forecast_***` function to the `utils/prepare_df.py` file.
3. Specify your forecast in the `init` function of the trading strategy in `strategy/run_backtest_for_ticker.py` file.
4. Code the rules for determining the desired position size in the `get_desired_current_position_size` function in `get_position_size_main.py` file.
5. Review and, if desired, change the `tickers_all` list in the `constants.py` file.
6. Run the `run_strategy_main.py` file. When the script finishes running, view the `output.xlsx` file, as well as logs in the `app_run.log` file.

Note 1. The file `output.xlsx` is created only if the number of tickers is more than one.

Note 2. If you wish, you can use several different forecasts at the same time, as well as additional features for filtering trades.

Coding forecasts and rules for determining the desired position size are the steps where you create value.

# Understanding the Benefits of This Repo

# Output.xlsx File Overview and Explanations

Your `output.xlsx` file may look like the following:
![Python backtesting output file](./img/output.PNG)

If you are a trader, you probably understand the meaning of its rows. The only row that requires explanation is `SQN_modified`. 

System Quality Number (SQN) is a popular indicator of the trading system's quality developed by Dr. Van Tharp. Its classic formula has a drawback: it tends to produce overly optimistic results when analyzing more than 100 trades, particularly when the number of trades exceeds 150-200. 

`SQN_modified` is devoid of this drawback. It is simply the average of trade profits divided by the standard deviation of profits. A trading system is considered not bad if its `SQN_modified` has a positive value of at least 0.1. Systems whose `SQN_modified` value exceeds 0.2 are deemed decent or even good. By looking through the `output.xlsx` file, you can easily calculate the average  `SQN_modified` for all tickers.

