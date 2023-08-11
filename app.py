import random as rand
from datetime import datetime, date

from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3 as sql
import hashlib

app = Flask(__name__)
SESSION_TYPE = 'redis'
app.config.from_object(__name__)
app.config.update(SECRET_KEY='\xd8\xe3+\x14\x0e\xa93\x80 \xae\xdd\x9d\xb0{\xae\xd8',
                  ENV='development')

host = 'http://127.0.0.1:5000/'

hash_func = hashlib.sha256


@app.route('/', methods=['POST', 'GET'])
def index():
    if request.method == 'POST':
        # Get the username and password from the form
        username = request.form['email']
        password = request.form['password']
        user_type = request.form['dropdown']

        # Connect to db and retrieve the hashed password for the given username
        conn = sql.connect('data.db')
        result = conn.execute('SELECT password FROM users WHERE email = ?', (username,))
        row = result.fetchone()

        # If the username doesn't exist or passwords don't match, show an error message
        if row is None or hash_func(password.encode('utf-8')).hexdigest() != row[0]:
            return render_template('index.html', error='Invalid email or password')

        # Check user type from dropdown
        session['user_email'] = username
        if user_type == 'seller':
            result_seller = conn.execute('SELECT * FROM sellers WHERE email = ?', (username,))
            row_seller = result_seller.fetchone()
            result_local_vendor = conn.execute('SELECT * FROM local_vendors WHERE email = ?', (username,))
            row_local_vendor = result_local_vendor.fetchone()
            if row_seller is None and row_local_vendor is None:
                return render_template('index.html', error='Invalid user permissions')
            result_seller_auctions = conn.execute('SELECT * FROM auction_listings WHERE seller_email = ?', (username,))
            seller_auctions = result_seller_auctions.fetchall()
            active_auctions = []
            inactive_auctions = []
            complete_auctions = []
            # Collect relevant info of seller's current auctions and create links to edit each auction
            for auction in seller_auctions:
                auction_dict = {'listing_id': auction[1], 'category': auction[2], 'auction_title': auction[3],
                                'product_name': auction[4], 'product_desc': auction[5], 'quantity': auction[6],
                                'reserve_price': auction[7], 'max_bids': auction[8]}
                result_current_bids = conn.execute('SELECT COUNT(*) FROM bids WHERE listing_id = ?', (auction[1],))
                current_bids = result_current_bids.fetchone()
                auction_dict['current_bids'] = current_bids[0]
                result_max_bid = conn.execute('SELECT max(bid_price) FROM bids WHERE listing_id = ?', (auction[1],))
                max_bid = result_max_bid.fetchone()
                if max_bid:
                    auction_dict['highest_bid'] = max_bid[0]
                if auction[9] == 1:
                    link = f"/edit_auction/{auction[1]}"
                    auction_dict['link'] = link
                    auction_dict['status'] = 'Ongoing'
                    active_auctions.append(auction_dict)
                elif auction[9] == 2:
                    auction_dict['link'] = ''
                    auction_dict['status'] = 'Payment received'
                    complete_auctions.append(auction_dict)
                else:
                    auction_dict['link'] = f"/edit_auction/{auction[1]}"
                    auction_dict['status'] = 'Inactive or awaiting payment'
                    inactive_auctions.append(auction_dict)
            conn.close()
            return render_template('seller.html', active_auctions=active_auctions, inactive_auctions=inactive_auctions,
                                   complete_auctions=complete_auctions)

        if user_type == 'helpdesk':
            result_helpdesk = conn.execute('SELECT * FROM helpdesk WHERE email = ?', (username,))
            row_helpdesk = result_helpdesk.fetchone()
            if row_helpdesk is None:
                return render_template('index.html', error='Invalid user permissions')
            result_assigned_requests = conn.execute('SELECT * FROM requests WHERE helpdesk_staff_email = ?',
                                                    (username,))
            result_unassigned_requests = conn.execute('SELECT * FROM requests WHERE helpdesk_staff_email = ?',
                                                      ('helpdeskteam@lsu.edu',))
            assigned_requests = result_assigned_requests.fetchall()
            unassigned_requests = result_unassigned_requests.fetchall()
            conn.close()
            return render_template('helpdesk.html', assigned_requests=assigned_requests,
                                   unassigned_requests=unassigned_requests)

        if user_type == 'bidder':
            result_bidder = conn.execute('SELECT * FROM bidders WHERE email = ?', (username,))
            row_bidder = result_bidder.fetchone()
            if row_bidder is None:
                return render_template('index.html', error='Invalid user permissions')
            # Fetch bidder information for welcome page
            address_cursor = conn.cursor()
            address_cursor.execute('SELECT zipcode, street_name FROM address WHERE address_id = ?', (row_bidder[5],))
            address = address_cursor.fetchone()
            address_cursor.close()
            result_zipcode = conn.execute('SELECT city, state FROM zipcode_info WHERE zipcode = ?', (address[0],))
            zipcode_info = result_zipcode.fetchone()
            result_cc = conn.execute('SELECT credit_card_num FROM credit_cards WHERE owner_email = ?', (username,))
            cc = result_cc.fetchone()
            cc = cc[0][-4:]
            conn.close()
            return render_template('bidder.html', email=username, user=row_bidder, address=address,
                                   zipcode_info=zipcode_info, cc=cc)

        conn.close()
    return render_template('index.html')


