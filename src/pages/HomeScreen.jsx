import React, { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import Header from '../components/common/Header'
import ProductCard from '../components/common/ProductCard'
import Button from '../components/common/Button'
import { useAppStore } from '../store/useAppStore'
import { dataService } from '../services/dataService'
import { 
  ArrowRight, 
  ChevronRight, 
  ChevronLeft,
  Truck, 
  ShieldCheck, 
  Award, 
  Sparkles, 
  Leaf, 
  HeartHandshake, 
  Ruler, 
  Star, 
  Bot, 
  Compass,
  Hammer
} from 'lucide-react'

export default function HomeScreen() {
  const navigate = useNavigate()
  const { user, openAIChat } = useAppStore()
  const [products, setProducts] = useState([])
  const [activeCategoryFilter, setActiveCategoryFilter] = useState('all')
  const [activeHeroSlide, setActiveHeroSlide] = useState(0)

  // Role separation: If an admin opens the customer home page, redirect directly to Admin console
  useEffect(() => {
    if (user?.role === 'admin') {
      navigate('/admin', { replace: true })
    }
  }, [user, navigate])

  useEffect(() => {
    async function loadProducts() {
      const { data } = await dataService.getProducts()
      if (data) setProducts(data)
    }
    loadProducts()
  }, [])

  // 3 Curated Architectural Hero Scenes (Completely replaces old plain green couch)
  const heroSlides = [
    {
      id: 'teak-suite',
      tag: 'HANDCRAFTED ROYAL BEDROOM',
      title: 'Royal Teak King Cot Penthouse Suite',
      highlight: 'Burma Teakwood • Hand-Carved Arch Headboard',
      description: 'Masterfully sculpted from 100% kiln-seasoned Burmese timber with precision interlocking mortise-and-tenon joinery and organic hand-rubbed satin finish.',
      price: '₹38,999',
      originalPrice: '₹48,000',
      rating: '4.9',
      reviews: '480+ Homes',
      categoryQuery: 'Cot / Wooden Bed',
      badge: 'Bestseller 2026',
      image: 'https://images.unsplash.com/photo-1540518614846-7ede433c4ef2?auto=format&fit=crop&w=1600&q=85',
      accentColor: 'from-walnut-950 via-walnut-900 to-[#1F1713]'
    },
    {
      id: 'dining-sanctuary',
      tag: 'MASTER WOODWORK EDITION',
      title: 'Imperial Sheesham 6-Seater Dining Sanctuary',
      highlight: 'Solid Rosewood Slab • Artisanal Ergonomic Chairs',
      description: 'Substantial 38mm solid timber tabletop showcasing dramatic natural growth rings, reinforced with traditional butterfly joints and cushioned teak chairs.',
      price: '₹44,500',
      originalPrice: '₹56,000',
      rating: '5.0',
      reviews: '310+ Homes',
      categoryQuery: 'Dining Table',
      badge: 'Heirloom Grade',
      image: 'https://images.unsplash.com/photo-1617806118233-18e1de247200?auto=format&fit=crop&w=1600&q=85',
      accentColor: 'from-[#1A1816] via-[#241E1A] to-[#171310]'
    },
    {
      id: 'living-diwan',
      tag: 'HERITAGE LIVING ATELIER',
      title: 'Architectural Solid Teak Diwan & Credenza',
      highlight: 'Hand-Turned Spindles • Natural Linen Upholstery',
      description: 'A timeless living centerpiece sealed with zero-VOC botanical oils, engineered to anchor luxury Hyderabad drawing rooms with understated regal warmth.',
      price: '₹34,000',
      originalPrice: '₹42,000',
      rating: '4.9',
      reviews: '520+ Homes',
      categoryQuery: 'Sofa Set',
      badge: 'Artisan Favorite',
      image: 'https://images.unsplash.com/photo-1618221195710-dd6b41faaea6?auto=format&fit=crop&w=1600&q=85',
      accentColor: 'from-[#1C1A17] via-walnut-950 to-[#221A15]'
    }
  ]

  // Auto-advance hero carousel every 6 seconds
  useEffect(() => {
    const interval = setInterval(() => {
      setActiveHeroSlide(prev => (prev + 1) % heroSlides.length)
    }, 6000)
    return () => clearInterval(interval)
  }, [heroSlides.length])

  const categories = [
    {
      name: 'Cot / Wooden Bed',
      specs: 'King & Queen Teak',
      badge: 'Bestseller',
      image: 'https://images.unsplash.com/photo-1505693416388-ac5ce068fe85?auto=format&fit=crop&w=600&q=80',
      query: 'Cot / Wooden Bed'
    },
    {
      name: 'Dressing Table',
      specs: 'Vanity Mirror & Drawers',
      badge: 'Handcrafted',
      image: 'https://images.unsplash.com/photo-1595428774223-ef52624120d2?auto=format&fit=crop&w=600&q=80',
      query: 'Dressing Table'
    },
    {
      name: 'Sofa & Diwan Sets',
      specs: 'Solid 3+1+1 & Diwans',
      badge: 'Popular',
      image: 'https://images.unsplash.com/photo-1555041469-a586c61ea9bc?auto=format&fit=crop&w=600&q=80',
      query: 'Sofa Set'
    },
    {
      name: 'Headboards',
      specs: 'Carved Floral Panels',
      badge: 'Custom',
      image: 'https://images.unsplash.com/photo-1616594039964-ae9021a400a0?auto=format&fit=crop&w=600&q=80',
      query: 'Headboard'
    },
    {
      name: 'Dining Tables',
      specs: '4 & 6 Seater Solid',
      badge: 'Heirloom',
      image: 'https://images.unsplash.com/photo-1615066390971-03e4e1c36ddf?auto=format&fit=crop&w=600&q=80',
      query: 'Dining Table'
    },
    {
      name: 'Dining Chairs',
      specs: 'Ergonomic Teak Pairs',
      badge: 'Top Rated',
      image: 'https://images.unsplash.com/photo-1503602642458-232111445657?auto=format&fit=crop&w=600&q=80',
      query: 'Dining Chairs'
    },
    {
      name: 'Pooja Mandir',
      specs: 'Hand-Carved Mandapam',
      badge: 'Sacred Teak',
      image: 'https://images.unsplash.com/photo-1600585154340-be6161a56a0c?auto=format&fit=crop&w=600&q=80',
      query: 'Pooja Mandir'
    },
    {
      name: 'Podimes & Peetas',
      specs: 'Traditional Peeta Benches',
      badge: 'Artisanal',
      image: 'https://images.unsplash.com/photo-1586023492125-27b2c045efd7?auto=format&fit=crop&w=600&q=80',
      query: 'Podimes'
    },
  ]

  const featuredProducts = products.filter(p => p.featured)
  const displayFeatured = featuredProducts.length > 0 ? featuredProducts : products

  // Filter products by category tab
  const filteredProducts = displayFeatured.filter(product => {
    if (activeCategoryFilter === 'all') return true
    if (activeCategoryFilter === 'cots') return product.category?.toLowerCase().includes('cot') || product.category?.toLowerCase().includes('bed')
    if (activeCategoryFilter === 'dining') return product.category?.toLowerCase().includes('dining')
    if (activeCategoryFilter === 'living') return product.category?.toLowerCase().includes('sofa') || product.category?.toLowerCase().includes('diwan')
    return true
  })

  const currentHero = heroSlides[activeHeroSlide]

  return (
    <div className="min-h-screen bg-[#FAF7F2] text-walnut-900 pb-24 md:pb-16 w-full font-sans antialiased selection:bg-gold-500 selection:text-white">
      <Header />

      <div className="w-full px-3 sm:px-6 lg:px-10 space-y-12 md:space-y-16 pt-3 sm:pt-4">
        
        {/* ========================================================= */}
        {/* 1. ULTRA-MODERN CINEMATIC HERO SECTION (Completely redesigned) */}
        {/* ========================================================= */}
        <section className="relative rounded-2xl sm:rounded-3xl overflow-hidden shadow-2xl border border-walnut-800/40 bg-gradient-to-br from-walnut-950 via-walnut-900 to-[#1A120D] text-white">
          
          {/* Subtle Ambient Studio Lighting Glow */}
          <div className="absolute -top-32 -left-32 w-96 h-96 bg-gold-600/15 rounded-full blur-3xl pointer-events-none" />
          <div className="absolute -bottom-32 -right-32 w-96 h-96 bg-walnut-600/20 rounded-full blur-3xl pointer-events-none" />

          {/* Main Hero Content Grid */}
          <div className="relative z-10 grid grid-cols-1 lg:grid-cols-12 gap-8 items-center p-5 sm:p-8 md:p-10 lg:p-12">
            
            {/* LEFT COLUMN: Editorial Typography & Studio Actions (6 Cols on desktop) */}
            <div className="lg:col-span-6 xl:col-span-6 space-y-5 sm:space-y-6">
              
              {/* Studio Origin Tag */}
              <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-gold-500/10 border border-gold-500/30 text-gold-400 text-[10px] sm:text-xs font-semibold tracking-wider uppercase backdrop-blur-md">
                <Sparkles className="w-3.5 h-3.5 text-gold-400" />
                <span>Hyderabad Master Artisanal Studio • Est. 2014</span>
              </div>

              {/* Dynamic Slide Headline with Haute-Couture Serif Typography */}
              <div className="space-y-2">
                <span className="text-[11px] sm:text-xs font-bold tracking-widest text-gold-400 uppercase block font-sans">
                  {currentHero.tag}
                </span>
                <h1 className="font-serif font-extrabold text-2xl sm:text-4xl lg:text-5xl text-cream-50 leading-[1.12] tracking-tight">
                  {currentHero.title}
                </h1>
                <p className="font-editorial italic text-base sm:text-lg text-gold-200/90 font-medium">
                  {currentHero.highlight}
                </p>
              </div>

              {/* Description Body */}
              <p className="text-xs sm:text-sm text-cream-200/80 leading-relaxed max-w-xl font-normal">
                {currentHero.description}
              </p>

              {/* Pricing & Guarantee Callout */}
              <div className="flex items-baseline gap-3 pt-1">
                <span className="text-2xl sm:text-3xl font-bold font-serif text-white">
                  {currentHero.price}
                </span>
                <span className="text-xs sm:text-sm text-cream-400/60 line-through">
                  {currentHero.originalPrice}
                </span>
                <span className="text-[10px] sm:text-xs font-semibold bg-gold-500/20 text-gold-300 border border-gold-500/40 px-2 py-0.5 rounded">
                  Direct Workshop Price
                </span>
                <div className="hidden sm:flex items-center gap-1 text-gold-400 text-xs ml-auto">
                  <Star className="w-3.5 h-3.5 fill-gold-400" />
                  <span className="font-bold">{currentHero.rating}</span>
                  <span className="text-cream-400/60">({currentHero.reviews})</span>
                </div>
              </div>

              {/* Action Buttons */}
              <div className="pt-2 flex flex-wrap items-center gap-3 sm:gap-4">
                <Button
                  variant="accent"
                  size="md"
                  onClick={() => navigate(`/catalog?category=${encodeURIComponent(currentHero.categoryQuery)}`)}
                  icon={ArrowRight}
                  className="bg-gold-500 hover:bg-gold-400 text-walnut-950 font-bold px-6 py-3 rounded-full text-xs sm:text-sm shadow-lg hover:shadow-gold-500/30 transition-all active-tap"
                >
                  Explore Collection
                </Button>

                <button
                  onClick={() => navigate('/custom-request')}
                  className="inline-flex items-center gap-2 px-5 py-3 rounded-full text-xs sm:text-sm font-semibold text-cream-100 bg-white/10 hover:bg-white/20 border border-white/20 backdrop-blur-md transition-all active-tap"
                >
                  <Ruler className="w-3.5 h-3.5 text-gold-400" />
                  <span>Custom Room Sizing</span>
                </button>
              </div>

              {/* Slide Thumbnail Tabs (Direct Interactive Switching) */}
              <div className="pt-4 border-t border-white/10">
                <span className="text-[10px] font-semibold text-cream-400/80 uppercase tracking-widest block mb-2.5">
                  Featured Atelier Suites:
                </span>
                <div className="grid grid-cols-3 gap-2">
                  {heroSlides.map((slide, idx) => (
                    <button
                      key={slide.id}
                      onClick={() => setActiveHeroSlide(idx)}
                      className={`text-left p-2 sm:p-2.5 rounded-xl border transition-all duration-300 ${
                        activeHeroSlide === idx
                          ? 'bg-white/15 border-gold-400/80 shadow-md ring-1 ring-gold-400/40'
                          : 'bg-white/5 border-white/10 hover:bg-white/10 opacity-70 hover:opacity-100'
                      }`}
                    >
                      <div className="flex items-center justify-between text-[9px] font-bold text-gold-400 mb-0.5">
                        <span>0{idx + 1}</span>
                        {activeHeroSlide === idx && <span className="w-1.5 h-1.5 rounded-full bg-gold-400 animate-pulse" />}
                      </div>
                      <p className="text-[10px] sm:text-xs font-semibold text-white truncate">
                        {slide.title.split(' ')[1] || slide.title.split(' ')[0]}
                      </p>
                      <span className="text-[9px] text-cream-300/70 block mt-0.5">{slide.price}</span>
                    </button>
                  ))}
                </div>
              </div>

            </div>

            {/* RIGHT COLUMN: Cinematic Architectural Image Showcase (6 Cols on desktop) */}
            <div className="lg:col-span-6 xl:col-span-6 relative">
              <div className="relative aspect-[4/3] sm:aspect-[16/11] lg:aspect-[4/3] w-full rounded-2xl overflow-hidden shadow-2xl border border-white/15 group">
                <img
                  src={currentHero.image}
                  alt={currentHero.title}
                  className="w-full h-full object-cover object-center transition-all duration-700 group-hover:scale-105"
                />
                
                {/* Subtle Vignette & Gradient Overlays */}
                <div className="absolute inset-0 bg-gradient-to-t from-walnut-950/80 via-transparent to-black/20 pointer-events-none" />

                {/* Floating Glassmorphism Badge (Top Left) */}
                <div className="absolute top-3 left-3 sm:top-4 sm:left-4 bg-walnut-950/85 backdrop-blur-md border border-gold-500/30 px-3 py-1.5 rounded-full flex items-center gap-2 shadow-lg">
                  <span className="w-2 h-2 rounded-full bg-gold-400 animate-ping" />
                  <span className="text-[10px] sm:text-xs font-bold text-gold-300 tracking-wide">
                    {currentHero.badge}
                  </span>
                </div>

                {/* Floating Glassmorphism Spec Card (Bottom Right) */}
                <div className="absolute bottom-3 right-3 left-3 sm:left-auto sm:right-4 sm:bottom-4 bg-walnut-950/90 backdrop-blur-md border border-white/15 p-3 sm:p-3.5 rounded-xl text-white shadow-xl max-w-xs">
                  <div className="flex items-center justify-between gap-2 mb-1">
                    <span className="text-[10px] font-semibold text-gold-400 uppercase tracking-wider">
                      Handcrafted Spec
                    </span>
                    <span className="text-[10px] text-cream-300/80 flex items-center gap-1">
                      <ShieldCheck className="w-3 h-3 text-gold-400" /> 10-Yr Warranty
                    </span>
                  </div>
                  <h4 className="font-serif font-bold text-xs sm:text-sm text-white line-clamp-1">
                    {currentHero.title}
                  </h4>
                  <div className="flex items-center justify-between mt-2 pt-2 border-t border-white/10">
                    <span className="text-xs font-bold text-gold-300">{currentHero.price}</span>
                    <button
                      onClick={() => navigate(`/catalog?category=${encodeURIComponent(currentHero.categoryQuery)}`)}
                      className="text-[10px] font-semibold text-white hover:text-gold-400 flex items-center gap-1 transition-colors"
                    >
                      View Piece <ChevronRight className="w-3 h-3" />
                    </button>
                  </div>
                </div>

                {/* Carousel Navigation Arrows */}
                <button
                  onClick={() => setActiveHeroSlide(prev => (prev === 0 ? heroSlides.length - 1 : prev - 1))}
                  className="absolute left-2 top-1/2 -translate-y-1/2 w-8 h-8 rounded-full bg-walnut-950/70 hover:bg-walnut-900 text-white border border-white/20 backdrop-blur-md flex items-center justify-center transition-all opacity-80 hover:opacity-100"
                  aria-label="Previous Slide"
                >
                  <ChevronLeft className="w-4 h-4" />
                </button>
                <button
                  onClick={() => setActiveHeroSlide(prev => (prev + 1) % heroSlides.length)}
                  className="absolute right-2 top-1/2 -translate-y-1/2 w-8 h-8 rounded-full bg-walnut-950/70 hover:bg-walnut-900 text-white border border-white/20 backdrop-blur-md flex items-center justify-center transition-all opacity-80 hover:opacity-100"
                  aria-label="Next Slide"
                >
                  <ChevronRight className="w-4 h-4" />
                </button>
              </div>
            </div>

          </div>

          {/* BOTTOM STUDIO CREDENTIALS BANNER */}
          <div className="border-t border-white/10 bg-walnut-950/90 backdrop-blur-md py-3.5 px-4 sm:px-8 grid grid-cols-2 md:grid-cols-4 gap-3 sm:gap-4 text-cream-200">
            <div className="flex items-center gap-2.5">
              <div className="w-8 h-8 rounded-lg bg-gold-500/10 border border-gold-500/20 flex items-center justify-center text-gold-400 flex-shrink-0">
                <Leaf className="w-4 h-4" />
              </div>
              <div>
                <span className="text-[11px] sm:text-xs font-bold text-white block">100% Seasoned Timber</span>
                <span className="text-[9px] sm:text-[10px] text-cream-400/70 block">Zero MDF or particle board</span>
              </div>
            </div>

            <div className="flex items-center gap-2.5">
              <div className="w-8 h-8 rounded-lg bg-gold-500/10 border border-gold-500/20 flex items-center justify-center text-gold-400 flex-shrink-0">
                <ShieldCheck className="w-4 h-4" />
              </div>
              <div>
                <span className="text-[11px] sm:text-xs font-bold text-white block">10-Year Guarantee</span>
                <span className="text-[9px] sm:text-[10px] text-cream-400/70 block">Termite & joint protection</span>
              </div>
            </div>

            <div className="flex items-center gap-2.5">
              <div className="w-8 h-8 rounded-lg bg-gold-500/10 border border-gold-500/20 flex items-center justify-center text-gold-400 flex-shrink-0">
                <Truck className="w-4 h-4" />
              </div>
              <div>
                <span className="text-[11px] sm:text-xs font-bold text-white block">White-Glove Setup</span>
                <span className="text-[9px] sm:text-[10px] text-cream-400/70 block">Free delivery & assembly</span>
              </div>
            </div>

            <div className="flex items-center gap-2.5">
              <div className="w-8 h-8 rounded-lg bg-gold-500/10 border border-gold-500/20 flex items-center justify-center text-gold-400 flex-shrink-0">
                <Ruler className="w-4 h-4" />
              </div>
              <div>
                <span className="text-[11px] sm:text-xs font-bold text-white block">Custom Sizing</span>
                <span className="text-[9px] sm:text-[10px] text-cream-400/70 block">Built to room blueprint</span>
              </div>
            </div>
          </div>

        </section>


        {/* ========================================================= */}
        {/* 2. SHOP BY LIVING SPACE & CATEGORY SECTION (8 Architectural Boxes) */}
        {/* ========================================================= */}
        <section className="space-y-4">
          <div className="flex flex-col sm:flex-row sm:items-end justify-between gap-2">
            <div>
              <div className="flex items-center gap-1.5 text-gold-600 text-xs font-bold tracking-widest uppercase mb-1">
                <Compass className="w-3.5 h-3.5" />
                <span>Handcrafted Living Spaces</span>
              </div>
              <h2 className="font-serif font-bold text-xl sm:text-2xl md:text-3xl text-walnut-950">
                Shop by Category
              </h2>
              <p className="text-xs sm:text-sm text-softgray mt-1">
                Select a dedicated workshop collection designed for luxury living
              </p>
            </div>

            <button 
              onClick={() => navigate('/catalog')} 
              className="self-start sm:self-auto text-xs font-bold text-walnut-900 hover:text-gold-600 transition-colors flex items-center gap-1.5 group pb-1"
            >
              <span>Explore Complete Catalog</span>
              <ArrowRight className="w-3.5 h-3.5 group-hover:translate-x-1 transition-transform" />
            </button>
          </div>

          <div className="grid grid-cols-2 sm:grid-cols-4 lg:grid-cols-8 gap-2.5 sm:gap-3.5">
            {categories.map((cat, idx) => (
              <div
                key={idx}
                onClick={() => navigate(`/catalog?category=${encodeURIComponent(cat.query)}`)}
                className="bg-white hover:bg-[#F8F4EE] rounded-2xl p-2.5 text-center cursor-pointer transition-all duration-300 active-tap group border border-walnut-200/60 hover:border-gold-500/60 shadow-xs hover:shadow-md flex flex-col items-center justify-between"
              >
                {/* Category Image Container */}
                <div className="relative w-full aspect-[4/3] rounded-xl overflow-hidden mb-2 bg-[#F3EEE7]">
                  <img
                    src={cat.image}
                    alt={cat.name}
                    loading="lazy"
                    className="w-full h-full object-cover group-hover:scale-108 transition-transform duration-500"
                  />
                  {/* Subtle Badge */}
                  <span className="absolute top-1.5 right-1.5 text-[8px] font-bold bg-walnut-950/80 backdrop-blur-xs text-gold-300 px-1.5 py-0.5 rounded shadow-xs">
                    {cat.badge}
                  </span>
                </div>

                {/* Title and Specs */}
                <div className="w-full">
                  <h3 className="font-serif font-bold text-xs sm:text-[13px] text-walnut-950 group-hover:text-gold-700 transition-colors leading-tight line-clamp-2 min-h-[30px] flex items-center justify-center">
                    {cat.name}
                  </h3>
                  <p className="text-[10px] text-softgray font-medium mt-1 truncate">
                    {cat.specs}
                  </p>
                </div>
              </div>
            ))}
          </div>
        </section>


        {/* ========================================================= */}
        {/* 3. FEATURED ATELIER MASTERPIECES (Curated Catalog) */}
        {/* ========================================================= */}
        <section className="space-y-5">
          <div className="flex flex-col md:flex-row md:items-end justify-between gap-4">
            <div>
              <span className="text-gold-600 text-xs font-bold tracking-widest uppercase block mb-1">
                ✦ Master Woodwork Selection
              </span>
              <h2 className="font-serif font-bold text-xl sm:text-2xl md:text-3xl text-walnut-950">
                Featured Studio Pieces
              </h2>
              <p className="text-xs sm:text-sm text-softgray mt-1">
                Individually numbered solid wood heirlooms available for direct dispatch
              </p>
            </div>

            {/* Category Filter Pills */}
            <div className="flex items-center gap-1.5 sm:gap-2 overflow-x-auto pb-1 no-scrollbar">
              {[
                { label: 'All Masterpieces', value: 'all' },
                { label: 'Cots & Beds', value: 'cots' },
                { label: 'Dining Sanctuaries', value: 'dining' },
                { label: 'Living Diwans', value: 'living' },
              ].map(filter => (
                <button
                  key={filter.value}
                  onClick={() => setActiveCategoryFilter(filter.value)}
                  className={`px-3.5 py-1.5 rounded-full text-xs font-bold transition-all whitespace-nowrap active-tap ${
                    activeCategoryFilter === filter.value
                      ? 'bg-walnut-900 text-white shadow-xs'
                      : 'bg-white text-walnut-700 hover:bg-walnut-100/70 border border-walnut-200/60'
                  }`}
                >
                  {filter.label}
                </button>
              ))}
            </div>
          </div>

          {/* Product Grid */}
          <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-4 xl:grid-cols-5 gap-3.5 sm:gap-5">
            {filteredProducts.slice(0, 10).map(product => (
              <ProductCard key={product.id} product={product} layout="grid" />
            ))}
          </div>

          <div className="pt-2 text-center">
            <button
              onClick={() => navigate('/catalog')}
              className="inline-flex items-center gap-2 px-8 py-3 rounded-full bg-white hover:bg-walnut-900 text-walnut-900 hover:text-white font-bold text-xs sm:text-sm border border-walnut-300 shadow-sm transition-all duration-300 group"
            >
              <span>View All Handcrafted Products</span>
              <ChevronRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
            </button>
          </div>
        </section>


        {/* ========================================================= */}
        {/* 4. THE GLORY WORKSHOP STANDARD (Artisanal Craftsmanship) */}
        {/* ========================================================= */}
        <section className="bg-[#1E1712] text-white rounded-2xl sm:rounded-3xl p-6 sm:p-10 md:p-12 relative overflow-hidden border border-walnut-800 shadow-xl">
          
          <div className="max-w-3xl space-y-3 mb-8 sm:mb-10">
            <span className="text-gold-400 text-xs font-bold tracking-widest uppercase block">
              Generational Woodcraft Integrity
            </span>
            <h2 className="font-serif font-bold text-2xl sm:text-3xl md:text-4xl text-cream-50 leading-tight">
              The Glory Workshop Standard
            </h2>
            <p className="text-xs sm:text-sm text-cream-200/80 leading-relaxed">
              We reject short-lived engineered boards and toxic resin binders. Every single piece is shaped inside our Hyderabad workshop using authentic timber and heirloom carpentry techniques.
            </p>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 sm:gap-6">
            
            {/* Step 1 */}
            <div className="bg-white/5 border border-white/10 rounded-2xl p-5 hover:bg-white/10 transition-all">
              <span className="text-gold-400 text-2xl font-serif font-bold block mb-2">01</span>
              <h4 className="font-serif font-bold text-base text-white mb-1.5">
                Kiln-Seasoned Timber
              </h4>
              <p className="text-xs text-cream-300/70 leading-relaxed">
                Raw logs undergo 45-day controlled chamber seasoning to reduce moisture to 8–10%, eliminating warping and shrinkage.
              </p>
            </div>

            {/* Step 2 */}
            <div className="bg-white/5 border border-white/10 rounded-2xl p-5 hover:bg-white/10 transition-all">
              <span className="text-gold-400 text-2xl font-serif font-bold block mb-2">02</span>
              <h4 className="font-serif font-bold text-base text-white mb-1.5">
                Mortise & Tenon Joints
              </h4>
              <p className="text-xs text-cream-300/70 leading-relaxed">
                We interlock solid wood with mechanical wood-on-wood joints. No fragile dowels or staples that loosen after two years.
              </p>
            </div>

            {/* Step 3 */}
            <div className="bg-white/5 border border-white/10 rounded-2xl p-5 hover:bg-white/10 transition-all">
              <span className="text-gold-400 text-2xl font-serif font-bold block mb-2">03</span>
              <h4 className="font-serif font-bold text-base text-white mb-1.5">
                5-Coat Hand Polish
              </h4>
              <p className="text-xs text-cream-300/70 leading-relaxed">
                Sanded up to 400-grit velvet smoothness, sealed with non-yellowing PU and botanical oils to enhance the timber's natural grain.
              </p>
            </div>

            {/* Step 4 */}
            <div className="bg-white/5 border border-white/10 rounded-2xl p-5 hover:bg-white/10 transition-all">
              <span className="text-gold-400 text-2xl font-serif font-bold block mb-2">04</span>
              <h4 className="font-serif font-bold text-base text-white mb-1.5">
                White-Glove Direct Delivery
              </h4>
              <p className="text-xs text-cream-300/70 leading-relaxed">
                Delivered in padded blankets by our trained studio team and assembled directly inside your chosen room.
              </p>
            </div>

          </div>

          <div className="mt-8 pt-6 border-t border-white/10 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-full bg-gold-500/20 border border-gold-400 flex items-center justify-center text-gold-400">
                <Hammer className="w-5 h-5" />
              </div>
              <div>
                <h5 className="text-xs sm:text-sm font-bold text-white">Need custom carvings or specific wood species?</h5>
                <p className="text-[11px] text-cream-300/70">Share your bedroom dimensions and reference drawings with our master artisan.</p>
              </div>
            </div>

            <Button
              variant="accent"
              size="sm"
              onClick={() => navigate('/custom-request')}
              className="bg-gold-500 hover:bg-gold-400 text-walnut-950 font-bold px-6 py-2.5 rounded-full text-xs shadow-md whitespace-nowrap active-tap"
            >
              Request Custom Spec
            </Button>
          </div>

        </section>


        {/* ========================================================= */}
        {/* 5. INTERACTIVE GLORYAI CONCIERGE CARD */}
        {/* ========================================================= */}
        <section className="bg-gradient-to-r from-[#241A14] via-[#2F2119] to-[#201712] rounded-2xl sm:rounded-3xl p-6 sm:p-8 md:p-10 border border-gold-500/30 shadow-lg text-white flex flex-col lg:flex-row items-center justify-between gap-6">
          
          <div className="space-y-3 max-w-xl">
            <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-gold-500/20 text-gold-300 border border-gold-500/30 text-[10px] font-bold uppercase tracking-wider">
              <Bot className="w-3.5 h-3.5" />
              <span>GloryAI Interior Studio Concierge</span>
            </div>
            <h3 className="font-serif font-bold text-xl sm:text-2xl md:text-3xl text-cream-50 leading-tight">
              Unsure which solid wood suits your room?
            </h3>
            <p className="text-xs sm:text-sm text-cream-200/80 leading-relaxed">
              Ask GloryAI to compare Burma Teak vs Sheesham, calculate ideal cot clearance for your bedroom, or recommend stain finishes to match your flooring.
            </p>
            <div className="flex flex-wrap gap-2 pt-1">
              <span className="text-[10px] bg-white/10 px-2.5 py-1 rounded-full text-cream-200 border border-white/10">
                💬 "Which wood is best for Hyderabad humid weather?"
              </span>
              <span className="text-[10px] bg-white/10 px-2.5 py-1 rounded-full text-cream-200 border border-white/10">
                💬 "Recommend cot size for 12x14 ft bedroom"
              </span>
            </div>
          </div>

          <div className="flex-shrink-0">
            <button
              onClick={() => openAIChat()}
              className="px-6 py-3.5 rounded-full bg-gradient-to-r from-gold-500 to-gold-400 hover:from-gold-400 hover:to-gold-300 text-walnut-950 font-bold text-xs sm:text-sm shadow-xl flex items-center gap-2.5 transition-all active-tap"
            >
              <Bot className="w-4 h-4" />
              <span>Launch GloryAI Concierge</span>
              <ArrowRight className="w-4 h-4" />
            </button>
          </div>

        </section>


        {/* ========================================================= */}
        {/* 6. VERIFIED HYDERABAD PATRON STORIES */}
        {/* ========================================================= */}
        <section className="space-y-5">
          <div className="text-center max-w-xl mx-auto">
            <span className="text-gold-600 text-xs font-bold tracking-widest uppercase block mb-1">
              ✦ Verified Hyderabad Homeowners
            </span>
            <h2 className="font-serif font-bold text-xl sm:text-2xl md:text-3xl text-walnut-950">
              Heirlooms in Real Homes
            </h2>
            <p className="text-xs sm:text-sm text-softgray mt-1">
              Read authentic feedback from patrons who furnished their dream villas and apartments
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 sm:gap-6">
            
            <div className="bg-white p-6 rounded-2xl border border-walnut-200/60 shadow-xs space-y-3 flex flex-col justify-between">
              <div className="space-y-2">
                <div className="flex items-center gap-1 text-gold-500">
                  {[...Array(5)].map((_, i) => (
                    <Star key={i} className="w-3.5 h-3.5 fill-gold-500" />
                  ))}
                </div>
                <p className="font-serif italic text-xs sm:text-sm text-walnut-900 leading-relaxed">
                  "The King Cot we ordered for our Jubilee Hills villa is an absolute heirloom. Solid Burma teak, flawless joinery, and the mattress fit was exact down to the centimeter."
                </p>
              </div>
              <div className="pt-3 border-t border-walnut-100 flex items-center justify-between">
                <div>
                  <h5 className="font-bold text-xs text-walnut-950">Dr. Rajesh & Sunitha K.</h5>
                  <span className="text-[10px] text-softgray">Jubilee Hills, Hyderabad</span>
                </div>
                <span className="text-[9px] font-semibold text-mutedgreen bg-mutedgreen/10 px-2 py-0.5 rounded">
                  Verified Buyer
                </span>
              </div>
            </div>

            <div className="bg-white p-6 rounded-2xl border border-walnut-200/60 shadow-xs space-y-3 flex flex-col justify-between">
              <div className="space-y-2">
                <div className="flex items-center gap-1 text-gold-500">
                  {[...Array(5)].map((_, i) => (
                    <Star key={i} className="w-3.5 h-3.5 fill-gold-500" />
                  ))}
                </div>
                <p className="font-serif italic text-xs sm:text-sm text-walnut-900 leading-relaxed">
                  "Our 6-seater Sheesham dining table is the talk of every family gathering. Solid heavy wood with natural live-edge grain. Delivered and installed within 10 days."
                </p>
              </div>
              <div className="pt-3 border-t border-walnut-100 flex items-center justify-between">
                <div>
                  <h5 className="font-bold text-xs text-walnut-950">Vikramaditya R.</h5>
                  <span className="text-[10px] text-softgray">Financial District, Gachibowli</span>
                </div>
                <span className="text-[9px] font-semibold text-mutedgreen bg-mutedgreen/10 px-2 py-0.5 rounded">
                  Verified Buyer
                </span>
              </div>
            </div>

            <div className="bg-white p-6 rounded-2xl border border-walnut-200/60 shadow-xs space-y-3 flex flex-col justify-between">
              <div className="space-y-2">
                <div className="flex items-center gap-1 text-gold-500">
                  {[...Array(5)].map((_, i) => (
                    <Star key={i} className="w-3.5 h-3.5 fill-gold-500" />
                  ))}
                </div>
                <p className="font-serif italic text-xs sm:text-sm text-walnut-900 leading-relaxed">
                  "Glory carved our Teak Pooja Mandir with unbelievable devotion. The brass bells and lotus motifs on pure wood are divine. Exceptional craftsmanship."
                </p>
              </div>
              <div className="pt-3 border-t border-walnut-100 flex items-center justify-between">
                <div>
                  <h5 className="font-bold text-xs text-walnut-950">Lakshmi & Murthy S.</h5>
                  <span className="text-[10px] text-softgray">Madhapur, Hyderabad</span>
                </div>
                <span className="text-[9px] font-semibold text-mutedgreen bg-mutedgreen/10 px-2 py-0.5 rounded">
                  Verified Buyer
                </span>
              </div>
            </div>

          </div>
        </section>


        {/* ========================================================= */}
        {/* 7. STUDIO VALUE BADGES (Refined Modern Cards) */}
        {/* ========================================================= */}
        <section className="pt-2 grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3 sm:gap-4">
          <div className="bg-white p-4 sm:p-5 rounded-2xl border border-walnut-200/60 shadow-xs flex items-start gap-3.5">
            <div className="w-9 h-9 rounded-xl bg-gold-500/10 border border-gold-500/20 flex items-center justify-center text-gold-600 flex-shrink-0 mt-0.5">
              <Award className="w-5 h-5" />
            </div>
            <div>
              <h4 className="font-serif font-bold text-xs sm:text-sm text-walnut-950 mb-0.5">100% Solid Seasoned Timber</h4>
              <p className="text-[11px] text-softgray leading-snug">Built exclusively with kiln-dried pure teak & rosewood timber.</p>
            </div>
          </div>

          <div className="bg-white p-4 sm:p-5 rounded-2xl border border-walnut-200/60 shadow-xs flex items-start gap-3.5">
            <div className="w-9 h-9 rounded-xl bg-gold-500/10 border border-gold-500/20 flex items-center justify-center text-gold-600 flex-shrink-0 mt-0.5">
              <Sparkles className="w-5 h-5" />
            </div>
            <div>
              <h4 className="font-serif font-bold text-xs sm:text-sm text-walnut-950 mb-0.5">Modern & Architectural</h4>
              <p className="text-[11px] text-softgray leading-snug">Contemporary minimalist silhouettes meeting classical joinery.</p>
            </div>
          </div>

          <div className="bg-white p-4 sm:p-5 rounded-2xl border border-walnut-200/60 shadow-xs flex items-start gap-3.5">
            <div className="w-9 h-9 rounded-xl bg-gold-500/10 border border-gold-500/20 flex items-center justify-center text-gold-600 flex-shrink-0 mt-0.5">
              <Leaf className="w-5 h-5" />
            </div>
            <div>
              <h4 className="font-serif font-bold text-xs sm:text-sm text-walnut-950 mb-0.5">Eco-Friendly & Non-Toxic</h4>
              <p className="text-[11px] text-softgray leading-snug">Hand-rubbed with organic oils and child-safe zero-VOC finishes.</p>
            </div>
          </div>

          <div className="bg-white p-4 sm:p-5 rounded-2xl border border-walnut-200/60 shadow-xs flex items-start gap-3.5">
            <div className="w-9 h-9 rounded-xl bg-gold-500/10 border border-gold-500/20 flex items-center justify-center text-gold-600 flex-shrink-0 mt-0.5">
              <HeartHandshake className="w-5 h-5" />
            </div>
            <div>
              <h4 className="font-serif font-bold text-xs sm:text-sm text-walnut-950 mb-0.5">Direct Studio Pricing</h4>
              <p className="text-[11px] text-softgray leading-snug">No middleman markup. 100% factory direct pricing from workshop.</p>
            </div>
          </div>
        </section>

      </div>
    </div>
  )
}
