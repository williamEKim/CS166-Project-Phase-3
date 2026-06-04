from flask import Flask, render_template_string, redirect, url_for, request, session
import sys

from EmbeddedSQL import *
from actions import *
from buyer import *
from seller import *

app = Flask(__name__)
app.secret_key = "ebay_gui_secret"
db = None

# Templates 

MAIN_MENU = """
<h2>eBay DB Interface - Main Menu</h2>
<a href="/login"><button>Login</button></a><br><br>
<a href="/register_buyer"><button>Register as Buyer</button></a><br><br>
<a href="/register_seller"><button>Register as Seller</button></a>
"""

LOGIN_PAGE = """
<h2>Login</h2>
<form method="POST" action="/login">
    <label>Login: <input type="text" name="login" required></label><br><br>
    <label>Password: <input type="password" name="password" required></label><br><br>
    <button type="submit">Login</button>
</form>
<br><a href="/">Back</a>
{% if error %}
    <p style="color:red;">{{ error }}</p>
{% endif %}
"""

REGISTER_PAGE = """
<h2>Register as {{ role }}</h2>
<form method="POST">
    <label>Login: <input type="text" name="login" required></label><br><br>
    <label>Phone: <input type="text" name="phone"></label><br><br>
    <label>Password: <input type="password" name="password" required></label><br><br>
    <label>Address: <input type="text" name="address"></label><br><br>
    <label>Favorite Category (optional): <input type="text" name="favorite_category"></label><br><br>
    <button type="submit">Register</button>
</form>

<a href="/login"><button type="button">Login</button></a>
<br>

<br><a href="/">Back</a>
{% if error %}
    <p style="color:red;">{{ error }}</p>
{% endif %}
{% if success %}
    <p style="color:green;">{{ success }}</p>
{% endif %}
"""

BUYER_MENU = """
<h2>Buyer Menu — Welcome, {{ login }}!</h2>
<a href="/browse"><button>Browse Active Auctions</button></a><br><br>
<a href="/search"><button>Search Auctions</button></a><br><br>
<a href="/place_bid"><button>Place Bid</button></a><br><br>
<a href="/my_bids"><button>View My Bids</button></a><br><br>
<a href="/make_payment"><button>Make Payment</button></a><br><br>
<a href="/profile"><button>View Profile</button></a><br><br>
<a href="/logout"><button>Logout</button></a>
"""

SELLER_MENU = """
<h2>Seller Menu — Welcome, {{ login }}!</h2>
<a href="/browse"><button>Browse Active Auctions</button></a><br><br>
<a href="/create_item"><button>Create Item and Auction</button></a><br><br>
<a href="/end_auction"><button>End Auction</button></a><br><br>
<a href="/profile"><button>View Profile</button></a><br><br>
<a href="/logout"><button>Logout</button></a>
"""

PROFILE_PAGE = """
<h2>My Profile</h2>
<a href="/dashboard"><button>Back to Menu</button></a>
<br><br>
{% if profile %}
<table border="1" cellpadding="8" cellspacing="0">
    <tr><th>Login</th><td>{{ profile[0] }}</td></tr>
    <tr><th>Phone</th><td>{{ profile[1] }}</td></tr>
    <tr><th>Role</th><td>{{ profile[2] }}</td></tr>
    <tr><th>Address</th><td>{{ profile[3] }}</td></tr>
    <tr><th>Favorite Category</th><td>{{ profile[4] }}</td></tr>
</table>
<br>
<a href="/edit_profile"><button>Edit Profile</button></a>
{% endif %}
"""

EDIT_PROFILE_PAGE = """
<h2>Edit Profile</h2>
<form method="POST">
    <label>Phone: <input type="text" name="phone" value="{{ profile[1] }}"></label><br><br>
    <label>Address: <input type="text" name="address" value="{{ profile[3] }}"></label><br><br>
    <label>Favorite Category: <input type="text" name="favorite_category" value="{{ profile[4] or '' }}"></label><br><br>
    <button type="submit">Save</button>
</form>
<br><a href="/profile">Back</a>
{% if success %}
    <p style="color:green;">{{ success }}</p>
{% endif %}
"""

