from werkzeug.utils import redirect
from flask import Flask, render_template, request, redirect, url_for, flash,session, send_file
import os
from flask_mysqldb import MySQL
import random
import string
import qrcode
from io import BytesIO
import datetime

app=Flask('__name__')
app.secret_key='your-secret-key'

app.config['MYSQL_HOST']='localhost'
app.config['MYSQL_USER']='root'
app.config['MYSQL_PASSWORD']=''
app.config['MYSQL_DB']='royal'

mysql=MySQL(app)

UPLOAD_FOLDER = os.path.join('static', 'uploads')
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def generate_captcha():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))

@app.route('/')
def index():
    if 'usernm' not in session:
        return redirect(url_for('login'))  # Redirect to login page if session is not started (not logged in)
    return render_template('index.html', username=session['usernm'])  # Display the index page if logged in


@app.route("/login", methods=['GET', 'POST'])
def login():
    if 'attempts' not in session:
        session['attempts'] = 0

    if request.method == 'POST':
        username = request.form['usernm']
        pwd = request.form['password']
        captcha_response = request.form.get('captcha')  # Getting CAPTCHA response from form

        # Check CAPTCHA only after 3 failed attempts
        if session['attempts'] >= 3:
            if captcha_response != session.get('captcha'):
                return render_template('login.html', error="Invalid CAPTCHA", show_captcha=True)

        cur = mysql.connection.cursor()
        cur.execute(f"SELECT usernm, password, email, phonno FROM registration WHERE usernm = '{username}'")
        user = cur.fetchone()
        cur.close()

        if user and pwd == user[1]:
            # Set session variables after successful login
            session['usernm'] = user[0]
            session['email'] = user[2]  # Set email to session after successful login
            session['phonno'] = user[3]  # Set phonno to session
            session['attempts'] = 0  # Reset failed attempts on successful login

            # If user has an existing cart, load it from the user_cart table
            cur = mysql.connection.cursor()
            cur.execute("SELECT id, quantity FROM cart WHERE userid = (SELECT id FROM registration WHERE usernm = %s)", (username,))
            cart_items = cur.fetchall()

            # Store cart items in session
            session['cart'] = {}
            for item in cart_items:
                session['cart'][str(item[0])] = item[1]

            mysql.connection.commit()
            cur.close()

            return redirect(url_for('index'))  # Redirect to home page after login
        else:
            session['attempts'] += 1  # Increment failed attempts
            if session['attempts'] >= 3:
                session['captcha'] = generate_captcha()  # Generate a CAPTCHA after 3 failed attempts
            return render_template('login.html', error='Invalid username or password', show_captcha=session['attempts'] >= 3)

    return render_template('login.html', show_captcha=session['attempts'] >= 3)


@app.route('/logout_user')
def logout_user():
    if 'usernm' in session:
        username = session['usernm']  # Get the username from the session

        # Fetch the user ID from the database based on the username
        cur = mysql.connection.cursor()
        cur.execute("SELECT userid FROM registration WHERE usernm = %s", (username,))
        user = cur.fetchone()

        if user:
            user_id = user[0]  # Get the user_id from the database result

            # Check if there's any data in the session cart
            if 'cart' in session:
                for product_id, quantity in session['cart'].items():
                    # Save it to the user_cart table
                    cur.execute("SELECT userid FROM cart WHERE userid = %s AND id = %s", (user_id, product_id))
                    cart_item = cur.fetchone()

                    if cart_item:
                        # If product already exists, update quantity
                        cur.execute("UPDATE cart SET quantity = quantity + %s WHERE userid = %s AND id = %s",
                                    (quantity, user_id, product_id))
                    else:
                        # Insert new cart item
                        cur.execute("INSERT INTO cart (userid, id, quantity) VALUES (%s, %s, %s)",
                                    (user_id, product_id, quantity))

                mysql.connection.commit()
                cur.close()

        session.clear()  # Clear the session data
    return redirect(url_for('login'))  # Redirect to login page


