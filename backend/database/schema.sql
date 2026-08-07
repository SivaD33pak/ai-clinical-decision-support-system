-- ========================================================
-- AI Clinical Decision Support System (AI-CDSS)
-- Supabase PostgreSQL Database Schema
-- Phase 1 - Project Foundation
-- ========================================================

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- 1. Users Table
CREATE TABLE IF NOT EXISTS public.users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email TEXT UNIQUE NOT NULL,
    name TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);

-- 2. Predictions Table
CREATE TABLE IF NOT EXISTS public.predictions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES public.users(id) ON DELETE CASCADE,
    module TEXT NOT NULL CHECK (module IN ('XRAY', 'BLOOD', 'SYMPTOMS')),
    disease TEXT NOT NULL,
    confidence NUMERIC(5, 4) NOT NULL,
    image_url TEXT,
    heatmap_url TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);

-- Index for user prediction history lookup
CREATE INDEX IF NOT EXISTS idx_predictions_user_id ON public.predictions(user_id);
CREATE INDEX IF NOT EXISTS idx_predictions_module ON public.predictions(module);

-- Enable Row Level Security (RLS)
ALTER TABLE public.users ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.predictions ENABLE ROW LEVEL SECURITY;

-- Note for Supabase Storage Buckets:
-- Storage Bucket Name: xray-images (Public or Private depending on security needs)
-- Future Storage Bucket: heatmaps