# Used on all back buttons. Checks user permissions and fetches relevant info to user and displays homepage again
# This function is very similar to index in how it works
@app.route('/check_permissions_back')
def check_permissions_back():
    conn = sql.connect('data.db')
    result_bidder = conn.execute('SELECT * FROM bidders WHERE email = ?', (session['user_email'],))
    row_bidder = result_bidder.fetchone()
    result_seller = conn.execute('SELECT * FROM sellers WHERE email = ?', (session['user_email'],))
    row_seller = result_seller.fetchone()
    result_helpdesk = conn.execute('SELECT * FROM helpdesk WHERE email = ?', (session['user_email'],))
    row_helpdesk = result_helpdesk.fetchone()
    result_local_vendor = conn.execute('SELECT * FROM local_vendors WHERE email = ?', (session['user_email'],))
    row_local_vendor = result_local_vendor.fetchone()
    if row_helpdesk:
        result_assigned_requests = conn.execute('SELECT * FROM requests WHERE helpdesk_staff_email = ?',
                                                (session['user_email'],))
        result_unassigned_requests = conn.execute('SELECT * FROM requests WHERE helpdesk_staff_email = ?',
                                                  ('helpdeskteam@lsu.edu',))
        assigned_requests = result_assigned_requests.fetchall()
        unassigned_requests = result_unassigned_requests.fetchall()
        conn.close()
        return render_template('helpdesk.html', assigned_requests=assigned_requests,
                               unassigned_requests=unassigned_requests)
    if row_bidder:
        # Fetch bidder information for welcome page
        address_cursor = conn.cursor()
        address_cursor.execute('SELECT zipcode, street_name FROM address WHERE address_id = ?', (row_bidder[5],))
        address = address_cursor.fetchone()
        address_cursor.close()
        result_zipcode = conn.execute('SELECT city, state FROM zipcode_info WHERE zipcode = ?', (address[0],))
        zipcode_info = result_zipcode.fetchone()
        result_cc = conn.execute('SELECT credit_card_num FROM credit_cards WHERE owner_email = ?',
                                 (session['user_email'],))
        cc = result_cc.fetchone()
        cc = cc[0][-4:]
        conn.close()
        return render_template('bidder.html', email=session['user_email'], user=row_bidder, address=address,
                               zipcode_info=zipcode_info, cc=cc)
    if row_seller or row_local_vendor:
        result_seller_auctions = conn.execute('SELECT * FROM auction_listings WHERE seller_email = ?',
                                              (session['user_email'],))
        seller_auctions = result_seller_auctions.fetchall()
        active_auctions = []
        inactive_auctions = []
        complete_auctions = []
        # Collect relevant info of seller's current auctions and create links to edit each auction
        for auction in seller_auctions:
            auction_dict = {'listing_id': auction[1], 'category': auction[2], 'auction_title': auction[3],
                            'product_name': auction[4], 'product_desc': auction[5], 'quantity': auction[6],
                            'reserve_price': auction[7], 'max_bids': auction[8]}
            result_current_bids = conn.execute('SELECT COUNT(*) FROM bids WHERE listing_id = ?', (auction[1],))
            current_bids = result_current_bids.fetchone()
            auction_dict['current_bids'] = current_bids[0]
            result_max_bid = conn.execute('SELECT max(bid_price) FROM bids WHERE listing_id = ?', (auction[1],))
            max_bid = result_max_bid.fetchone()
            if max_bid:
                auction_dict['highest_bid'] = max_bid[0]
            if auction[9] == 1:
                link = f"/edit_auction/{auction[1]}"
                auction_dict['link'] = link
                auction_dict['status'] = 'Ongoing'
                active_auctions.append(auction_dict)
            elif auction[9] == 2:
                auction_dict['link'] = ''
                auction_dict['status'] = 'Payment received'
                complete_auctions.append(auction_dict)
            else:
                auction_dict['link'] = f"/edit_auction/{auction[1]}"
                auction_dict['status'] = 'Inactive or awaiting payment'
                inactive_auctions.append(auction_dict)
        conn.close()
        return render_template('seller.html', active_auctions=active_auctions,
                               inactive_auctions=inactive_auctions,
                               complete_auctions=complete_auctions)


