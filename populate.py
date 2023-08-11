import csv
import sqlite3 as sql
import hashlib

hash_func = hashlib.sha256

# Open all data and split by row
with open('users.csv', newline='') as users:
    csv_reader = csv.reader(users)
    next(csv_reader)
    rowsUsers = list(csv_reader)

with open('helpdesk.csv', newline='') as helpdesk:
    csv_reader = csv.reader(helpdesk)
    next(csv_reader)
    rowsHelpdesk = list(csv_reader)

with open('requests.csv', newline='') as requests:
    csv_reader = csv.reader(requests)
    next(csv_reader)
    rowsRequests = list(csv_reader)

with open('bidders.csv', newline='') as bidders:
    csv_reader = csv.reader(bidders)
    next(csv_reader)
    rowsBidders= list(csv_reader)

with open('credit_cards.csv', newline='') as credit_cards:
    csv_reader = csv.reader(credit_cards)
    next(csv_reader)
    rowsCC = list(csv_reader)

with open('address.csv', newline='') as address:
    csv_reader = csv.reader(address)
    next(csv_reader)
    rowsAddress = list(csv_reader)

with open('zipcode_info.csv', newline='') as zipcode_info:
    csv_reader = csv.reader(zipcode_info)
    next(csv_reader)
    rowsZipcode = list(csv_reader)

with open('sellers.csv', newline='') as sellers:
    csv_reader = csv.reader(sellers)
    next(csv_reader)
    rowsSellers = list(csv_reader)

with open('local_vendors.csv', newline='') as local_vendors:
    csv_reader = csv.reader(local_vendors)
    next(csv_reader)
    rowsLocalVendors = list(csv_reader)

with open('categories.csv', newline='') as categories:
    csv_reader = csv.reader(categories)
    next(csv_reader)
    rowsCategories = list(csv_reader)

with open('auction_listings.csv', newline='') as auction_listings:
    csv_reader = csv.reader(auction_listings)
    next(csv_reader)
    rowsAuction_Listings = list(csv_reader)

with open('bids.csv', newline='') as bids:
    csv_reader = csv.reader(bids)
    next(csv_reader)
    rowsBids = list(csv_reader)

with open('transactions.csv', newline='') as transactions:
    csv_reader = csv.reader(transactions)
    next(csv_reader)
    rowsTransactions = list(csv_reader)

with open('ratings.csv', newline='') as ratings:
    csv_reader = csv.reader(ratings)
    next(csv_reader)
    rowsRatings = list(csv_reader)