BROWSE_PAGE = """
<h2>Active Auctions</h2>
<a href="/dashboard"><button>Back to Menu</button></a>
<br><br>
{% if auctions %}
<table border="1" cellpadding="8" cellspacing="0">
    <tr>
        <th>Auction ID</th>
        <th>Item Name</th>
        <th>Category</th>
        <th>Condition</th>
        <th>Starting Price</th>
        <th>Current Highest Bid</th>
        <th>Seller</th>
    </tr>
    {% for row in auctions %}
    <tr>
        <td>{{ row[0] }}</td>
        <td>{{ row[1] }}</td>
        <td>{{ row[2] }}</td>
        <td>{{ row[3] }}</td>
        <td>${{ "%.2f"|format(row[4]) }}</td>
        <td>{% if row[5] %} ${{ "%.2f"|format(row[5]) }} {% else %} No bids yet {% endif %}</td>
        <td>{{ row[6] }}</td>
    </tr>
    {% endfor %}
</table>
{% else %}
    <p>No active auctions found.</p>
{% endif %}
"""

CREATE_ITEM_PAGE = """
<h2>Create Item and Auction</h2>
<form method="POST">
    <label>Item Name: <input type="text" name="item_name" required></label><br><br>
    <label>Category: <input type="text" name="category"></label><br><br>
    <label>Image URL (optional): <input type="text" name="image_url"></label><br><br>
    <label>Condition:
        <select name="condition">
            <option value="available">Available</option>
            <option value="sold">Sold</option>
            <option value="removed">Removed</option>
        </select>
    </label><br><br>
    <label>Starting Price:</label><br>
    <div style="display:inline-flex; align-items:center; border:1px solid #ccc; padding:2px 6px;">
        <span>$</span>
        <input type="number" step="0.01" name="starting_price" required
            style="border:none; outline:none; margin-left:4px;">
    </div>
    <br><br>
    <label>Description: <textarea name="description" required></textarea></label><br><br>
    <button type="submit">Create</button>
</form>
<br><a href="/dashboard">Back</a>
{% if error %}
    <p style="color:red;">{{ error }}</p>
{% endif %}
{% if success %}
    <p style="color:green;">{{ success }}</p>
{% endif %}
"""

PLACE_BID_PAGE = """
<h2>Place Bid</h2>
<form method="POST">
    <label>Auction ID: <input type="text" name="auction_id" required></label><br><br>
    <label>Bid Amount:</label><br>
    <div style="display:inline-flex; align-items:center; border:1px solid #ccc; padding:2px 6px;">
        <span>$</span>
        <input type="number" step="0.01" name="bid_amount" required
               style="border:none; outline:none; margin-left:4px;">
    </div>
    <br><br>
    <button type="submit">Place Bid</button>
</form>
<br><a href="/dashboard">Back</a>
{% if error %}
    <p style="color:red;">{{ error }}</p>
{% endif %}
{% if success %}
    <p style="color:green;">{{ success }}</p>
{% endif %}
"""

VIEW_BIDS_PAGE = """
<h2>My Bids</h2>
<a href="/dashboard"><button>Back to Menu</button></a>
<br><br>
{% if bids %}
<table border="1" cellpadding="8" cellspacing="0">
    <tr>
        <th>Bid ID</th>
        <th>Auction ID</th>
        <th>Item Name</th>
        <th>My Bid</th>
        <th>Current Highest Bid</th>
        <th>Auction Status</th>
        <th>Timestamp</th>
    </tr>
    {% for row in bids %}
    <tr>
        <td>{{ row[0] }}</td>
        <td>{{ row[1] }}</td>
        <td>{{ row[2] }}</td>
        <td>${{ "%.2f"|format(row[3]) }}</td>
        <td>${{ "%.2f"|format(row[4]) }}</td>
        <td>{{ row[5] }}</td>
        <td>{{ row[6] }}</td>
    </tr>
    {% endfor %}
</table>
{% else %}
    <p>You have not placed any bids yet.</p>
{% endif %}
"""