@app.route("/add_to_cart", methods=['POST'])
def add_to_cart():
    product_id = request.form['product_id']
    quantity = int(request.form['quantity'])

    cur = mysql.connection.cursor()
    cur.execute("SELECT stock FROM product WHERE id = %s", (product_id,))
    product = cur.fetchone()

    if not product:
        return "Product not found", 404

    available_stock = product[0]

    if available_stock == 0:
        flash("Sorry, this product is out of stock!", "danger")
        return redirect(url_for('product'))

    if quantity > available_stock:
        flash(f"Only {available_stock} units available!", "warning")
        return redirect(url_for('product'))

    # Deduct stock immediately when added to cart
    cur.execute("UPDATE product SET stock = stock - %s WHERE id = %s", (quantity, product_id))
    mysql.connection.commit()
    cur.close()

    # Store cart in session
    if 'cart' not in session:
        session['cart'] = {}

    session['cart'][product_id] = session['cart'].get(product_id, 0) + quantity
    session.modified = True

    flash("Item added to cart!", "success")

    # ✅ Redirect to cart page after adding the product
    return redirect(url_for('cart'))

@app.route('/cart')
def cart():
    # Fetch the cart items from the session
    cart_items = session.get('cart', {})

    # Initialize a list to hold the updated cart items
    updated_cart_items = []
    total_price = 0

    # Iterate over the cart items (product IDs and quantities)
    for product_id, quantity in cart_items.items():
        # Fetch product details from the database based on product_id
        cur = mysql.connection.cursor()
        cur.execute("SELECT id, name, price, image FROM product WHERE id = %s", (product_id,))
        product = cur.fetchone()
        cur.close()

        if product:
            # Add the product and its quantity to the updated list
            updated_cart_items.append({
                'id': product[0],
                'name': product[1],
                'price': product[2],
                'quantity': quantity,
                'image': product[3]  # This is the relative path to the product image
            })
            # Calculate the total price for this product and add it to the total price
            total_price += product[2] * quantity
        else:
            # Handle the case where the product is not found in the database
            updated_cart_items.append({
                'id': None,
                'name': 'Unknown Product',
                'price': 0,
                'quantity': 0,
                'image': 'default.jpg'  # Use a default image if the product is not found
            })

    # Assuming you have a session-based user identification, get the user ID
    user_id = session.get('userid')  # Or however you are identifying the user

    if user_id:
        # Update the total price in the cart table
        cur = mysql.connection.cursor()
        cur.execute("UPDATE cart SET total = %s WHERE userid = %s", (total_price, user_id))
        mysql.connection.commit()
        cur.close()

    # Render the cart page with the updated cart items and total price
    return render_template('cart.html', cart=updated_cart_items, total_price=total_price)




@app.route('/generate_qr/<data>')
def generate_qr(data):
    # Generate QR code
    img = qrcode.make(data)

    # Save the QR code in memory
    img_io = BytesIO()
    img.save(img_io, 'PNG')
    img_io.seek(0)

    return send_file(img_io, mimetype='image/png')




@app.route("/registration", methods=['GET','POST'])
def registration():
    if request.method == 'POST':
      #  userid=request.form['userid']
        firstnm = request.form['firstnm']
        lastnm = request.form['lastnm']
        usernm = request.form['usernm']
        password = request.form['password']
        email = request.form['email']
        phonno = request.form['phonno']
        address = request.form['address']
        country = request.form['country']
        state = request.form['state']
        date = request.form['date']
        cur=mysql.connection.cursor()
        cur.execute(f"insert into registration(firstnm,lastnm,usernm,password,email,phonno,address,country,state,date) values ('{firstnm}','{lastnm}','{usernm}','{password}','{email}','{phonno}','{address}','{country}','{state}','{date}')")

        session['usernm']=usernm
        session['email'] = email
        session['phonno'] = phonno

        mysql.connection.commit()
        cur.close()
        return redirect(url_for('login'))
    return render_template('registration.html')


@app.route("/about")
def about():
    return render_template('about.html')


@app.route('/remove_from_cart/<string:product_id>', methods=['POST'])
def remove_from_cart(product_id):
    # Fetch the cart from the session
    cart = session.get('cart', {})

    # Remove the product from the cart if it exists
    if product_id in cart:
        del cart[product_id]  # Delete the product from the cart

    # Update the session with the modified cart
    session['cart'] = cart

    # Redirect back to the cart page
    return redirect(url_for('cart'))




@app.route("/product")
def product():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM product")
    products = cur.fetchall()
    cur.close()
    return render_template('product.html', products=products)


