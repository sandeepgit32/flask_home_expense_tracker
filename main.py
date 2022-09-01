from flask import render_template, request, redirect, url_for, session, flash
from datetime import date, datetime
from models import UserModel, TransactionModel
from flask_bcrypt import Bcrypt
from functools import wraps
from app import app
from db import db


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
        data = UserModel.query.filter_by(username=u).first()
        if data is not None:
            # Password is checked
            if bcrypt_obj.check_password_hash(data.password, p): 
                session['logged_in'] = True
                session['user'] = u # Store the username in session variable for display after redirection
                return redirect(url_for('index'))
        return render_template('login.html', message="Incorrect Details!")


@app.route('/logout', methods=['GET', 'POST'])
def logout():
    session['logged_in'] = False
    session['user'] = None
    return redirect(url_for('index'))


# def format_transaction_values(list_of_transactions):
#     for transaction in list_of_transactions:
#         transaction.value = '{:,}'.format(transaction.value)


@app.route('/')
@authentication_required
def index():
    current_date = date.today()
    current_month_text = current_date.strftime("%B")
    display_month_year = f'{current_month_text}-{current_date.year}'
    positive_transactions = TransactionModel.find_by_year_month_type(
        transaction_type='positive',
        transaction_year=current_date.year,
        transaction_month=current_date.month,
        user=session['user']
    )
    if positive_transactions is None:
        positive_transactions = []
        total_budget = 0
    else:
        total_budget = round(sum([x.value for x in positive_transactions]), 1)

    negative_transactions = TransactionModel.find_by_year_month_type(
        transaction_type='negative',
        transaction_year=current_date.year,
        transaction_month=current_date.month,
        user=session['user']
    )
    if negative_transactions is None:
        negative_transactions = []
        total_expense = 0
    else:
        total_expense = round(sum([x.value for x in negative_transactions]), 1)
    percentage_list = []
    if total_budget == 0:
        total_val = round(sum([x.value for x in negative_transactions]), 1)
        percentage_list = [-round(x.value*100/total_val, 1) for x in negative_transactions]
    else:
        percentage_list = [round(x.value*100/total_budget, 1) for x in negative_transactions]
    if total_budget == 0:
        overall_percentage = '--'
    else:
        overall_percentage = round(total_expense*100/total_budget, 1)
    if total_budget >= total_expense:
        available_budget = '+{:,}'.format(round(total_budget-total_expense, 1))
    elif total_budget < total_expense:
        available_budget = '-{:,}'.format(round(total_expense-total_budget, 1))

    return render_template('index.html', positive_transactions=positive_transactions, \
        negative_transactions_percentages=zip(negative_transactions, percentage_list),\
        total_budget='{:,}'.format(total_budget), total_expense='{:,}'.format(total_expense), \
        overall_percentage=overall_percentage, available_budget=available_budget, 
        display_month_year=display_month_year, \
        today=f'{current_date.year}-{current_date.month}-{current_date.day}', user=session['user'])
    

@app.route('/add', methods=['GET', 'POST'])
@authentication_required
def add():
    if request.method == 'GET':
        return redirect(url_for('index'))
    else:
        selected_date = request.form['date']
        selected_year, selected_month, selected_day = selected_date.split('-')
        
        if request.form['description'] == '':
            flash('No description entered!')
            return redirect(url_for('index'))
        else:
            description = request.form['description']

        try:
            inserted_value = float(request.form['value'])
        except:
            flash('You have provided an invalid value!')
            return redirect(url_for('index'))

        transaction_item = TransactionModel(
            user=session['user'],
            description=description,
            transaction_day=int(selected_day),
            transaction_month=int(selected_month),
            transaction_year=int(selected_year),
            transaction_type=request.form['transaction_type'],
            storing_datetime=datetime.now(),
            value=round(inserted_value, 1)
        )
        TransactionModel.save_to_db(transaction_item)
        return redirect(url_for('index'))


@app.route('/delete', methods=['GET','POST'])
@authentication_required
def delete():
    if request.method == 'GET':
        return redirect(url_for('index'))
    else:
        transaction_id = request.form.get("transaction_id")
        transaction = TransactionModel.find_by_id(id=transaction_id)
        TransactionModel.delete_from_db(transaction)
        return redirect(url_for('index'))


if __name__ == '__main__':
    db.create_all()
    app.run()