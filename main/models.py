from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

db=SQLAlchemy()


class Admin(db.Model):
    admin_id=db.Column(db.Integer, autoincrement=True,primary_key=True)
    admin_username=db.Column(db.String(20),nullable=True)
    admin_pwd=db.Column(db.String(200),nullable=True)



class User(db.Model):  
    user_id = db.Column(db.Integer, autoincrement=True,primary_key=True)
    user_fullname = db.Column(db.String(100),nullable=False)
    user_pwd=db.Column(db.String(120),nullable=True)
    user_datereg=db.Column(db.DateTime(), default=datetime.utcnow)
    store_name = db.Column(db.String(100),nullable=False)
    admin_id = db.Column(db.Integer, db.ForeignKey('admin.admin_id'),nullable=False) 

    #set relationship
    dispdets = db.relationship("Dispensory",back_populates="userdets")
    



class Store(db.Model):
    store_id = db.Column(db.Integer, autoincrement=True,primary_key=True)
    store_name = db.Column(db.String(100),nullable=False)
    store_add = db.Column(db.String(100),nullable=False)
    store_datereg=db.Column(db.DateTime(), default=datetime.utcnow)
    admin_id = db.Column(db.Integer, db.ForeignKey('admin.admin_id'),nullable=False)
    


class Supplier(db.Model):
    supplier_id = db.Column(db.Integer, autoincrement=True,primary_key=True)
    supplier_name = db.Column(db.String(100),nullable=False)
    supplier_phone = db.Column(db.String(100),nullable=False)
    supplier_add = db.Column(db.String(100),nullable=False)
    supplier_email = db.Column(db.String(120),nullable=False) 
    supplier_datereg=db.Column(db.DateTime(), default=datetime.utcnow)
    admin_id = db.Column(db.Integer, db.ForeignKey('admin.admin_id'),nullable=False)


class Category(db.Model):
     category_id = db.Column(db.Integer, autoincrement=True,primary_key=True)
     category_name = db.Column(db.String(100),nullable=False)
     admin_id = db.Column(db.Integer, db.ForeignKey('admin.admin_id'),nullable=True)
     user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'),nullable=True)


class Warehouse(db.Model):
    product_id = db.Column(db.Integer, autoincrement=True,primary_key=True)
    product_name = db.Column(db.String(100),nullable=False)
    product_category = db.Column(db.String(100),nullable=False)
    product_qty = db.Column(db.Integer,nullable=False)
    total_productqty = db.Column(db.Integer,nullable=False)
    product_limit = db.Column(db.Integer,nullable=False)
    supplier_name = db.Column(db.String(100),nullable=False)
    cost_price = db.Column(db.Float,nullable=False)
    selling_price = db.Column(db.Float,nullable=False)
    total_selling_price = db.Column(db.Float,nullable=False)
    total_cost_price = db.Column(db.Float,nullable=False)
    created_datereg=db.Column(db.DateTime(), default=datetime.utcnow)
    comment = db.Column(db.String(100),nullable=True)
    admin_id = db.Column(db.Integer, db.ForeignKey('admin.admin_id'),nullable=False)




class Dispensory(db.Model):
     dispens_id = db.Column(db.Integer, autoincrement=True,primary_key=True)
     product_name = db.Column(db.String(100),nullable=False)
     product_category = db.Column(db.String(100),nullable=False)
     product_qty = db.Column(db.Integer,nullable=False)
     total_qty = db.Column(db.Integer,nullable=False)
     selling_price = db.Column(db.Float,nullable=False)
     store_name = db.Column(db.String(100),nullable=False)
     product_limit = db.Column(db.Integer,nullable=False)
     comment = db.Column(db.String(100),nullable=True)
     dispensed_datereg=db.Column(db.DateTime(), default=datetime.utcnow)
     admin_id = db.Column(db.Integer, db.ForeignKey('admin.admin_id'),nullable=False)
     user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'),nullable=True)

     #set relationship
     userdets = db.relationship("User",back_populates="dispdets")


class Sales(db.Model):
    sales_id = db.Column(db.Integer, autoincrement=True,primary_key=True)
    product_name = db.Column(db.String(100),nullable=False)
    product_category = db.Column(db.String(100),nullable=False)
    selling_price = db.Column(db.Float,nullable=False)
    product_qty = db.Column(db.Integer,nullable=False)
    comment = db.Column(db.String(100),nullable=True)
    total = db.Column(db.Float,nullable=False)
    sales_date=db.Column(db.DateTime(), default=datetime.utcnow)
    admin_id = db.Column(db.Integer, db.ForeignKey('admin.admin_id'),nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'),nullable=False)



class Warehouseupdate(db.Model):
    update_id = db.Column(db.Integer, autoincrement=True,primary_key=True)
    product_name = db.Column(db.String(100),nullable=False)
    product_category = db.Column(db.String(100),nullable=False)
    product_qty = db.Column(db.Integer,nullable=False)
    supplier_name = db.Column(db.String(100),nullable=False)
    cost_price = db.Column(db.Float,nullable=False)
    created_datereg=db.Column(db.DateTime(), default=datetime.utcnow)
    comment = db.Column(db.String(100),nullable=True)
    admin_id = db.Column(db.Integer, db.ForeignKey('admin.admin_id'),nullable=False)


class Dispensoryupdate(db.Model):
     update_id = db.Column(db.Integer, autoincrement=True,primary_key=True)
     product_name = db.Column(db.String(100),nullable=False)
     product_category = db.Column(db.String(100),nullable=False)
     product_qty = db.Column(db.Integer,nullable=False)
     total_qty = db.Column(db.Integer,nullable=False)
     selling_price = db.Column(db.Float,nullable=False)
     store_name = db.Column(db.String(100),nullable=False)
     comment = db.Column(db.String(100),nullable=True)
     update_datereg=db.Column(db.DateTime(), default=datetime.utcnow)
     admin_id = db.Column(db.Integer, db.ForeignKey('admin.admin_id'),nullable=False)
    

   




     

