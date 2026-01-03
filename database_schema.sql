-- ClarityVault Database Schema
-- Run this SQL in your Supabase SQL Editor (Dashboard -> SQL Editor -> New Query)

-- Users table
CREATE TABLE IF NOT EXISTS users (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc', NOW())
);

-- Documents table
CREATE TABLE IF NOT EXISTS documents (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    filename VARCHAR(500) NOT NULL,
    document_type VARCHAR(100),
    content TEXT,
    pages_count INTEGER DEFAULT 1,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc', NOW())
);

-- Analyses table (for caching analysis results)
CREATE TABLE IF NOT EXISTS analyses (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    document_id UUID REFERENCES documents(id) ON DELETE CASCADE,
    analysis_type VARCHAR(50) NOT NULL,
    result JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc', NOW()),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc', NOW())
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_documents_user_id ON documents(user_id);
CREATE INDEX IF NOT EXISTS idx_analyses_document_id ON analyses(document_id);

-- Enable Row Level Security (RLS) - IMPORTANT for Supabase
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE documents ENABLE ROW LEVEL SECURITY;
ALTER TABLE analyses ENABLE ROW LEVEL SECURITY;

-- Create policies to allow access (since we handle auth in our app)
CREATE POLICY "Enable all operations for users table" ON users FOR ALL USING (true) WITH CHECK (true);
CREATE POLICY "Enable all operations for documents table" ON documents FOR ALL USING (true) WITH CHECK (true);
CREATE POLICY "Enable all operations for analyses table" ON analyses FOR ALL USING (true) WITH CHECK (true);
