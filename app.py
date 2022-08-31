from flask import Flask

app = Flask(__name__, template_folder='template')

# Using a development configuration
app.config.from_object('config.DevConfig')

# Using a production configuration
# app.config.from_object('config.ProdConfig')