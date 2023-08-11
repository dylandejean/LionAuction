LionAuction Functionality Implementation - Dylan DeJean

When running the app you will be directed to 'index.html' where you may login with any valid user in the users table. You can also choose which permissions to login with: bidder, seller, or helpdesk. Bidders will see their personal information as well as buttons that take them to the category browser as well as their notifications page which allows bidders to see their outstanding bids and allows them to pay when they win. After paying, bidders can rate the seller 1-5 also with a description. The category browser allows the user to pick a root category from a dropdown list. After clicking submit, the table will populate with auction information and a link with more information which also allows the user to bid on the item. The dropdown will also repopulate with all subcategories under the previously chosen category. The user can traverse the heirachy until they reach a category with no sub categories. From here, the user can click the 'clear' button which will return to the root categories as options. 

On login, sellers and local vendors will see their auctions categorized by status. They can edit active and inactive auctions. They also have the ability to create new auctions. Helpdesk will see assigned and unassigned requests. Sellers and Helpdesk can also browse categories, bid, and see bidding notifications.

In the project folder also contains a script named 'populate.py' which, when ran, will populate the database with all 
emails and passwords (which will be encrypted by the script) from a file named 'users.csv' in the root folder. 

Instructions:
	1. Run the 'populate.py' script which will populate the 'data.db' database with all information in the csv files.
	2. Run 'app.py' 
	3. Navigate to 'http://127.0.0.1:5000/' in your browser
