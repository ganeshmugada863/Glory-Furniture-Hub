import React, { useState, useEffect, useMemo } from 'react'
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
  const [sortBy, setSortBy] = useState('popular')
  const [isFilterModalOpen, setIsFilterModalOpen] = useState(false)
  const [searchQuery, setSearchQuery] = useState('')

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

  // Filter products by category, style, price limit, and search query
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
      const matchesSearch = !searchQuery || pName.includes(searchQuery.toLowerCase()) || pDesc.includes(searchQuery.toLowerCase())

      return matchesCategory && matchesStyle && matchesPrice && matchesSearch
    }).sort((a, b) => {
      if (sortBy === 'price-low') return (a.price || 0) - (b.price || 0)
      if (sortBy === 'price-high') return (b.price || 0) - (a.price || 0)
      if (sortBy === 'rating') return (b.rating || 0) - (a.rating || 0)
      return (b.reviewCount || 0) - (a.reviewCount || 0)
    })
  }, [products, selectedCategory, selectedStyle, maxPrice, sortBy, searchQuery])

  const hasExtraFilters = selectedStyle !== 'All' || maxPrice < 250000

  return (
    <div className="min-h-screen bg-[#FDFBF7] text-walnut-900 pb-20 md:pb-12 w-full font-sans">
      <Header 
        title="Furniture Catalog" 
        rightAction={
          <div className="flex items-center gap-2">
            <span className="text-xs font-semibold text-gray-600 hidden sm:inline">Category:</span>
            <div className="relative">
              <select
                value={selectedCategory}
                onChange={(e) => handleCategorySelect(e.target.value)}
                className="appearance-none bg-white border border-gray-300 hover:border-gray-400 text-gray-900 text-xs sm:text-sm font-semibold rounded-full pl-3.5 pr-8 py-1.5 focus:outline-none focus:ring-2 focus:ring-gray-950 shadow-2xs cursor-pointer"
              >
                {categories.map(cat => (
                  <option key={cat} value={cat}>
                    {cat === 'All' ? 'All Categories' : cat}
                  </option>
                ))}
              </select>
              <ChevronDown className="w-3.5 h-3.5 text-gray-500 absolute right-2.5 top-1/2 -translate-y-1/2 pointer-events-none" />
            </div>
          </div>
        } 
      />

      <div className="w-full px-4 sm:px-6 lg:px-10 pt-4">
        {/* Active Filters Summary (Shown only when category is filtered) */}
        {selectedCategory !== 'All' && (
          <div className="mb-4 flex items-center gap-2 text-xs">
            <span className="text-gray-500 font-medium">Filtering by:</span>
            <span className="inline-flex items-center gap-1.5 bg-gray-950 text-white px-3 py-1 rounded-full text-xs font-semibold shadow-2xs">
              <span>{selectedCategory}</span>
              <X className="w-3.5 h-3.5 cursor-pointer hover:text-red-400 transition-colors" onClick={() => handleCategorySelect('All')} />
            </span>
            <button
              onClick={() => handleCategorySelect('All')}
              className="text-xs text-gray-500 hover:text-gray-900 underline ml-1 cursor-pointer"
            >
              Reset
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

      {/* Sleek Slide-over / Centered Filter Modal for Deep Options (Style & Price) */}
      <Modal
        isOpen={isFilterModalOpen}
        onClose={() => setIsFilterModalOpen(false)}
        title="Filter Handcrafted Collection"
        position="center"
      >
        <div className="space-y-4 text-xs">
          
          {/* Category Quick Select in Modal */}
          <div>
            <label className="block text-xs font-bold text-walnut-900 mb-2">Furniture Category</label>
            <div className="flex flex-wrap gap-1.5">
              {categories.map(cat => (
                <button
                  key={cat}
                  onClick={() => handleCategorySelect(cat)}
                  className={`px-3 py-1 rounded-full text-xs font-medium transition-all ${
                    selectedCategory === cat
                      ? 'bg-walnut-900 text-gold-400 font-bold'
                      : 'bg-cream-100 text-walnut-800 hover:bg-cream-200'
                  }`}
                >
                  {cat}
                </button>
              ))}
            </div>
          </div>

          {/* Style Filter */}
          <div>
            <label className="block text-xs font-bold text-walnut-900 mb-2">Woodworking Style</label>
            <div className="flex flex-wrap gap-1.5">
              {styles.map(st => (
                <button
                  key={st}
                  onClick={() => setSelectedStyle(st)}
                  className={`px-3 py-1 rounded-full text-xs font-medium transition-all ${
                    selectedStyle === st
                      ? 'bg-walnut-900 text-gold-400 font-bold'
                      : 'bg-cream-100 text-walnut-800 hover:bg-cream-200'
                  }`}
                >
                  {st}
                </button>
              ))}
            </div>
          </div>

          {/* Price Range Slider */}
          <div>
            <div className="flex items-center justify-between text-xs font-bold text-walnut-900 mb-1.5">
              <span>Maximum Budget:</span>
              <span className="text-gold-700 font-bold">₹{maxPrice.toLocaleString('en-IN')}</span>
            </div>
            <input
              type="range"
              min="10000"
              max="250000"
              step="5000"
              value={maxPrice}
              onChange={(e) => setMaxPrice(Number(e.target.value))}
              className="w-full accent-walnut-900 cursor-pointer"
            />
          </div>

          <div className="pt-3 border-t border-walnut-100 flex items-center gap-2">
            <Button
              variant="secondary"
              size="sm"
              className="flex-1"
              onClick={() => {
                setSelectedCategory('All')
                setSelectedStyle('All')
                setMaxPrice(250000)
              }}
            >
              Reset All
            </Button>
            <Button
              variant="primary"
              size="sm"
              className="flex-1"
              icon={Check}
              onClick={() => setIsFilterModalOpen(false)}
            >
              Show Results
            </Button>
          </div>

        </div>
      </Modal>

    </div>
  )
}
