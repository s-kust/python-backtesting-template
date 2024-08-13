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



