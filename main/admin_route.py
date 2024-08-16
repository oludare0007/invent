import random,os,string
import json
import locale
from functools import wraps
import re
from flask import render_template,request,abort,redirect,flash,make_response,url_for,session,jsonify 
from werkzeug.security import generate_password_hash,check_password_hash
from sqlalchemy import or_,func  
from sqlalchemy.orm import aliased
from sqlalchemy.exc import IntegrityError
from datetime import datetime ,date,timedelta




#Local Imports
from main import app, csrf,mail,Message
from main.models import *
from main.forms import *

def login_required(f):
    @wraps(f)#this ensures that details(meta data) about the original function f, that is being decorated is still available
    def login_check(*args,**kwargs):
        if session.get("adminuser") != None:
            return f(*args,**kwargs)
        else:
            flash("Access Denied")
            return redirect("/login")
    return login_check






@app.route("/admin/")
def admin_page():
   if session.get("adminuser") == None or session.get("role")  !='admin':
      return render_template("admin/adminlogin.html")
   else:
      return redirect(url_for('admin_dashboard'))
   

@app.route("/admin/login/",methods=["GET","POST"])
def admin_login():
   if request.method =='GET':
      return render_template('admin/login.html')
   else:
      #retrieve form data
      username = request.form.get("username")
      pwd = request.form.get("pwd")
     
      check = db.session.query(Admin).filter(Admin.admin_username==username,Admin.admin_pwd==pwd).first()
      
      if check: 
         session['adminuser']=check.admin_id
         session['role']='admin'
         adminid = session.get('adminuser')
         admindeet = db.session.query(Admin).get_or_404(adminid)
         return redirect(url_for('admin_dashboard'))
        
      else: 
         flash('Invalid Login',category='error')
         return redirect(url_for('admin_login'))



@app.route("/admin/dashboard/")
@login_required
def admin_dashboard():
   lowstock = db.session.query(Warehouse).filter(Warehouse.product_qty <= Warehouse.product_limit).order_by(Warehouse.created_datereg.desc()).all() 
   admindeet = db.session.query(Admin).first()
   if session.get("adminuser") == None or session.get("role")  !='admin':
      return redirect(url_for("admin_login"))
   else:
      
      return render_template('admin/dashboard.html',admindeet=admindeet,lowstock=lowstock)
   


@app.route("/admin/logout")
def admin_logout():
   if session.get("adminuser") != None:
      session.pop("adminuser",None)
      session.pop("role",None)
      flash("You are logged out",category="info")
      return redirect(url_for("admin_login"))
   else:
      return redirect(url_for('admin_login'))




@app.route("/admin/register/",methods=['GET','POST'])
@login_required
def register():
    regform = RegForm()
    adm = session.get('adminuser')
    stores = db.session.query(Store.store_name).all()
    all_users = db.session.query(User).all()
    

    if request.method == "GET":
        return render_template("admin/register.html", regform=regform,stores=stores,all_users=all_users)
    else:
        if regform.validate_on_submit():
            admin = db.session.query(Admin).filter(Admin.admin_id == adm).first()

            if admin is None:
                flash("Admin user not found. Please check your session data.")
                return redirect('/admin/register')  # Redirect to the registration page

            # Retrieve the form data
            fullname = request.form.get("fullname")
            pwd = request.form.get("pwd")
            storename = request.form.get("supplier")
            existing_user = User.query.filter_by(user_fullname=fullname).first()

            if existing_user:
                flash("User Name already exists. Please choose a different Name.")
                return render_template("admin/register.html", regform=regform)

            
            admin_id = admin.admin_id
            new_user = User(user_fullname=fullname, user_pwd=pwd,store_name=storename,admin_id=admin_id)
            db.session.add(new_user)
            db.session.commit()
            flash("An account has been created for you.")
            return redirect('/admin/register')
        else:
            return render_template("admin/register.html", regform=regform)
        