@app.route('/bidder', methods=['POST', 'GET'])
def bidder():
    return render_template('bidder.html')


@app.route('/seller', methods=['POST', 'GET'])
def seller():
    return render_template('seller.html')


@app.route('/helpdesk', methods=['POST', 'GET'])
def helpdesk():
    return render_template('helpdesk.html')


# Fills dropdown with root categories
@app.route('/categories', methods=['POST', 'GET'])
def categories():
    conn = sql.connect('data.db')
    result_root = conn.execute('SELECT category_name FROM categories WHERE parent_category = ?', ('Root',))
    root_categories = result_root.fetchall()
    conn.close()
    return render_template('categories.html', categories=root_categories)


# Dynamically updates category dropdown with children of chosen category
@app.route('/update_subcategories', methods=['POST'])
def update_subcategories():
    conn = sql.connect('data.db')
    # Get the selected main category from the form data
    root_category = request.form['root_category']
    # Populate list of dictionaries for displaying products
    root_listings_result = conn.execute('SELECT * FROM auction_listings WHERE category = ?  AND status=?',
                                        (root_category, 1,))
    root_listings = root_listings_result.fetchall()
    rows = []
    for row in root_listings:
        row_dict = {'auction_title': row[3], 'product_name': row[4]}
        link = f"/details/{row[1]}"
        row_dict['link'] = link
        rows.append(row_dict)
    # Query the database for the subcategories associated with the main category
    resultSubcategories = conn.execute('SELECT category_name FROM categories WHERE parent_category = ?',
                                       (root_category,))
    subcategories = resultSubcategories.fetchall()
    conn.close()
    return render_template('categories.html', categories=subcategories, rows=rows)


# Clears the dropdown to root categories
@app.route('/clear_dropdown', methods=['POST'])
def clear_dropdown():
    conn = sql.connect('data.db')
    result_root = conn.execute('SELECT category_name FROM categories WHERE parent_category = ?', ('Root',))
    root_categories = result_root.fetchall()
    conn.close()
    return render_template('categories.html', categories=root_categories)


