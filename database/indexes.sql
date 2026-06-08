DROP INDEX IF EXISTS auction_status_idx;
DROP INDEX IF EXISTS auction_seller_idx;
DROP INDEX IF EXISTS auction_buyer_idx;
DROP INDEX IF EXISTS auction_item_idx;

DROP INDEX IF EXISTS item_seller_idx;
DROP INDEX IF EXISTS item_category_idx;

DROP INDEX IF EXISTS bid_auction_idx;
DROP INDEX IF EXISTS bid_buyer_idx;
DROP INDEX IF EXISTS bid_auction_amount_idx;

DROP INDEX IF EXISTS payment_buyer_idx;

DROP INDEX IF EXISTS shipment_status_idx;


CREATE INDEX auction_status_idx ON Auction USING BTREE (auctionStatus);
CREATE INDEX auction_seller_idx ON Auction USING BTREE (sellerLogin);
CREATE INDEX auction_buyer_idx ON Auction USING BTREE (buyerLogin);
CREATE INDEX auction_item_idx ON Auction USING BTREE (itemID);

CREATE INDEX item_seller_idx ON Item USING BTREE (sellerLogin);
CREATE INDEX item_category_idx ON Item USING BTREE (category);

CREATE INDEX bid_auction_idx ON Bid USING BTREE (auctionID);
CREATE INDEX bid_buyer_idx ON Bid USING BTREE (buyerLogin);
CREATE INDEX bid_auction_amount_idx ON Bid USING BTREE (auctionID, bidAmount);

CREATE INDEX payment_buyer_idx ON Payment USING BTREE (buyerLogin);

CREATE INDEX shipment_status_idx ON Shipment USING BTREE (shipmentStatus);