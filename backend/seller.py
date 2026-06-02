import uuid

def make_id(prefix, max_length):
    return (prefix + uuid.uuid4().hex)[:max_length]

def create_item_and_auction(db, seller_login):
    print("\n--- Create Item and Auction ---")

    item_id = make_id("ITEM", 20)
    auction_id = make_id("AUC", 30)

    item_name = input("Item name: ").strip()
    category = input("Category: ").strip()
    image_url = input("Image URL, optional: ").strip()
    condition = input("Condition [available/sold/removed]: ").strip()

    try:
        starting_price = float(input("Starting price: ").strip())
    except ValueError:
        print("Invalid starting price.")
        return

    description = input("Description: ").strip()

    if condition not in ["available", "sold", "removed"]:
        print("Invalid condition.")
        return

    if not item_name or not description:
        print("Item name and description are required.")
        return
    
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

    success = db.execute_transaction([
        (
            insert_item,
            (
                item_id,
                item_name,
                category,
                image_url,
                condition,
                starting_price,
                description,
                seller_login
            )
        ),
        (
            insert_auction,
            (
                auction_id,
                starting_price,
                seller_login,
                item_id
            )
        )
    ])

    if success:
        print("Item and auction created successfully.")
        print("Item ID:", item_id)
        print("Auction ID:", auction_id)


def view_my_items(db, seller_login):
    print("\n--- My Items ---")

    query = """
        SELECT itemID, itemName, category, condition, startingPrice, description
        FROM Item
        WHERE sellerLogin = %s
        ORDER BY itemID;
    """

    db.execute_query(query, (seller_login,))


def view_my_auctions(db, seller_login):
    print("\n--- My Auctions ---")

    query = """
        SELECT
            Auction.auctionID,
            Item.itemName,
            Item.category,
            Auction.currentHighestBid,
            Auction.auctionStatus,
            Auction.buyerLogin
        FROM Auction
        JOIN Item ON Auction.itemID = Item.itemID
        WHERE Auction.sellerLogin = %s
        ORDER BY Auction.auctionID;
    """

    db.execute_query(query, (seller_login,))


def end_auction(db, seller_login):
    print("\n--- End Auction ---")

    auction_id = input("Auction ID: ").strip()

    auction = db.fetch_one("""
        SELECT auctionID
        FROM Auction
        WHERE auctionID = %s
          AND sellerLogin = %s
          AND auctionStatus = 'active';
    """, (auction_id, seller_login))

    if auction is None:
        print("Auction not found, not yours, or already closed.")
        return

    winner = db.fetch_one("""
        SELECT buyerLogin
        FROM Bid
        WHERE auctionID = %s
        ORDER BY bidAmount DESC, bidTimestamp ASC
        LIMIT 1;
    """, (auction_id,))

    winner_login = winner[0].strip() if winner else None

    update_auction = """
        UPDATE Auction
        SET auctionStatus = 'closed',
            buyerLogin = %s
        WHERE auctionID = %s;
    """

    statements = [
        (update_auction, (winner_login, auction_id))
    ]

    if winner_login:
        update_item = """
            UPDATE Item
            SET condition = 'sold'
            WHERE itemID = (
                SELECT itemID
                FROM Auction
                WHERE auctionID = %s
            );
        """

        statements.append((update_item, (auction_id,)))

    success = db.execute_transaction(statements)

    if success:
        if winner_login:
            print("Auction closed. Winner:", winner_login)
        else:
            print("Auction closed. No bids were placed.")


def create_shipment(db, seller_login):
    print("\n--- Create Shipment ---")

    auction_id = input("Auction ID: ").strip()
    shipment_id = make_id("SHIP", 30)
    address = input("Shipping address: ").strip()
    tracking_input = input("Tracking number, optional numeric only: ").strip()

    tracking_number = None

    if tracking_input:
        try:
            tracking_number = int(tracking_input)
        except ValueError:
            print("Tracking number must be numeric.")
            return

    result = db.fetch_one("""
        SELECT Auction.auctionID
        FROM Auction
        JOIN Payment ON Auction.auctionID = Payment.auctionID
        WHERE Auction.auctionID = %s
          AND Auction.sellerLogin = %s
          AND Auction.auctionStatus = 'closed'
          AND Payment.paymentStatus = 'completed';
    """, (auction_id, seller_login))

    if result is None:
        print("Auction not found, not yours, not closed, or payment is not completed.")
        return

    query = """
        INSERT INTO Shipment
        (ShipmentID, address, shipmentStatus, trackingNumber, auctionID)
        VALUES (%s, %s, 'pending', %s, %s);
    """

    success = db.execute_update(query, (shipment_id, address, tracking_number, auction_id))

    if success:
        print("Shipment created.")
        print("Shipment ID:", shipment_id)