# Fetches all relevant listing details and allows for bidding
@app.route('/details/<id>', methods=['POST', 'GET'])
def details(id):
    error = None
    conn = sql.connect('data.db')
    result_product = conn.execute('SELECT * FROM auction_listings WHERE listing_id = ?', (id,))
    product_info = result_product.fetchone()
    result_bid_count = conn.execute('SELECT COUNT(*) FROM bids WHERE listing_id = ?', (id,))
    bid_count = result_bid_count.fetchone()
    remaining_bids = product_info[8] - bid_count[0]
    result_max_bid = conn.execute('SELECT MAX(bid_price) FROM bids WHERE listing_id = ?', (id,))
    max_bid = result_max_bid.fetchone()
    result_seller_rating = conn.execute('SELECT avg(rating) FROM ratings WHERE seller_email = ?',
                                        (product_info[0],))
    seller_rating = result_seller_rating.fetchone()
    seller_rating = round(seller_rating[0], 2)
    conn.close()

    # Check if bid amount is valid
    if request.method == 'POST':
        # Check to make sure current user doesn't bid twice at once
        conn = sql.connect('data.db')
        result_double_bid = conn.execute('SELECT bidder_email FROM bids WHERE listing_id = ? ORDER BY bid_price DESC',
                                         (id,))
        double_bid = result_double_bid.fetchone()
        conn.close()
        if remaining_bids == 0:
            error = "Auction has ended."
            return render_template('product_details.html', product_info=product_info, remaining_bids=remaining_bids,
                                   max_bid=max_bid, error=error, rating=seller_rating[0])
        else:
            if double_bid is None or double_bid[0] != session['user_email']:
                result = submit_bid(product_info[0], id, session['user_email'], request.form['bid'], max_bid[0],
                                    remaining_bids)
            else:
                error = "Cannot bid twice until another user has bid."
                return render_template('product_details.html', product_info=product_info, remaining_bids=remaining_bids,
                                       max_bid=max_bid, error=error, rating=seller_rating)
        if result:
            error = None
            conn = sql.connect('data.db')
            new_result_product = conn.execute('SELECT * FROM auction_listings WHERE listing_id = ?', (id,))
            new_product_info = new_result_product.fetchone()
            new_result_bid_count = conn.execute('SELECT COUNT(*) FROM bids WHERE listing_id = ?', (id,))
            new_bid_count = new_result_bid_count.fetchone()
            new_remaining_bids = new_product_info[8] - new_bid_count[0]
            new_result_max_bid = conn.execute('SELECT MAX(bid_price) FROM bids WHERE listing_id = ?', (id,))
            new_max_bid = new_result_max_bid.fetchone()
            conn.close()
            return render_template('product_details.html', product_info=new_product_info,
                                   remaining_bids=new_remaining_bids,
                                   max_bid=new_max_bid, error=error, rating=seller_rating)
        else:
            error = "Invalid bid. Bids must be at least $1 over current bid."
            conn.close()
            return render_template('product_details.html', product_info=product_info, remaining_bids=remaining_bids,
                                   max_bid=max_bid, error=error, rating=seller_rating)
    return render_template('product_details.html', product_info=product_info, remaining_bids=remaining_bids,
                           max_bid=max_bid, error=error, rating=seller_rating)


# Submits bid if it is valid
def submit_bid(seller_email, listing_id, bidder_email, bid_amount, max_bid, remaining_bids_post):
    conn = sql.connect('data.db')
    if remaining_bids_post == 0:
        return False
    # Check if bid is more than $1 over last bid
    if max_bid is None or int(bid_amount) >= (int(max_bid) + 1):
        # Generate unique bid id
        new_id = []
        while len(new_id) < 1:
            bid_id = rand.randint(0, 9999)
            cursor = conn.cursor()
            cursor.execute('SELECT bid_id FROM bids WHERE bid_id = ?', (bid_id,))
            existing_id = cursor.fetchone()
            cursor.close()
            if not existing_id:
                new_id.append(bid_id)

        # Insert bid into table
        conn.execute('INSERT INTO bids VALUES (?, ?, ?, ?, ?)',
                     (new_id[0], seller_email, listing_id, bidder_email, bid_amount,))
        conn.commit()
        conn.close()

        # Check to see if this new bid ends the auction
        auction_check = sql.connect('data.db')
        result_product = auction_check.execute('SELECT * FROM auction_listings WHERE listing_id = ?', (listing_id,))
        product_info = result_product.fetchone()
        result_bid_count = auction_check.execute('SELECT COUNT(*) FROM bids WHERE listing_id = ?', (listing_id,))
        bid_count = result_bid_count.fetchone()
        remaining_bids = product_info[8] - bid_count[0]
        if remaining_bids == 0:
            auction_check.execute('UPDATE auction_listings SET status=0 WHERE listing_id = ?', (listing_id,))
            auction_check.commit()
            auction_check.close()
        return True
    else:
        return False