SEARCH_PAGE = """
<h2>Search Auctions</h2>
<form method="POST">
    <label>Keyword: <input type="text" name="keyword" required></label>
    <button type="submit">Search</button>
</form>
<br><a href="/dashboard">Back</a>
<br><br>
{% if results is not none %}
    {% if results %}
    <table border="1" cellpadding="8" cellspacing="0">
        <tr>
            <th>Auction ID</th>
            <th>Item Name</th>
            <th>Category</th>
            <th>Description</th>
            <th>Current Highest Bid</th>
            <th>Status</th>
            <th>Seller</th>
        </tr>
        {% for row in results %}
        <tr>
            <td>{{ row[0] }}</td>
            <td>{{ row[1] }}</td>
            <td>{{ row[2] }}</td>
            <td>{{ row[3] }}</td>
            <td>${{ "%.2f"|format(row[4]) }}</td>
            <td>{{ row[5] }}</td>
            <td>{{ row[6] }}</td>
        </tr>
        {% endfor %}
    </table>
    {% else %}
        <p>No auctions matched your search.</p>
    {% endif %}
{% endif %}
"""

END_AUCTION_PAGE = """
<h2>End Auction</h2>
<a href="/dashboard"><button>Back to Menu</button></a>
<br><br>
{% if error %}
    <p style="color:red;">{{ error }}</p>
{% endif %}
{% if success %}
    <p style="color:green;">{{ success }}</p>
{% endif %}
{% if auctions %}
<table border="1" cellpadding="8" cellspacing="0">
    <tr>
        <th>Auction ID</th>
        <th>Item Name</th>
        <th>Category</th>
        <th>Current Highest Bid</th>
        <th>Action</th>
    </tr>
    {% for row in auctions %}
    <tr>
        <td>{{ row[0] }}</td>
        <td>{{ row[1] }}</td>
        <td>{{ row[2] }}</td>
        <td>{% if row[3] %} ${{ "%.2f"|format(row[3]) }} {% else %} No bids yet {% endif %}</td>
        <td>
            <form method="POST">
                <input type="hidden" name="auction_id" value="{{ row[0] }}">
                <button type="submit">End</button>
            </form>
        </td>
    </tr>
    {% endfor %}
</table>
{% else %}
    <p>You have no active auctions.</p>
{% endif %}
"""

MAKE_PAYMENT_PAGE = """
<h2>Make Payment</h2>
<a href="/dashboard"><button>Back to Menu</button></a>
<br><br>
{% if error %}
    <p style="color:red;">{{ error }}</p>
{% endif %}
{% if success %}
    <p style="color:green;">{{ success }}</p>
{% endif %}
{% if auctions %}
<table border="1" cellpadding="8" cellspacing="0">
    <tr>
        <th>Auction ID</th>
        <th>Item Name</th>
        <th>Amount Due</th>
        <th>Seller</th>
        <th>Action</th>
    </tr>
    {% for row in auctions %}
    <tr>
        <td>{{ row[0] }}</td>
        <td>{{ row[1] }}</td>
        <td>${{ "%.2f"|format(row[2]) }}</td>
        <td>{{ row[3] }}</td>
        <td>
            <form method="POST">
                <input type="hidden" name="auction_id" value="{{ row[0] }}">
                <input type="hidden" name="amount" value="{{ row[2] }}">
                <button type="submit">Pay</button>
            </form>
        </td>
    </tr>
    {% endfor %}
</table>
{% else %}
    <p>No pending payments.</p>
{% endif %}
"""

# Routes 

@app.route("/")
def main_menu():
    return render_template_string(MAIN_MENU)


