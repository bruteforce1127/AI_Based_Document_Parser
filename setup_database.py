"""
Database Setup Script - Run this once to create tables in Supabase
"""
import requests
import config

# Supabase REST API endpoint for SQL
SUPABASE_REST_URL = f"{config.SUPABASE_URL}/rest/v1/rpc"

# SQL statements to create tables (executed via Supabase Management API)
# Note: We need to use the Supabase client to create tables

from supabase import create_client

supabase = create_client(config.SUPABASE_URL, config.SUPABASE_KEY)

print("Setting up ClarityVault database...")
print(f"Supabase URL: {config.SUPABASE_URL}")

# Test connection by trying a simple query
try:
    # Try to select from users table to see if it exists
    result = supabase.table('users').select('id').limit(1).execute()
    print("✅ 'users' table already exists!")
except Exception as e:
    print(f"⚠️  Tables may not exist yet: {e}")
    print("\n" + "="*60)
    print("MANUAL STEP REQUIRED:")
    print("="*60)
    print("\nPlease run this SQL in Supabase Dashboard -> SQL Editor:\n")
    
    sql = '''
-- Users table
CREATE TABLE IF NOT EXISTS users (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Documents table
CREATE TABLE IF NOT EXISTS documents (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    filename VARCHAR(500) NOT NULL,
    document_type VARCHAR(100),
    content TEXT,
    pages_count INTEGER DEFAULT 1,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Analyses table
CREATE TABLE IF NOT EXISTS analyses (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    document_id UUID REFERENCES documents(id) ON DELETE CASCADE,
    analysis_type VARCHAR(50) NOT NULL,
    result JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Enable RLS and create policies
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE documents ENABLE ROW LEVEL SECURITY;
ALTER TABLE analyses ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Allow all for users" ON users FOR ALL USING (true);
CREATE POLICY "Allow all for documents" ON documents FOR ALL USING (true);
CREATE POLICY "Allow all for analyses" ON analyses FOR ALL USING (true);
'''
    print(sql)

print("\nTesting table access...")

# Test each table
tables = ['users', 'documents', 'analyses']
for table in tables:
    try:
        result = supabase.table(table).select('*').limit(1).execute()
        print(f"✅ '{table}' table is accessible")
    except Exception as e:
        print(f"❌ '{table}' table error: {e}")

print("\nSetup check complete!")
