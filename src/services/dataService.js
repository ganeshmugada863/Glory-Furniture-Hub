import { supabase, isSupabaseConfigured } from '../lib/supabase'
import { MOCK_PRODUCTS } from '../data/mockData'

const LOCAL_PRODUCTS_KEY = 'glory_custom_products'

function getStoredLocalProducts() {
  try {
    const raw = localStorage.getItem(LOCAL_PRODUCTS_KEY)
    return raw ? JSON.parse(raw) : []
  } catch (e) {
    return []
  }
}

function saveLocalProducts(products) {
  try {
    localStorage.setItem(LOCAL_PRODUCTS_KEY, JSON.stringify(products))
  } catch (e) {
    console.warn('Failed to save to localStorage', e)
  }
}

function normalizeProduct(p) {
  if (!p) return null

  let sizeVariants = []
  if (Array.isArray(p.sizeVariants) && p.sizeVariants.length > 0) {
    sizeVariants = p.sizeVariants
  } else if (Array.isArray(p.size_variants) && p.size_variants.length > 0) {
    sizeVariants = p.size_variants
  } else if (typeof p.size_variants === 'string') {
    try { sizeVariants = JSON.parse(p.size_variants) } catch (e) {}
  } else if (typeof p.sizeVariants === 'string') {
    try { sizeVariants = JSON.parse(p.sizeVariants) } catch (e) {}
  }

  sizeVariants = sizeVariants
    .filter(v => v && v.size)
    .map(v => ({ size: String(v.size), price: Number(v.price) || Number(p.price) || 0 }))

  const isBed = Boolean(
    p.category === 'Cot / Wooden Bed' ||
    p.category === 'Bedroom' ||
    (p.category && p.category.toLowerCase().includes('bed')) ||
    (p.category && p.category.toLowerCase().includes('cot')) ||
    (p.name && p.name.toLowerCase().includes('bed')) ||
    (p.name && p.name.toLowerCase().includes('cot'))
  )
  if (isBed && sizeVariants.length === 0 && p.price) {
    const basePrice = Number(p.price)
    sizeVariants = [
      { size: '6/6 ft (King)', price: basePrice },
      { size: '5/6 ft (Queen)', price: Math.round(basePrice * 0.88) },
      { size: '4/6 ft (Double)', price: Math.round(basePrice * 0.75) },
      { size: '3/6 ft (Single)', price: Math.round(basePrice * 0.60) }
    ]
  }

  return {
    ...p,
    id: p.id,
    name: p.name || 'Handcrafted Furniture',
    price: Number(p.price) || 0,
    category: p.category || 'Living Room',
    roomType: p.roomType || p.room_type || p.category || 'Living Room',
    material: p.material || 'Solid Wood',
    style: p.style || 'Modern Minimalist',
    dimensions: p.dimensions || 'Custom Dimensions',
    leadTime: p.leadTime || p.lead_time || '5 - 7 Days Delivery',
    description: p.description || '',
    inStock: p.inStock !== undefined ? p.inStock : (p.in_stock !== undefined ? p.in_stock : true),
    rating: Number(p.rating) || 5.0,
    reviewCount: Number(p.reviewCount || p.review_count) || 1,
    images: Array.isArray(p.images) && p.images.length > 0 
      ? p.images 
      : ['https://images.unsplash.com/photo-1555041469-a586c61ea9bc?auto=format&fit=crop&w=800&q=80'],
    finishes: Array.isArray(p.finishes) && p.finishes.length > 0 ? p.finishes : ['Natural Teak', 'Polished Walnut'],
    featured: p.featured !== undefined ? Boolean(p.featured) : true,
    newArrival: p.newArrival !== undefined ? Boolean(p.newArrival) : Boolean(p.new_arrival),
    sizeVariants: sizeVariants
  }
}

// Runtime in-memory cache for ultra-fast instant lookups
let inMemoryProductsCache = null

function getLocalOrMockProduct(id) {
  const numId = Number(id)
  const strId = String(id)

  // 1. Check local storage products
  const localProducts = getStoredLocalProducts()
  const foundLocal = localProducts.find(p => p.id === numId || String(p.id) === strId)
  if (foundLocal) return normalizeProduct(foundLocal)

  // 2. Check in-memory products cache
  if (inMemoryProductsCache) {
    const foundMem = inMemoryProductsCache.find(p => p.id === numId || String(p.id) === strId)
    if (foundMem) return normalizeProduct(foundMem)
  }

  // 3. Check mock products
  const foundMock = MOCK_PRODUCTS.find(p => p.id === numId || String(p.id) === strId)
  if (foundMock) return normalizeProduct(foundMock)

  return null
}