# Fetches relevant information for bidding notifications
@app.route('/notifications_bidder')
def notifications_bidder():
    conn = sql.connect('data.db')
    result_user_bids = conn.execute('SELECT * FROM bids WHERE bidder_email = ?', (session['user_email'],))
    user_bids = result_user_bids.fetchall()
    rows = []
    # Add all outstanding bids
    for bid in user_bids:
        # Check if auction is ongoing
        result_is_auction_closed = conn.execute('SELECT * FROM auction_listings WHERE listing_id = ?', (bid[2],))
        is_auction_closed = result_is_auction_closed.fetchone()
        result_is_max_bidder = conn.execute(
            'SELECT bidder_email FROM bids WHERE listing_id = ? ORDER BY bid_price DESC',
            (bid[2],))
        is_max_bidder = result_is_max_bidder.fetchone()
        result_user_bid_info = conn.execute('SELECT * FROM auction_listings WHERE listing_id = ?', (bid[2],))
        user_bid_info = result_user_bid_info.fetchone()
        row_dict = {'auction_title': user_bid_info[3], 'listing_id': user_bid_info[1], 'product_name': user_bid_info[4],
                    'price': bid[4]}
        if is_auction_closed[9] == 1:
            row_dict['status'] = "Ongoing"
            row_dict['payment'] = ''
            row_dict['payment_text'] = ""
            rows.append(row_dict)
        # Don't display sold auctions
        elif is_auction_closed[9] == 2:
            continue
        # if auction is closed, check if the user won or lost
        elif is_max_bidder[0] == session['user_email']:
            # Don't display if winning bid is less than reserve price
            if bid[4] < user_bid_info[6]:
                continue
            row_dict['status'] = "Won"
            link = f"/payment/{user_bid_info[1]}"
            row_dict['payment'] = link
            row_dict['payment_text'] = "Pay"
            rows.append(row_dict)
        else:
            row_dict['payment'] = ''
            row_dict['status'] = "Lost"
            row_dict['payment_text'] = ""
            rows.append(row_dict)

    # Add all completed transactions by bidder
    result_is_purchaser = conn.execute('SELECT * FROM transactions WHERE buyer_email = ?',
                                       (session['user_email'],))
    is_purchaser = result_is_purchaser.fetchall()
    for transaction in is_purchaser:
        result_user_bid_info = conn.execute('SELECT * FROM auction_listings WHERE listing_id = ?', (transaction[2],))
        user_bid_info = result_user_bid_info.fetchone()
        row_dict = {'auction_title': user_bid_info[3], 'listing_id': user_bid_info[1], 'product_name': user_bid_info[4],
                    'price': transaction[5], 'status': 'Purchased', 'payment': '', 'payment_text': ''}
        rows.append(row_dict)
    conn.close()
    return render_template('notifications_bidder.html', user_bids=rows)