@app.route("/admin/changepassword/<int:id>", methods=['GET','POST'])
def changepass(id):
    regform = RegForm()
    adm = session.get('adminuser')
    admin = db.session.query(Admin).filter(Admin.admin_id == adm).first()
    user = db.session.query(User).filter(User.user_id == id).first_or_404()
  
    
    if request.method == "GET":
        return render_template("admin/changepass.html", admin=admin,user=user)
    else:
        if admin is None:
            flash("Admin user not found. Please check your session data.")
            return redirect('/admin/register')
        if user is None:
            flash("User not found")
            return render_template("admin/changepass.html", admin=admin,user=user)
       
        old_password = request.form['oldpass']
        new_password = request.form['newpass']
        confirm_pass = request.form['confirmpass']

        if old_password != user.user_pwd:
            flash("Incorrect old password")
            return render_template("admin/changepass.html", admin=admin,user=user)
        
        if new_password == old_password:
            flash("New password and Old password cannot be the same")
            return render_template("admin/changepass.html", admin=admin,user=user)
    
        
        if new_password != confirm_pass:
            flash("New Passwords do not match")
            return render_template("admin/changepass.html", admin=admin,user=user)
        
        user.user_pwd = new_password
        db.session.commit()
        
        flash("Password Changed Successfully")
        return render_template("admin/register.html",user=user,admin=admin,regform=regform)

                


@app.route("/admin/store/", methods=['GET', 'POST'])
@login_required
def store():
    adm = session.get('adminuser')
    admin = db.session.query(Admin).filter(Admin.admin_id == adm).first()
    allstores = db.session.query(Store).all()

    if request.method == "GET":
        return render_template("admin/store.html",allstores=allstores)
    else:
        if admin is None:
            flash("Admin user not found. Please check your session data.")
            return redirect('/admin/register')  # Redirect to the registration page

        storenam = request.form.get("storename")
        storead = request.form.get("storeadd")

        # Check if any field is empty
        if not (storenam and storead):
            flash("Fill All Fields")
            return render_template("admin/store.html")

        existing_store = Store.query.filter_by(store_name=storenam).first()

        if existing_store:
            flash("Store Name already exists. Please choose a different Name.")
            return render_template("admin/store.html")

        admin_id = admin.admin_id
        new_store = Store(store_name=storenam, store_add=storead, admin_id=admin_id)
        db.session.add(new_store)
        db.session.commit()
        flash("A Store has been created for you.")
        return redirect('/admin/store')

    return render_template("admin/store.html")


@app.route("/admin/deletestore/<int:id>")
@login_required
def store_delete(id):
   store = db.session.query(Store).get_or_404(id)
   db.session.delete(store)
   db.session.commit()
   flash("Store record deleted")
   return redirect(url_for('store'))






@app.route("/admin/supplier/", methods=['GET', 'POST'])
@login_required
def supplier():
    adm = session.get('adminuser')
    admin = db.session.query(Admin).filter(Admin.admin_id == adm).first()
    allsupplier = db.session.query(Supplier).all()

    if request.method == "GET":
        return render_template("admin/supplier.html",allsupplier=allsupplier)
    else:
        if admin is None:
            flash("Admin user not found. Please check your session data.")
            return redirect('/admin/register')  # Redirect to the registration page
        
        suppliernam = request.form.get("suppname")
        supplierpho = request.form.get("stuppnum")
        supplieradd = request.form.get("stuppadd")
        supplieremail = request.form.get("stuppemail")

        # Check if any field is empty
        if not (suppliernam and supplierpho and supplieradd and supplieremail):
            flash("Fill in all the fields before submitting.")
            return render_template("admin/supplier.html",allsupplier=allsupplier)
        
        existing_supplier = Supplier.query.filter_by(supplier_name=suppliernam).first()

        if existing_supplier:
            flash("Supplier Name already exists. Please choose a different Name.")
            return render_template("admin/supplier.html")
        
        admin_id = admin.admin_id
        new_supplier = Supplier(supplier_name=suppliernam, supplier_phone=supplierpho,supplier_add=supplieradd,supplier_email=supplieremail, admin_id=admin_id)
        db.session.add(new_supplier)
        db.session.commit()
        flash("A New Supplier has been created.")
        return redirect('/admin/supplier')




