import getpass

def register_user(db):
    print("\n--- Register New Buyer ---")

    login = input("Login: ").strip()
    phone = input("Phone number: ").strip()
    password = getpass.getpass("Password: ")
    address = input("Address: ").strip()
    favorite_category = input("Favorite category, optional: ").strip()

    if not login or not password:
        print("Login and password are required.")
        return

    query = """
        INSERT INTO "User"
        (login, phoneNum, role, password, address, favoriteCategory)
        VALUES (%s, %s, 'Buyer', %s, %s, %s);
    """

    db.execute_update(query, (login, phone, password, address, favorite_category))

def register_seller(db):
    print("\n--- Register New Seller ---")

    login = input("Login: ").strip()
    phone = input("Phone number: ").strip()
    password = getpass.getpass("Password: ")
    address = input("Address: ").strip()
    favorite_category = input("Favorite category, optional: ").strip()

    if not login or not password:
        print("Login and password are required.")
        return

    query = """
        INSERT INTO "User"
        (login, phoneNum, role, password, address, favoriteCategory)
        VALUES (%s, %s, 'Seller', %s, %s, %s);
    """

    db.execute_update(query, (login, phone, password, address, favorite_category))

def login_user(db):
    print("\n--- Login ---")

    login = input("Login: ").strip()
    password = getpass.getpass("Password: ")

    query = """
        SELECT login, role
        FROM "User"
        WHERE login = %s AND password = %s;
    """

    user = db.fetch_one(query, (login, password))

    if user is None:
        print("Invalid login or password.")
        return None, None

    user_login = user[0].strip()
    role = user[1].strip()

    print(f"Welcome, {user_login}! Role: {role}")
    return user_login, role


def browse_active_auctions(db):
    print("\n--- Active Auctions ---")

    query = """
        SELECT
            Auction.auctionID,
            Item.itemName,
            Item.category,
            Item.condition,
            Item.startingPrice,
            Auction.currentHighestBid,
            Auction.auctionStatus,
            Auction.sellerLogin
        FROM Auction
        JOIN Item ON Auction.itemID = Item.itemID
        WHERE Auction.auctionStatus = 'active'
        ORDER BY Auction.auctionID;
    """

    db.execute_query(query)


def search_auctions(db):
    print("\n--- Search Auctions ---")

    keyword = input("Search item name/category/description: ").strip()
    pattern = f"%{keyword}%"

    query = """
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
                LOWER(Item.itemName) LIKE LOWER(%s)
                OR LOWER(Item.category) LIKE LOWER(%s)
                OR LOWER(Item.description) LIKE LOWER(%s)
              )
        ORDER BY Auction.currentHighestBid;
    """

    db.execute_query(query, (pattern, pattern, pattern))


def view_profile(db, login):
    print("\n--- My Profile ---")

    query = """
        SELECT login, phoneNum, role, address, favoriteCategory
        FROM "User"
        WHERE login = %s;
    """

    db.execute_query(query, (login,))


def edit_profile(db, login):
    print("\n--- Edit Profile ---")
    print("Login and role cannot be changed here.")

    phone = input("New phone number: ").strip()
    address = input("New address: ").strip()
    favorite_category = input("New favorite category: ").strip()

    query = """
        UPDATE "User"
        SET phoneNum = %s,
            address = %s,
            favoriteCategory = %s
        WHERE login = %s;
    """

    db.execute_update(query, (phone, address, favorite_category, login))