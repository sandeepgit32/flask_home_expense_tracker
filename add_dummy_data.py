import random
from datetime import datetime
# from db import db
from utils import *
from models import TransactionModel


month_wise_day_count = {
    1: 31,
    2: 28,
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
}


def add_dummy_item(transaction_item):
    transaction_item_obj = TransactionModel(
        user=transaction_item['user'],
        description=transaction_item['description'],
        transaction_day=transaction_item['transaction_day'],
        transaction_month=transaction_item['transaction_month'],
        transaction_year=transaction_item['transaction_year'],
        transaction_type=transaction_item['transaction_type'],
        storing_datetime=transaction_item['storing_datetime'],
        category=transaction_item['category'],
        value=transaction_item['value']
    )
    TransactionModel.save_to_db(transaction_item_obj)

    if transaction_item['transaction_type'] == 'positive':
        update_monthly_income_value(transaction_item['user'], transaction_item['transaction_year'], \
            transaction_item['transaction_month'])
        update_daily_income_value(transaction_item['user'], transaction_item['transaction_year'], \
            transaction_item['transaction_month'], transaction_item['transaction_day'])
    elif transaction_item['transaction_type'] == 'negative':
        update_monthly_expenditure_value(transaction_item['user'], transaction_item['transaction_year'], \
            transaction_item['transaction_month'], transaction_item['category'])
        update_daily_expenditure_value(transaction_item['user'], transaction_item['transaction_year'], \
            transaction_item['transaction_month'], transaction_item['transaction_day'])


def create_transaction_item(user, transaction_year, transaction_month, transaction_day, type, description, value):
    return {
        'user': user, 
        'description': description, 
        'transaction_day': transaction_day,
        'transaction_month': transaction_month,
        'transaction_year': transaction_year, 
        'transaction_type': type,
        'storing_datetime': datetime.now(),
        'value': value,
        'category': random.choice([
            'Food',
            'Travelling',
            'Groceries',
            'Medical expense',
            'Monthly bill',
            'Others'
        ])
    }


def create_dummy_data():
    user = 'sandip'
    for year in [2021, 2022]:
        for month in range(1, 13):
            for day in range(1, month_wise_day_count[month]+1):
                if day == 1:
                    income_transaction = create_transaction_item(user, year, month, day, 'positive', \
                        f'Budget {year} month_{month}', random.choice([10000, 15000]))
                    print(f'Income transaction added for year_{year}_month_{month}')
                    add_dummy_item(income_transaction)
                num_transactions = random.choice([1,2,2,3,3,3,4,4,5,5,6])
                for count in range(num_transactions):
                    expense_transaction = create_transaction_item(user, year, month, day, 'negative', \
                        f'Expense for {day} {count}', round(random.randint(10, 1500), 1))
                    print(f'Expense transaction added for year_{year}_month_{month}_day_{day}_{count}')
                    add_dummy_item(expense_transaction)


if __name__ == '__main__':
    create_dummy_data()