import pytz
from db import db
import pandas as pd
from datetime import datetime


def get_month_wise_day_count(year, month):
    if (year % 4 == 0): # leap year
        feb_month_days = 29
    else:
        feb_month_days = 28
    return {
        1: 31,
        2: feb_month_days,
        3: 31,
        4: 30,
        5: 31,
        6: 30,
        7: 31,
        8: 31,
        9: 30,
        10: 31,
        11: 30,
        12: 31
    }[month]


MONTH_MAP = {
    1: "Jan",
    2: "Feb",
    3: "Mar",
    4: "Apr",
    5: "May",
    6: "Jun",
    7: "Jul",
    8: "Aug",
    9: "Sep",
    10: "Oct",
    11: "Nov",
    12: "Dec",
}


def get_current_datetime_in_given_timezone(timezone):
    now_tz = datetime.now(pytz.timezone(timezone))
    return now_tz


def create_year_month_time_bucket(current_year, current_month):
    if current_month <= 9:
        return f'{current_year}_0{current_month}'
    else:
        return f'{current_year}_{current_month}'


def get_YTD_time_buckets(current_year, current_month):
    return [create_year_month_time_bucket(current_year, x) for x in range(1, current_month+1)]


def get_cumulative_list(a_list):
    output = []
    for ind, _ in enumerate(a_list):
        output.append(round(sum(a_list[:(ind+1)]), 1))
    return output


def get_last_few_months_year_month_time_bucket(current_year, current_month):
    past_num_months = 6
    if current_month >= past_num_months:
        return [create_year_month_time_bucket(current_year, y) for y in range(current_month-5, current_month+1)]
    else:
        time_buckets_in_CY = [create_year_month_time_bucket(current_year, y) for y in range(1, current_month+1)]
        num_months_LY = past_num_months - current_month
        time_buckets_in_LY = [create_year_month_time_bucket(current_year-1, y) for y in range(12-num_months_LY+1, 13)]
        return time_buckets_in_LY + time_buckets_in_CY


def time_bucket_to_month_year_text(time_bucket):
    year = time_bucket[:4]
    month = int(time_bucket[5:])
    return f"{MONTH_MAP[month]}-{year[2:]}"


def get_month_year_text_for_last_few_months_(current_year, current_month):
    time_bucket_list = get_last_few_months_year_month_time_bucket(current_year, current_month)
    return [time_bucket_to_month_year_text(time_bucket) for time_bucket in time_bucket_list]


def get_from_summarization_MTD_expenditure(user, current_year, current_month, current_day):
    time_bucket = create_year_month_time_bucket(current_year, current_month)
    query = f'''
    SELECT SUM(value) FROM daily_summarization_model
    WHERE user = '{user}'
    AND transaction_year_month = '{time_bucket}'
    AND transaction_day <= {current_day}
    AND transaction_type = 'negative';
    '''
    result = db.engine.execute(query).fetchall()
    if (len(result) > 0) and (result[0][0] != None):
        return float(result[0][0])
    else:
        return 0


def get_from_summarization_current_month_income(user, current_year, current_month):
    time_bucket = create_year_month_time_bucket(current_year, current_month)
    query = f'''
    SELECT SUM(value) FROM daily_summarization_model
    WHERE user = '{user}'
    AND transaction_year_month = '{time_bucket}'
    AND transaction_type = 'positive';
    '''
    result = db.engine.execute(query).fetchall()
    if (len(result) > 0) and (result[0][0] != None):
        return float(result[0][0])
    else:
        return 0


def get_from_summarization_YTD_expenditure(user, current_year, current_month, current_day):
    MTD_expenditure = get_from_summarization_MTD_expenditure(user, current_year, current_month, current_day)
    past_time_bucket_list = get_YTD_time_buckets(current_year, current_month)[:-1]
    if len(past_time_bucket_list) > 1:
        query = f'''
        SELECT SUM(value) FROM monthly_summarization_model
        WHERE user = '{user}'
        AND transaction_year_month IN {tuple(past_time_bucket_list)}
        AND transaction_type = 'positive';
        '''
    elif len(past_time_bucket_list) == 1:
        query = f'''
        SELECT SUM(value) FROM monthly_summarization_model
        WHERE user = '{user}'
        AND transaction_year_month = '{past_time_bucket_list[0]}'
        AND transaction_type = 'positive';
        '''
    else:
        return MTD_expenditure
    result = db.engine.execute(query).fetchall()
    if (len(result) > 0) and (result[0][0] != None):
        return float(result[0][0]) + MTD_expenditure
    else:
        return MTD_expenditure