@app.route('/feedback', methods=['GET', 'POST'])
def feedback():
    if 'usernm' in session:
        usernm = session['usernm']
        email = session['email']
        phonno = session['phonno']

        if request.method == 'POST':
            feedback_msg = request.form.get('message')  # using .get() to avoid KeyError

            if feedback_msg:  # Ensure the message is not empty
                cur = mysql.connection.cursor()
                cur.execute("INSERT INTO feedback(usernm, email, phonno, message) VALUES (%s, %s, %s, %s)",
                            (usernm, email, phonno, feedback_msg))
                mysql.connection.commit()
                cur.close()

                # Optionally, you could redirect to a 'thank you' page or show a success message
                return render_template('feedback.html', usernm=usernm, email=email, phonno=phonno, success=True)
            else:
                # If no message was provided, you can either show an error message or handle it in some other way
                return render_template('feedback.html', usernm=usernm, email=email, phonno=phonno,
                                       error="Message cannot be empty")

        return render_template('feedback.html', usernm=usernm, email=email, phonno=phonno)

    return render_template('login.html')


@app.route("/checkout", methods=['GET', 'POST'])
def checkout():
    if 'cart' not in session or not session['cart']:
        flash("Your cart is empty!", "warning")
        return redirect(url_for('cart'))  # Redirect if the cart is empty

    # Fetch cart items from the session
    cart_items = session['cart']
    total_price = 0
    updated_cart_items = []

    # Fetch user ID from session (if logged in)
    username = session.get('usernm')
    cur = mysql.connection.cursor()

    # ✅ Retrieve the user's ID
    cur.execute("SELECT userid FROM registration WHERE usernm = %s", (username,))
    user = cur.fetchone()
    user_id = user[0] if user else None

    if not user_id:
        flash("Error: User not found!", "danger")
        return redirect(url_for('login'))  # Redirect if user is not found

    # ✅ Check if user already has a cart in the database
    cur.execute("SELECT cart_id FROM cart WHERE userid = %s LIMIT 1", (user_id,))
    cart = cur.fetchone()

    if cart:
        cart_id = cart[0]  # Existing cart_id
    else:
        # Create a new cart entry (Use the first available product for cart creation)
        first_product_id = next(iter(cart_items))
        cur.execute("INSERT INTO cart (userid, id, quantity, total) VALUES (%s, %s, %s, %s)",
                    (user_id, first_product_id, 0, 0))  # Placeholder values
        mysql.connection.commit()
        cart_id = cur.lastrowid  # Get the newly created cart ID

    # ✅ Update the cart table with correct quantity and total price
    for product_id, quantity in cart_items.items():
        cur.execute("SELECT id, name, price FROM product WHERE id = %s", (product_id,))
        product = cur.fetchone()

        if product:
            price = product[2]
            total_price += price * quantity

            # Update the cart table with the correct quantity and total
            cur.execute("""
                UPDATE cart 
                SET quantity = %s, total = %s 
                WHERE userid = %s AND id = %s
            """, (quantity, price * quantity, user_id, product_id))

            updated_cart_items.append({
                'id': product[0],
                'name': product[1],
                'price': price,
                'quantity': quantity
            })

    # ✅ Handle checkout form submission
    if request.method == 'POST':
        full_name = request.form['full_name']
        email = request.form['email']
        address = request.form['address']
        city = request.form['city']
        zip_code = request.form['zip_code']
        country = request.form['country']
        payment_method = request.form['payment_method']

        # Generate a unique QR code for the order
        qrcode_value = ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
        qr = qrcode.make(qrcode_value)
        qr_path = os.path.join(UPLOAD_FOLDER, f"{qrcode_value}.png")
        qr.save(qr_path)

        gst = total_price * 0.28  # 28% GST Example
        net_amount = total_price + gst

        # ✅ Insert order details into `orders` table
        order_ids = []
        for product_id, quantity in cart_items.items():
            cur.execute("SELECT price FROM product WHERE id = %s", (product_id,))
            product = cur.fetchone()
            if product:
                price = product[0]
                cur.execute(
                    "INSERT INTO orders (cart_id, o_date, price, qty, total, status, qrcode, usernm) "
                    "VALUES (%s, NOW(), %s, %s, %s, %s, %s, %s)",
                    (cart_id, price, quantity, price * quantity, 'Pending', qrcode_value, username)
                )
                order_ids.append(cur.lastrowid)

        # ✅ Insert billing details if orders exist
        if order_ids:
            latest_o_id = order_ids[0]  # Use the first order ID
            cur.execute("""
                INSERT INTO bill (o_id, total, gst, net_amt, bill_date)
                VALUES (%s, %s, %s, %s, NOW())
            """, (latest_o_id, total_price, gst, net_amount))
        else:
            flash("Error: No order was created!", "danger")
            return redirect(url_for('cart'))

        mysql.connection.commit()
        cur.close()

        # ✅ Clear cart session after checkout
        session['cart'] = {}
        flash("Order placed successfully!", "success")

        return redirect(url_for('order_confirmation', cart_id=cart_id))

    cur.close()
    return render_template('checkout.html', cart=updated_cart_items, total_price=total_price)


