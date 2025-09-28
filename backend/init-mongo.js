// MongoDB initialization script
db = db.getSiblingDB("market_data");

// Create collections
db.createCollection("market_data");
db.createCollection("data_requests");
db.createCollection("data_quality");

// Create indexes
db.market_data.createIndex({ symbol: 1, date: 1 }, { unique: true });
db.market_data.createIndex({ symbol: 1 });
db.market_data.createIndex({ date: 1 });
db.market_data.createIndex({ created_at: 1 });

db.data_requests.createIndex({ symbol: 1 });
db.data_requests.createIndex({ status: 1 });
db.data_requests.createIndex({ requested_at: 1 });

db.data_quality.createIndex({ symbol: 1 });
db.data_quality.createIndex({ quality_score: 1 });
db.data_quality.createIndex({ analyzed_at: 1 });

print("Database initialized successfully");