# Confirms that the bidder wants to complete auction
@app.route('/payment/<listing_id>', methods=['POST', 'GET'])
def payment(listing_id):
    conn = sql.connect('data.db')
    # Check to make sure it's the right user accessing the page
    result_correct_bidder = conn.execute(
        'SELECT bidder_email, bid_price FROM bids WHERE listing_id = ? ORDER BY bid_price DESC', (listing_id,))
    correct_bidder = result_correct_bidder.fetchone()
    if correct_bidder[0] != session['user_email']:
        error = "Invalid user permissions"
        conn.close()
        return render_template('payment.html', listing_id=listing_id, error=error)
    # Get information for display in webpage
    result_credit_card = conn.execute('SELECT credit_card_num FROM credit_cards WHERE owner_email = ?',
                                      (session['user_email'],))
    credit_card = result_credit_card.fetchone()
    credit_card = credit_card[0][-4:]
    result_listing_info = conn.execute('SELECT * FROM auction_listings WHERE listing_id = ?', (listing_id,))
    listing_info = result_listing_info.fetchone()
    bid_price = correct_bidder[1]
    # Create payment link for button
    link = f"/complete_payment/{listing_id}"
    conn.close()
    return render_template('payment.html', listing_id=listing_id, credit_card=credit_card, listing_info=listing_info,
                           bid_price=bid_price, link=link)


# Completes payment for an auction and adds to transactions table
@app.route('/complete_payment/<listing_id>', methods=['POST', 'GET'])
def complete_payment(listing_id):
    conn = sql.connect('data.db')
    # Update listing to sold
    conn.execute('UPDATE auction_listings SET status=2 WHERE listing_id = ?', (listing_id,))
    # Fetch listing information
    result_bid_price = conn.execute('SELECT bid_price FROM bids WHERE listing_id = ? ORDER BY bid_price DESC',
                                    (listing_id,))
    bid_price = result_bid_price.fetchone()
    bid_price = bid_price[0]
    result_seller_email = conn.execute('SELECT seller_email FROM auction_listings WHERE listing_id = ?', (listing_id,))
    seller_email = result_seller_email.fetchone()
    seller_email = seller_email[0]
    current_day = date.today()
    formatted_date = current_day.strftime("%m/%d/%Y")
    formatted_date = str(formatted_date)
    # Insert information into transactions table
    conn.execute(
        'INSERT INTO transactions (seller_email, listing_id, buyer_email, date, payment) VALUES (?, ?, ?, ?, ?)',
        (seller_email, listing_id, session['user_email'], formatted_date, bid_price))
    conn.commit()
    conn.close()
    return render_template('complete_payment.html', listing_id=listing_id)


# Edits a seller's auction
@app.route('/edit_auction/<listing_id>', methods=['POST', 'GET'])
def edit_auction(listing_id):
    # Get auction information
    conn = sql.connect('data.db')
    result_auction = conn.execute('SELECT * FROM auction_listings WHERE listing_id = ?', (listing_id,))
    auction = result_auction.fetchone()
    if auction[0] != session['user_email']:
        error = "Invalid user permissions"
        conn.close()
        return render_template('edit_auction.html', error=error)
    auction_dict = {'listing_id': auction[1], 'category': auction[2], 'auction_title': auction[3],
                    'product_name': auction[4], 'product_desc': auction[5], 'quantity': auction[6],
                    'reserve_price': auction[7], 'max_bids': auction[8]}
    result_current_bids = conn.execute('SELECT COUNT(*) FROM bids WHERE listing_id = ?', (auction[1],))
    current_bids = result_current_bids.fetchone()
    auction_dict['current_bids'] = current_bids[0]
    result_max_bid = conn.execute('SELECT max(bid_price) FROM bids WHERE listing_id = ?', (auction[1],))
    max_bid = result_max_bid.fetchone()
    auction_dict['highest_bid'] = max_bid[0]
    conn.close()
    # Edit auction
    if request.method == 'POST':
        auction_title = request.form['auction_title']
        product_name = request.form['product_name']
        product_desc = request.form['product_desc']
        reserve_price = request.form['reserve_price']
        conn = sql.connect('data.db')
        conn.execute(
            'UPDATE auction_listings SET auction_title = ?, product_name = ?, product_description = ?, reserve_price = ? WHERE listing_id = ?',
            (auction_title, product_name, product_desc, reserve_price, listing_id))
        # Update page with new info
        auction_dict['auction_title'] = auction_title
        auction_dict['product_name'] = product_name
        auction_dict['product_desc'] = product_desc
        conn.commit()
        conn.close()
        return render_template('edit_auction.html', auction=auction_dict)
    return render_template('edit_auction.html', auction=auction_dict)