@app.route("/admin/deletesupplier/<int:id>")
@login_required
def supplier_delete(id):
   suppliers = db.session.query(Supplier).get_or_404(id)
   db.session.delete(suppliers)
   db.session.commit()
   flash("Supplier record deleted")
   return redirect(url_for('supplier'))





@app.route("/admin/editsupplier/<int:id>", methods=['GET', 'POST'])
@login_required
def edit_supplier(id):
    supplier_id = id
    adm = session.get('adminuser')
    session['supp_id'] = supplier_id
    supplier_id = session.get('supp_id')
    allsupplier = db.session.query(Supplier).filter(Supplier.supplier_id == supplier_id).first()
    selected_supplier = Supplier.query.get(supplier_id)
    admin = db.session.query(Admin).filter(Admin.admin_id == adm).first()

    if request.method == "GET":
        return render_template("admin/editsupplier.html", allsupplier=allsupplier, selected_supplier=selected_supplier)
    elif request.method == "POST":
        if admin is None:
            flash("Admin user not found. Please check your session data.")
            return redirect('/admin/register')  # Redirect to the registration page

        suppliernam = request.form.get("suppname")
        supplierpho = request.form.get("stuppnum")
        supplieradd = request.form.get("stuppadd")
        supplieremail = request.form.get("stuppemail")

        # Check if any field is empty
        if not (suppliernam and supplierpho and supplieradd and supplieremail):
            flash("Fill in all the fields before submitting.")
            return render_template("admin/supplier.html", allsupplier=allsupplier)

        
        # Update the supplier record
        selected_supplier.supplier_name = suppliernam
        selected_supplier.supplier_phone = supplierpho
        selected_supplier.supplier_add = supplieradd
        selected_supplier.supplier_email = supplieremail

        db.session.commit()
        flash("Supplier Record Edited Successfully.")
        return redirect('/admin/supplier')

    


@app.route("/admin/category/", methods=['GET', 'POST'])
@login_required
def create_category():
    cat = db.session.query(Category).all()
    adm = session.get('adminuser')
    
    admin = db.session.query(Admin).filter(Admin.admin_id == adm).first()
    if request.method == "GET":
        return render_template("admin/category.html",cat=cat)
    else:
        if admin is None:
            flash("Admin user not found. Please check your session data.")
            return redirect('/admin/register')  # Redirect to the registration page
        categorynam = request.form.get("categoryName")
        
        if not (categorynam):
            flash("Fill in all the fields before submitting.")
            return render_template("admin/category.html")
        existing_category = Category.query.filter_by(category_name=categorynam).first()
        

        if existing_category:
            flash("Category already exists. Please choose a different Name.")
            return render_template("admin/category.html")
        
        admin_id = admin.admin_id
        
        new_category = Category(category_name=categorynam,admin_id=admin_id)
        db.session.add(new_category)
        db.session.commit()
        flash("A New Category has been created.")
        return render_template("admin/category.html")
    

@app.route("/admin/deletecat/<int:id>")
@login_required
def category_delete(id):
   cat = db.session.query(Category).get_or_404(id)
   db.session.delete(cat)
   db.session.commit()
   flash("Category deleted")
   return redirect(url_for('create_category'))