def get_from_summarization_cumulative_expenditure_day_wise_MTD(user, current_year, current_month, current_day):
    time_bucket = create_year_month_time_bucket(current_year, current_month)
    query = f'''
    SELECT transaction_day, value FROM daily_summarization_model
    WHERE user = '{user}'
    AND transaction_year_month = '{time_bucket}'
    AND transaction_day <= {current_day}
    AND transaction_type = 'negative'
    ORDER BY transaction_day ASC;
    '''
    result = db.engine.execute(query).fetchall()
    value_list = [x[1] for x in result]
    return get_cumulative_list(value_list)


def get_from_summarization_cumulative_expected_expenditure_day_wise(user, current_year, current_month):
    total_budget = get_from_summarization_current_month_income(user, current_year, current_month)
    num_of_days_in_current_month = get_month_wise_day_count(current_year, current_month)
    value_list = [round(total_budget*x/num_of_days_in_current_month, 1) for x in range(1, num_of_days_in_current_month+1)]
    return value_list


def get_from_summarization_month_wise_expenditure_last_few_months(user, current_year, current_month):
    time_bucket_list = get_last_few_months_year_month_time_bucket(current_year, current_month)
    query = f'''
    SELECT transaction_year_month, SUM(value) FROM monthly_summarization_model
    WHERE user = '{user}'
    AND transaction_year_month IN {tuple(time_bucket_list)}
    AND transaction_type = 'negative'
    GROUP BY transaction_year_month
    ORDER BY transaction_year_month ASC;
    '''
    result = db.engine.execute(query).fetchall()
    result_dict = {x[0]:x[1] for x in result}
    output = []
    for time_bucket in time_bucket_list:
        if result_dict.get(time_bucket):
            output.append(round(result_dict.get(time_bucket), 1))
        else:
            output.append(0)

    return output


def get_from_summarization_month_wise_income_last_few_months(user, current_year, current_month):
    time_bucket_list = get_last_few_months_year_month_time_bucket(current_year, current_month)
    query = f'''
    SELECT transaction_year_month, SUM(value) FROM monthly_summarization_model
    WHERE user = '{user}'
    AND transaction_year_month IN {tuple(time_bucket_list)}
    AND transaction_type = 'positive'
    GROUP BY transaction_year_month
    ORDER BY transaction_year_month ASC;
    '''
    result = db.engine.execute(query).fetchall()
    return [round(x[1], 1) if x[1] is not None else 0 for x in result]


def get_from_summarization_category_wise_expenditure_MTD(user, current_year, current_month):
    time_bucket = create_year_month_time_bucket(current_year, current_month)
    query = f'''
    SELECT category, value FROM monthly_summarization_model
    WHERE user = '{user}'
    AND transaction_year_month = '{time_bucket}'
    AND transaction_type = 'negative'
    ORDER BY FIELD(category, 'Food', 'Travelling', 'Groceries', 'Medical expense', 'Monthly bill', 'Others');
    '''
    result = db.engine.execute(query).fetchall()
    output = {
        "category": [], "MTD_expenditure": []
    }
    for x in result:
        output['category'].append(x[0])
        if x[1] is not None:
            output['MTD_expenditure'].append(round(x[1], 1))
        else:
            output['MTD_expenditure'].append(0)
    return output


def get_from_transaction_monthly_income_value(user, current_year, current_month):
    query = f'''
    SELECT SUM(value) FROM transaction_model
    WHERE user = '{user}'
    AND transaction_year = {current_year}
    AND transaction_month = {current_month}
    AND transaction_type = 'positive';
    '''
    result = db.engine.execute(query).fetchall()
    if (len(result) > 0) and (result[0][0] != None):
        return float(result[0][0])
    else:
        return None


def get_from_transaction_monthly_expenditure_value(user, current_year, current_month, category):
    query = f'''
    SELECT SUM(value) FROM transaction_model
    WHERE user = '{user}'
    AND transaction_year = {current_year}
    AND transaction_month = {current_month}
    AND transaction_type = 'negative'
    AND category = '{category}';
    '''
    result = db.engine.execute(query).fetchall()
    if (len(result) > 0) and (result[0][0] != None):
        return float(result[0][0])
    else:
        return None


