import React, { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import ProductCard from '../components/common/ProductCard'
import Button from '../components/common/Button'
import { Search, X, ArrowLeft, Clock, Sparkles } from 'lucide-react'
import { RECENT_SEARCHES, POPULAR_SEARCHES } from '../data/mockData'
import { dataService } from '../services/dataService'
import { useAppStore } from '../store/useAppStore'

export default function SearchScreen() {
  const navigate = useNavigate()
  const { openAIChat } = useAppStore()
  const [query, setQuery] = useState('')
  const [products, setProducts] = useState([])
  const [recentTerms, setRecentTerms] = useState(RECENT_SEARCHES)

  useEffect(() => {
    async function loadProducts() {
      const { data } = await dataService.getProducts()
      if (data) setProducts(data)
    }
    loadProducts()

    const saved = localStorage.getItem('recentSearches')
    if (saved) {
      try { setRecentTerms(JSON.parse(saved)) } catch (e) {}
    }
  }, [])

  const handleSelectTerm = (term) => {
    setQuery(term)
    saveRecentTerm(term)
  }

  const saveRecentTerm = (term) => {
    if (!term.trim()) return
    const updated = [term, ...recentTerms.filter(t => t.toLowerCase() !== term.toLowerCase())].slice(0, 6)
    setRecentTerms(updated)
    localStorage.setItem('recentSearches', JSON.stringify(updated))
  }

  const results = query.trim()
    ? products.filter(p =>
        p.name.toLowerCase().includes(query.toLowerCase()) ||
        p.material.toLowerCase().includes(query.toLowerCase()) ||
        p.category.toLowerCase().includes(query.toLowerCase()) ||
        p.style.toLowerCase().includes(query.toLowerCase())
      )
    : []

  return (
    <div className="min-h-screen bg-cream-100 pb-28">
      {/* Search Header */}
      <div className="sticky top-0 z-30 bg-white border-b border-walnut-100 p-4 shadow-sm flex items-center gap-3">
        <button onClick={() => navigate(-1)} className="p-1 text-walnut-700 active-tap">
          <ArrowLeft className="w-5 h-5" />
        </button>
        
        <div className="relative flex-1">
          <Search className="w-4 h-4 text-softgray absolute left-3 top-3" />
          <input
            type="text"
            autoFocus
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && saveRecentTerm(query)}
            placeholder="Search products, materials, styles..."
            className="w-full text-xs bg-cream-100 border border-walnut-200 rounded-full pl-9 pr-9 py-2.5 focus:outline-none focus:ring-2 focus:ring-walnut-500 text-charcoal"
          />
          {query && (
            <button onClick={() => setQuery('')} className="absolute right-3 top-3 text-softgray">
              <X className="w-4 h-4" />
            </button>
          )}
        </div>
      </div>

      {!query ? (
        <div className="px-5 py-4 space-y-6">
          {/* Recent Searches */}
          <div>
            <h4 className="text-xs font-semibold text-walnut-800 mb-2 flex items-center gap-1.5">
              <Clock className="w-3.5 h-3.5 text-gold-600" /> Recent Searches
            </h4>
            <div className="flex flex-wrap gap-2">
              {recentTerms.map(term => (
                <button
                  key={term}
                  onClick={() => handleSelectTerm(term)}
                  className="px-3 py-1.5 bg-white border border-walnut-200/80 rounded-full text-xs text-walnut-700 hover:bg-cream-200 active-tap shadow-sm"
                >
                  {term}
                </button>
              ))}
            </div>
          </div>

          {/* Popular Searches */}
          <div>
            <h4 className="text-xs font-semibold text-walnut-800 mb-2">Popular Suggested Items</h4>
            <div className="flex flex-wrap gap-2">
              {POPULAR_SEARCHES.map(term => (
                <button
                  key={term}
                  onClick={() => handleSelectTerm(term)}
                  className="px-3 py-1.5 bg-cream-200 text-walnut-800 rounded-full text-xs font-medium hover:bg-walnut-500 hover:text-white active-tap transition-colors"
                >
                  {term}
                </button>
              ))}
            </div>
          </div>
        </div>
      ) : (
        <div className="px-5 py-4">
          <p className="text-xs text-softgray mb-3">
            Found <strong className="text-walnut-800">{results.length}</strong> results for "{query}"
          </p>

          {results.length > 0 ? (
            <div className="grid grid-cols-2 gap-3.5">
              {results.map(product => (
                <ProductCard key={product.id} product={product} layout="grid" />
              ))}
            </div>
          ) : (
            <div className="py-12 text-center px-4">
              <p className="text-xs text-softgray mb-4">No exact matches found for "{query}".</p>
              <Button
                variant="accent"
                size="md"
                onClick={() => openAIChat({ name: query })}
                icon={Sparkles}
                className="mx-auto"
              >
                Ask GloryAI to Find or Custom Build It
              </Button>
            </div>
          )}
        </div>
      )}
    </div>
  )
}