@app.route("/admin/warehouse/", methods=['GET', 'POST'])
@login_required
def warehouse():
    adm = session.get('adminuser')
    admin = db.session.query(Admin).filter(Admin.admin_id == adm).first()
    cat = db.session.query(Category).all()
    supp = db.session.query(Supplier).all()
    allstock = db.session.query(Warehouse).order_by(Warehouse.created_datereg.desc()).limit(30).all()
    

    if request.method == "GET":
        return render_template("admin/warehouse.html",cat=cat,supp=supp,allstock=allstock)
    
    
    else:
        if admin is None:
            flash("Admin user not found. Please check your session data.")
            return redirect('/admin/register')  # Redirect to the registration page
        
        productnam = request.form.get("productname")
        productcat = request.form.get("category")
        productsupp = request.form.get("supplier")
        productqty = request.form.get("productqty")
        productcost = request.form.get("costprice")
        productsell = request.form.get("sellingprice")
        productcomment = request.form.get("comment")
        productlimit = request.form.get("plimit")
        totalproducrqty = request.form.get("totalproductqty")

        # Validation
        if not (productnam and productcat and productsupp and productqty and productcost and productsell and totalproducrqty and  productlimit):
            flash("Fill in all the fields before submitting.")
            return render_template("admin/warehouse.html")
        
        total_cost_price = float(productcost) * int(totalproducrqty)
        total_selling_price = float(productsell) * int(totalproducrqty)


        
        admin_id = admin.admin_id
        new_stock = Warehouse(product_name=productnam, product_category=productcat,product_qty=productqty,total_productqty=totalproducrqty,supplier_name=productsupp, cost_price=productcost,selling_price=productsell,comment=productcomment,product_limit=productlimit,total_cost_price=total_cost_price,total_selling_price=total_selling_price,admin_id=admin_id)
        db.session.add(new_stock)
        db.session.commit()

        flash("Stock details sent to ware house")

    
        return redirect('/admin/warehouse')
    




@app.route("/admin/warehouseupdate/", methods=['GET', 'POST'])
@login_required
def warehouseupdate():
    adm = session.get('adminuser')
    admin = db.session.query(Admin).filter(Admin.admin_id == adm).first()
    cat = db.session.query(Category).all()
    supp = db.session.query(Supplier).all()
    prod_name = db.session.query(Warehouse).all()
    warehouse_update = db.session.query(Warehouseupdate).all()

    if request.method == "GET":
        return render_template("admin/warehouseupdate.html", cat=cat, supp=supp, prod_name=prod_name,warehouse_update=warehouse_update)
    else:
        if admin is None:
            flash("Admin user not found. Please check your session data.")
            return redirect('/admin/register')  # Redirect to the registration page

        productnam = request.form.get("productname")
        productcat = request.form.get("category")
        productsupp = request.form.get("supplier")
        productqty = int(request.form.get("productqty"))  # Convert to integer
        productcost = request.form.get("costprice")
        productcomment = request.form.get("comment")

        # Validation
        if not (productnam and productcat and productsupp and productqty and productcost):
            flash("Fill in all the fields before submitting.")
            return render_template("admin/warehouseupdate.html")

        selected_product = Warehouse.query.filter(Warehouse.product_name == productnam).first()
        
       
        
        if selected_product:
            admin_id = admin.admin_id
            
            
            
            selected_product.product_qty += productqty  # Update product quantity
            selected_product.total_productqty += productqty #Update Total product quantity
            selected_product.cost_price = productcost #Update cost price
            stock_update = Warehouseupdate(
                product_name=productnam, product_category=productcat, product_qty=productqty,
                supplier_name=productsupp, cost_price=productcost, comment=productcomment,admin_id=admin_id
            )
            db.session.add(stock_update)
            try:
                db.session.commit()
                flash("Warehouse Updated")
            except IntegrityError:
                db.session.rollback()
                flash("An error occurred while updating the warehouse")
        

        return redirect('/admin/warehouseupdate')

    

@app.route("/admin/totalstock/", methods=['GET', 'POST'])
@login_required
def totalstock():
    admindeet = db.session.query(Admin).first()
    adm = session.get('adminuser')
    admin = db.session.query(Admin).filter(Admin.admin_id == adm).first()
    total_all_stock = db.session.query(Warehouse).order_by(Warehouse.created_datereg.desc()).all()

    if admin is None:
            flash("Admin user not found. Please check your session data.")
            return redirect('/admin/register')
    else:
        return render_template('/admin/allstock.html',total_all_stock=total_all_stock,admindeet=admindeet)




@app.route("/admin/delete/<int:id>")
@login_required
def stock_delete(id):
   record = db.session.query(Warehouse).get_or_404(id)
   db.session.delete(record)
   db.session.commit()
   flash("Stock record deleted")
   return redirect(url_for('warehouse'))




