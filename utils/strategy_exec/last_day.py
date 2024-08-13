from .misc import retrieve_variable_name


def process_last_day_res(last_day_res: dict):
    # TODO implement - send notification
    # if last_day_res contains signal to do trade
    pass


def create_last_day_results(*args) -> dict:
    """
    Fill last_day_results with provided values.
    Assign None to all the values ​​that are not provided.
    """
    res: dict = dict()
    all_columns = [
        "current_position_num_stocks",
        "all_current_trades",
        "today_special_situation_msg",
        "current_position_size",
        "desired_size",
        "desired_size_msg",
        "today_action",
    ]
    for column in all_columns:
        res[column] = None
    for var in args:
        var_name = retrieve_variable_name(var)
        if var_name not in all_columns:
            continue
        res[var_name] = var
    return res