@app.route('/bill/<cart_id>')
def bill(cart_id):
    cur = mysql.connection.cursor()

    # Fetch bill details along with customer info and product details
    cur.execute("""
        SELECT b.bill_id, b.total, b.gst, b.net_amt, b.bill_date, 
               r.firstnm AS customer_name, r.phonno AS contact_number, 
               o.cart_id, o.usernm, 
               p.name AS vehicle_model, p.price, 
               o.total AS other_charges
        FROM bill b
        JOIN orders o ON b.o_id = o.o_id
        JOIN registration r ON o.usernm = r.usernm
        JOIN cart c ON o.cart_id = c.cart_id
        JOIN product p ON c.id = p.id
        WHERE o.cart_id = %s
    """, (cart_id,))

    bill_data = cur.fetchone()

    # Fetch product details for the invoice table
    cur.execute("""
        SELECT p.name, o.qty, p.price, 
               (p.price * o.qty) AS amount,
               (p.price * o.qty * 0.28) AS gst,
               (p.price * o.qty * 0.72) AS rate
        FROM orders o
        JOIN product p ON o.cart_id = %s AND o.o_id = p.id
    """, (cart_id,))

    products = cur.fetchall()
    cur.close()

    if bill_data:
        (bill_id, total, gst, net_amount, bill_date, customer_name,
         contact_number, cart_id, usernm, vehicle_model,
         price, other_charges) = bill_data

        return render_template(
            'bill.html',
            bill_id=bill_id,
            total=total,
            gst=gst,
            net_amount=net_amount,
            bill_date=bill_date,
            customer_name=customer_name,
            contact_number=contact_number,
            vehicle_model=vehicle_model,
            products=products  # Pass product details
        )
    else:
        return "Bill not found for this order.", 404


@app.route('/order_confirmation/<cart_id>')
def order_confirmation(cart_id):
    cur = mysql.connection.cursor()

    # Get the QR code
    cur.execute("SELECT qrcode FROM orders WHERE cart_id = %s LIMIT 1", (cart_id,))
    order = cur.fetchone()
    qrcode_value = order[0] if order else None

    cur.execute("""
        SELECT bill_id, total, gst, net_amt, bill_date 
        FROM bill 
        WHERE o_id = (SELECT o_id FROM orders WHERE cart_id = %s LIMIT 1)
    """, (cart_id,))
    bill = cur.fetchone()

    if bill:
        bill_id, total, gst, net_amount, bill_date = bill
    else:
        bill_id = total = gst = net_amount = bill_date = None

    cur.close()

    return render_template(
        'order_confirmation.html',
        qrcode=qrcode_value,
        bill_id=bill_id,
        total=total,
        gst=gst,
        net_amount=net_amount,
        bill_date=bill_date,
        cart_id=cart_id  # Ensure this is passed!
    )

@app.route("/admin_login", methods=['GET','POST'])
def admin_login():
    if request.method == 'POST':
        adminnm = request.form['adminnm']
        pwd = request.form['password']
        cur = mysql.connection.cursor()
        cur.execute(f"select adminnm,password from admin_login where adminnm = '{adminnm}'")
        user1 = cur.fetchone()
        cur.close()
        if user1 and pwd == user1[1]:
            session['adminnm'] = user1[0]
            return redirect(url_for('dashboard'))
        else:
            return render_template('admin_login.html', error='invalid adminnm and password')


    return render_template('admin_login.html')


@app.route("/dashboard")
def dashboard():
    if 'adminnm' in session:
        return render_template('dashboard.html',adminnm=session['adminnm'])
    else:
        return render_template('dashboard.html')

