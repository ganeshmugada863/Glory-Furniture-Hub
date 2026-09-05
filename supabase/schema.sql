-- ====================================================================
-- GLORY FURNITURE HUB — SUPABASE DATABASE SCHEMA & RLS POLICIES
-- ====================================================================

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- --------------------------------------------------------------------
-- 1. PROFILES TABLE (Linked to Supabase Auth)
-- --------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS public.profiles (
    id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
    full_name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    phone TEXT,
    role TEXT NOT NULL DEFAULT 'customer' CHECK (role IN ('customer', 'admin')),
    avatar_url TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);

-- --------------------------------------------------------------------
-- 2. PRODUCTS TABLE
-- --------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS public.products (
    id BIGSERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    category TEXT NOT NULL,
    room_type TEXT NOT NULL,
    price NUMERIC(10, 2) NOT NULL,
    in_stock BOOLEAN DEFAULT true,
    rating NUMERIC(3, 2) DEFAULT 5.0,
    review_count INTEGER DEFAULT 0,
    material TEXT NOT NULL,
    style TEXT NOT NULL,
    dimensions TEXT NOT NULL,
    lead_time TEXT NOT NULL,
    description TEXT NOT NULL,
    finishes TEXT[] DEFAULT '{}',
    images TEXT[] DEFAULT '{}',
    featured BOOLEAN DEFAULT false,
    new_arrival BOOLEAN DEFAULT false,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);

-- --------------------------------------------------------------------
-- 3. WISHLISTS TABLE
-- --------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS public.wishlists (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES public.profiles(id) ON DELETE CASCADE,
    product_id BIGINT NOT NULL REFERENCES public.products(id) ON DELETE CASCADE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL,
    UNIQUE(user_id, product_id)
);

-- --------------------------------------------------------------------
-- 4. BOOKINGS TABLE
-- --------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS public.bookings (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    reference_id TEXT UNIQUE NOT NULL,
    user_id UUID REFERENCES public.profiles(id) ON DELETE SET NULL,
    product_id BIGINT REFERENCES public.products(id) ON DELETE SET NULL,
    product_name TEXT NOT NULL,
    image_url TEXT,
    price NUMERIC(10, 2) NOT NULL,
    quantity INTEGER NOT NULL DEFAULT 1,
    finish TEXT,
    status TEXT NOT NULL DEFAULT 'Pending' CHECK (status IN ('Pending', 'Confirmed', 'In Production', 'Delivered', 'Cancelled')),
    delivery_date DATE NOT NULL,
    delivery_address TEXT NOT NULL,
    customization_notes TEXT,
    special_instructions TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);

-- --------------------------------------------------------------------
-- 5. CUSTOM FURNITURE REQUESTS TABLE
-- --------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS public.custom_requests (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    reference_id TEXT UNIQUE NOT NULL,
    user_id UUID REFERENCES public.profiles(id) ON DELETE SET NULL,
    furniture_type TEXT NOT NULL,
    room TEXT NOT NULL,
    dimensions TEXT NOT NULL,
    wood TEXT NOT NULL,
    finish TEXT,
    style TEXT NOT NULL,
    budget TEXT NOT NULL,
    required_date DATE,
    contact_name TEXT NOT NULL,
    contact_phone TEXT NOT NULL,
    reference_images TEXT[] DEFAULT '{}',
    status TEXT NOT NULL DEFAULT 'Under Review' CHECK (status IN ('Under Review', 'Quoted', 'In Production', 'Completed', 'Rejected')),
    description TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);

-- --------------------------------------------------------------------
-- 6. NOTIFICATIONS TABLE
-- --------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS public.notifications (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES public.profiles(id) ON DELETE CASCADE,
    title TEXT NOT NULL,
    description TEXT NOT NULL,
    type TEXT NOT NULL CHECK (type IN ('booking', 'request', 'system', 'promo')),
    target_id TEXT,
    is_read BOOLEAN DEFAULT false,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);

-- --------------------------------------------------------------------
-- 7. AI CHAT MESSAGES TABLE
-- --------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS public.ai_chat_messages (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES public.profiles(id) ON DELETE CASCADE,
    sender TEXT NOT NULL CHECK (sender IN ('user', 'ai')),
    text TEXT NOT NULL,
    product_id BIGINT REFERENCES public.products(id) ON DELETE SET NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);

-- ====================================================================
-- ROW-LEVEL SECURITY (RLS) POLICIES
-- ====================================================================

-- Enable RLS on all tables
ALTER TABLE public.profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.products ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.wishlists ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.bookings ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.custom_requests ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.notifications ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.ai_chat_messages ENABLE ROW LEVEL SECURITY;

-- Helper function to check if current user is Admin
CREATE OR REPLACE FUNCTION public.is_admin()
RETURNS BOOLEAN AS $$
BEGIN
  RETURN EXISTS (
    SELECT 1 FROM public.profiles
    WHERE id = auth.uid() AND role = 'admin'
  );
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- --- Profiles Policies ---
DROP POLICY IF EXISTS "Public profiles are viewable by owner and admin" ON public.profiles;
CREATE POLICY "Public profiles are viewable by owner and admin" 
ON public.profiles FOR SELECT 
USING (auth.uid() = id OR public.is_admin());

