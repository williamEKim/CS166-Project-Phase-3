# CS166 Project eBay DB Setup

PostgreSQL setup scripts for the CS166 eBay project. Works on Mac, Linux, and Windows.

## Requirements

- PostgreSQL 16+
- Mac: [Homebrew](https://brew.sh)
- Windows: [winget](https://learn.microsoft.com/en-us/windows/package-manager/winget/)

## Files

| File | Description |
|------|-------------|
| `Ebay_DB.sh` / `.bat` | Runs the Python Script that executes all required SQL scripts and shows GUI(to be implemented) |

## Usage

### Mac / Linux

```bash
# 1. Initiate DB and runs SQL script, then run the Python Script to execute the GUI
Ebay_DB.sh
```

### Windows

```bat
:: 1. Initiate DB and runs SQL script, then run the Python Script to execute the GUI
Ebay_DB.bat
```

## Database Schema
 
### User
| Column | Type | Constraint |
|--------|------|------------|
| `login` | TEXT | PK, NOT NULL |
| `phoneNum` | CHAR(20) | |
| `role` | TEXT | NOT NULL, IN ('Seller', 'Buyer') |
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

## Notes

- The database is initialized at `~/myDB/data` (Mac/Linux) or `%USERPROFILE%\myDB\data` (Windows)
- The database is named `<yourUsername>_eBay_DB`