@app.route("/contact")
def contact():
    return render_template('contact.html')




@app.route('/pro')
def pro():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM product")
    data = cur.fetchall()
    cur.close()
    return render_template('pro.html', students=data)


# Route to add a new product
@app.route("/add", methods=['POST'])
def add():
    if request.method == 'POST':
        pnm = request.form['pnm']
        price = request.form['price']
        description = request.form['description']
        stock = request.form['stock']

        # Handle file upload
        image = request.files.get('image')  # Using 'get' to prevent KeyError
        image_filename = None  # Initialize the variable
        filename = None  # Initialize filename to avoid unassigned variable warning

        if image:
            filename = image.filename
            image_filename = os.path.join(UPLOAD_FOLDER, filename)  # Save in 'static/uploads' folder
            image.save(image_filename)  # Save the image in the uploads folder

        # Insert into database with the relative path to the image
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO product (name, price, description, image, stock) VALUES (%s, %s, %s, %s, %s)",
                    (pnm, price, description, f"uploads/{filename}" if filename else None,
                     stock))  # Save relative path if filename exists
        mysql.connection.commit()
        flash("Product added successfully!")
        cur.close()

        return redirect(url_for('pro'))


# Route to update product details
@app.route('/update', methods=['POST'])
def update():
    if request.method == 'POST':
        product_id = request.form['id']
        pnm = request.form['pnm']
        price = request.form['price']
        description = request.form['description']
        stock = request.form['stock']

        # Handle the image upload
        image = request.files.get('image')  # Using 'get' to prevent KeyError
        image_filename = None  # Initialize the variable
        filename = None  # Initialize filename to avoid unassigned variable warning

        if image:
            filename = image.filename
            image_filename = os.path.join(UPLOAD_FOLDER, filename)  # Save in 'static/uploads' folder
            image.save(image_filename)  # Save the image in the uploads folder

        # Update the product in the database
        cur = mysql.connection.cursor()

        # Update the product entry with new data (image is optional)
        cur.execute("""
            UPDATE product
            SET name=%s, price=%s, description=%s, image=%s, stock=%s
            WHERE id=%s
        """, (
            pnm,
            price,
            description,
            f"uploads/{filename}" if filename else None,  # Only update image if a new one is uploaded
            stock,
            product_id
        ))

        mysql.connection.commit()
        flash("Product updated successfully!", "success")
        cur.close()

        return redirect(url_for('pro'))  # Redirect to the product list page

# Route to delete product
@app.route('/delete/<string:id>', methods=['GET'])
def delete(id):
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM product WHERE id=%s", (id,))
    mysql.connection.commit()
    flash("Product deleted successfully!")
    cur.close()
    return redirect(url_for('pro'))


@app.route("/logout")
def logout():
    session.clear()  # Remove the admin session variable
    return redirect(url_for('index'))  # Redirect to the login page


@app.route("/manage_order")
def manage_order():
    if 'adminnm' in session:
        # Fetch all the orders from the database, including the status
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM orders ORDER BY o_date DESC")  # Fetch orders, latest first
        # cur.execute("SELECT o.o_id, o.cart_id, o.o_date, o.qty, o.total, o.status, o.usernm FROM orders o ORDER BY o.o_date DESC")

        orders = cur.fetchall()
        cur.close()

        return render_template('manage_order.html', orders=orders)
    else:
        return redirect(url_for('admin_login'))

@app.route('/update_order_status/<int:o_id>', methods=['POST'])
def update_order_status(o_id):
    # Get the new status from the form
    new_status = request.form['status']

    # Update the order status in the database
    cur = mysql.connection.cursor()
    cur.execute("UPDATE orders SET status = %s WHERE o_id = %s", (new_status, o_id))
    mysql.connection.commit()
    cur.close()

    # Flash a success message and redirect back to the manage orders page
    flash("Order status updated successfully!", "success")
    return redirect(url_for('manage_order'))