# Connect to DB and create tables if they do not exist
conn = sql.connect('data.db')
conn.execute('CREATE TABLE IF NOT EXISTS users (email TEXT PRIMARY KEY, password TEXT)')
conn.execute('CREATE TABLE IF NOT EXISTS zipcode_info (zipcode INT PRIMARY KEY, city TEXT, state TEXT)')
conn.execute('CREATE TABLE IF NOT EXISTS address (address_id TEXT PRIMARY KEY, zipcode INT, street_num int, street_name TEXT, FOREIGN KEY (zipcode) REFERENCES zipcode_info(zipcode))')
conn.execute('CREATE TABLE IF NOT EXISTS helpdesk (email TEXT PRIMARY KEY, position TEXT)')
conn.execute('CREATE TABLE IF NOT EXISTS requests (request_id INTEGER PRIMARY KEY AUTOINCREMENT, sender_email TEXT, helpdesk_staff_email TEXT, request_type TEXT, request_desc TEXT, request_status int)')
conn.execute('CREATE TABLE IF NOT EXISTS bidders (email TEXT PRIMARY KEY REFERENCES users(email), first_name TEXT, last_name TEXT, gender TEXT, age int, home_address_id TEXT, major TEXT, FOREIGN KEY (home_address_id) REFERENCES address(address_id))')
conn.execute('CREATE TABLE IF NOT EXISTS credit_cards (credit_card_num TEXT PRIMARY KEY, card_type TEXT, expire_month int, expire_year int, security_code int, owner_email TEXT, FOREIGN KEY (owner_email) REFERENCES users(email))')
conn.execute('CREATE TABLE IF NOT EXISTS sellers (email TEXT PRIMARY KEY REFERENCES users(email), bank_routing_number TEXT, bank_account_number INT, balance INT)')
conn.execute('CREATE TABLE IF NOT EXISTS local_vendors (email TEXT PRIMARY KEY REFERENCES sellers(email), business_name TEXT, business_address_id TEXT, customer_service_phone_number TEXT, FOREIGN KEY (business_address_id) REFERENCES address(address_id))')
conn.execute('CREATE TABLE IF NOT EXISTS categories (parent_category TEXT, category_name TEXT PRIMARY KEY)')
conn.execute('CREATE TABLE IF NOT EXISTS auction_listings (seller_email TEXT REFERENCES users(email), listing_id INTEGER, category TEXT, auction_title TEXT, product_name TEXT, product_description TEXT, quantity INT, reserve_price TEXT, max_bids INT, status INT, FOREIGN KEY (category) REFERENCES categories(category_name), PRIMARY KEY (seller_email, listing_id))')
conn.execute('CREATE TABLE IF NOT EXISTS bids (bid_id INT PRIMARY KEY, seller_email TEXT, listing_id INT, bidder_email TEXT, bid_price INT, FOREIGN KEY (seller_email) REFERENCES sellers(email), FOREIGN KEY (bidder_email) REFERENCES bidders(email), FOREIGN KEY (listing_id) REFERENCES auction_listings(listing_id))')
conn.execute('CREATE TABLE IF NOT EXISTS transactions (transaction_id INTEGER PRIMARY KEY AUTOINCREMENT, seller_email TEXT, listing_id INT, buyer_email TEXT, date TEXT, payment INT, FOREIGN KEY (seller_email) REFERENCES sellers(email), FOREIGN KEY (buyer_email) REFERENCES bidders(email), FOREIGN KEY (listing_id) REFERENCES auction_listings(listing_id))')
conn.execute('CREATE TABLE IF NOT EXISTS ratings (bidder_email TEXT REFERENCES bidders(email), seller_email TEXT REFERENCES sellers(email), date TEXT, rating INT, rating_desc TEXT, PRIMARY KEY (bidder_email, seller_email, date))')

# Find number of rows in the table (keeps the script from causing an error if ran when not needed)
cur = conn.cursor()
cur.execute('SELECT COUNT(*) FROM users')
count = cur.fetchone()[0]
# Hash the passwords and insert each row into the table
if count == 0:
    for row in rowsUsers:
        email, password = row
        hashed_password = hash_func(password.encode('utf-8')).hexdigest()
        conn.execute('INSERT INTO users (email, password) VALUES (? ,?)', (email, hashed_password))

# Insert into Zipcode_Info
cur = conn.cursor()
cur.execute('SELECT COUNT(*) FROM zipcode_info')
count = cur.fetchone()[0]
if count == 0:
    for row in rowsZipcode:
        zipcode, city, state = row
        conn.execute('INSERT INTO zipcode_info (zipcode, city, state) VALUES (? ,?, ?)', (zipcode, city, state))

# Insert into Address
cur = conn.cursor()
cur.execute('SELECT COUNT(*) FROM address')
count = cur.fetchone()[0]
if count == 0:
    for row in rowsAddress:
        address_id, zipcode, street_num, street_name = row
        conn.execute('INSERT INTO address (address_id, zipcode, street_num, street_name) VALUES (? ,?, ?, ?)', (address_id, zipcode, street_num, street_name))

# Insert into Helpdesk
cur = conn.cursor()
cur.execute('SELECT COUNT(*) FROM helpdesk')
count = cur.fetchone()[0]
if count == 0:
    for row in rowsHelpdesk:
        email, position = row
        conn.execute('INSERT INTO helpdesk (email, position) VALUES (? ,?)', (email, position))

# Insert into Requests
cur = conn.cursor()
cur.execute('SELECT COUNT(*) FROM requests')
count = cur.fetchone()[0]
if count == 0:
    for row in rowsRequests:
        request_id, sender_email, helpdesk_staff_email, request_type, request_desc, request_status = row
        conn.execute('INSERT INTO requests (request_id, sender_email, helpdesk_staff_email, request_type, request_desc, request_status) VALUES (? ,?, ?, ?, ?, ?)', (request_id, sender_email, helpdesk_staff_email, request_type, request_desc, request_status))

