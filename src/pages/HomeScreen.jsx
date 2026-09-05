import React, { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import Header from '../components/common/Header'
import ProductCard from '../components/common/ProductCard'
import Button from '../components/common/Button'
import { useAppStore } from '../store/useAppStore'
import { dataService } from '../services/dataService'
import { ArrowRight, ChevronRight, Truck, RefreshCw, ShieldCheck, Award, Sparkles, Leaf, HeartHandshake } from 'lucide-react'

export default function HomeScreen() {
  const navigate = useNavigate()
  const { user } = useAppStore()
  const [products, setProducts] = useState([])

  // Strict role separation: If an admin opens the customer home page, redirect directly to Admin console
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

  const categories = [
    {
      name: 'Cot / Wooden Bed',
      count: 'King & Queen',
      image: 'https://images.unsplash.com/photo-1505693416388-ac5ce068fe85?auto=format&fit=crop&w=400&q=80',
      query: 'Cot / Wooden Bed'
    },
    {
      name: 'Dressing Table',
      count: 'Mirror & Drawers',
      image: 'https://images.unsplash.com/photo-1595428774223-ef52624120d2?auto=format&fit=crop&w=400&q=80',
      query: 'Dressing Table'
    },
    {
      name: 'Sofa Set',
      count: '3+1+1 & Diwan',
      image: 'https://images.unsplash.com/photo-1555041469-a586c61ea9bc?auto=format&fit=crop&w=400&q=80',
      query: 'Sofa Set'
    },
    {
      name: 'Headboard',
      count: 'Carved Wood',
      image: 'https://images.unsplash.com/photo-1616594039964-ae9021a400a0?auto=format&fit=crop&w=400&q=80',
      query: 'Headboard'
    },
    {
      name: 'Dining Table',
      count: '4 & 6 Seater',
      image: 'https://images.unsplash.com/photo-1615066390971-03e4e1c36ddf?auto=format&fit=crop&w=400&q=80',
      query: 'Dining Table'
    },
    {
      name: 'Dining Chairs',
      count: 'Sets of 2 & 4',
      image: 'https://images.unsplash.com/photo-1503602642458-232111445657?auto=format&fit=crop&w=400&q=80',
      query: 'Dining Chairs'
    },
    {
      name: 'Pooja Mandir',
      count: 'Teak Altar',
      image: 'https://images.unsplash.com/photo-1600585154340-be6161a56a0c?auto=format&fit=crop&w=400&q=80',
      query: 'Pooja Mandir'
    },
    {
      name: 'Podimes',
      count: 'Peeta Bench',
      image: 'https://images.unsplash.com/photo-1586023492125-27b2c045efd7?auto=format&fit=crop&w=400&q=80',
      query: 'Podimes'
    },
  ]

  const featuredProducts = products.filter(p => p.featured)
  const displayProducts = featuredProducts.length > 0 ? featuredProducts : products
  const newArrivals = products.filter(p => p.newArrival)

  return (
    <div className="min-h-screen bg-[#FDFBF7] text-walnut-900 pb-24 md:pb-16 w-full font-sans">
      <Header />

      <div className="w-full px-3 sm:px-6 lg:px-10 space-y-8 md:space-y-10 pt-4">
        
        {/* 1. HERO SECTION (Compact, Minimized) */}
        <section className="bg-[#F7F2EB] rounded-2xl p-5 sm:p-7 md:p-8 border border-walnut-200/50 shadow-2xs relative overflow-hidden flex flex-col md:flex-row items-center justify-between gap-6 md:gap-8">
          
          {/* Left Text Block */}
          <div className="flex-1 space-y-4 max-w-lg">
            <span className="text-[11px] font-semibold tracking-wider uppercase text-gold-600 block">
              Handcrafted Wooden Elegance
            </span>

            <h1 className="font-serif font-bold text-2xl sm:text-3xl lg:text-4xl text-walnut-900 leading-tight">
              Design Your Dream Space
            </h1>

            <p className="text-xs sm:text-sm text-softgray leading-relaxed">
              Premium solid wood furniture pieces crafted for comfort, style, and lasting quality. Handcrafted in our studio.
            </p>

            <div className="pt-1">
              <Button
                variant="primary"
                size="md"
                onClick={() => navigate('/catalog')}
                icon={ArrowRight}
                className="bg-walnut-900 hover:bg-walnut-800 text-white px-6 py-2.5 rounded-full text-xs font-semibold shadow-xs"
              >
                Shop Now
              </Button>
            </div>

            {/* 3 Feature Badges Row */}
            <div className="pt-4 border-t border-walnut-200/60 grid grid-cols-3 gap-3 text-walnut-800">
              <div className="flex items-center gap-2">
                <Truck className="w-4 h-4 text-gold-600 flex-shrink-0" />
                <div>
                  <span className="text-[11px] font-bold block">Free Delivery</span>
                  <span className="text-[9px] text-softgray block">On consultation</span>
                </div>
              </div>

              <div className="flex items-center gap-2">
                <RefreshCw className="w-4 h-4 text-gold-600 flex-shrink-0" />
                <div>
                  <span className="text-[11px] font-bold block">Custom Specs</span>
                  <span className="text-[9px] text-softgray block">Tailored sizing</span>
                </div>
              </div>

              <div className="flex items-center gap-2">
                <ShieldCheck className="w-4 h-4 text-gold-600 flex-shrink-0" />
                <div>
                  <span className="text-[11px] font-bold block">Verified Studio</span>
                  <span className="text-[9px] text-softgray block">100% genuine</span>
                </div>
              </div>
            </div>
          </div>

          {/* Right Banner Image */}
          <div className="flex-1 w-full relative">
            <div className="relative aspect-[16/10] sm:aspect-[4/3] w-full rounded-xl overflow-hidden shadow-2xs">
              <img
                src="https://images.unsplash.com/photo-1555041469-a586c61ea9bc?auto=format&fit=crop&w=1200&q=80"
                alt="Aesthetic Living Room"
                className="w-full h-full object-cover"
              />
            </div>
          </div>

        </section>

        {/* 2. SHOP BY CATEGORY SECTION (Decreased Size, 8 Individual Boxes) */}
        <section className="space-y-3">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="font-serif font-bold text-lg md:text-xl text-walnut-900">Shop by Category</h2>
              <p className="text-[11px] text-softgray mt-0.5">Explore our handcrafted furniture catalog</p>
            </div>
            <button 
              onClick={() => navigate('/catalog')} 
              className="text-xs font-semibold text-walnut-800 hover:text-gold-600 transition-colors flex items-center gap-1"
            >
              View all <ChevronRight className="w-3.5 h-3.5" />
            </button>
          </div>

          <div className="grid grid-cols-2 sm:grid-cols-4 lg:grid-cols-8 gap-2 sm:gap-2.5">
            {categories.map((cat, idx) => (
              <div
                key={idx}
                onClick={() => navigate(`/catalog?category=${encodeURIComponent(cat.query)}`)}
                className="bg-[#F8F5F0] hover:bg-[#F2ECE2] rounded-xl p-2 text-center cursor-pointer transition-all active-tap group border border-walnut-200/50 hover:border-walnut-400/80 shadow-2xs hover:shadow-xs flex flex-col items-center justify-between"
              >
                <div className="w-full aspect-[4/3] rounded-lg overflow-hidden mb-1.5 bg-white shadow-2xs">
                  <img
                    src={cat.image}
                    alt={cat.name}
                    className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
                  />
                </div>
                <h3 className="font-serif font-bold text-[11px] text-walnut-900 group-hover:text-gold-600 transition-colors leading-tight line-clamp-2 min-h-[26px] flex items-center justify-center">
                  {cat.name}
                </h3>
                <span className="text-[9px] text-softgray block mt-0.5 font-medium">{cat.count}</span>
              </div>
            ))}
          </div>
        </section>

        {/* 3. FEATURED PRODUCTS SECTION (Compact Card Grid) */}
        <section className="space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="font-serif font-bold text-lg md:text-xl text-walnut-900">Featured Products</h2>
            <button 
              onClick={() => navigate('/catalog')} 
              className="text-xs font-semibold text-walnut-800 hover:text-gold-600 transition-colors flex items-center gap-1"
            >
              View all <ChevronRight className="w-3.5 h-3.5" />
            </button>
          </div>

          <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-4 xl:grid-cols-5 gap-3 sm:gap-4">
            {displayProducts.slice(0, 10).map(product => (
              <ProductCard key={product.id} product={product} layout="grid" />
            ))}
          </div>
        </section>

        {/* 4. PROMO BANNER SECTION */}
        <section className="bg-[#2D3328] text-white rounded-2xl overflow-hidden shadow-2xs border border-walnut-900 flex flex-col md:flex-row items-center justify-between">
          <div className="p-6 sm:p-8 md:p-10 flex-1 space-y-3 max-w-lg">
            <span className="text-[11px] font-bold uppercase tracking-wider text-gold-400">
              Studio Artisanal Offer
            </span>
            <h2 className="font-serif font-bold text-xl sm:text-2xl md:text-3xl text-white leading-tight">
              Bespoke Custom Furniture
            </h2>
            <p className="text-xs sm:text-sm text-cream-200 leading-relaxed">
              Refresh your space with timeless solid wood pieces built to your exact room dimensions and wood preferences.
            </p>
            <div className="pt-1">
              <Button
                variant="accent"
                size="sm"
                onClick={() => navigate('/custom-request')}
                icon={ArrowRight}
                className="bg-[#EFEAE2] hover:bg-white text-walnut-900 px-5 py-2.5 rounded-full text-xs font-bold shadow-xs"
              >
                Request Custom Spec
              </Button>
            </div>
          </div>

          <div className="flex-1 w-full h-56 md:h-72 relative">
            <img
              src="https://images.unsplash.com/photo-1586023492125-27b2c045efd7?auto=format&fit=crop&w=1000&q=80"
              alt="Bespoke Showcase"
              className="w-full h-full object-cover"
            />
          </div>
        </section>

        {/* 5. TRUST VALUE BADGES FOOTER ROW */}
        <section className="pt-2 grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3 sm:gap-4">
          <div className="bg-[#F7F2EB] p-4 rounded-xl border border-walnut-200/50 flex items-start gap-3">
            <Award className="w-5 h-5 text-gold-600 flex-shrink-0 mt-0.5" />
            <div>
              <h4 className="font-serif font-bold text-xs sm:text-sm text-walnut-900 mb-0.5">High Quality Materials</h4>
              <p className="text-[11px] text-softgray leading-snug">Built to last with kiln-dried solid teak & walnut wood.</p>
            </div>
          </div>

          <div className="bg-[#F7F2EB] p-4 rounded-xl border border-walnut-200/50 flex items-start gap-3">
            <Sparkles className="w-5 h-5 text-gold-600 flex-shrink-0 mt-0.5" />
            <div>
              <h4 className="font-serif font-bold text-xs sm:text-sm text-walnut-900 mb-0.5">Modern & Timeless</h4>
              <p className="text-[11px] text-softgray leading-snug">Handcrafted furniture that fits every space and aesthetic.</p>
            </div>
          </div>

          <div className="bg-[#F7F2EB] p-4 rounded-xl border border-walnut-200/50 flex items-start gap-3">
            <Leaf className="w-5 h-5 text-gold-600 flex-shrink-0 mt-0.5" />
            <div>
              <h4 className="font-serif font-bold text-xs sm:text-sm text-walnut-900 mb-0.5">Sustainable Timber</h4>
              <p className="text-[11px] text-softgray leading-snug">Eco-friendly responsibly harvested natural timber.</p>
            </div>
          </div>

          <div className="bg-[#F7F2EB] p-4 rounded-xl border border-walnut-200/50 flex items-start gap-3">
            <HeartHandshake className="w-5 h-5 text-gold-600 flex-shrink-0 mt-0.5" />
            <div>
              <h4 className="font-serif font-bold text-xs sm:text-sm text-walnut-900 mb-0.5">Customer Satisfaction</h4>
              <p className="text-[11px] text-softgray leading-snug">Trusted by thousands of happy home owners.</p>
            </div>
          </div>
        </section>

      </div>
    </div>
  )
}