@app.route("/order")
def order():
    if 'usernm' not in session:
        return redirect(url_for('login'))  # Redirect to login if not logged in

    usernm = session['usernm']  # Get logged-in user ID

    # Fetch only the orders belonging to the logged-in user
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT o.o_id, o.cart_id, o.o_date, o.qty, o.total, o.status, o.usernm
        FROM orders o
        WHERE o.usernm = %s
        ORDER BY o.o_date DESC
    """, (usernm,))

    orders = cur.fetchall()
    cur.close()

    return render_template('order.html', orders=orders)



@app.route('/manage_customer')
def manage_customer():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM registration")
    registration = cur.fetchall()
    cur.close()
    return render_template('manage_customer.html', registration=registration)






@app.route("/view_feedback")
def view_feedback():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM feedback")
    feedback = cur.fetchall()
    cur.close()
    return render_template('view_feedback.html', feedback=feedback)


@app.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        # Fetching the form data
        email = request.form['email']
        old_password = request.form['old_password']
        new_password = request.form['new_password']

        # Check if the email exists in the database
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM registration WHERE email = %s", (email,))
        user = cur.fetchone()

        if user:
            # Verify the old password
            if old_password == user[1]:  # Assuming 'user[1]' is the password column
                # Update the password in the database
                cur.execute("UPDATE registration SET password = %s WHERE email = %s", (new_password, email))
                mysql.connection.commit()
                flash("Password updated successfully!", "success")
                return redirect(url_for('login'))
            else:
                flash("Old password is incorrect.", "error")
        else:
            flash("No user found with that email.", "error")

    return render_template('forgot_password.html')


@app.route('/add_service', methods=['POST'])
def add_service():
    # Get form data
    service_type = request.form.get("service_id")  # This is the service type, e.g., washing, oil_changes
    user_id = session.get("usernm")  # Get user_id from the session

    # Randomly generate a Vehicle ID
    random_number = ''.join(random.choices(string.digits, k=4))  # 4-digit random number
    vehicle_id = f"GJ14{random_number}"

    # Fetch service date from the registration table
    try:
        cur = mysql.connection.cursor()
        cur.execute("SELECT date FROM registration WHERE usernm = %s", (user_id,))
        result = cur.fetchone()
        cur.close()

        if result:
            service_date = result[0]  # Get the service date from the registration table
        else:
            service_date = datetime.datetime.now().strftime('%Y-%m-%d')  # Default to today's date

    except Exception as e:
        return f"An error occurred while fetching the service date: {str(e)}", 500

    # Generate a unique service ID
    service_unique_id = f"SV{random.randint(1000, 9999)}"

    # Validate that user_id is not empty
    if not user_id:
        return "User is not logged in or userid is missing.", 400

    # Debugging: Print vehicle_id and service_date to see if they're being captured
    print(f"Generated Vehicle ID: {vehicle_id}")
    print(f"Fetched Service Date: {service_date}")

    # Insert into the database
    try:
        cur = mysql.connection.cursor()
        query = """
            INSERT INTO services (service_id, usernm, vehicle_id, service_type, date)
            VALUES (%s, %s, %s, %s, %s)
        """
        cur.execute(query, (service_unique_id, user_id, vehicle_id, service_type, service_date))
        mysql.connection.commit()
        cur.close()

        # Redirect to view_service to see the updated list
        return redirect(url_for('service'))

    except Exception as e:
        return f"An error occurred while adding the service: {str(e)}", 500



@app.route('/view_service')
def view_service():
    try:
        # Fetch all services for the admin view
        cur = mysql.connection.cursor()
        cur.execute("""
            SELECT s.service_id, s.usernm, s.vehicle_id, s.service_type, s.date, u.usernm 
            FROM services s
            JOIN registration u ON s.usernm = u.usernm
            ORDER BY s.date DESC
        """)
        services = cur.fetchall()
        cur.close()
        return render_template('view_service.html', services=services)
    except Exception as e:
        return f"An error occurred while fetching the services: {str(e)}", 500

@app.route('/delete_service/<string:service_id>', methods=['GET', 'POST'])
def delete_service(service_id):
    try:
        # Delete the service from the database
        cur = mysql.connection.cursor()
        cur.execute("DELETE FROM services WHERE service_id = %s", (service_id,))
        mysql.connection.commit()
        cur.close()

        flash("Service deleted successfully!", "success")
        return redirect(url_for('view_service'))  # Redirect to the admin view

    except Exception as e:
        return f"An error occurred while deleting the service: {str(e)}", 500


@app.route('/service')
def service():
    return render_template('service.html')


if __name__=='__main__':
    app.run(debug=True)