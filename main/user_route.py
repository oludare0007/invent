import random,os,string
import json

from functools import wraps
import re
from flask import Flask, render_template,request,abort,redirect,flash,make_response,url_for,session, jsonify 
from flask_wtf.csrf import CSRFProtect
from werkzeug.security import generate_password_hash,check_password_hash
from sqlalchemy import or_,func
from sqlalchemy.orm import aliased
from datetime import datetime , date,timedelta





#Local Imports
from main import app, csrf,mail,Message
from main.models import *
from main.forms import *



def login_required(f):
   @wraps(f) #This ensures that details(meta data) about the original function f, that is being decorated is still available
   def login_check(*args,**kwargs):
      if session.get("userloggedin") !=None:
         return f(*args,**kwargs)
      else:
         flash("Access Denied")
         return redirect('/login')
   return login_check


@app.route('/user/login/',methods=["POST","GET"])
def user_login():
   
   if request.method =='GET':
      return render_template('user/userlogin.html')
   else:
      username = request.form.get('username')
      password = request.form.get('pwd')
      check = db.session.query(User).filter(User.user_fullname==username,User.user_pwd==password).first()

      if check: 
         session['userloggedin']=check.user_id
         session['role']='user'
         userid = session.get('userloggedin')
         userdeets = db.session.query(User).get_or_404(userid)
         return redirect(url_for('user_dashboard'))
        
      else: 
         flash('Invalid Login Details',category='error')
         return redirect(url_for('user_login'))


@app.route("/user/dashboard/")
@login_required
def user_dashboard():
   usersession = session.get('userloggedin')
   user = db.session.query(User).get(usersession)
   
   lowstock = db.session.query(Dispensory).\
    filter(Dispensory.store_name == user.store_name).\
    filter(Dispensory.product_qty <= Dispensory.product_limit).\
    all()
   store_names = db.session.query(Dispensory.store_name).distinct().all()
   usersession = session.get('userloggedin')
   userdeet = db.session.query(User).get(usersession)
   if session.get("userloggedin") == None or session.get("role")  !='user':
      return redirect(url_for("user_login"))
   else:
      
      return render_template('user/dashboard.html',userdeet=userdeet,usersession=usersession,store_names=store_names,lowstock=lowstock)
   
   

@app.route("/user/logout/")
def user_logout():
   if session.get('userloggedin') != None:
      session.pop('userloggedin',None)
      session.pop('role',None)
      flash('You are Logged Out',category="info")
      return redirect(url_for('user_login'))
   else:
      return redirect(url_for('user_login'))
   
   
   

@app.route("/user/allstock/")
def allstock():

   usersession = session.get('userloggedin')
   userdeet = db.session.query(User).get(usersession)
   user = db.session.query(User).get(usersession)
   allstock = db.session.query(Dispensory).filter(Dispensory.store_name==user.store_name).all()
    
   return render_template("user/allstock.html",allstock=allstock,user=user,userdeet=userdeet)



@app.route("/ajax_options/",methods=["POST"])
@csrf.exempt
def ajax_options():
   if request.method=="POST":
      product_name = request.form.get('productname')
      product_deets = Dispensory.query.filter_by(product_name=product_name).first()
      product_category = product_deets.product_category if product_deets else None 
      # selling_price = product_deets = Dispensory.query.filter_by(product_name=product_name).first()
      # cost_price = product_deets = Dispensory.query.filter_by(product_name=product_name).first()

      selling_price = product_deets.selling_price if product_deets else None
     

      return jsonify({'product_cat': product_category,'selling_P':selling_price})
   return jsonify({'error':'Invalid request'})






@app.route("/user/sales/", methods=['GET', 'POST'])
def sales():
    usersession = session.get('userloggedin')
    userdeet = db.session.query(User).get(usersession)
    user = db.session.query(User).filter(User.user_id == usersession).first()
    allstock = db.session.query(Dispensory).filter(Dispensory.store_name == user.store_name).all()
    
    if request.method == "GET":
        today = datetime.now().date()
        daily_sales = (
            db.session.query(
                func.sum(Sales.total).label('total_sales')
            )
            .filter(func.date(Sales.sales_date) == today)
            .scalar()
        )

        daily_sales_formatted = "{:,.2f}".format(daily_sales or 0.0)

        return render_template("user/sales.html", userdeet=userdeet, allstock=allstock, daily_sales_formatted=daily_sales_formatted or 0.0)
        
    else:
        if user is None:
            flash("User not found. Please check your session data.")
            return redirect('/user/login')


        productname = request.form.get("productname")
        salesprice = request.form.get("sellingprice")
        productquantity = request.form.get("productqty")
        productcategory = request.form.get("category")
        salescomment = request.form.get("comment")
        salestotal = request.form.get("total")
        

        # Check if any field is empty
        if not (productname and salesprice and productquantity and productcategory and salestotal):
            flash("Fill in all the fields before submitting.")
            return render_template("user/sales.html", userdeet=userdeet, allstock=allstock)
        user_login = user.user_id
        
        selected_product = Dispensory.query.filter(Dispensory.product_name == productname).\
                           filter(Dispensory.store_name == user.store_name).\
                              first()
       
        new_sales = Sales(product_name=productname, product_category=productcategory,
                             selling_price=salesprice, product_qty=productquantity,
                             comment=salescomment,total=salestotal, user_id=user_login)
        if selected_product:
            if selected_product.product_qty == 0:
               flash(" Product Finished")
               return redirect(url_for('sales'))
           
            elif selected_product.product_qty < int(productquantity):
               flash(" Check Available Quantity")
               return redirect(url_for('sales'))
        
        db.session.add(new_sales)
        db.session.commit()
      
        if selected_product:
           selected_product.product_qty -= int(productquantity)
           db.session.commit()
        flash("Sales Saved ")
        return render_template("user/sales.html", userdeet=userdeet, allstock=allstock)



@app.route("/user/todaysales/", methods=['GET', 'POST'])
def today_sales():
   usersession = session.get('userloggedin')
   userdeet = db.session.query(User).get(usersession)
   user = db.session.query(User).filter(User.user_id == usersession).first()
   today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
   today_end = today_start + timedelta(days=1)
   all_daily_sale = db.session.query(Sales).filter(Sales.sales_date >= today_start, Sales.sales_date < today_end).all()

   if user is None:
            flash("User not found. Please check your session data.")
            return redirect('/user/login')
   else:
      return render_template("user/todaysales.html",userdeet=userdeet,all_daily_sale=all_daily_sale)















   
      
      
   
