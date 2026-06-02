from datetime import datetime
import uuid


def make_id(prefix, max_length):
    return (prefix + uuid.uuid4().hex)[:max_length]


def place_bid(db, buyer_login):
    print("\n--- Place Bid ---")

    auction_id = input("Auction ID: ").strip()

    try:
        bid_amount = float(input("Bid amount: ").strip())
    except ValueError:
        print("Invalid bid amount.")
        return

    auction = db.fetch_one("""
        SELECT sellerLogin, currentHighestBid, auctionStatus
        FROM Auction
        WHERE auctionID = %s;
    """, (auction_id,))

    if auction is None:
        print("Auction not found.")
        return

    seller_login = auction[0].strip()
    current_highest_bid = auction[1]
    auction_status = auction[2]

    if auction_status != "active":
        print("This auction is not active.")
        return

    if seller_login == buyer_login:
        print("You cannot bid on your own auction.")
        return

    if current_highest_bid is not None and bid_amount <= float(current_highest_bid):
        print("Bid must be greater than the current highest bid.")
        return

    bid_id = make_id("BID", 30)

    insert_bid = """
        INSERT INTO Bid
        (bidId, bidAmount, bidTimestamp, buyerLogin, auctionID)
        VALUES (%s, %s, %s, %s, %s);
    """

    update_auction = """
        UPDATE Auction
        SET currentHighestBid = %s
        WHERE auctionID = %s;
    """

    success = db.execute_transaction([
        (
            insert_bid,
            (bid_id, bid_amount, datetime.now(), buyer_login, auction_id)
        ),
        (
            update_auction,
            (bid_amount, auction_id)
        )
    ])

    if success:
        print("Bid placed successfully.")
        print("Bid ID:", bid_id)


def view_my_bids(db, buyer_login):
    print("\n--- My Bids ---")

    query = """
        SELECT
            Bid.bidId,
            Bid.auctionID,
            Item.itemName,
            Bid.bidAmount,
            Bid.bidTimestamp,
            Auction.currentHighestBid,
            Auction.auctionStatus
        FROM Bid
        JOIN Auction ON Bid.auctionID = Auction.auctionID
        JOIN Item ON Auction.itemID = Item.itemID
        WHERE Bid.buyerLogin = %s
        ORDER BY Bid.bidTimestamp DESC;
    """

    db.execute_query(query, (buyer_login,))


def view_won_auctions(db, buyer_login):
    print("\n--- Auctions I Won ---")

    query = """
        SELECT
            Auction.auctionID,
            Item.itemName,
            Auction.currentHighestBid,
            Auction.auctionStatus,
            Auction.sellerLogin
        FROM Auction
        JOIN Item ON Auction.itemID = Item.itemID
        WHERE Auction.buyerLogin = %s
        ORDER BY Auction.auctionID;
    """

    db.execute_query(query, (buyer_login,))


def make_payment(db, buyer_login):
    print("\n--- Make Payment ---")

    auction_id = input("Auction ID: ").strip()

    auction = db.fetch_one("""
        SELECT currentHighestBid, buyerLogin, auctionStatus
        FROM Auction
        WHERE auctionID = %s;
    """, (auction_id,))

    if auction is None:
        print("Auction not found.")
        return

    amount, winner_login, auction_status = auction

    if winner_login is None or winner_login.strip() != buyer_login:
        print("You are not the winner of this auction.")
        return

    if auction_status != "closed":
        print("Auction must be closed before payment.")
        return

    payment_id = make_id("PAY", 30)

    query = """
        INSERT INTO Payment
        (paymentID, amount, paymentStatus, buyerLogin, auctionID)
        VALUES (%s, %s, 'completed', %s, %s);
    """

    success = db.execute_update(query, (payment_id, amount, buyer_login, auction_id))

    if success:
        print("Payment completed.")
        print("Payment ID:", payment_id)