@app.route("/login", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        login_input = request.form["login"].strip()
        password    = request.form["password"].strip()

        query = """
            SELECT login, role
            FROM "User"
            WHERE login = %s AND password = %s;
        """
        user = db.fetch_one(query, (login_input, password))

        if user is None:
            error = "Invalid login or password."
        else:
            session["login"] = user[0].strip()
            session["role"]  = user[1].strip()
            return redirect(url_for("dashboard"))

    return render_template_string(LOGIN_PAGE, error=error)

@app.route("/register_buyer", methods=["GET", "POST"])
def register_buyer():
    error = None
    success = None

    if request.method == "POST":
        login        = request.form["login"].strip()
        phone        = request.form["phone"].strip()
        password     = request.form["password"].strip()
        address      = request.form["address"].strip()
        fav_category = request.form["favorite_category"].strip()

        if not login or not password:
            error = "Login and password are required."
        else:
            query = """
                INSERT INTO "User"
                (login, phoneNum, role, password, address, favoriteCategory)
                VALUES (%s, %s, 'Buyer', %s, %s, %s);
            """
            db.execute_update(query, (login, phone, password, address, fav_category))
            success = f"Buyer '{login}' registered! You can now log in."

    return render_template_string(REGISTER_PAGE, role="Buyer", error=error, success=success)


@app.route("/register_seller", methods=["GET", "POST"])
def register_seller_route():
    error = None
    success = None

    if request.method == "POST":
        login        = request.form["login"].strip()
        phone        = request.form["phone"].strip()
        password     = request.form["password"].strip()
        address      = request.form["address"].strip()
        fav_category = request.form["favorite_category"].strip()

        if not login or not password:
            error = "Login and password are required."
        else:
            query = """
                INSERT INTO "User"
                (login, phoneNum, role, password, address, favoriteCategory)
                VALUES (%s, %s, 'Seller', %s, %s, %s);
            """
            db.execute_update(query, (login, phone, password, address, fav_category))
            success = f"Seller '{login}' registered! You can now log in."

    return render_template_string(REGISTER_PAGE, role="Seller", error=error, success=success)

@app.route("/dashboard")
def dashboard():
    if "login" not in session:
        return redirect(url_for("main_menu"))
    if session["role"] == "Buyer":
        return render_template_string(BUYER_MENU, login=session["login"])
    else:
        return render_template_string(SELLER_MENU, login=session["login"])

@app.route("/profile")
def profile():
    if "login" not in session:
        return redirect(url_for("main_menu"))

    data = db.fetch_one("""
        SELECT login, phoneNum, role, address, favoriteCategory
        FROM "User" WHERE login = %s;
    """, (session["login"],))

    return render_template_string(PROFILE_PAGE, profile=data)


@app.route("/edit_profile", methods=["GET", "POST"])
def edit_profile():
    if "login" not in session:
        return redirect(url_for("main_menu"))

    success = None
    data = db.fetch_one("""
        SELECT login, phoneNum, role, address, favoriteCategory
        FROM "User" WHERE login = %s;
    """, (session["login"],))

    if request.method == "POST":
        phone        = request.form["phone"].strip()
        address      = request.form["address"].strip()
        fav_category = request.form["favorite_category"].strip()

        db.execute_update("""
            UPDATE "User"
            SET phoneNum = %s, address = %s, favoriteCategory = %s
            WHERE login = %s;
        """, (phone, address, fav_category, session["login"]))

        success = "Profile updated!"
        data = db.fetch_one("""
            SELECT login, phoneNum, role, address, favoriteCategory
            FROM "User" WHERE login = %s;
        """, (session["login"],))

    return render_template_string(EDIT_PROFILE_PAGE, profile=data, success=success)

@app.route("/browse")
def browse():
    if "login" not in session:
        return redirect(url_for("main_menu"))

    query = """
        SELECT
            Auction.auctionID,
            Item.itemName,
            Item.category,
            Item.condition,
            Item.startingPrice,
            Auction.currentHighestBid,
            Auction.sellerLogin
        FROM Auction
        JOIN Item ON Auction.itemID = Item.itemID
        WHERE Auction.auctionStatus = 'active'
        ORDER BY Auction.auctionID;
    """

    auctions = db.fetch_all(query)
    return render_template_string(BROWSE_PAGE, auctions=auctions)

@app.route("/create_item", methods=["GET", "POST"])
def create_item():
    if "login" not in session or session["role"] != "Seller":
        return redirect(url_for("main_menu"))

    error = None
    success = None

    if request.method == "POST":
        item_name     = request.form["item_name"].strip()
        category      = request.form["category"].strip()
        image_url     = request.form["image_url"].strip()
        condition     = request.form["condition"]
        description   = request.form["description"].strip()
        seller_login  = session["login"]

        try:
            starting_price = float(request.form["starting_price"])
        except ValueError:
            error = "Invalid starting price."
            return render_template_string(CREATE_ITEM_PAGE, error=error, success=success)

        item_id    = ("ITEM" + uuid.uuid4().hex)[:20]
        auction_id = ("AUC"  + uuid.uuid4().hex)[:30]

        insert_item = """
            INSERT INTO Item
            (itemID, itemName, category, imageURL, condition, startingPrice, description, sellerLogin)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s);
        """
        insert_auction = """
            INSERT INTO Auction
            (auctionID, auctionStatus, currentHighestBid, sellerLogin, itemID, buyerLogin)
            VALUES (%s, 'active', %s, %s, %s, NULL);
        """

        ok = db.execute_transaction([
            (insert_item,    (item_id, item_name, category, image_url, condition, starting_price, description, seller_login)),
            (insert_auction, (auction_id, starting_price, seller_login, item_id))
        ])

        if ok:
            success = f"Created! Auction ID: {auction_id}"
        else:
            error = "Something went wrong. Check the terminal for details."

    return render_template_string(CREATE_ITEM_PAGE, error=error, success=success)

@app.route("/place_bid", methods=["GET", "POST"])
def place_bid():
    if "login" not in session or session["role"] != "Buyer":
        return redirect(url_for("main_menu"))

    error = None
    success = None

    if request.method == "POST":
        auction_id   = request.form["auction_id"].strip()
        buyer_login  = session["login"]

        try:
            bid_amount = float(request.form["bid_amount"])
        except ValueError:
            error = "Invalid bid amount."
            return render_template_string(PLACE_BID_PAGE, error=error, success=success)

        auction = db.fetch_one("""
            SELECT sellerLogin, currentHighestBid, auctionStatus
            FROM Auction WHERE auctionID = %s;
        """, (auction_id,))

        if auction is None:
            error = "Auction not found."
        elif auction[2] != "active":
            error = "This auction is not active."
        elif auction[0].strip() == buyer_login:
            error = "You cannot bid on your own auction."
        elif auction[1] is not None and bid_amount <= float(auction[1]):
            error = f"Bid must be greater than current highest bid (${auction[1]:.2f})."
        else:
            bid_id = ("BID" + uuid.uuid4().hex)[:30]

            ok = db.execute_transaction([
                (
                    """INSERT INTO Bid (bidId, bidAmount, bidTimestamp, buyerLogin, auctionID)
                       VALUES (%s, %s, %s, %s, %s);""",
                    (bid_id, bid_amount, datetime.now(), buyer_login, auction_id)
                ),
                (
                    """UPDATE Auction SET currentHighestBid = %s WHERE auctionID = %s;""",
                    (bid_amount, auction_id)
                )
            ])

            if ok:
                success = f"Bid placed successfully! Bid ID: {bid_id}"
            else:
                error = "Something went wrong. Check terminal for details."

    return render_template_string(PLACE_BID_PAGE, error=error, success=success)

@app.route("/my_bids")
def my_bids():
    if "login" not in session or session["role"] != "Buyer":
        return redirect(url_for("main_menu"))

    bids = db.fetch_all("""
        SELECT
            Bid.bidId,
            Bid.auctionID,
            Item.itemName,
            Bid.bidAmount,
            Auction.currentHighestBid,
            Auction.auctionStatus,
            Bid.bidTimestamp
        FROM Bid
        JOIN Auction ON Bid.auctionID = Auction.auctionID
        JOIN Item ON Auction.itemID = Item.itemID
        WHERE Bid.buyerLogin = %s
        ORDER BY Bid.bidTimestamp DESC;
    """, (session["login"],))

    return render_template_string(VIEW_BIDS_PAGE, bids=bids)

@app.route("/search", methods=["GET", "POST"])
def search():
    if "login" not in session:
        return redirect(url_for("main_menu"))

    results = None

    if request.method == "POST":
        keyword = request.form["keyword"].strip()
        pattern = f"%{keyword}%"

        results = db.fetch_all("""
            SELECT
                Auction.auctionID,
                Item.itemName,
                Item.category,
                Item.description,
                Auction.currentHighestBid,
                Auction.auctionStatus,
                Auction.sellerLogin
            FROM Auction
            JOIN Item ON Auction.itemID = Item.itemID
            WHERE Auction.auctionStatus = 'active'
              AND (
                    LOWER(Item.itemName)    LIKE LOWER(%s)
                OR  LOWER(Item.category)   LIKE LOWER(%s)
                OR  LOWER(Item.description) LIKE LOWER(%s)
              )
            ORDER BY Auction.currentHighestBid;
        """, (pattern, pattern, pattern))

    return render_template_string(SEARCH_PAGE, results=results)

@app.route("/end_auction", methods=["GET", "POST"])
def end_auction():
    if "login" not in session or session["role"] != "Seller":
        return redirect(url_for("main_menu"))

    error = None
    success = None

    if request.method == "POST":
        auction_id   = request.form["auction_id"].strip()
        seller_login = session["login"]

        auction = db.fetch_one("""
            SELECT auctionID FROM Auction
            WHERE auctionID = %s
              AND sellerLogin = %s
              AND auctionStatus = 'active';
        """, (auction_id, seller_login))

        if auction is None:
            error = "Auction not found, not yours, or already closed."
        else:
            winner = db.fetch_one("""
                SELECT buyerLogin FROM Bid
                WHERE auctionID = %s
                ORDER BY bidAmount DESC, bidTimestamp ASC
                LIMIT 1;
            """, (auction_id,))

            winner_login = winner[0].strip() if winner else None

            statements = [(
                """UPDATE Auction
                   SET auctionStatus = 'closed', buyerLogin = %s
                   WHERE auctionID = %s;""",
                (winner_login, auction_id)
            )]

            if winner_login:
                statements.append((
                    """UPDATE Item SET condition = 'sold'
                       WHERE itemID = (
                           SELECT itemID FROM Auction WHERE auctionID = %s
                       );""",
                    (auction_id,)
                ))

            ok = db.execute_transaction(statements)

            if ok:
                if winner_login:
                    success = f"Auction closed. Winner: {winner_login}"
                else:
                    success = "Auction closed. No bids were placed."
            else:
                error = "Something went wrong."

    # always reload active auctions after POST too
    auctions = db.fetch_all("""
        SELECT
            Auction.auctionID,
            Item.itemName,
            Item.category,
            Auction.currentHighestBid
        FROM Auction
        JOIN Item ON Auction.itemID = Item.itemID
        WHERE Auction.sellerLogin = %s
          AND Auction.auctionStatus = 'active'
        ORDER BY Auction.auctionID;
    """, (session["login"],))

    return render_template_string(END_AUCTION_PAGE, auctions=auctions, error=error, success=success)

@app.route("/make_payment", methods=["GET", "POST"])
def make_payment():
    if "login" not in session or session["role"] != "Buyer":
        return redirect(url_for("main_menu"))

    error = None
    success = None
    buyer_login = session["login"]

    if request.method == "POST":
        auction_id = request.form["auction_id"].strip()
        amount     = float(request.form["amount"])

        # verify buyer is the winner and auction is closed
        auction = db.fetch_one("""
            SELECT currentHighestBid, buyerLogin, auctionStatus
            FROM Auction WHERE auctionID = %s;
        """, (auction_id,))

        if auction is None:
            error = "Auction not found."
        elif auction[1] is None or auction[1].strip() != buyer_login:
            error = "You are not the winner of this auction."
        elif auction[2] != "closed":
            error = "Auction must be closed before payment."
        else:
            # check if already paid
            existing = db.fetch_one("""
                SELECT paymentID FROM Payment WHERE auctionID = %s;
            """, (auction_id,))

            if existing:
                error = "Payment already made for this auction."
            else:
                payment_id = ("PAY" + uuid.uuid4().hex)[:30]
                ok = db.execute_update("""
                    INSERT INTO Payment (paymentID, amount, paymentStatus, buyerLogin, auctionID)
                    VALUES (%s, %s, 'completed', %s, %s);
                """, (payment_id, amount, buyer_login, auction_id))

                if ok:
                    success = f"Payment of ${amount:.2f} completed! Payment ID: {payment_id}"
                else:
                    error = "Something went wrong."

    # show auctions won but not yet paid
    auctions = db.fetch_all("""
        SELECT
            Auction.auctionID,
            Item.itemName,
            Auction.currentHighestBid,
            Auction.sellerLogin
        FROM Auction
        JOIN Item ON Auction.itemID = Item.itemID
        LEFT JOIN Payment ON Auction.auctionID = Payment.auctionID
        WHERE Auction.buyerLogin = %s
          AND Auction.auctionStatus = 'closed'
          AND Payment.paymentID IS NULL;
    """, (buyer_login,))

    return render_template_string(MAKE_PAYMENT_PAGE, auctions=auctions, error=error, success=success)

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("main_menu"))


# Main Logic

def main():
    global db
    if len(sys.argv) != 4:
        print(f"Usage: python {sys.argv[0]} <dbname> <port> <user>", file=sys.stderr)
        return

    dbname, dbport, user = sys.argv[1], sys.argv[2], sys.argv[3]
    db = EmbeddedSQL(dbname, dbport, user, "")

    print("Open your browser: http://localhost:5000")
    app.run(debug=False, port=5000)

if __name__ == "__main__":
    main()