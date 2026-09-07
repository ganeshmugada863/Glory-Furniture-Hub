import React, { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import Header from '../components/common/Header'
import Footer from '../components/common/Footer'
import ProductCard from '../components/common/ProductCard'
import { useAppStore } from '../store/useAppStore'
import { dataService } from '../services/dataService'
import { ArrowRight, ChevronRight } from 'lucide-react'

export default function HomeScreen() {
  const navigate = useNavigate()
  const { user } = useAppStore()
  const [products, setProducts] = useState([])
  const [activeCategoryFilter, setActiveCategoryFilter] = useState('all')

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

  // 5 Category Cards
  const roomCards = [
    {
      title: 'SOFA COLLECTIONS',
      subtitle: 'Modern secollections',
      image: '/images/card_sofa.jpg',
      query: 'Sofa Set'
    },
    {
      title: 'DINING SETS',
      subtitle: 'Teak/resik wood with...',
      image: '/images/card_dining.jpg',
      query: 'Dining Table'
    },
    {
      title: 'BEDROOM ESSENTIALS',
      subtitle: 'Canopy teak bed',
      image: '/images/card_bed.jpg',
      query: 'Cot / Wooden Bed'
    },
    {
      title: 'ACCENTS & DECOR',
      subtitle: 'Console table and decor',
      image: '/images/card_decor.jpg',
      query: 'Dressing Table'
    },
    {
      title: 'OFFICE COMFORTS',
      subtitle: 'Sleak teak desk',
      image: '/images/card_office.jpg',
      query: 'Podimes'
    },
  ]

  const featuredProducts = products.filter(p => p.featured)
  const displayProducts = featuredProducts.length > 0 ? featuredProducts : products

  // Filter tabs per user instruction (Bed, Sofa, Dining, Dressing, Diwancut, Chairs)
  const filterTabs = [
    { label: 'All Pieces', value: 'all' },
    { label: 'Bed', value: 'bed' },
    { label: 'Sofa', value: 'sofa' },
    { label: 'Dining', value: 'dining' },
    { label: 'Dressing', value: 'dressing' },
    { label: 'Diwancut', value: 'diwancut' },
    { label: 'Chairs', value: 'chairs' },
  ]

  const filteredProducts = displayProducts.filter(product => {
    if (activeCategoryFilter === 'all') return true
    const cat = (product.category || '').toLowerCase()
    const name = (product.name || '').toLowerCase()
    if (activeCategoryFilter === 'bed') return cat.includes('cot') || cat.includes('bed') || name.includes('bed') || name.includes('cot')
    if (activeCategoryFilter === 'sofa') return cat.includes('sofa') || name.includes('sofa')
    if (activeCategoryFilter === 'dining') return (cat.includes('dining table') || cat.includes('dining')) && !cat.includes('chair')
    if (activeCategoryFilter === 'dressing') return cat.includes('dressing') || name.includes('dressing')
    if (activeCategoryFilter === 'diwancut') return cat.includes('diwan') || cat.includes('podime') || name.includes('diwan')
    if (activeCategoryFilter === 'chairs') return cat.includes('chair') || name.includes('chair')
    return true
  })

  return (
    <div className="min-h-screen bg-[#FDFDFD] text-gray-900 w-full font-sans antialiased selection:bg-gray-900 selection:text-white flex flex-col justify-between">
      <div>
        <Header />

        <div className="w-full px-3 sm:px-6 lg:px-10 space-y-6 sm:space-y-8 pt-4 sm:pt-6">
          
          {/* ========================================================= */}
          {/* 1. HERO SECTION (Exact Replica of Reference UI) */}
          {/* ========================================================= */}
          <section className="relative rounded-2xl sm:rounded-3xl lg:rounded-[28px] overflow-hidden shadow-xs border border-gray-100 w-full aspect-[16/11] sm:aspect-[16/8] lg:aspect-[2.35/1] min-h-[440px] sm:min-h-[480px] lg:min-h-[520px] flex items-center">
            
            {/* Background High-Definition Image */}
            <img
              src="/images/hero_epoxy_teak.jpg"
              alt="Glory Artisanal Teak Furniture"
              className="absolute inset-0 w-full h-full object-cover object-center"
            />

            {/* Left Dark Vignette Overlay for Crisp Typography Contrast */}
            <div className="absolute inset-0 bg-gradient-to-r from-black/85 via-black/45 to-transparent pointer-events-none" />

            {/* Left Text Content Box */}
            <div className="relative z-10 p-6 sm:p-10 md:p-12 lg:p-16 max-w-2xl space-y-3 sm:space-y-4 text-white">
              
              <h1 className="font-sans font-extrabold text-2xl sm:text-4xl md:text-5xl lg:text-[50px] leading-[1.12] tracking-tight drop-shadow-md">
                Elevate Your Home with<br />
                Glory's Artisanal Teak<br />
                Furniture.
              </h1>

              <p className="text-xs sm:text-sm md:text-base text-gray-200/95 leading-relaxed max-w-md drop-shadow-xs font-normal">
                Discover timeless pieces crafted with natural teak wood and vibrant epoxy resin.
              </p>

              <div className="pt-2 sm:pt-3">
                <button
                  onClick={() => navigate('/catalog')}
                  className="inline-flex items-center gap-2.5 px-6 sm:px-7 py-3 rounded-full bg-[#0F1E36] hover:bg-[#1A2E50] text-white text-xs sm:text-sm font-medium shadow-xl transition-all duration-300 active-tap"
                >
                  <span>Explore Collection</span>
                  <ArrowRight className="w-3.5 h-3.5 sm:w-4 sm:h-4" />
                </button>
              </div>

            </div>

            {/* Carousel Pagination Dots (Bottom Center matching reference) */}
            <div className="absolute bottom-4 sm:bottom-6 left-1/2 -translate-x-1/2 flex items-center gap-1.5 z-10">
              <div className="w-6 sm:w-7 h-1.5 rounded-full bg-white shadow-xs transition-all" />
              <div className="w-1.5 h-1.5 rounded-full bg-white/60 backdrop-blur-xs" />
              <div className="w-1.5 h-1.5 rounded-full bg-white/60 backdrop-blur-xs" />
              <div className="w-1.5 h-1.5 rounded-full bg-white/60 backdrop-blur-xs" />
            </div>

          </section>


          {/* ========================================================= */}
          {/* 2. 5 HORIZONTAL CATEGORY CARDS (With Clean Customer-Friendly Font) */}
          {/* ========================================================= */}
          <section>
            <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-3 sm:gap-4 lg:gap-4.5">
              {roomCards.map((card, idx) => (
                <div
                  key={idx}
                  onClick={() => navigate(`/catalog?category=${encodeURIComponent(card.query)}`)}
                  className="bg-white rounded-2xl p-2.5 sm:p-3 border border-gray-100 shadow-2xs hover:shadow-md transition-all duration-300 cursor-pointer group flex flex-col justify-between"
                >
                  {/* Image Container with Rounded Corners */}
                  <div className="relative w-full aspect-[4/3] rounded-xl overflow-hidden bg-gray-50 mb-2.5">
                    <img
                      src={card.image}
                      alt={card.title}
                      loading="lazy"
                      className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500"
                    />
                  </div>

                  {/* Card Title & Subtitle with Arrow Icon */}
                  <div className="flex items-center justify-between gap-1 pt-0.5">
                    <div className="min-w-0 flex-1">
                      <h3 className="font-sans font-bold text-xs sm:text-[13px] text-gray-950 uppercase tracking-wide group-hover:text-gray-700 transition-colors truncate">
                        {card.title}
                      </h3>
                      <p className="font-sans text-[10px] sm:text-[11px] text-gray-500 font-normal truncate mt-0.5">
                        {card.subtitle}
                      </p>
                    </div>

                    <div className="w-6 h-6 rounded-full flex items-center justify-center text-gray-700 group-hover:translate-x-1 transition-transform flex-shrink-0">
                      <ArrowRight className="w-3.5 h-3.5" />
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </section>


          {/* ========================================================= */}
          {/* 3. FEATURED PRODUCTS CATALOG (With Updated Filter Pills & No Filler Sentences) */}
          {/* ========================================================= */}
          <section className="space-y-4 pt-4 sm:pt-6">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-gray-100 pb-3">
              <div>
                <h2 className="font-sans font-extrabold text-xl sm:text-2xl text-gray-950 tracking-tight">
                  Featured Masterpieces
                </h2>
              </div>

              {/* Filter Pills (Bed, Sofa, Dining, Dressing, Diwancut, Chairs) */}
              <div className="flex items-center gap-1.5 sm:gap-2 overflow-x-auto no-scrollbar py-0.5">
                {filterTabs.map((tab) => (
                  <button
                    key={tab.value}
                    onClick={() => setActiveCategoryFilter(tab.value)}
                    className={`px-4 py-1.5 rounded-full text-xs font-semibold transition-all whitespace-nowrap active-tap ${
                      activeCategoryFilter === tab.value
                        ? 'bg-gray-950 text-white shadow-xs'
                        : 'bg-gray-100 text-gray-700 hover:bg-gray-200/80'
                    }`}
                  >
                    {tab.label}
                  </button>
                ))}
              </div>
            </div>

            {/* Product Grid */}
            <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-4 xl:grid-cols-5 gap-3.5 sm:gap-4.5">
              {filteredProducts.slice(0, 10).map(product => (
                <ProductCard key={product.id} product={product} layout="grid" />
              ))}
            </div>

            <div className="pt-3 text-center">
              <button
                onClick={() => navigate('/catalog')}
                className="inline-flex items-center gap-2 px-8 py-3 rounded-full bg-white hover:bg-gray-950 text-gray-900 hover:text-white font-bold text-xs sm:text-sm border border-gray-200 shadow-2xs transition-all duration-300 group"
              >
                <span>Explore Complete Catalog</span>
                <ChevronRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
              </button>
            </div>
          </section>

        </div>
      </div>

      {/* ========================================================= */}
      {/* 4. FOOTER (Added at bottom of main page) */}
      {/* ========================================================= */}
      <Footer />
    </div>
  )
}