@app.route("/admin/deletedispense/<int:id>")
@login_required
def dispense_delete(id):
    record_dis = db.session.query(Dispensory).get_or_404(id)
    
    # Retrieve the quantity to be added to Warehouse product_qty
    quantity_to_add = record_dis.product_qty
    # Delete the Dispensory record
    db.session.delete(record_dis)
    db.session.commit()
    # Update Warehouse product_qty by adding the quantity from Dispensory
    warehouse_record = db.session.query(Warehouse).filter_by(product_name=record_dis.product_name).first()
    if warehouse_record:
        warehouse_record.product_qty += quantity_to_add
        db.session.commit()
        flash("Dispensary record deleted and Warehouse updated")
    else:
        flash("Dispensary record deleted but corresponding Warehouse record not found")

    return redirect(url_for('dispense_conf'))




@app.route("/admin/editcomment/<int:id>", methods=["POST", "GET"])
@login_required
def editcomment(id):
    editcomment=EditComment()
   
    record = db.session.query(Warehouse).filter(Warehouse.product_id== id).first_or_404()

    if request.method == "GET":
        return render_template("admin/editcomment.html", record=record,editcomment=editcomment)
    else: 
        if editcomment.validate_on_submit():
            comment_update = Warehouse.query.get(id)
            comment_update.comment = request.form.get("comment")
        
            db.session.commit()
            flash("Message updated")
        else:
            flash("Message not updated. Comment cannot be empty.")
            
    return render_template("admin/editcomment.html", record=record,editcomment=editcomment)




@app.route("/admin/edithstock/<int:id>", methods=['GET', 'POST'])
@login_required
def edithstock(id):
    adm = session.get('adminuser')
    admin = db.session.query(Admin).filter(Admin.admin_id == adm).first()
    cat = db.session.query(Category).all()
    supp = db.session.query(Supplier).all()
    allstock = db.session.query(Warehouse).filter(Warehouse.product_id == id).first_or_404()
    
    if request.method == "GET":
        return render_template("admin/editstock.html", cat=cat, supp=supp, allstock=allstock)
    else:
        if admin is None:
            flash("Admin user not found. Please check your session data.")
            return redirect('/admin/register')  # Redirect to the registration page

        productnam = request.form.get("productname")
        productcat = request.form.get("category")
        productsupp = request.form.get("supplier")
        productqty = request.form.get("productqty")
        productcost = request.form.get("costprice")
        productsell = request.form.get("sellingprice")
        productcomment = request.form.get("comment")
        productlimit = request.form.get("plimit")
        totalproducrqty = request.form.get("totalproductqty")

        # Validation
        if not (productnam and productcat and productsupp and productqty and productcost and productsell and productlimit and totalproducrqty):
            flash("Fill in all the fields before submitting.")
            return redirect(request.url)  # Redirect back to the edit page
        
        total_cost_price = float(productcost) * int(totalproducrqty)
        total_selling_price = float(productsell) * int(totalproducrqty)

        stock_update = Warehouse.query.get(id)
        stock_update.product_name = productnam
        stock_update.product_category = productcat
        stock_update.supplier_name = productsupp
        stock_update.product_qty = productqty
        stock_update.cost_price = productcost
        stock_update.selling_price = productsell
        stock_update.comment = productcomment
        stock_update.product_limit = productlimit
        stock_update.total_productqty = totalproducrqty
        stock_update.total_cost_price = total_cost_price
        stock_update.total_selling_price = total_selling_price

        

        db.session.commit()
        flash("Stock details updated")
        return render_template("admin/editstock.html", cat=cat, supp=supp, allstock=allstock)
       


@app.route("/admin/dispense_conf", methods=['GET', 'POST'])
@login_required
def dispense_conf():
    all_dispensed_stock = db.session.query(Dispensory).order_by(Dispensory.dispensed_datereg.desc()).all()
    allproduct = db.session.query(Warehouse).all()

    if request.method == 'GET':
        return render_template("admin/dispense_conf.html", allproduct=allproduct, all_dispensed_stock=all_dispensed_stock)
    else:
        product_id = request.form.get("productname")
        if not product_id:
            flash("Select the product you want to dispense.", "error")
            return redirect(url_for("dispense_conf"))

        session['prod_id'] = product_id
        return redirect(url_for("dispense", id=product_id))