export const dataService = {
  // Synchronous instant lookup for 0ms page rendering
  getInstantProductById(id) {
    return getLocalOrMockProduct(id)
  },

  // Fetch All Products (Cached in memory + Supabase + Local Cache)
  async getProducts() {
    const localProducts = getStoredLocalProducts()

    // If already cached in memory, return instantly
    if (inMemoryProductsCache && inMemoryProductsCache.length > 0) {
      return { data: inMemoryProductsCache, error: null }
    }

    // Default fast baseline from local cache + mock data
    const baseline = [...localProducts, ...MOCK_PRODUCTS].map(normalizeProduct)

    if (!isSupabaseConfigured) {
      inMemoryProductsCache = baseline
      return { data: baseline, error: null }
    }

    try {
      // 1.5s timeout so slow networks or Supabase cold starts never block the UI
      const fetchPromise = supabase
        .from('products')
        .select('*')
        .order('id', { ascending: false })

      const timeoutPromise = new Promise((_, reject) =>
        setTimeout(() => reject(new Error('Supabase request timeout')), 1500)
      )

      const { data: supaData, error } = await Promise.race([fetchPromise, timeoutPromise])

      if (error || !supaData || supaData.length === 0) {
        inMemoryProductsCache = baseline
        return { data: baseline, error: null }
      }

      // Merge Supabase products with local additions and base mock products
      const supaIds = new Set(supaData.map(p => String(p.id)))
      const unSyncedLocals = localProducts.filter(lp => !supaIds.has(String(lp.id)))
      const mockRemaining = MOCK_PRODUCTS.filter(mp => !supaIds.has(String(mp.id)) && !unSyncedLocals.some(ul => String(ul.id) === String(mp.id)))
      const all = [...unSyncedLocals, ...supaData, ...mockRemaining].map(normalizeProduct)

      inMemoryProductsCache = all
      return { data: all, error: null }
    } catch (err) {
      // Fallback immediately to baseline without hanging
      inMemoryProductsCache = baseline
      return { data: baseline, error: null }
    }
  },

  // Fetch Single Product by ID (Instant Local Hit + Fast Supabase Fallback)
  async getProductById(id) {
    // 1. Instant check in local or mock data
    const instant = getLocalOrMockProduct(id)
    if (instant) {
      return { data: instant, error: null }
    }

    // 2. If not found locally, query Supabase with a 1.5s timeout
    if (isSupabaseConfigured) {
      try {
        const queryPromise = supabase
          .from('products')
          .select('*')
          .eq('id', id)
          .single()

        const timeoutPromise = new Promise((_, reject) =>
          setTimeout(() => reject(new Error('Supabase single timeout')), 1500)
        )

        const { data, error } = await Promise.race([queryPromise, timeoutPromise])

        if (!error && data) {
          const normalized = normalizeProduct(data)
          return { data: normalized, error: null }
        }
      } catch (e) {
        // Fallback below
      }
    }

    return { data: normalizeProduct(MOCK_PRODUCTS[0]), error: null }
  },

  // Create Product in Supabase & Local Cache
  async createProduct(productPayload) {
    const normalized = normalizeProduct({
      ...productPayload,
      id: productPayload.id || Date.now()
    })

    // 1. Always save to local storage cache immediately
    const existing = getStoredLocalProducts()
    saveLocalProducts([normalized, ...existing.filter(p => p.id !== normalized.id)])

    // 2. If Supabase is configured, also persist to Supabase products table
    if (isSupabaseConfigured) {
      try {
        const dbRow = {
          name: normalized.name,
          category: normalized.category,
          room_type: normalized.roomType,
          price: normalized.price,
          in_stock: normalized.inStock,
          rating: normalized.rating,
          review_count: normalized.reviewCount,
          material: normalized.material,
          style: normalized.style,
          dimensions: normalized.dimensions,
          lead_time: normalized.leadTime,
          description: normalized.description,
          finishes: normalized.finishes,
          images: normalized.images,
          featured: normalized.featured,
          new_arrival: normalized.newArrival
        }

        if (normalized.sizeVariants && normalized.sizeVariants.length > 0) {
          dbRow.size_variants = normalized.sizeVariants
        }

        let { data, error } = await supabase
          .from('products')
          .insert([dbRow])
          .select()
          .single()

        if (error && error.message && error.message.includes('size_variants')) {
          delete dbRow.size_variants
          const retry = await supabase.from('products').insert([dbRow]).select().single()
          data = retry.data
          error = retry.error
        }

        if (!error && data) {
          const synced = normalizeProduct({ ...data, sizeVariants: normalized.sizeVariants })
          // Update local cache with Supabase assigned ID
          const updatedLocals = [synced, ...existing.filter(p => p.id !== normalized.id)]
          saveLocalProducts(updatedLocals)
          inMemoryProductsCache = null
          return { data: synced, error: null }
        } else if (error) {
          console.warn('Supabase product insert notice:', error.message)
        }
      } catch (err) {
        console.warn('Supabase insert failed, retained in local storage', err)
      }
    }

    inMemoryProductsCache = null
    return { data: normalized, error: null }
  },

  // Delete Product
  async deleteProduct(id) {
    // Remove from local cache
    const existing = getStoredLocalProducts()
    saveLocalProducts(existing.filter(p => p.id !== id && String(p.id) !== String(id)))
    inMemoryProductsCache = null

    if (isSupabaseConfigured) {
      try {
        await supabase.from('products').delete().eq('id', id)
      } catch (e) {
        console.warn('Failed to delete from Supabase:', e)
      }
    }

    return { error: null }
  },

  // Create Order Booking
  async createBooking(bookingPayload) {
    if (!isSupabaseConfigured) {
      return { data: bookingPayload, error: null }
    }

    const { data, error } = await supabase
      .from('bookings')
      .insert([bookingPayload])
      .select()
      .single()

    return { data: data || bookingPayload, error }
  },

  // Create Custom Furniture Specification Request
  async createCustomRequest(requestPayload) {
    if (!isSupabaseConfigured) {
      return { data: requestPayload, error: null }
    }

    const { data, error } = await supabase
      .from('custom_requests')
      .insert([requestPayload])
      .select()
      .single()

    return { data: data || requestPayload, error }
  },

  // Upload Product / Reference Image to Supabase Storage with Base64 Fallback
  async uploadReferenceImage(file) {
    return this.uploadProductImage(file)
  },

  async uploadProductImage(file) {
    if (!file) return { publicUrl: null, error: 'No file provided' }

    // Helper for base64 fallback
    const getBase64 = () => new Promise((resolve) => {
      const reader = new FileReader()
      reader.onload = () => resolve(reader.result)
      reader.onerror = () => resolve(URL.createObjectURL(file))
      reader.readAsDataURL(file)
    })

    if (!isSupabaseConfigured) {
      const base64Url = await getBase64()
      return { publicUrl: base64Url, error: null }
    }

    try {
      const fileExt = file.name ? file.name.split('.').pop() : 'jpg'
      const fileName = `${Date.now()}-${Math.random().toString(36).substring(2, 8)}.${fileExt}`
      const filePath = `products/${fileName}`

      // Attempt upload to 'product-images' bucket
      let { data: uploadData, error: uploadError } = await supabase.storage
        .from('product-images')
        .upload(filePath, file, { cacheControl: '3600', upsert: true })

      if (uploadError) {
        // Try 'custom-references' bucket as secondary
        const fallbackPath = `custom-refs/${fileName}`
        const { error: fallbackError } = await supabase.storage
          .from('custom-references')
          .upload(fallbackPath, file, { cacheControl: '3600', upsert: true })

        if (!fallbackError) {
          const { data } = supabase.storage.from('custom-references').getPublicUrl(fallbackPath)
          return { publicUrl: data.publicUrl, error: null }
        }

        // If Supabase Storage RLS blocked the upload, gracefully fall back to base64 Data URL!
        console.warn('Storage upload fallback to DataURL:', uploadError.message)
        const base64Url = await getBase64()
        return { publicUrl: base64Url, error: null }
      }

      const { data } = supabase.storage
        .from('product-images')
        .getPublicUrl(filePath)

      return { publicUrl: data.publicUrl, error: null }
    } catch (err) {
      console.warn('Storage upload error, using local data URL fallback', err)
      const base64Url = await getBase64()
      return { publicUrl: base64Url, error: null }
    }
  }
}
