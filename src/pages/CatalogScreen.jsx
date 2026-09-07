import React, { useState, useEffect, useMemo, useRef } from 'react'
import { useNavigate, useSearchParams } from 'react-router-dom'
import Header from '../components/common/Header'
import ProductCard from '../components/common/ProductCard'
import Modal from '../components/common/Modal'
import Button from '../components/common/Button'
import { ProductGridSkeleton } from '../components/common/Skeleton'
import { useAppStore } from '../store/useAppStore'
import { dataService } from '../services/dataService'
import { Filter, ArrowUpDown, X, Check, Search, SlidersHorizontal, Sparkles, ChevronDown } from 'lucide-react'

export default function CatalogScreen() {
  const navigate = useNavigate()
  const { user } = useAppStore()
  const [searchParams] = useSearchParams()
  const categoryParam = searchParams.get('category')

  // If an admin opens the customer catalog, redirect directly to Admin console
  useEffect(() => {
    if (user?.role === 'admin') {
      navigate('/admin', { replace: true })
    }
  }, [user, navigate])

  const [products, setProducts] = useState([])
  const [isLoading, setIsLoading] = useState(true)
  const [selectedCategory, setSelectedCategory] = useState(categoryParam || 'All')
  const [selectedStyle, setSelectedStyle] = useState('All')
  const [maxPrice, setMaxPrice] = useState(250000)
  const [inStockOnly, setInStockOnly] = useState(false)
  const [sortBy, setSortBy] = useState('popular')
  const [isFilterOpen, setIsFilterOpen] = useState(false)
  const [searchQuery, setSearchQuery] = useState('')
  const filterDropdownRef = useRef(null)

  // Sync category state when URL search param changes (e.g. user clicks Bed on HomeScreen)
  useEffect(() => {
    if (categoryParam) {
      setSelectedCategory(categoryParam)
    } else {
      setSelectedCategory('All')
    }
  }, [categoryParam])

  useEffect(() => {
    async function loadCatalog() {
      setIsLoading(true)
      const { data } = await dataService.getProducts()
      if (data) setProducts(data)
      setIsLoading(false)
    }
    loadCatalog()
  }, [])

  const categories = [
    'All',
    'Cot / Wooden Bed',
    'Dressing Table',
    'Sofa Set',
    'Headboard',
    'Dining Table',
    'Dining Chairs',
    'Pooja Mandir',
    'Podimes'
  ]

  const styles = ['All', 'Classic', 'Modern Minimalist', 'Rustic', 'Traditional']

  const handleCategorySelect = (cat) => {
    setSelectedCategory(cat)
    if (cat === 'All') {
      navigate('/catalog')
    } else {
      navigate(`/catalog?category=${encodeURIComponent(cat)}`)
    }
  }

  // Close filter dropdown when clicking outside
  useEffect(() => {
    function handleClickOutside(event) {
      if (filterDropdownRef.current && !filterDropdownRef.current.contains(event.target)) {
        setIsFilterOpen(false)
      }
    }
    if (isFilterOpen) {
      document.addEventListener('mousedown', handleClickOutside)
    }
    return () => {
      document.removeEventListener('mousedown', handleClickOutside)
    }
  }, [isFilterOpen])

  // Filter products by category, style, price limit, inStock, and search query
  const filteredProducts = useMemo(() => {
    return products.filter(product => {
      const pCat = (product.category || '').toLowerCase().trim()
      const sCat = selectedCategory.toLowerCase().trim()
      const pName = (product.name || '').toLowerCase().trim()
      const pDesc = (product.description || '').toLowerCase()

      let matchesCategory = false
      if (selectedCategory === 'All') {
        matchesCategory = true
      } else if (pCat === sCat) {
        matchesCategory = true
      } else if (selectedCategory === 'Cot / Wooden Bed') {
        matchesCategory = pCat.includes('bed') || pCat.includes('cot') || pCat === 'bedroom' || pName.includes('bed') || pName.includes('cot')
      } else if (selectedCategory === 'Dressing Table') {
        matchesCategory = pCat.includes('dressing') || pName.includes('dressing') || pName.includes('vanity')
      } else if (selectedCategory === 'Sofa Set') {
        matchesCategory = pCat.includes('sofa') || pCat === 'living room' || pName.includes('sofa') || pName.includes('couch')
      } else if (selectedCategory === 'Headboard') {
        matchesCategory = pCat.includes('headboard') || pName.includes('headboard')
      } else if (selectedCategory === 'Dining Table') {
        matchesCategory = (pCat.includes('dining table') || (pCat.includes('dining') && !pCat.includes('chair'))) || (pName.includes('dining table') || (pName.includes('table') && pName.includes('dining')))
      } else if (selectedCategory === 'Dining Chairs') {
        matchesCategory = pCat.includes('chair') || pName.includes('chair')
      } else if (selectedCategory === 'Pooja Mandir') {
        matchesCategory = pCat.includes('mandir') || pCat.includes('pooja') || pName.includes('mandir') || pName.includes('pooja') || pName.includes('temple')
      } else if (selectedCategory === 'Podimes') {
        matchesCategory = pCat.includes('podimes') || pCat.includes('podime') || pName.includes('podime') || pName.includes('peeta') || pName.includes('bench')
      }

      const matchesStyle = selectedStyle === 'All' || (product.style && product.style.toLowerCase() === selectedStyle.toLowerCase())
      const matchesPrice = (product.price || 0) <= maxPrice
      const matchesStock = !inStockOnly || product.inStock !== false
      const matchesSearch = !searchQuery || pName.includes(searchQuery.toLowerCase()) || pDesc.includes(searchQuery.toLowerCase())

      return matchesCategory && matchesStyle && matchesPrice && matchesStock && matchesSearch
    }).sort((a, b) => {
      if (sortBy === 'price-low') return (a.price || 0) - (b.price || 0)
      if (sortBy === 'price-high') return (b.price || 0) - (a.price || 0)
      if (sortBy === 'rating') return (b.rating || 0) - (a.rating || 0)
      return (b.reviewCount || 0) - (a.reviewCount || 0)
    })
  }, [products, selectedCategory, selectedStyle, maxPrice, inStockOnly, sortBy, searchQuery])

  const extraFiltersCount = (selectedStyle !== 'All' ? 1 : 0) + (maxPrice < 250000 ? 1 : 0) + (inStockOnly ? 1 : 0)
  const hasExtraFilters = extraFiltersCount > 0

  return (
    <div className="min-h-screen bg-[#FDFBF7] text-walnut-900 pb-20 md:pb-12 w-full font-sans">
      <Header 
        title="Furniture Catalog" 
        rightAction={
          <div className="flex items-center gap-1.5 sm:gap-2 flex-shrink-0">
            {/* 1. Category Dropdown */}
            <div className="relative">
              <select
                value={selectedCategory}
                onChange={(e) => handleCategorySelect(e.target.value)}
                className="appearance-none bg-white border border-gray-300 hover:border-gray-400 text-gray-900 text-xs sm:text-sm font-semibold rounded-full pl-3 pr-7 py-1.5 focus:outline-none focus:ring-2 focus:ring-gray-950 shadow-2xs cursor-pointer max-w-[125px] sm:max-w-[165px] truncate"
                aria-label="Filter by Category"
              >
                {categories.map(cat => (
                  <option key={cat} value={cat}>
                    {cat === 'All' ? 'All Categories' : cat}
                  </option>
                ))}
              </select>
              <ChevronDown className="w-3.5 h-3.5 text-gray-500 absolute right-2 top-1/2 -translate-y-1/2 pointer-events-none" />
            </div>

            {/* 2. Filter Dropdown Button & Popover */}
            <div className="relative" ref={filterDropdownRef}>
              <button
                type="button"
                onClick={() => setIsFilterOpen(!isFilterOpen)}
                className={`inline-flex items-center gap-1.5 px-2.5 sm:px-3 py-1.5 rounded-full border text-xs sm:text-sm font-semibold transition-all cursor-pointer active-tap ${
                  hasExtraFilters || isFilterOpen
                    ? 'bg-gray-950 text-white border-gray-950 shadow-xs'
                    : 'bg-white hover:bg-gray-50 text-gray-800 border-gray-300 shadow-2xs'
                }`}
                aria-label="Filter products"
              >
                <SlidersHorizontal className="w-3.5 h-3.5 stroke-[2.2]" />
                <span>Filters</span>
                {extraFiltersCount > 0 && (
                  <span className="w-4 h-4 rounded-full bg-amber-500 text-white text-[10px] font-bold flex items-center justify-center -mr-0.5">
                    {extraFiltersCount}
                  </span>
                )}
              </button>

              {/* Floating Filter Dropdown Popover */}
              {isFilterOpen && (
                <div className="fixed inset-x-4 top-28 sm:absolute sm:right-0 sm:top-full sm:mt-2 sm:inset-x-auto sm:w-80 bg-white rounded-2xl shadow-xl border border-gray-200/90 p-4 z-50 text-gray-900 animate-fade-in font-sans">
                  {/* Dropdown Header */}
                  <div className="flex items-center justify-between pb-3 border-b border-gray-100">
                    <div className="flex items-center gap-1.5">
                      <SlidersHorizontal className="w-4 h-4 text-gray-800" />
                      <span className="font-bold text-sm text-gray-900">Filter Pieces</span>
                      {extraFiltersCount > 0 && (
                        <span className="bg-amber-100 text-amber-800 text-[10px] font-bold px-2 py-0.5 rounded-full">
                          {extraFiltersCount} active
                        </span>
                      )}
                    </div>
                    <button
                      type="button"
                      onClick={() => setIsFilterOpen(false)}
                      className="p-1 text-gray-400 hover:text-gray-700 rounded-full hover:bg-gray-100 cursor-pointer"
                    >
                      <X className="w-4 h-4" />
                    </button>
                  </div>

                  {/* Budget / Price Range Slider */}
                  <div className="py-3 border-b border-gray-100">
                    <div className="flex items-center justify-between text-xs font-semibold text-gray-800 mb-2">
                      <span>Max Budget:</span>
                      <span className="font-bold text-gray-950 text-sm">₹{maxPrice.toLocaleString('en-IN')}</span>
                    </div>
                    <input
                      type="range"
                      min="10000"
                      max="250000"
                      step="5000"
                      value={maxPrice}
                      onChange={(e) => setMaxPrice(Number(e.target.value))}
                      className="w-full accent-gray-950 cursor-pointer"
                    />
                    <div className="flex items-center justify-between text-[10px] text-gray-400 mt-1">
                      <span>₹10,000</span>
                      <span>₹2,50,000+</span>
                    </div>

                    {/* Quick Budget Chips */}
                    <div className="flex flex-wrap gap-1 mt-2.5">
                      {[
                        { label: 'Any', val: 250000 },
                        { label: '< ₹50k', val: 50000 },
                        { label: '< ₹1L', val: 100000 },
                        { label: '< ₹1.5L', val: 150000 }
                      ].map(b => (
                        <button
                          key={b.label}
                          type="button"
                          onClick={() => setMaxPrice(b.val)}
                          className={`text-[11px] px-2 py-0.5 rounded-full border cursor-pointer transition-colors ${
                            maxPrice === b.val
                              ? 'bg-gray-950 text-white border-gray-950 font-semibold'
                              : 'bg-gray-50 text-gray-700 border-gray-200 hover:bg-gray-100'
                          }`}
                        >
                          {b.label}
                        </button>
                      ))}
                    </div>
                  </div>

                  {/* Woodworking Style */}
                  <div className="py-3 border-b border-gray-100">
                    <label className="block text-xs font-bold text-gray-800 mb-2">Woodworking Style</label>
                    <div className="flex flex-wrap gap-1.5">
                      {styles.map(st => (
                        <button
                          key={st}
                          type="button"
                          onClick={() => setSelectedStyle(st)}
                          className={`px-2.5 py-1 rounded-full text-xs font-medium cursor-pointer transition-all ${
                            selectedStyle === st
                              ? 'bg-gray-950 text-white font-bold shadow-2xs'
                              : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                          }`}
                        >
                          {st}
                        </button>
                      ))}
                    </div>
                  </div>

                  {/* In-Stock Only */}
                  <div className="py-3 border-b border-gray-100 flex items-center justify-between">
                    <span className="text-xs font-bold text-gray-800">In-Stock Only</span>
                    <label className="relative inline-flex items-center cursor-pointer">
                      <input
                        type="checkbox"
                        checked={inStockOnly}
                        onChange={(e) => setInStockOnly(e.target.checked)}
                        className="sr-only peer"
                      />
                      <div className="w-8 h-4 bg-gray-200 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-3 after:w-3 after:transition-all peer-checked:bg-gray-950"></div>
                    </label>
                  </div>

                  {/* Dropdown Footer Actions */}
                  <div className="pt-3 flex items-center gap-2">
                    <button
                      type="button"
                      onClick={() => {
                        setSelectedCategory('All')
                        setSelectedStyle('All')
                        setMaxPrice(250000)
                        setInStockOnly(false)
                      }}
                      className="flex-1 py-1.5 text-xs font-semibold text-gray-600 hover:text-gray-900 border border-gray-300 rounded-lg hover:bg-gray-50 cursor-pointer transition-colors"
                    >
                      Reset All
                    </button>
                    <button
                      type="button"
                      onClick={() => setIsFilterOpen(false)}
                      className="flex-1 py-1.5 text-xs font-semibold bg-gray-950 text-white rounded-lg hover:bg-black cursor-pointer transition-colors flex items-center justify-center gap-1 shadow-2xs"
                    >
                      <Check className="w-3.5 h-3.5" />
                      <span>Apply ({filteredProducts.length})</span>
                    </button>
                  </div>
                </div>
              )}
            </div>

            {/* 3. Popular / Sort Dropdown */}
            <div className="relative">
              <select
                value={sortBy}
                onChange={(e) => setSortBy(e.target.value)}
                className="appearance-none bg-white border border-gray-300 hover:border-gray-400 text-gray-900 text-xs sm:text-sm font-semibold rounded-full pl-3 pr-7 py-1.5 focus:outline-none focus:ring-2 focus:ring-gray-950 shadow-2xs cursor-pointer max-w-[105px] sm:max-w-[140px]"
                aria-label="Sort products"
              >
                <option value="popular">Popular</option>
                <option value="price-low">Price: Low to High</option>
                <option value="price-high">Price: High to Low</option>
                <option value="rating">Top Rated</option>
              </select>
              <ChevronDown className="w-3.5 h-3.5 text-gray-500 absolute right-2 top-1/2 -translate-y-1/2 pointer-events-none" />
            </div>
          </div>
        } 
      />

      <div className="w-full px-4 sm:px-6 lg:px-10 pt-4">
        {/* Active Filters Summary (Shown when any filter is active) */}
        {(selectedCategory !== 'All' || selectedStyle !== 'All' || maxPrice < 250000 || inStockOnly) && (
          <div className="mb-4 flex items-center gap-2 flex-wrap text-xs">
            <span className="text-gray-500 font-medium">Active filters:</span>

            {selectedCategory !== 'All' && (
              <span className="inline-flex items-center gap-1.5 bg-gray-950 text-white px-3 py-1 rounded-full text-xs font-semibold shadow-2xs">
                <span>Category: {selectedCategory}</span>
                <X className="w-3.5 h-3.5 cursor-pointer hover:text-red-300 transition-colors" onClick={() => handleCategorySelect('All')} />
              </span>
            )}

            {selectedStyle !== 'All' && (
              <span className="inline-flex items-center gap-1.5 bg-gray-900 text-white px-3 py-1 rounded-full text-xs font-semibold shadow-2xs">
                <span>Style: {selectedStyle}</span>
                <X className="w-3.5 h-3.5 cursor-pointer hover:text-red-300 transition-colors" onClick={() => setSelectedStyle('All')} />
              </span>
            )}

            {maxPrice < 250000 && (
              <span className="inline-flex items-center gap-1.5 bg-gray-900 text-white px-3 py-1 rounded-full text-xs font-semibold shadow-2xs">
                <span>Budget: ≤ ₹{maxPrice.toLocaleString('en-IN')}</span>
                <X className="w-3.5 h-3.5 cursor-pointer hover:text-red-300 transition-colors" onClick={() => setMaxPrice(250000)} />
              </span>
            )}

            {inStockOnly && (
              <span className="inline-flex items-center gap-1.5 bg-gray-900 text-white px-3 py-1 rounded-full text-xs font-semibold shadow-2xs">
                <span>In-Stock Only</span>
                <X className="w-3.5 h-3.5 cursor-pointer hover:text-red-300 transition-colors" onClick={() => setInStockOnly(false)} />
              </span>
            )}

            <button
              onClick={() => {
                handleCategorySelect('All')
                setSelectedStyle('All')
                setMaxPrice(250000)
                setInStockOnly(false)
              }}
              className="text-xs text-gray-500 hover:text-gray-950 underline ml-1 cursor-pointer font-medium"
            >
              Clear All
            </button>
          </div>
        )}

        {/* Catalog Header Info */}
        <div className="mb-3 flex items-center justify-between text-xs text-softgray">
          <div>
            Showing <strong className="text-walnut-900 font-bold">{filteredProducts.length}</strong> handcrafted pieces {selectedCategory !== 'All' ? `in ${selectedCategory}` : ''}
          </div>
          {selectedCategory !== 'All' && (
            <button
              onClick={() => handleCategorySelect('All')}
              className="text-xs font-semibold text-walnut-800 hover:text-gold-600 transition-colors"
            >
              ← Show All Categories
            </button>
          )}
        </div>

        {/* 100% FULL-WIDTH COMPACT PRODUCT GRID (No Bulky Sidebar!) */}
        <div className="w-full">
          {isLoading ? (
            <ProductGridSkeleton count={10} />
          ) : filteredProducts.length > 0 ? (
            <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-4 xl:grid-cols-5 gap-3 sm:gap-4">
              {filteredProducts.map(product => (
                <ProductCard key={product.id} product={product} layout="grid" />
              ))}
            </div>
          ) : (
            <div className="py-12 text-center px-4 bg-white rounded-2xl border border-walnut-100 shadow-2xs my-4 max-w-lg mx-auto">
              <div className="w-12 h-12 rounded-full bg-cream-100 flex items-center justify-center mx-auto mb-2 text-walnut-600">
                <Filter className="w-5 h-5" />
              </div>
              <h4 className="font-sans font-bold text-sm text-walnut-900 mb-1">No pieces found</h4>
              <p className="text-xs text-softgray mb-4">No items currently match this category or price range.</p>
              <Button
                variant="primary"
                size="sm"
                onClick={() => {
                  handleCategorySelect('All')
                  setSelectedStyle('All')
                  setMaxPrice(250000)
                  setSearchQuery('')
                }}
              >
                View Full Collection
              </Button>
            </div>
          )}
        </div>

      </div>

    </div>
  )
}