@app.route("/admin/dispense/<int:id>", methods=['GET', 'POST'])
@login_required
def dispense(id):
    product_id = session.get('prod_id')
    adm = session.get('adminuser')
    admin = db.session.query(Admin).filter(Admin.admin_id == adm).first()
    cat = db.session.query(Category).all()
    supp = db.session.query(Supplier).all()
    allstore = db.session.query(Store).all()
    allproduct = db.session.query(Warehouse).all()
    selected_product = Warehouse.query.get(product_id)
    
    
    if request.method == "GET":
        return render_template("admin/dispensory.html",cat=cat,supp=supp,allproduct=allproduct,allstore=allstore,product_id=product_id,selected_product=selected_product)
    else:
        if admin is None:
            flash("Admin user not found. Please check your session data.")
            return redirect('/admin/register')  # Redirect to the registration page
        
        productnam = request.form.get("productname")
        store = request.form.get("store")
        productdis = request.form.get("productqty")
        productsell = request.form.get("sellingprice")
        productlimit = request.form.get("productlimit")
        totalqty = request.form.get("totqty")
        productcomment = request.form.get("comment")
        productcategory = request.form.get("category")
        

        # Validation
        if not (productnam and store and productdis and productsell and productlimit and productcategory and totalqty):
            flash("Fill in all the fields before submitting.")
            return render_template("admin/dispensory.html",cat=cat,supp=supp,allproduct=allproduct,allstore=allstore,product_id=product_id,selected_product=selected_product)
        
        available_product = Warehouse.query.filter_by(product_name=productnam).first()
        if available_product:
            if available_product.product_qty == 0:
                flash('Out Of Stock')
                return redirect(url_for('dispense', id=product_id))


        if available_product.product_qty < int(productdis):
                flash('Warehouse stock lower than dispense')
                return redirect(url_for('dispense', id=product_id))
        admin_id = admin.admin_id
        dispense_stock = Dispensory(product_name=productnam, store_name=store,product_qty=productdis,selling_price=productsell,comment=productcomment,product_category=productcategory,product_limit=productlimit,total_qty=totalqty,admin_id=admin_id)
        db.session.add(dispense_stock)
        db.session.commit()
        
        warehouse_alias = aliased(Warehouse)
        product_to_update = db.session.query(warehouse_alias).filter(warehouse_alias.product_id == product_id).first()

        if product_to_update:
            product_to_update.product_qty -= int(productdis)
            db.session.commit()
        flash("Stock Dispensed and Warehouse Updated")
        return redirect('/admin/warehouse')
    



@app.route("/ajax_opt/", methods=['POST'])
@csrf.exempt
def ajax_option():
    if request.method == 'POST':
        dispens_id = request.form.get('productname')
        product_deets = Dispensory.query.filter_by(dispens_id=dispens_id).first()
        store_name = product_deets.store_name if product_deets else None
        

        return jsonify({'store_nam': store_name})
    return jsonify({'error': 'Invalid request'})

        





@app.route("/admin/dispensecon_update", methods=['GET', 'POST'])
@login_required
def dispensecon_update():
    allstore = db.session.query(Store).all()
    allproduct = db.session.query(Dispensory).all()

    if request.method == 'GET':
        return render_template("admin/dispensecon_update.html", allproduct=allproduct,allstore=allstore)
    else:
        dispens_id = request.form.get("productname")
        if not dispens_id:
            flash("Select the product you want to update.", "error")
            return redirect(url_for("dispensecon_update"))

        session['dis_id'] = dispens_id
        return redirect(url_for("dispense_update", id=dispens_id))
    

    



