import os
from dotenv import load_dotenv
load_dotenv('.env', verbose=True)
from flask import render_template, request, redirect, url_for, session, flash
from datetime import date, datetime
from models import UserModel, TransactionModel
from flask_bcrypt import Bcrypt
from functools import wraps
from app import create_app
from db import db
from utils import *

app = create_app(os.environ.get("FLASK_ENV"))
bcrypt_obj = Bcrypt(app)


def authentication_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs): 
        if session.get('logged_in'):
            return func(*args, **kwargs)
        else:
            return render_template('login.html')
    return wrapper


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        if request.form['password'] != request.form['repassword']:
            return render_template('register.html', message="Passwords do not match!")
        # Hashing the password
        hashPassword = bcrypt_obj.generate_password_hash(request.form['password'])
        try:
            user_obj = UserModel(
                username = request.form['username'],
                name = request.form['name'], 
                surname = request.form['surname'], 
                password = hashPassword
            )
            db.session.add(user_obj)
            db.session.commit()
            return redirect(url_for('login'))
        except:
            return render_template('register.html', message="User Already Exists!")
    else:
        return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    else:
        u = request.form['username']
        p = request.form['password']  # Hashing the password
        user_data = UserModel.query.filter_by(username=u).first()
        if user_data is not None:
            # Password is checked
            if bcrypt_obj.check_password_hash(user_data.password, p): 
                session['logged_in'] = True
                session['user'] = u # Store the username in session variable for display after redirection
                session['name'] = user_data.name
                session['surname'] = user_data.surname
                session['last_login_time'] = user_data.last_login_time
                session['current_login_time'] = datetime.now()
                return redirect(url_for('index'))
        return render_template('login.html', message="Incorrect Details!")


@app.route('/logout', methods=['GET', 'POST'])
def logout():
    user_data = UserModel.query.filter_by(username=session['user']).first()
    user_data.last_login_time = session.get('current_login_time')
    db.session.commit()
    session['logged_in'] = False
    session['user'] = None
    session['name'] = None
    session['surname'] = None
    session['last_login_time'] = None
    session['current_login_time'] = None
    return redirect(url_for('index'))


# def format_transaction_values(list_of_transactions):
#     for transaction in list_of_transactions:
#         transaction.value = '{:,}'.format(transaction.value)


@app.route('/')
@authentication_required
def index():
    x = get_from_transaction_monthly_income_value('sandip', 2022, 9)
    return render_template('index.html')


@app.route('/transactions', methods=['GET', 'POST'])
@authentication_required
def transactions():
    if request.method == 'GET':
        current_date = date.today()
        transaction_year, transaction_month = current_date.year, current_date.month
    elif request.method == 'POST':
        transaction_year, transaction_month = int(request.form['transaction_list_year']), \
            int(request.form['transaction_list_month']) # request.form always send data as string
        # current_month_text = current_date.strftime("%B")

    positive_transactions = TransactionModel.find_by_year_month_type(
        transaction_type='positive',
        transaction_year=transaction_year,
        transaction_month=transaction_month,
        user=session['user']
    )
    if positive_transactions is None:
        positive_transactions = []
        total_budget = 0
    else:
        total_budget = round(sum([x.value for x in positive_transactions]), 1)

    negative_transactions = TransactionModel.find_by_year_month_type(
        transaction_type='negative',
        transaction_year=transaction_year,
        transaction_month=transaction_month,
        user=session['user']
    )
    if negative_transactions is None:
        negative_transactions = []
        total_expense = 0
    else:
        total_expense = round(sum([x.value for x in negative_transactions]), 1)

    total_income = round(sum([x.value for x in positive_transactions]), 1)
    income_percentage_list = [-round(x.value*100/total_income, 1) for x in positive_transactions]
    if total_budget == 0:
        total_expense = round(sum([x.value for x in negative_transactions]), 1)
        expense_percentage_list = [-round(x.value*100/total_expense, 1) for x in negative_transactions]
    else:
        expense_percentage_list = [round(x.value*100/total_budget, 1) for x in negative_transactions]

    return render_template('transactions.html', 
        positive_transactions_percentages=zip(positive_transactions, income_percentage_list), \
        negative_transactions_percentages=zip(negative_transactions, expense_percentage_list),\
        transaction_year=transaction_year,
        transaction_month=transaction_month, 
        user=session['user'],
        name_display=f'{session["name"]} {session["surname"]}')
    

@app.route('/add', methods=['GET', 'POST'])
@authentication_required
def add():
    if request.method == 'GET':
        return redirect(url_for('transactions'))
    else:
        selected_date = request.form['date']
        selected_year, selected_month, selected_day = selected_date.split('-')
        
        if request.form['description'] == '':
            flash('No description entered!')
            return redirect(url_for('transactions'))
        else:
            description = request.form['description']

        try:
            inserted_value = float(request.form['value'])
        except:
            flash('You have provided an invalid value!')
            return redirect(url_for('transactions'))
        
        if request.form['transaction_type'] == 'negative':
            category = request.form['category']
        else:
            category = None

        transaction_item = TransactionModel(
            user=session['user'],
            description=description,
            transaction_day=int(selected_day),
            transaction_month=int(selected_month),
            transaction_year=int(selected_year),
            transaction_type=request.form['transaction_type'],
            storing_datetime=datetime.now(),
            category=category,
            value=round(inserted_value, 1)
        )
        TransactionModel.save_to_db(transaction_item)

        # TODO: Use task queue for this
        if request.form['transaction_type'] == 'positive':
            update_monthly_income_value(session['user'], int(selected_year), int(selected_month))
            update_daily_income_value(session['user'], int(selected_year), int(selected_day))
        elif request.form['transaction_type'] == 'negative':
            update_monthly_expenditure_value(session['user'], int(selected_year), int(selected_month), \
                category)
            update_daily_expenditure_value(session['user'], int(selected_year), int(selected_month), \
                int(selected_day))
        return redirect(url_for('transactions'))


@app.route('/delete', methods=['GET','POST'])
@authentication_required
def delete():
    if request.method == 'GET':
        return redirect(url_for('transactions'))
    else:
        transaction_id = request.form.get("transaction_id")
        transaction = TransactionModel.find_by_id(id=transaction_id)
        TransactionModel.delete_from_db(transaction)
        
        # TODO: Use task queue for this
        if transaction.transaction_type == 'positive':
            update_monthly_income_value(session['user'], int(transaction.transaction_year), \
                int(transaction.transaction_month))
            update_daily_income_value(session['user'], int(transaction.transaction_year), \
                int(transaction.transaction_month))
        elif transaction.transaction_type == 'negative':
            update_monthly_expenditure_value(session['user'], int(transaction.transaction_year), \
                int(transaction.transaction_month), transaction.category)
            update_daily_expenditure_value(session['user'], int(transaction.transaction_year), \
                int(transaction.transaction_month), int(transaction.transaction_day))
        return redirect(url_for('transactions'))


if __name__ == '__main__':
    # db.create_all()
    app.run(host='0.0.0.0', port=5000, debug=True)