DROP POLICY IF EXISTS "Users can update own profile" ON public.profiles;
CREATE POLICY "Users can update own profile" 
ON public.profiles FOR UPDATE 
USING (auth.uid() = id);

-- --- Products Policies ---
DROP POLICY IF EXISTS "Products are viewable by everyone" ON public.products;
CREATE POLICY "Products are viewable by everyone" 
ON public.products FOR SELECT 
USING (true);

DROP POLICY IF EXISTS "Only admins can insert products" ON public.products;
CREATE POLICY "Allow insert products" 
ON public.products FOR INSERT 
WITH CHECK (true);

DROP POLICY IF EXISTS "Only admins can update products" ON public.products;
CREATE POLICY "Allow update products" 
ON public.products FOR UPDATE 
USING (true);

DROP POLICY IF EXISTS "Only admins can delete products" ON public.products;
CREATE POLICY "Allow delete products" 
ON public.products FOR DELETE 
USING (true);

-- --- Wishlist Policies ---
DROP POLICY IF EXISTS "Users can view own wishlist" ON public.wishlists;
CREATE POLICY "Users can view own wishlist" 
ON public.wishlists FOR SELECT 
USING (auth.uid() = user_id);

DROP POLICY IF EXISTS "Users can insert into own wishlist" ON public.wishlists;
CREATE POLICY "Users can insert into own wishlist" 
ON public.wishlists FOR INSERT 
WITH CHECK (auth.uid() = user_id);

DROP POLICY IF EXISTS "Users can delete from own wishlist" ON public.wishlists;
CREATE POLICY "Users can delete from own wishlist" 
ON public.wishlists FOR DELETE 
USING (auth.uid() = user_id);

-- --- Bookings Policies ---
DROP POLICY IF EXISTS "Users can view own bookings or admin views all" ON public.bookings;
CREATE POLICY "Users can view own bookings or admin views all" 
ON public.bookings FOR SELECT 
USING (auth.uid() = user_id OR public.is_admin());

DROP POLICY IF EXISTS "Authenticated users can create bookings" ON public.bookings;
CREATE POLICY "Authenticated users can create bookings" 
ON public.bookings FOR INSERT 
WITH CHECK (auth.role() = 'authenticated');

DROP POLICY IF EXISTS "Users can update pending bookings or admin updates all" ON public.bookings;
CREATE POLICY "Users can update pending bookings or admin updates all" 
ON public.bookings FOR UPDATE 
USING (auth.uid() = user_id OR public.is_admin());

-- --- Custom Requests Policies ---
DROP POLICY IF EXISTS "Users can view own requests or admin views all" ON public.custom_requests;
CREATE POLICY "Users can view own requests or admin views all" 
ON public.custom_requests FOR SELECT 
USING (auth.uid() = user_id OR public.is_admin());

DROP POLICY IF EXISTS "Authenticated users can create requests" ON public.custom_requests;
CREATE POLICY "Authenticated users can create requests" 
ON public.custom_requests FOR INSERT 
WITH CHECK (auth.role() = 'authenticated');

DROP POLICY IF EXISTS "Admins can update request status" ON public.custom_requests;
CREATE POLICY "Admins can update request status" 
ON public.custom_requests FOR UPDATE 
USING (public.is_admin());

-- --- Notifications Policies ---
DROP POLICY IF EXISTS "Users can view own notifications" ON public.notifications;
CREATE POLICY "Users can view own notifications" 
ON public.notifications FOR SELECT 
USING (auth.uid() = user_id);

DROP POLICY IF EXISTS "Users can update own notifications" ON public.notifications;
CREATE POLICY "Users can update own notifications" 
ON public.notifications FOR UPDATE 
USING (auth.uid() = user_id);

-- --- AI Chat Messages Policies ---
DROP POLICY IF EXISTS "Users can view own chat messages" ON public.ai_chat_messages;
CREATE POLICY "Users can view own chat messages" 
ON public.ai_chat_messages FOR SELECT 
USING (auth.uid() = user_id);

DROP POLICY IF EXISTS "Users can insert into own chat messages" ON public.ai_chat_messages;
CREATE POLICY "Users can insert into own chat messages" 
ON public.ai_chat_messages FOR INSERT 
WITH CHECK (auth.uid() = user_id);

-- ====================================================================
-- STORAGE BUCKETS CONFIGURATION (Product & Reference Images)
-- ====================================================================
INSERT INTO storage.buckets (id, name, public) VALUES ('product-images', 'product-images', true) ON CONFLICT DO NOTHING;
INSERT INTO storage.buckets (id, name, public) VALUES ('custom-references', 'custom-references', true) ON CONFLICT DO NOTHING;
INSERT INTO storage.buckets (id, name, public) VALUES ('avatars', 'avatars', true) ON CONFLICT DO NOTHING;

DROP POLICY IF EXISTS "Public storage read" ON storage.objects;
CREATE POLICY "Public storage read" ON storage.objects FOR SELECT USING (true);

DROP POLICY IF EXISTS "Authenticated storage upload" ON storage.objects;
DROP POLICY IF EXISTS "Allow public storage upload" ON storage.objects;
CREATE POLICY "Allow public storage upload" ON storage.objects FOR INSERT WITH CHECK (true);

DROP POLICY IF EXISTS "Allow update storage objects" ON storage.objects;
CREATE POLICY "Allow update storage objects" ON storage.objects FOR UPDATE USING (true);
