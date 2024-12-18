import sys

import pandas as pd
from dotenv import load_dotenv

from constants import LOG_FILE, tickers_all
from customizable import add_features_v1_basic
from customizable.misc import get_ma_200_relation_label
from utils.bootstrap import analyze_values_by_group, get_bootstrapped_mean_ci
from utils.get_df_with_fwd_ret import add_fwd_ret
from utils.local_data import TickersData

if __name__ == "__main__":
    load_dotenv()

    # clear LOG_FILE every time
    open(LOG_FILE, "w").close()

    EXCEL_FILE_NAME_BY_GROUP = "res_ma_200_by_group.xlsx"
    EXCEL_FILE_NAME_SIMPLE = "res_ma_200_above_below.xlsx"
    GROUP_COL_NAME = "close_rel_ma_200_group"

    # The first step is to collect DataFrames with data and derived columns
    # for all the tickers we are interested in.
    # This data is stored in the TickersData class instance
    # as a dictionary whose keys are tickers and the values ​​are DFs.

    # For more details, see the class TickersData internals,
    # and the add_features_v1_basic function.
    required_feature_columns = {"ma_200", "atr_14", "feature_basic", "feature_advanced"}
    tickers_data = TickersData(
        tickers=tickers_all,
        add_feature_cols_func=add_features_v1_basic,
        required_feature_cols=required_feature_columns,
    )

    # Now add forward returns column fwd_ret_4 to analyze it

    # NOTE We don't need forward returns to run backtests,
    # so we add them only here,
    # not inside the TickersData class or anywhere else.
    for ticker in tickers_data.tickers_data_with_features:
        tickers_data.tickers_data_with_features[ticker] = add_fwd_ret(
            ohlc_df=tickers_data.tickers_data_with_features[ticker], num_days=4
        )

    # Add a column with a group label
    # and concatenate the DFs of all tickers into one large DF.
    combined_ohlc_all = pd.DataFrame()
    for ticker in tickers_data.tickers_data_with_features:
        df = tickers_data.tickers_data_with_features[ticker]
        df[GROUP_COL_NAME] = df.apply(get_ma_200_relation_label, axis=1)
        
        # NOTE 
        # You must still create combined_ohlc_all, 
        # even if you don't plan to split the data into groups.
        combined_ohlc_all = pd.concat([combined_ohlc_all, df])
    
    combined_ohlc_all = combined_ohlc_all.dropna()

    # just in case...
    print(f"{combined_ohlc_all.shape=}")
    print(f"{combined_ohlc_all.columns=}")
    print(combined_ohlc_all.tail())

    # Up until this point there has been preparation,
    # and now the analysis will be carried out.

    # simple separation: close above and below MA_200

    # NOTE
    # in add_features_v1_basic()
    # res["feature"] = res["Close"] < res[f"ma_{MOVING_AVERAGE_N}"]

    res = dict()
    res["CLOSE_BELOW_MA_200"] = get_bootstrapped_mean_ci(
        data=combined_ohlc_all[combined_ohlc_all["feature_basic"] == True]["fwd_ret_4"]
        .dropna()
        .values
    )
    res["CLOSE_ABOVE_MA_200"] = get_bootstrapped_mean_ci(
        data=combined_ohlc_all[combined_ohlc_all["feature_basic"] == False]["fwd_ret_4"]
        .dropna()
        .values
    )
    pd.DataFrame(res).T.to_excel(EXCEL_FILE_NAME_SIMPLE)

    # advanced separation: by groups

    # NOTE This is for convenient sorting of rows
    # in the resulting Excel file.
    group_order_ma_200_rel = {
        "HIGHLY_ABOVE": 1,
        "MODERATELY_ABOVE": 2,
        "SLIGHTLY_ABOVE": 3,
        "SLIGHTLY_BELOW": 4,
        "MODERATELY_BELOW": 5,
        "HIGHLY_BELOW": 6,
        "all_data": 7,  # all_data row is important, don't miss it
    }

    analyze_values_by_group(
        df=combined_ohlc_all,
        group_col_name=GROUP_COL_NAME,
        values_col_name="fwd_ret_4",
        group_order_map=group_order_ma_200_rel,
        excel_file_name=EXCEL_FILE_NAME_BY_GROUP,
    )
    print(
        f"Analysis complete! Now you may explore the results files {EXCEL_FILE_NAME_SIMPLE} and {EXCEL_FILE_NAME_BY_GROUP}",
        file=sys.stderr,
    )
