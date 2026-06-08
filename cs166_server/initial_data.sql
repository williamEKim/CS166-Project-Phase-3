-- Update role constraint to allow Admin
ALTER TABLE "User" DROP CONSTRAINT IF EXISTS "User_role_check";
ALTER TABLE "User" ADD CONSTRAINT "User_role_check"
    CHECK (role IN ('Buyer', 'Seller', 'Admin'));

-- Users
INSERT INTO "User" (login, phoneNum, role, password, address, favoriteCategory)
VALUES
    ('admin',    '0000000000', 'Admin',  'admin123', 'Admin HQ',        NULL),
    ('buyer01',  '0123456789', 'Buyer',  '0123',     '123 Buyer St',    'Electronics'),
    ('buyer02',  '0987654321', 'Buyer',  '0123',     '456 Buyer Ave',   'Music'),
    ('seller01', '0123456789', 'Seller', '1234',     '456 Seller Ave',  'Electronics'),
    ('seller02', '1122334455', 'Seller', '1234',     '789 Seller Blvd', 'Music');

-- Items
INSERT INTO Item (itemID, itemName, category, imageURL, condition, startingPrice, description, sellerLogin)
VALUES
    ('ITEM000000000000001', 'Vintage Guitar',    'Music',       'https://www.musicstreet.co.uk/cdn/shop/articles/7f25b1c1-8a87-4dac-935b-7f39a66494d0_backup.webp?v=1774127658', 'available', 50.00,  'A beautiful vintage acoustic guitar from the 1970s.', 'seller01'),
    ('ITEM000000000000002', 'Mechanical Keyboard','Electronics', '', 'available', 80.00,  'Cherry MX Blue switches, TKL layout, barely used.', 'seller01'),
    ('ITEM000000000000003', 'Vinyl Record Set',  'Music',       '', 'available', 30.00,  'Collection of 10 classic jazz vinyl records from the 1960s.', 'seller02'),
    ('ITEM000000000000004', 'Retro Camera',      'Electronics', '', 'available', 120.00, 'Film SLR camera in excellent working condition.', 'seller02');

-- Auctions
INSERT INTO Auction (auctionID, auctionStatus, currentHighestBid, sellerLogin, itemID, buyerLogin)
VALUES
    ('AUC000000000001', 'active', 50.00,  'seller01', 'ITEM000000000000001', NULL),
    ('AUC000000000002', 'active', 80.00,  'seller01', 'ITEM000000000000002', NULL),
    ('AUC000000000003', 'active', 30.00,  'seller02', 'ITEM000000000000003', NULL),
    ('AUC000000000004', 'active', 120.00, 'seller02', 'ITEM000000000000004', NULL);