-- ============================================================================
-- INITIAL CRYPTOCURRENCY METADATA
-- ============================================================================

INSERT INTO crypto_metadata (crypto_id, symbol, name, category, description) VALUES
('bitcoin', 'BTC', 'Bitcoin', 'Layer 1', 'The first and most well-known cryptocurrency'),
('ethereum', 'ETH', 'Ethereum', 'Layer 1', 'Decentralized platform for smart contracts'),
('cardano', 'ADA', 'Cardano', 'Layer 1', 'Proof-of-stake blockchain platform'),
('solana', 'SOL', 'Solana', 'Layer 1', 'High-performance blockchain for dApps'),
('polkadot', 'DOT', 'Polkadot', 'Layer 0', 'Multi-chain protocol for blockchain interoperability'),
('ripple', 'XRP', 'XRP', 'Payment', 'Digital payment protocol and cryptocurrency'),
('dogecoin', 'DOGE', 'Dogecoin', 'Meme', 'Cryptocurrency based on the Doge meme'),
('avalanche-2', 'AVAX', 'Avalanche', 'Layer 1', 'Platform for decentralized applications'),
('chainlink', 'LINK', 'Chainlink', 'Oracle', 'Decentralized oracle network'),
('polygon', 'MATIC', 'Polygon', 'Layer 2', 'Ethereum scaling solution')
ON CONFLICT (crypto_id) DO UPDATE SET
    symbol = EXCLUDED.symbol,
    name = EXCLUDED.name,
    category = EXCLUDED.category,
    description = EXCLUDED.description;