# Deletes a seller's auction
@app.route('/delete_auction/<listing_id>', methods=['POST', 'GET'])
def delete_auction(listing_id):
    if request.method == 'POST':
        removal_reason = request.form['removal_reason']
        conn = sql.connect('data.db')
        # Create removed_listings table
        conn.execute(
            'CREATE TABLE IF NOT EXISTS removed_listings (listing_id INT PRIMARY KEY, seller_email TEXT, removal_reason TEXT, remaining_bids TEXT, auction_title TEXT, category TEXT)')
        result_listing_info = conn.execute('SELECT * FROM auction_listings WHERE listing_id = ?', (listing_id,))
        listing_info = result_listing_info.fetchone()
        result_bid_count = conn.execute('SELECT COUNT(*) FROM bids WHERE listing_id = ?', (listing_id,))
        bid_count = result_bid_count.fetchone()
        # Calculate remaining bids
        if bid_count:
            remaining_bids = listing_info[8] - bid_count[0]
        else:
            remaining_bids = listing_info[8]

        # Insert listing information into removed_listings
        conn.execute('INSERT INTO removed_listings VALUES (?, ?, ?, ?, ?, ?)',
                     (listing_id, session['user_email'], removal_reason, remaining_bids, listing_info[3],
                      listing_info[2],))
        conn.execute('DELETE FROM auction_listings WHERE listing_id = ?', (listing_id,))
        conn.commit()
        conn.close()
    return render_template('delete_auction.html')


# Takes the rating from the bidder and inserts
@app.route('/rate_seller/<listing_id>', methods=['POST'])
def rate_seller(listing_id):
    conn = sql.connect('data.db')
    number_rating = request.form['number_rating']
    rating_desc = request.form['rating_desc']
    result_seller_email = conn.execute('SELECT seller_email FROM auction_listings WHERE listing_id = ?', (listing_id,))
    seller_email = result_seller_email.fetchone()
    current_day = date.today()
    formatted_date = current_day.strftime("%m/%d/%Y")
    formatted_date = str(formatted_date)
    conn.execute('INSERT INTO ratings VALUES (?, ?, ?, ?, ?)',
                 (session['user_email'], seller_email[0], formatted_date, number_rating, rating_desc))
    conn.commit()
    conn.close()
    return render_template('/post_rating.html')


# Fetches category information and then redirects to create_listing
@app.route('/create_auction')
def create_auction():
    conn = sql.connect('data.db')
    result_categories = conn.execute('SELECT DISTINCT category_name FROM categories')
    categories = result_categories.fetchall()
    conn.close()
    return render_template('/create_listing.html', categories=categories)


# Creates listing for seller
@app.route('/create_listing', methods=['POST', 'GET'])
def create_listing():
    if request.method == 'POST':
        new_id = []
        conn = sql.connect('data.db')
        # Random listing id that is new
        while len(new_id) < 1:
            listing_id = rand.randint(0, 9999)
            cursor = conn.cursor()
            cursor.execute('SELECT listing_id FROM auction_listings WHERE listing_id = ?', (listing_id,))
            existing_id = cursor.fetchone()
            cursor.close()
            if not existing_id:
                new_id.append(listing_id)
        category = request.form['category']
        auction_title = request.form['auction_title']
        product_name = request.form['product_name']
        product_desc = request.form['product_desc']
        quantity = request.form['quantity']
        reserve_price = '$' + str(request.form['reserve_price'])
        max_bids = request.form['max_bids']
        status = 1
        conn.execute('INSERT INTO auction_listings VALUES (?,?,?,?,?,?,?,?,?,?)',
                     (session['user_email'], new_id[0], category, auction_title, product_name, product_desc, quantity,
                      reserve_price, max_bids, status))
        conn.commit()
        conn.close()
    return render_template('/complete_new_listing.html')


if __name__ == '__main__':
    app.run()
