import os
import getpass

from EmbeddedSQL import *
from actions import *
from buyer import *
from seller import *

def buyer_menu(db, login):
    while True:
        print("""
        ==============================
        Buyer Menu
        ==============================
        1. Browse active auctions
        2. Search auctions
        3. Place bid
        4. View my bids
        5. View auctions I won
        6. Make payment
        7. View profile
        8. Edit profile
        0. Logout
        """)

        choice = input("Choose option: ").strip()

        if choice == "1":
            browse_active_auctions(db)
        elif choice == "2":
            search_auctions(db)
        elif choice == "3":
            place_bid(db, login)
        elif choice == "4":
            view_my_bids(db, login)
        elif choice == "5":
            view_won_auctions(db, login)
        elif choice == "6":
            make_payment(db, login)
        elif choice == "7":
            view_profile(db, login)
        elif choice == "8":
            edit_profile(db, login)
        elif choice == "0":
            break
        else:
            print("Invalid option.")


def seller_menu(db, login):
    while True:
        print("""
        ==============================
        Seller Menu
        ==============================
        1. Browse active auctions
        2. Search auctions
        3. Place bid
        4. View profile
        5. Edit profile
        6. Create item and auction
        7. View my items
        8. View my auctions
        9. End one of my auctions
        10. Create shipment
        0. Logout
        """)

        choice = input("Choose option: ").strip()

        if choice == "1":
            browse_active_auctions(db)
        elif choice == "2":
            search_auctions(db)
        elif choice == "3":
            place_bid(db, login)
        elif choice == "4":
            view_profile(db, login)
        elif choice == "5":
            edit_profile(db, login)
        elif choice == "6":
            create_item_and_auction(db, login)
        elif choice == "7":
            view_my_items(db, login)
        elif choice == "8":
            view_my_auctions(db, login)
        elif choice == "9":
            end_auction(db, login)
        elif choice == "10":
            create_shipment(db, login)
        elif choice == "0":
            break
        else:
            print("Invalid option.")


def main():
    if len(sys.argv) != 4:
        print(
            f"Usage: python {sys.argv[0]} <dbname> <port> <user>",
            file=sys.stderr
        )
        return

    dbname = sys.argv[1]
    dbport = sys.argv[2]
    user   = sys.argv[3]

    db = EmbeddedSQL(dbname, dbport, user, "")

    while True:
        print("""
        ==============================
        eBay DB Interface - Main Menu
        ==============================
        1. Login
        2. Register new Buyer
        3. Register new Seller
        0. Exit
        """)

        choice = input("Choose option: ").strip()

        if choice == "1":
            login, role = login_user(db)

            if login is not None:
                if role == "Buyer":
                    buyer_menu(db, login)
                elif role == "Seller":
                    seller_menu(db, login)
                else:
                    print("Unknown role:", role)

        elif choice == "2":
            register_user(db)
            
        elif choice == "3":
            register_seller(db)
            
        elif choice == "0":
            db.cleanup()
            print("Goodbye.")
            break

        else:
            print("Invalid option.")


if __name__ == "__main__":
    main()