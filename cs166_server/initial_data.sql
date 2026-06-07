-- Users
INSERT INTO "User" (login, phoneNum, role, password, address, favoriteCategory)
VALUES 
    ('buyer01', '0123456789', 'Buyer',  '0123', '123 Buyer St', 'Electronics'),
    ('seller01', '0123456789', 'Seller', '1234', '456 Seller Ave', 'Electronics');

-- Item (owned by seller01)
INSERT INTO Item (itemID, itemName, category, imageURL, condition, startingPrice, description, sellerLogin)
VALUES 
    ('ITEM000000000000001', 'Vintage Guitar', 'Music', 'https://www.musicstreet.co.uk/cdn/shop/articles/7f25b1c1-8a87-4dac-935b-7f39a66494d0_backup.webp?v=1774127658', 'available', 50.00, 'A beautiful vintage acoustic guitar from the 1970s.', 'seller01');

-- Auction for that item
INSERT INTO Auction (auctionID, auctionStatus, currentHighestBid, sellerLogin, itemID, buyerLogin)
VALUES 
    ('AUC000000000001', 'active', 50.00, 'seller01', 'ITEM000000000000001', NULL);