from flask import Flask
from flask_restful import Resource, Api, reqparse, abort, fields, marshal_with
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
api = Api(app)
SQLALCHEMY_DATABASE_URI = "mysql+mysqlconnector://{username}:{password}@{hostname}/{databasename}".format(
    username="adix0911",
    password="nEt^/$Ud&pW|AfU;",
    hostname="adix0911.mysql.eu.pythonanywhere-services.com",
    databasename="adix0911$Crypto_app_db",
)
app.config["SQLALCHEMY_DATABASE_URI"] = SQLALCHEMY_DATABASE_URI
app.config["SQLALCHEMY_POOL_RECYCLE"] = 299
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db=SQLAlchemy(app)

class Accounts(db.Model):
    __tablename__='Accounts'
    Account_ID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    Login = db.Column(db.String(30), nullable=False)
    Password = db.Column(db.String(30), nullable=False)
    #too many accounts disable relation
    # wallets=db.relationship('Wallets',backref='accounts', lazy=True)

    def __repr__(self):
        return f"Login {self.Login} password {self.Password}"

class Wallets(db.Model):
    __tablename__='Wallets'
    Id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    Account_ID = db.Column(db.Integer, db.ForeignKey('accounts.Account_ID'))#,nullable=False)
    Name = db.Column(db.String(50), nullable=False)
    #too many accounts disable relation
    # wallet_detal=db.relationship("Wallet_Details",backref='wallets')


class Wallet_Details(db.Model):
    __tablename__='Wallet_Details'
    Id=db.Column(db.Integer,primary_key=True,autoincrement=True)
    Wallet_ID=db.Column(db.Integer,db.ForeignKey('wallets.Id'))#,nullable=False)
    # Wallet_ID=db.Column(db.Integer,db.ForeignKey('wallet_detail.Id'))
    Name=db.Column(db.String(80),nullable=False)
    Price_PLN=db.Column(db.Float,nullable=False)
    Price_USD=db.Column(db.Float,nullable=False)
    Quantity=db.Column(db.Float,nullable=False)


# db.create_all()
login_put_args = reqparse.RequestParser()
login_put_args.add_argument("login", type=str, help="Login is required", required=True)
login_put_args.add_argument("password", type=str, help="Password is required", required=True)

login_change_args = reqparse.RequestParser()
login_change_args.add_argument("login", type=str)
login_change_args.add_argument("password", type=str)

wallet_args=reqparse.RequestParser()
wallet_args.add_argument("Account_ID",type=str)
wallet_args.add_argument("Name",type=str)

wallet_detail_args=reqparse.RequestParser()
wallet_detail_args.add_argument("Name",type=str,help="Name of corrency", required=True)
wallet_detail_args.add_argument("Price_PLN",type=float,help="Price in PLN", required=True)
wallet_detail_args.add_argument("Price_USD",type=float,help="Price in USD", required=True)
wallet_detail_args.add_argument("Quantity",type=float,help="Amount of corrency", required=True)

resources_fields_accounts = {
    "Account_ID": fields.Integer,
    "Login": fields.String,
    "Password": fields.String,
}
resources_fields_wallets = {
    "Id": fields.Integer,
    "Account_ID": fields.Integer,
    "Name": fields.String,
}
resources_fields_wallet_detail={
    # "Id":fields.Integer,
    "Name":fields.String,
    "Price_PLN":fields.Float,
    "Price_USD":fields.Float,
    "Quantity":fields.Float
}

class Accounts_method(Resource):
    @marshal_with(resources_fields_accounts)
    def get(self, login_name):
        result = Accounts.query.filter_by(Login=login_name).first()
        if not result:
            abort(404, message="Dont have this login")
        return result

    @marshal_with(resources_fields_accounts)
    def put(self, login_name):
        args = login_put_args.parse_args()
        check_login = Accounts.query.filter_by(Login=login_name).first()
        if check_login:
            abort(409, massage="This login exists")
        new_login = Accounts(Login=login_name, Password=args["password"])
        db.session.add(new_login)
        db.session.commit()
        return new_login, 201

    @marshal_with(resources_fields_accounts)
    def patch(self, login_name):
        args = login_change_args.parse_args()
        change_in_account = Accounts.query.filter_by(Login=login_name).first()
        if not change_in_account:
            abort(409, massage="Login doesn't exist, cannot update")
        if args["login"]:
            change_in_account.Login = args["login"]
        if args["password"]:
            change_in_account.Password = args["password"]
        db.session.commit()
        return change_in_account, 201

    @marshal_with(resources_fields_accounts)
    def delete(self, login_name):
        account = Accounts.query.filter_by(Login=login_name).first()
        if not account:
            abort(409, massage="Login doesn't exist")
        db.session.delete(account)
        db.session.commit()
        return "", 204

class Wallet_detail_method(Resource):
    @marshal_with(resources_fields_wallet_detail)
    def get(self,wallet_id):
        result=Wallet_Details.query.filter_by(Wallet_ID=wallet_id).all()
        return result
    @marshal_with(resources_fields_wallet_detail)
    def put(self,wallet_id):
        args=wallet_detail_args.parse_args()
        new_value=Wallet_Details(Wallet_ID=wallet_id,Name=args['Name'],Price_PLN=args['Price_PLN'],Price_USD=args['Price_USD'],Quantity=args['Quantity'])
        db.session.add(new_value)
        db.session.commit()
        return new_value, 201

class Accounts_all(Resource):
    @marshal_with(resources_fields_accounts)
    def get(self):
        result = Accounts.query.filter_by().all()
        return result

class Wallets_method(Resource):
    @marshal_with(resources_fields_wallets)
    def get(self, ac_id):
        result = Wallets.query.filter_by(Account_ID=ac_id).all()
        return result,200
    @marshal_with(resources_fields_wallets)
    def put(self,ac_id):
        args=wallet_args.parse_args()
        new_wallet=Wallets(Account_ID=ac_id,Name=args['Name'])
        db.session.add(new_wallet)
        db.session.commit()
        return new_wallet,201

class Wallets_all(Resource):
    @marshal_with(resources_fields_wallets)
    def get(self):
        result = Wallets.query.filter_by().all()
        return result, 200


"""Wallet_details"""
api.add_resource(Wallet_detail_method,"/wallet_detail/<int:wallet_id>")
"""Accounts"""
api.add_resource(Accounts_method, "/authorization/<string:login_name>")
api.add_resource(Accounts_all, "/authorization/")
"""Wallets"""
api.add_resource(Wallets_method, "/wallets/<int:ac_id>")
api.add_resource(Wallets_all, "/wallets/")

# db.create_all()
if __name__ == "__main__":
    app.run(debug=True)
