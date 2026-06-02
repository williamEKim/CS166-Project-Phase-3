-- Drop tables if they exist
DROP TABLE IF EXISTS Bid;
DROP TABLE IF EXISTS Payment;
DROP TABLE IF EXISTS Shipment;
DROP TABLE IF EXISTS Auction;
DROP TABLE IF EXISTS Item;
DROP TABLE IF EXISTS "User";    -- it is because User is a reserved keyword


-- Drop types if they exist
DROP TYPE IF EXISTS itemCondition;
DROP TYPE IF EXISTS pStatus;
DROP TYPE IF EXISTS sStatus;
DROP TYPE IF EXISTS aStatus;


-- should we make a category as an enumeration?
CREATE TYPE itemCondition AS ENUM ('available', 'sold', 'removed'); --should this be like mint, lightly used, damaged, etc?
CREATE TYPE pStatus AS ENUM ('pending', 'completed', 'failed');
CREATE TYPE sStatus AS ENUM ('pending', 'shipped', 'delivered');
CREATE TYPE aStatus AS ENUM ('active', 'closed', 'cancelled');




CREATE TABLE "User" (
    login            TEXT NOT NULL PRIMARY KEY,    
    phoneNum         CHAR(20),
    role             TEXT NOT NULL CHECK (      
        role IN ('Seller', 'Buyer')
    ),                                  -- enforce user role to be either Seller or Buyer
    password         TEXT NOT NULL,
    address          TEXT,
    favoriteCategory TEXT
);


CREATE TABLE Item (
    itemID          CHAR(20) NOT NULL PRIMARY KEY,  
    itemName        TEXT NOT NULL,
    category        TEXT,
    imageURL        TEXT,
    condition       itemCondition NOT NULL,
    startingPrice   FLOAT NOT NULL,
    description     TEXT NOT NULL,


    -- (RELATIONSHIP) Manages: item need to be managed by one Seller (cannot enforce to be a Seller)
    sellerLogin     TEXT NOT NULL,
    CONSTRAINT fk_manages FOREIGN KEY (sellerLogin) REFERENCES "User"(login)
);


CREATE TABLE Auction (
    auctionID           CHAR(30) NOT NULL PRIMARY KEY,  
    auctionStatus       aStatus NOT NULL,
    currentHighestBid   FLOAT,


    -- (RELATIONSHIP) Creates: Auction must have a Creater (cannot enforce to be a Seller)
    sellerLogin     TEXT NOT NULL,
    CONSTRAINT fk_creates FOREIGN KEY (sellerLogin) REFERENCES "User"(login),


    -- (RELATIONSHIP) Listed In: item can be listed in an Auction
    itemID     CHAR(20) NOT NULL,
    CONSTRAINT fk_listed_in FOREIGN KEY (itemID) REFERENCES Item(itemID),


    -- (RELATIONSHIP) Wins: Auction can have a Winner (cannot enforce to be a Buyer)
    buyerLogin     TEXT,
    CONSTRAINT fk_wins FOREIGN KEY (buyerLogin) REFERENCES "User"(login)
);


CREATE TABLE Payment (
    paymentID       CHAR(30) NOT NULL PRIMARY KEY,  
    amount          FLOAT NOT NULL,
    paymentStatus   pStatus NOT NULL,


    -- (RELATIONSHIP) Makes: Payment need to be made by a Buyer (cannot enforce to be a Buyer)
    buyerLogin     TEXT NOT NULL,
    CONSTRAINT fk_makes FOREIGN KEY (buyerLogin) REFERENCES "User"(login),


    -- (RELATIONSHIP) Has: Auction can have a Payment
    auctionID     CHAR(30) NOT NULL UNIQUE,
    CONSTRAINT fk_payment_auction FOREIGN KEY (auctionID) REFERENCES Auction(auctionID)
);


CREATE TABLE Shipment (
    ShipmentID      CHAR(30) NOT NULL PRIMARY KEY,  
    address         TEXT NOT NULL,
    shipmentStatus  sStatus NOT NULL,
    trackingNumber  NUMERIC (10, 0),


    -- (RELATIONSHIP) Has: Auction can have a shipment (whereas shipment need to be under an Auction)
    auctionID     CHAR(30) NOT NULL UNIQUE,
    CONSTRAINT fk_shipment_auction FOREIGN KEY (auctionID) REFERENCES Auction(auctionID)
);


CREATE TABLE Bid (
    bidId           CHAR(30) NOT NULL PRIMARY KEY,  
    bidAmount       FLOAT NOT NULL,
    bidTimestamp    TIMESTAMP NOT NULL,


    -- (RELATIONSHIP) Places: Bid must be made by a Buyer (cannot enforce to be a Buyer)
    buyerLogin     TEXT NOT NULL,
    CONSTRAINT fk_places FOREIGN KEY (buyerLogin) REFERENCES "User"(login),


    -- (RELATIONSHIP) Receives: Bid must be received by an Auction
    auctionID     CHAR(30) NOT NULL,
    CONSTRAINT fk_receives FOREIGN KEY (auctionID) REFERENCES Auction(auctionID)
);