@app.route("/admin/dispenseupdate/<int:id>", methods=['GET', 'POST'])
@login_required
def dispense_update(id):
    dispens_id = session.get('dis_id')
    adm = session.get('adminuser')
    admin = db.session.query(Admin).filter(Admin.admin_id == adm).first()
    cat = db.session.query(Category).all()
    supp = db.session.query(Supplier).all()
    allstore = db.session.query(Store).all()
    allproduct = db.session.query(Warehouse).all()
    selected_product = Dispensory.query.get(dispens_id)
    
    if request.method == "GET":
        return render_template("admin/dispensoryupdate.html", cat=cat, supp=supp, allproduct=allproduct, allstore=allstore, dispens_id=dispens_id, selected_product=selected_product)
    else:
        if admin is None:
            flash("Admin user not found. Please check your session data.")
            return redirect('/admin/register')

        productnam = request.form.get("productname")
        store = request.form.get("store")
        productqty = request.form.get("productqty")
        productsell = request.form.get("sellingprice")
        totalqty = request.form.get("totqty")
        productcomment = request.form.get("comment")
        productcategory = request.form.get("category")

        # Validation
        if not (productnam and store and productqty and productsell and productcategory and totalqty):
            flash("Fill in all the fields before submitting.")
            return render_template("admin/dispensory.html", cat=cat, supp=supp, allproduct=allproduct, allstore=allstore, dispens_id=dispens_id, selected_product=selected_product)
        
        available_product = Warehouse.query.filter_by(product_name=productnam).first()
        if available_product:
            if available_product.product_qty == 0:
                flash('Out Of Stock')
                return redirect(url_for('dispense_update', id=dispens_id))


        if available_product.product_qty < int(productqty):
                flash('Warehouse stock lower than dispense')
                return redirect(url_for('dispense_update', id=dispens_id))


        admin_id = admin.admin_id
        dispense_update = Dispensoryupdate(product_name=productnam, store_name=store, product_qty=productqty, selling_price=productsell, comment=productcomment, product_category=productcategory, total_qty=totalqty, admin_id=admin_id)
        db.session.add(dispense_update)
        db.session.commit()

        product_to_update = db.session.query(Warehouse).filter(Warehouse.product_name == productnam).first()
        if product_to_update:
            product_to_update.product_qty -= int(productqty)
            db.session.commit()

        update_selected_product = Dispensory.query.filter(Dispensory.product_name == productnam,Dispensory.store_name == store).first()
        product_update = Dispensory.query.filter(Dispensory.product_name == productnam,Dispensory.store_name == store).first()

        if update_selected_product and product_update:
            update_selected_product.total_qty += int(productqty)
            product_update.product_qty += int(productqty)
            db.session.commit()

        flash("Stock and Warehouse Updated")
        return redirect('/admin/warehouse')





@app.route("/admin/edithdispens/<int:id>", methods=['GET', 'POST'])
@login_required
def edithdispen(id):
    adm = session.get('adminuser')
    admin = db.session.query(Admin).filter(Admin.admin_id == adm).first()
    allstock = db.session.query(Dispensory).filter(Dispensory.dispens_id == id).first_or_404()
    
    if request.method == "GET":
        return render_template("admin/editdispens.html", allstock=allstock)
    else:
        if admin is None:
            flash("Admin user not found. Please check your session data.")
            return redirect('/admin/register')  # Redirect to the registration page

        
        productqty = request.form.get("productqty")
        productsell = request.form.get("sellingprice")
        productcomment = request.form.get("comment")
        productlimit = request.form.get("plimit")

        # Validation
        if not ( productqty and productsell and productlimit):
            flash("Fill in all the fields before submitting.")
            return redirect(request.url)  # Redirect back to the edit page

        stock_update = Dispensory.query.get(id)
        stock_update.product_qty = productqty
        stock_update.selling_price = productsell
        stock_update.comment = productcomment
        stock_update.product_limit = productlimit

        db.session.commit()
        flash("Dispense details updated")
        return render_template("admin/dispense_conf.html",  allstock=allstock)




@app.route("/admin/stockupdate/", methods=['GET', 'POST'])
@login_required
def stockupdate():
    admindeet = db.session.query(Admin).first()
    adm = session.get('adminuser')
    admin = db.session.query(Admin).filter(Admin.admin_id == adm).first()
    total_stock_update = db.session.query(Warehouseupdate).order_by(Warehouseupdate.created_datereg.desc()).all()

    if admin is None:
            flash("Admin user not found. Please check your session data.")
            return redirect('/admin/register')
    else:
        return render_template('/admin/allstockupdate.html',total_stock_update=total_stock_update,admindeet=admindeet)
    