# Insert into Bidders
cur = conn.cursor()
cur.execute('SELECT COUNT(*) FROM bidders')
count = cur.fetchone()[0]
if count == 0:
    for row in rowsBidders:
        email, first_name, last_name, gender, age, home_address_id, major = row
        conn.execute('INSERT INTO bidders (email, first_name, last_name, gender, age, home_address_id, major) VALUES (? ,?, ?, ?, ?, ?, ?)', (email, first_name, last_name, gender, age, home_address_id, major))

# Insert into Credit_Cards
cur = conn.cursor()
cur.execute('SELECT COUNT(*) FROM credit_cards')
count = cur.fetchone()[0]
if count == 0:
    for row in rowsCC:
        credit_card_num, card_type, expire_month, expire_year, security_code, owner_email = row
        conn.execute('INSERT INTO credit_cards (credit_card_num, card_type, expire_month, expire_year, security_code, owner_email) VALUES (? ,?, ?, ?, ?, ?)', (credit_card_num, card_type, expire_month, expire_year, security_code, owner_email))

# Insert into Sellers
cur = conn.cursor()
cur.execute('SELECT COUNT(*) FROM sellers')
count = cur.fetchone()[0]
if count == 0:
    for row in rowsSellers:
        email, bank_routing_number, bank_account_number, balance = row
        conn.execute('INSERT INTO sellers (email, bank_routing_number, bank_account_number, balance) VALUES (? ,?, ?, ?)', (email, bank_routing_number, bank_account_number, balance))

# Insert into Local_Vendors
cur = conn.cursor()
cur.execute('SELECT COUNT(*) FROM local_vendors')
count = cur.fetchone()[0]
if count == 0:
    for row in rowsLocalVendors:
        email, business_name, business_address_id, customer_service_phone_number = row
        conn.execute('INSERT INTO local_vendors (email, business_name, business_address_id, customer_service_phone_number) VALUES (? ,?, ?, ?)', (email, business_name, business_address_id, customer_service_phone_number))

# Insert into Categories
cur = conn.cursor()
cur.execute('SELECT COUNT(*) FROM categories')
count = cur.fetchone()[0]
if count == 0:
    for row in rowsCategories:
        parent_category, category_name = row
        conn.execute('INSERT INTO categories (parent_category, category_name) VALUES (? ,?)', (parent_category, category_name))

# Insert into Auction_Listings
cur = conn.cursor()
cur.execute('SELECT COUNT(*) FROM auction_listings')
count = cur.fetchone()[0]
if count == 0:
    for row in rowsAuction_Listings:
        seller_email, listing_id, category, auction_title, product_name, product_description, quantity, reserve_price, max_bids, status = row
        conn.execute('INSERT INTO auction_listings (seller_email, listing_id, category, auction_title, product_name, product_description, quantity, reserve_price, max_bids, status) VALUES (? ,?, ?, ?, ?, ?, ?, ?, ?, ?)', (seller_email, listing_id, category, auction_title, product_name, product_description, quantity, reserve_price, max_bids, status))

# Insert into Bids
cur = conn.cursor()
cur.execute('SELECT COUNT(*) FROM bids')
count = cur.fetchone()[0]
if count == 0:
    for row in rowsBids:
        bid_id, seller_email, listing_id, bidder_email, bid_price = row
        conn.execute('INSERT INTO bids (bid_id, seller_email, listing_id, bidder_email, bid_price) VALUES (? ,?, ?, ?, ?)', (bid_id, seller_email, listing_id, bidder_email, bid_price))

# Insert into Transactions
cur = conn.cursor()
cur.execute('SELECT COUNT(*) FROM transactions')
count = cur.fetchone()[0]
if count == 0:
    for row in rowsTransactions:
        transaction_id, seller_email, listing_id, buyer_email, date, payment = row
        conn.execute('INSERT INTO transactions (transaction_id, seller_email, listing_id, buyer_email, date, payment) VALUES (? ,?, ?, ?, ?, ?)', (transaction_id, seller_email, listing_id, buyer_email, date, payment))

# Insert into Helpdesk
cur = conn.cursor()
cur.execute('SELECT COUNT(*) FROM ratings')
count = cur.fetchone()[0]
if count == 0:
    for row in rowsRatings:
        bidder_email, seller_email, date, rating, rating_desc = row
        conn.execute('INSERT INTO ratings (bidder_email, seller_email, date, rating, rating_desc) VALUES (? ,?, ?, ?, ?)', (bidder_email, seller_email, date, rating, rating_desc))

conn.commit()
conn.close()
