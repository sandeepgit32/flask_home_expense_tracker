def create_year_month_time_bucket(current_year, current_month):
    if current_month <= 9:
        return f'{current_year}_0{current_month}'
    else:
        return f'{current_year}_{current_month}'


def get_last_six_months_year_month_time_bucket(current_year, current_month):
    if current_month >= 6:
        return [(current_year, y) for y in range(current_month-5, current_month+1)]
    else:
        time_buckets_in_CY = [create_year_month_time_bucket(current_year, y) for y in range(1, current_month+1)]
        num_months_LY = 6 - current_month
        time_buckets_in_LY = [create_year_month_time_bucket(current_year-1, y) for y in range(12-num_months_LY+1, 13)]
        return time_buckets_in_LY + time_buckets_in_CY


def get_from_summarization_current_month_expenditure(user, current_year, current_month):
    time_bucket = create_year_month_time_bucket(current_year, current_month)
    query = f'''
    SELECT SUM(value) FROM monthly_summarization_model
    WHERE user = '{user}'
    AND transaction_year_month = '{time_bucket}'
    AND transaction_type = 'negative';
    '''


def get_from_summarization_current_month_income(user, current_year, current_month):
    time_bucket = create_year_month_time_bucket(current_year, current_month)
    query = f'''
    SELECT SUM(value) FROM monthly_summarization_model
    WHERE user = '{user}'
    AND transaction_year_month = '{time_bucket}'
    AND transaction_type = 'positive';
    '''


def get_from_summarization_cumulative_expenditure_day_wise_MTD(user, current_year, current_month):
    time_bucket = create_year_month_time_bucket(current_year, current_month)
    query = f'''
    SELECT transaction_day, value FROM daily_summarization_model
    WHERE user = '{user}'
    AND transaction_year_month = '{time_bucket}'
    AND transaction_type = 'negative'
    ORDER BY transaction_day AESC;
    '''


def get_from_summarization_month_wise_expenditure_last_six_months(user, current_year, current_month):
    time_bucket_list = get_last_six_months_year_month_time_bucket(current_year, current_month)
    query = f'''
    SELECT SUM(value) FROM monthly_summarization_model
    WHERE user = '{user}'
    AND transaction_year_month IN {tuple(time_bucket_list)}
    AND transaction_type = 'negative'
    ORDER BY transaction_year_month AESC;
    '''


def get_from_summarization_month_wise_income_last_six_months(user, current_year, current_month):
    time_bucket_list = get_last_six_months_year_month_time_bucket(current_year, current_month)
    query = f'''
    SELECT value FROM monthly_summarization_model
    WHERE user = '{user}'
    AND transaction_year_month IN {tuple(time_bucket_list)}
    AND transaction_type = 'positive'
    ORDER BY transaction_year_month AESC;
    '''


def get_from_summarization_category_wise_expenditure_and_percentage_MTD(user, current_year, current_month):
    time_bucket = create_year_month_time_bucket(current_year, current_month)
    query = f'''
    SELECT category, value FROM monthly_summarization_model
    WHERE user = '{user}'
    AND transaction_year_month = '{time_bucket}'
    AND transaction_type = 'negative';
    '''


def get_from_transaction_monthly_income_value(user, current_year, current_month):
    query = f'''
    SELECT SUM(value) FROM transaction_model
    WHERE user = '{user}'
    AND transaction_year = {current_year}
    AND transaction_month = {current_month}
    AND transaction_type = 'positive';
    '''


def get_from_transaction_monthly_expenditure_value(user, current_year, current_month, category):
    query = f'''
    SELECT SUM(value) FROM transaction_model
    WHERE user = '{user}'
    AND transaction_year = {current_year}
    AND transaction_month = {current_month}
    AND transaction_type = 'negative'
    AND category = '{category}';
    '''


def get_from_transaction_daily_income_value(user, current_year, current_month, current_day):
    query = f'''
    SELECT SUM(value) FROM transaction_model
    WHERE user = '{user}'
    AND transaction_year = {current_year}
    AND transaction_month = {current_month}
    AND transaction_day = {current_day}
    AND transaction_type = 'positive';
    '''


def get_from_transaction_daily_expenditure_value(user, current_year, current_month, current_day):
    query = f'''
    SELECT SUM(value) FROM transaction_model
    WHERE user = '{user}'
    AND transaction_year = {current_year}
    AND transaction_month = {current_month}
    AND transaction_day = {current_day}
    AND transaction_type = 'negative';
    '''


def update_daily_income_value(user, current_year, current_month, current_day):
    time_bucket = create_year_month_time_bucket(current_year, current_month)
    value = get_from_transaction_monthly_income_value(user, current_year, current_month)
    query = f'''
    REPLACE INTO daily_summarization_model
    SET user='{user}', transaction_year_month='{time_bucket}', value={value}
    transaction_type='positive', transaction_day={current_day};
    '''


def update_daily_expenditure_value(user, current_year, current_month, current_day):
    time_bucket = create_year_month_time_bucket(current_year, current_month)
    value = get_from_transaction_monthly_expenditure_value(user, current_year, current_month)
    query = f'''
    REPLACE INTO daily_summarization_model
    SET user='{user}', transaction_year_month='{time_bucket}', value={value}
    transaction_type='negative', transaction_day={current_day};
    '''


def update_monthly_income_value(user, current_year, current_month):
    time_bucket = create_year_month_time_bucket(current_year, current_month)
    value = get_from_transaction_monthly_income_value(user, current_year, current_month)
    query = f'''
    REPLACE INTO monthly_summarization_model
    SET user='{user}', transaction_year_month='{time_bucket}', value={value}
    transaction_type='positive';
    '''


def update_monthly_expenditure_value(user, current_year, current_month, category):
    time_bucket = create_year_month_time_bucket(current_year, current_month)
    value = get_from_transaction_monthly_expenditure_value(user, current_year, current_month, category)
    query = f'''
    REPLACE INTO monthly_summarization_model
    SET user='{user}', transaction_year_month='{time_bucket}', category='{category}', value={value}
    transaction_type='negative';
    '''