@app.route("/admin/dispensedupdate/", methods=['GET', 'POST'])
@login_required
def dispensed_update():
    admindeet = db.session.query(Admin).first()
    adm = session.get('adminuser')
    admin = db.session.query(Admin).filter(Admin.admin_id == adm).first()
    all_dispens_update = db.session.query(Dispensoryupdate).order_by(Dispensoryupdate.update_datereg.desc()).all()

    if admin is None:
            flash("Admin user not found. Please check your session data.")
            return redirect('/admin/register')
    else:
        return render_template('/admin/alldispensoryupdate.html',all_dispens_update=all_dispens_update,admindeet=admindeet)




@app.route("/admin/account/", methods=['GET', 'POST'])
@login_required
def account():
    admindeet = db.session.query(Admin).first()
    adm = session.get('adminuser')
    admin = db.session.query(Admin).filter(Admin.admin_id == adm).first()
    all_sales_record = (
     db.session.query(
         func.date_format(Sales.sales_date, '%Y-%m-%d').label('day'),
         func.sum(Sales.total).label('total_sales')
     )
     .group_by(func.date_format(Sales.sales_date, '%Y-%m-%d'))
     .order_by(func.date_format(Sales.sales_date, '%Y-%m-%d'))
     .all()
 )
    
    yearly_sales = (
    db.session.query(
        func.sum(Sales.total).label('total_sales')
    )
).scalar()
    
    
    totalt_sales_price = db.session.query(func.sum(Warehouse.total_selling_price)).scalar()
    wearhouse_exp = db.session.query(func.sum(Warehouse.total_cost_price)).scalar()
    total_exp = (wearhouse_exp or 0) 
    total_expected_profit = (totalt_sales_price or 0) - (total_exp or 0)

     # Formatting numerical values with commas
    yearly_sales_formatted = "{:,.2f}".format(yearly_sales or 0.0)
    totalt_sales_price_formatted = "{:,.2f}".format(totalt_sales_price or 0.0)
    total_exp_formatted = "{:,.2f}".format(total_exp or 0.0)
    total_expected_profit_formatted = "{:,.2f}".format(total_expected_profit or 0.0) 

    return render_template('/admin/account.html',admin=admin,admindeet=admindeet,all_sales_record=all_sales_record,yearly_sales_formatted=yearly_sales_formatted,total_exp_formatted=total_exp_formatted,total_expected_profit_formatted=total_expected_profit_formatted,totalt_sales_price_formatted=totalt_sales_price_formatted or 0.0)





@app.route("/admin/productrecords/", methods=['GET', 'POST'])
@login_required
def product_records():
    admindeet = db.session.query(Admin).first()
    adm = session.get('adminuser')
    admin = db.session.query(Admin).filter(Admin.admin_id == adm).first()
    all_product_rec = db.session.query(Dispensory).all()
    today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    today_end = today_start + timedelta(days=1)

    all_daily_sale = db.session.query(Sales).filter(Sales.sales_date >= today_start, Sales.sales_date < today_end).all()
    

    if admin is None:
            flash("Admin user not found. Please check your session data.")
            return redirect('/admin/register')
    else:
        return render_template('/admin/allproductsrec.html',all_product_rec=all_product_rec,all_daily_sale=all_daily_sale,admindeet=admindeet)



@app.route("/admin/allsales/", methods=['GET', 'POST'])
@login_required
def all_sales():
    admindeet = db.session.query(Admin).first()
    adm = session.get('adminuser')
    admin = db.session.query(Admin).filter(Admin.admin_id == adm).first()
    all_sales = db.session.query(Sales).all()

    if admin is None:
            flash("Admin user not found. Please check your session data.")
            return redirect('/admin/register')
    else:
        return render_template("/admin/allsales.html",all_sales=all_sales,admindeet=admindeet)












     