def get_from_transaction_daily_income_value(user, current_year, current_month, current_day):
    query = f'''
    SELECT SUM(value) FROM transaction_model
    WHERE user = '{user}'
    AND transaction_year = {current_year}
    AND transaction_month = {current_month}
    AND transaction_day = {current_day}
    AND transaction_type = 'positive';
    '''
    result = db.engine.execute(query).fetchall()
    if (len(result) > 0) and (result[0][0] != None):
        return float(result[0][0])
    else:
        return None


def get_from_transaction_daily_expenditure_value(user, current_year, current_month, current_day):
    query = f'''
    SELECT SUM(value) FROM transaction_model
    WHERE user = '{user}'
    AND transaction_year = {current_year}
    AND transaction_month = {current_month}
    AND transaction_day = {current_day}
    AND transaction_type = 'negative';
    '''
    result = db.engine.execute(query).fetchall()
    if (len(result) > 0) and (result[0][0] != None):
        return float(result[0][0])
    else:
        return None


def update_daily_income_value(user, current_year, current_month, current_day):
    time_bucket = create_year_month_time_bucket(current_year, current_month)
    value = get_from_transaction_daily_income_value(user, current_year, current_month, current_day)
    delete_query = f'''
    DELETE FROM daily_summarization_model
    WHERE user = '{user}'
    AND transaction_year_month = '{time_bucket}'
    AND transaction_day = {current_day}
    AND transaction_type='positive';
    '''
    db.engine.execute(delete_query)
    if value is not None:
        insert_query = f'''
        INSERT INTO daily_summarization_model(user, transaction_year_month, transaction_day, transaction_type, value)
        VALUES('{user}','{time_bucket}', {current_day}, 'positive', {value})
        '''
        db.engine.execute(insert_query)
    # print(value, delete_query, insert_query)


def update_daily_expenditure_value(user, current_year, current_month, current_day):
    time_bucket = create_year_month_time_bucket(current_year, current_month)
    value = get_from_transaction_daily_expenditure_value(user, current_year, current_month, current_day)
    delete_query = f'''
    DELETE FROM daily_summarization_model
    WHERE user = '{user}'
    AND transaction_year_month = '{time_bucket}'
    AND transaction_day = {current_day}
    AND transaction_type='negative';
    '''
    db.engine.execute(delete_query)
    if value is not None:
        insert_query = f'''
        INSERT INTO daily_summarization_model(user, transaction_year_month, transaction_day, transaction_type, value)
        VALUES('{user}','{time_bucket}', {current_day}, 'negative', {value})
        '''
        db.engine.execute(insert_query)


def update_monthly_income_value(user, current_year, current_month):
    time_bucket = create_year_month_time_bucket(current_year, current_month)
    value = get_from_transaction_monthly_income_value(user, current_year, current_month)
    delete_query = f'''
    DELETE FROM monthly_summarization_model
    WHERE user = '{user}'
    AND transaction_year_month = '{time_bucket}'
    AND transaction_type='positive';
    '''
    db.engine.execute(delete_query)
    if value is not None:
        insert_query = f'''
        INSERT INTO monthly_summarization_model(user, transaction_year_month, transaction_type, value)
        VALUES('{user}','{time_bucket}', 'positive', {value})
        '''
        db.engine.execute(insert_query)


def update_monthly_expenditure_value(user, current_year, current_month, category):
    time_bucket = create_year_month_time_bucket(current_year, current_month)
    value = get_from_transaction_monthly_expenditure_value(user, current_year, current_month, category)
    delete_query = f'''
    DELETE FROM monthly_summarization_model
    WHERE user = '{user}'
    AND transaction_year_month = '{time_bucket}'
    AND transaction_type='negative'
    AND category='{category}';
    '''
    db.engine.execute(delete_query)
    if value is not None:
        insert_query = f'''
        INSERT INTO monthly_summarization_model(user, transaction_year_month, category, transaction_type, value)
        VALUES('{user}','{time_bucket}', '{category}', 'negative', {value})
        '''
        db.engine.execute(insert_query)



def get_transaction_details(user, current_year, current_month):
    query = f'''
    SELECT CONCAT(transaction_day, '/', transaction_month, '/', transaction_year) AS transaction_date,
    transaction_type, description, category, value
    FROM transaction_model
    WHERE user = '{user}'
    AND transaction_year = {current_year}
    AND transaction_month = {current_month}
    ORDER BY transaction_day DESC; 
    '''
    result = db.engine.execute(query).fetchall()
    df = pd.DataFrame(result, columns= ['transaction_date','transaction_type', 'description', 'category', 'value'])
    return df
