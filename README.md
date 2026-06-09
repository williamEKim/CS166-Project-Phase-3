# CS166 Project eBay DB Setup
PostgreSQL setup scripts for the CS166 eBay project. Works on Mac, Linux, and Windows.

## Requirements
- PostgreSQL 16+
- Python 3.6+
- Mac: [Homebrew](https://brew.sh)
- Windows: [winget](https://learn.microsoft.com/en-us/windows/package-manager/winget/)

## Files
| File | Description |
|------|-------------|
| `Ebay_DB.sh` / `.bat` | Initializes the DB, installs dependencies, and launches the Flask web GUI |
| `backend/GUI.py` | Flask web application — main entry point for the GUI |
| `backend/main.py` | Original terminal-based interface (legacy) |
| `cs166_server/create_tables.sql` | Schema definition |
| `cs166_server/indexes.sql` | Performance indexes |
| `cs166_server/initial_data.sql` | Seed data |

## Usage

### Mac / Linux
```bash
# Initiate DB, install dependencies, and launch the Flask GUI
source eBay_DB.sh 
```

### Windows
```bat
:: Initiate DB, install dependencies, and launch the Flask GUI
eBay_DB.bat
```

### Accessing the GUI
The Flask app runs on the school server. Access it via SSH port forwarding from your local machine (you cannot directly access localhost unless you do forwarding):
```bash
ssh -L 5000:localhost:5000 <user>@cs166.cs.ucr.edu
# Then open: http://localhost:5000
```

## User Roles
| Role | Description |
|------|-------------|
| `Buyer` | Default role on registration. Can browse, search, bid, pay, and view order history |
| `Seller` | Granted by Admin. Can create and manage item listings, end auctions, and create shipments |
| `Admin` | Can manage all users, items, payments, and shipments across the platform |

New accounts always register as **Buyer**. An Admin must promote a user to Seller or Admin via the admin panel.

## Database Schema

### User
| Column | Type | Constraint |
|--------|------|------------|
| `login` | TEXT | PK, NOT NULL |
| `phoneNum` | CHAR(20) | |
| `role` | TEXT | NOT NULL, IN ('Buyer', 'Seller', 'Admin') |
| `password` | TEXT | NOT NULL |
| `address` | TEXT | |
| `favoriteCategory` | TEXT | |

### Item
| Column | Type | Constraint |
|--------|------|------------|
| `itemId` | CHAR(20) | PK, NOT NULL |
| `itemName` | TEXT | NOT NULL |
| `category` | TEXT | |
| `imageURL` | TEXT | |
| `condition` | itemCondition | NOT NULL |
| `startingPrice` | FLOAT | NOT NULL |
| `description` | TEXT | |
| `sellerLogin` | TEXT | FK → User.login (Manages) |

### Auction
| Column | Type | Constraint |
|--------|------|------------|
| `auctionId` | CHAR(30) | PK, NOT NULL |
| `auctionStatus` | aStatus | NOT NULL |
| `currentHighestBid` | FLOAT | |
| `sellerLogin` | TEXT | FK → User.login (Creates) |
| `itemId` | CHAR(20) | FK → Item.itemId (Listed In) |
| `buyerLogin` | TEXT | FK → User.login (Wins) |

### Payment
| Column | Type | Constraint |
|--------|------|------------|
| `paymentId` | CHAR(30) | PK, NOT NULL |
| `amount` | FLOAT | NOT NULL |
| `paymentStatus` | pStatus | NOT NULL |
| `buyerLogin` | TEXT | FK → User.login (Makes) |
| `auctionId` | CHAR(30) | FK → Auction.auctionId (Has), UNIQUE |

### Shipment
| Column | Type | Constraint |
|--------|------|------------|
| `shipmentId` | CHAR(30) | PK, NOT NULL |
| `address` | TEXT | NOT NULL |
| `shipmentStatus` | sStatus | NOT NULL |
| `trackingNumber` | NUMERIC(10,0) | |
| `auctionId` | CHAR(30) | FK → Auction.auctionId (Has), UNIQUE |

### Bid
| Column | Type | Constraint |
|--------|------|------------|
| `bidId` | CHAR(30) | PK, NOT NULL |
| `bidAmount` | FLOAT | NOT NULL |
| `bidTimestamp` | TIMESTAMP | NOT NULL |
| `buyerLogin` | TEXT | FK → User.login (Places) |
| `auctionId` | CHAR(30) | FK → Auction.auctionId (Receives) |

### ENUM Types
| Type | Values |
|------|--------|
| `itemCondition` | `available`, `sold`, `removed` |
| `aStatus` | `active`, `closed`, `cancelled` |
| `pStatus` | `pending`, `completed`, `failed` |
| `sStatus` | `pending`, `shipped`, `delivered` |

## Project Structure
```
CS166-Project-Phase-3/
├── backend/
│   ├── GUI.py            # Flask web application
│   ├── main.py           # Original terminal interface (legacy)
│   ├── actions.py        # Shared DB actions (login, browse, search, profile)
│   ├── buyer.py          # Buyer-specific actions (bid, payment)
│   ├── seller.py         # Seller-specific actions (listing, shipment)
│   └── EmbeddedSQL.py    # PostgreSQL connection wrapper
├── cs166_server/
│   ├── create_tables.sql
│   ├── indexes.sql
│   ├── initial_data.sql
│   ├── createPostgreDB.sh
│   ├── startPostgreSQL.sh
│   ├── stopPostgreDB.sh
│   ├── psql.sh / psql.bat
├── database/
├── .gitignore
├── eBay_DB.sh
├── eBay_DB.bat
├── requirements.txt
└── README.md
```

## Notes
- The database is initialized at `~/myDB/data` (Mac/Linux) or `%USERPROFILE%\myDB\data` (Windows)
- The database is named `<yourUsername>_eBay_DB`
- The GUI requires an active SSH tunnel to access from a local browser when running on a remote server
