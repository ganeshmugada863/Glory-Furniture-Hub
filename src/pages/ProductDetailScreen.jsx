import React, { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import Header from '../components/common/Header'
import Badge from '../components/common/Badge'
import Button from '../components/common/Button'
import Toast from '../components/common/Toast'
import Modal from '../components/common/Modal'
import ProductCard from '../components/common/ProductCard'
import { dataService } from '../services/dataService'
import { useAppStore } from '../store/useAppStore'
import { Star, Sparkles, Share2, Check, ArrowRight, Shield, Truck, Clock, Maximize2, ShoppingBag, Grid, Ruler, TreePine, Award, Leaf, HeartHandshake, Heart } from 'lucide-react'

export default function ProductDetailScreen() {
  const { id } = useParams()
  const navigate = useNavigate()
  const { openAIChat, wishlist, toggleWishlist } = useAppStore()

  // Instant synchronous initialization (0ms delay)
  const [product, setProduct] = useState(() => dataService.getInstantProductById(id))
  const [similarProducts, setSimilarProducts] = useState([])
  const [selectedImage, setSelectedImage] = useState(0)
  const [activeTab, setActiveTab] = useState('description')
  const [selectedBedSize, setSelectedBedSize] = useState('6/6 ft (King)')
  const [selectedWoodType, setSelectedWoodType] = useState('Teak Wood')
  const [isFullImageModalOpen, setIsFullImageModalOpen] = useState(false)
  const [toastMessage, setToastMessage] = useState('')

  const bedSizes = ['6/6 ft (King)', '5/6 ft (Queen)', '4/6 ft (Double)', '3/6 ft (Single)']
  const woodTypes = ['Teak Wood', 'American Walnut', 'Rosewood (Sheesham)', 'Mahogany', 'White Oak']

  // Update immediately when route ID changes
  useEffect(() => {
    const instant = dataService.getInstantProductById(id)
    if (instant) {
      setProduct(instant)
      setSelectedImage(0)
    }
  }, [id])

  useEffect(() => {
    let active = true

    async function loadProductData() {
      // 1. If not yet resolved, fetch single product
      let activeProduct = product || dataService.getInstantProductById(id)
      if (!activeProduct) {
        const { data } = await dataService.getProductById(id)
        if (active && data) {
          activeProduct = data
          setProduct(data)
        }
      }

      // 2. Fetch catalog for similar recommendations without blocking main product view
      const { data: allProducts } = await dataService.getProducts()
      if (!active || !allProducts || !activeProduct) return

      const matches = allProducts.filter(p => {
        if (String(p.id) === String(activeProduct.id)) return false
        const sameCategory = p.category === activeProduct.category
        const sameRoom = p.roomType === activeProduct.roomType
        const sameMaterial = p.material && activeProduct.material && p.material.toLowerCase().includes(activeProduct.material.split(' ')[0].toLowerCase())
        return sameCategory || sameRoom || sameMaterial
      })
      setSimilarProducts(matches.length > 0 ? matches : allProducts.filter(p => String(p.id) !== String(activeProduct.id)))
    }

    loadProductData()
    window.scrollTo({ top: 0, behavior: 'instant' })
    return () => { active = false }
  }, [id])

  if (!product) {
    return (
      <div className="min-h-screen bg-[#FDFBF7] flex items-center justify-center p-6">
        <p className="text-xs text-softgray font-medium">Loading handcrafted piece details...</p>
      </div>
    )
  }

  const isBedProduct = Boolean(
    product.category === 'Cot / Wooden Bed' ||
    product.category === 'Bedroom' || 
    (product.category && product.category.toLowerCase().includes('bed')) ||
    (product.category && product.category.toLowerCase().includes('cot')) ||
    (product.name && product.name.toLowerCase().includes('bed')) || 
    (product.name && product.name.toLowerCase().includes('cot')) ||
    (product.sizeVariants && product.sizeVariants.length > 0)
  )

  const sizeOptions = (product.sizeVariants && product.sizeVariants.length > 0)
    ? product.sizeVariants
    : (isBedProduct
      ? [
          { size: '6/6 ft (King)', price: product.price },
          { size: '5/6 ft (Queen)', price: Math.round(product.price * 0.88) },
          { size: '4/6 ft (Double)', price: Math.round(product.price * 0.75) },
          { size: '3/6 ft (Single)', price: Math.round(product.price * 0.60) }
        ]
      : [])

  useEffect(() => {
    if (sizeOptions.length > 0 && (!selectedBedSize || !sizeOptions.some(s => s.size === selectedBedSize))) {
      setSelectedBedSize(sizeOptions[0].size)
    }
  }, [product, sizeOptions])

  const activeVariant = sizeOptions.find(v => v.size === selectedBedSize) || sizeOptions[0]
  const currentPrice = activeVariant ? activeVariant.price : product.price
  const formattedPrice = `₹${currentPrice.toLocaleString('en-IN')}`

  const isWishlisted = wishlist.some(item => item.id === product.id)

  const handleBookNow = () => {
    let url = `/booking?productId=${product.id}&price=${currentPrice}`
    if (isBedProduct && selectedBedSize) {
      url += `&bedSize=${encodeURIComponent(selectedBedSize)}&woodType=${encodeURIComponent(selectedWoodType)}`
    }
    navigate(url)
  }

  return (
    <div className="min-h-screen bg-[#FDFBF7] text-walnut-900 pb-24 md:pb-16 w-full font-sans">
      <Header title="Product Details" showBack={true} />
      <Toast message={toastMessage} onClose={() => setToastMessage('')} />

      <div className="w-full px-4 sm:px-8 lg:px-12 space-y-10 pt-6">
        
        {/* TOP SECTION: 2-COLUMN MAIN PRODUCT SHOWCASE (Matching Reference UI Aesthetic) */}
        <div className="lg:grid lg:grid-cols-12 lg:gap-10 lg:items-start">
          
          {/* LEFT Column: Large Photography Gallery Container (Spans 7 cols) */}
          <div className="space-y-4 lg:col-span-7">
            <div className="relative bg-[#F2ECE4] aspect-[4/3] w-full overflow-hidden rounded-3xl border border-walnut-200/50 shadow-sm group">
              <img
                src={product.images[selectedImage] || product.images[0]}
                alt={product.name}
                className="w-full h-full object-cover transition-all duration-300"
              />

              <button
                onClick={() => setIsFullImageModalOpen(true)}
                className="absolute bottom-4 right-4 p-2.5 bg-walnut-900/80 backdrop-blur-md text-white rounded-xl text-xs flex items-center gap-1.5 active-tap shadow-md"
              >
                <Maximize2 className="w-4 h-4" /> Fullscreen View
              </button>

              <div className="absolute top-4 right-4 flex items-center gap-2 z-10">
                <button
                  onClick={() => toggleWishlist(product)}
                  className="p-2.5 bg-white/90 backdrop-blur-md rounded-full shadow-md text-walnut-800 active-tap hover:bg-white transition-all"
                  title="Toggle Wishlist"
                >
                  <Heart className={`w-4 h-4 ${isWishlisted ? 'fill-dustyrose text-dustyrose' : 'text-walnut-800'}`} />
                </button>
                <button
                  onClick={() => navigator.share?.({ title: product.name, url: window.location.href })}
                  className="p-2.5 bg-white/90 backdrop-blur-md rounded-full shadow-md text-walnut-800 active-tap hover:bg-white transition-all"
                  title="Share Product"
                >
                  <Share2 className="w-4 h-4" />
                </button>
              </div>
            </div>

            {/* Thumbnail Rail */}
            {product.images.length > 1 && (
              <div className="flex gap-3">
                {product.images.map((img, idx) => (
                  <button
                    key={idx}
                    onClick={() => setSelectedImage(idx)}
                    className={`w-20 h-20 rounded-2xl overflow-hidden border-2 shadow-sm transition-all ${
                      selectedImage === idx ? 'border-walnut-900 scale-105 ring-2 ring-gold-500/30' : 'border-white opacity-70 hover:opacity-100'
                    }`}
                  >
                    <img src={img} alt="" className="w-full h-full object-cover" />
                  </button>
                ))}
              </div>
            )}
          </div>

          {/* RIGHT Column: Product Details Card (Spans 5 cols) */}
          <div className="space-y-6 mt-6 lg:mt-0 lg:col-span-5">
            <div className="bg-[#F7F2EB] p-6 sm:p-8 rounded-3xl border border-walnut-200/50 shadow-sm space-y-5">
              
              <div className="flex items-center justify-between gap-2">
                <span className="text-xs font-semibold uppercase tracking-widest text-gold-600 bg-white/80 px-3 py-1 rounded-full border border-walnut-200/40">
                  {product.category}
                </span>
                
                <div className="flex items-center gap-1 text-xs text-walnut-800 font-semibold">
                  <Star className="w-4 h-4 fill-gold-500 text-gold-500" />
                  <span>{product.rating}</span>
                  <span className="text-softgray text-xs">({product.reviewCount} reviews)</span>
                </div>
              </div>

              <div>
                <h1 className="font-serif font-bold text-2xl sm:text-3xl lg:text-4xl text-walnut-900 leading-tight mb-2">
                  {product.name}
                </h1>

                <div className="flex items-baseline gap-2">
                  <span className="font-sans font-bold text-2xl sm:text-3xl text-walnut-900">{formattedPrice}</span>
                  <span className="text-xs text-softgray">Tax included • Free delivery consultation</span>
                </div>
              </div>

              {/* BED SPECIFIC SELECTORS: BED SIZE (ft) & WOOD TYPE */}
              {isBedProduct && sizeOptions.length > 0 && (
                <div className="space-y-4 pt-4 border-t border-walnut-200/60">
                  {/* Bed Size Selector */}
                  <div>
                    <label className="block text-xs sm:text-sm font-semibold text-walnut-900 mb-2 flex items-center justify-between">
                      <span className="flex items-center gap-1.5">
                        <Ruler className="w-4 h-4 text-gold-600" /> Select Bed Size:
                      </span>
                      <span className="text-[11px] text-gold-700 font-bold bg-cream-200/80 px-2 py-0.5 rounded-md">
                        {selectedBedSize}
                      </span>
                    </label>
                    <div className="grid grid-cols-2 gap-2.5">
                      {sizeOptions.map(variant => {
                        const isSelected = selectedBedSize === variant.size
                        return (
                          <button
                            key={variant.size}
                            type="button"
                            onClick={() => setSelectedBedSize(variant.size)}
                            className={`p-3 rounded-2xl text-left border transition-all active-tap flex flex-col justify-between ${
                              isSelected
                                ? 'bg-walnut-900 text-white border-walnut-900 shadow-sm ring-2 ring-gold-500/30'
                                : 'bg-white text-walnut-900 border-walnut-200 hover:bg-cream-100 hover:border-walnut-300'
                            }`}
                          >
                            <div className="flex items-center justify-between w-full">
                              <span className="font-semibold text-xs sm:text-sm">{variant.size}</span>
                              {isSelected && <Check className="w-3.5 h-3.5 text-gold-400" />}
                            </div>
                            <span className={`text-xs font-bold mt-1.5 ${
                              isSelected ? 'text-gold-400' : 'text-gold-600'
                            }`}>
                              ₹{Number(variant.price).toLocaleString('en-IN')}
                            </span>
                          </button>
                        )
                      })}
                    </div>
                  </div>

                  {/* Wood Type Selector */}
                  <div>
                    <label className="block text-xs sm:text-sm font-semibold text-walnut-900 mb-2 flex items-center gap-1.5">
                      <TreePine className="w-4 h-4 text-gold-600" /> Select Wood Type:
                    </label>
                    <div className="flex flex-wrap gap-2">
                      {woodTypes.map(wood => (
                        <button
                          key={wood}
                          onClick={() => setSelectedWoodType(wood)}
                          className={`px-3.5 py-2 rounded-xl text-xs sm:text-sm font-medium border transition-all active-tap flex items-center gap-1.5 ${
                            selectedWoodType === wood
                              ? 'bg-walnut-900 text-gold-400 border-walnut-900 font-semibold shadow-sm'
                              : 'bg-white text-walnut-900 border-walnut-200 hover:bg-cream-100'
                          }`}
                        >
                          {selectedWoodType === wood && <Check className="w-3.5 h-3.5 text-gold-400" />}
                          {wood}
                        </button>
                      ))}
                    </div>
                  </div>
                </div>
              )}

              {/* PRIMARY "BOOK NOW" ACTION BUTTON */}
              <div className="pt-2">
                <Button
                  variant="primary"
                  size="lg"
                  onClick={handleBookNow}
                  className="w-full bg-walnut-900 hover:bg-walnut-800 text-white rounded-2xl py-4 font-semibold text-base shadow-md"
                  icon={ShoppingBag}
                >
                  Book Now
                </Button>
              </div>

              {/* Ask GloryAI Context Button */}
              <button
                onClick={() => openAIChat(product)}
                className="w-full py-3 px-4 bg-[#EFEAE2] hover:bg-[#E7E0D6] text-walnut-900 font-sans font-semibold text-xs sm:text-sm rounded-2xl shadow-sm transition-all active-tap flex items-center justify-between border border-walnut-200/60"
              >
                <div className="flex items-center gap-2">
                  <Sparkles className="w-4 h-4 text-gold-600 animate-spin-slow" />
                  <span>Ask GloryAI About Finishes & Room Styling</span>
                </div>
                <ArrowRight className="w-4 h-4 text-walnut-800" />
              </button>
            </div>
          </div>

        </div>

        {/* MIDDLE SECTION: Description & Specifications Tab Box */}
        <div className="bg-[#F7F2EB] rounded-3xl border border-walnut-200/50 shadow-sm overflow-hidden">
          <div className="flex border-b border-walnut-200/60 bg-[#EFEAE2]/60">
            {[
              { id: 'description', label: 'Description' },
              { id: 'dimensions', label: 'Dimensions & Wood' },
              { id: 'customization', label: 'Custom Options' }
            ].map(tab => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`py-3.5 px-6 text-xs sm:text-sm font-semibold tracking-wide transition-all ${
                  activeTab === tab.id
                    ? 'border-b-2 border-walnut-900 text-walnut-900 bg-[#F7F2EB] font-bold'
                    : 'text-softgray hover:text-walnut-900'
                }`}
              >
                {tab.label}
              </button>
            ))}
          </div>

          <div className="p-6 sm:p-8 text-xs sm:text-sm text-walnut-800 leading-relaxed">
            {activeTab === 'description' && (
              <p className="text-walnut-800 leading-relaxed text-sm">{product.description}</p>
            )}

            {activeTab === 'dimensions' && (
              <div className="space-y-3">
                <div className="flex justify-between py-2 border-b border-walnut-200/40">
                  <span className="font-semibold text-walnut-900">Dimensions:</span>
                  <span className="text-walnut-800">{product.dimensions}</span>
                </div>
                <div className="flex justify-between py-2 border-b border-walnut-200/40">
                  <span className="font-semibold text-walnut-900">Material:</span>
                  <span className="text-walnut-800">{product.material}</span>
                </div>
                <div className="flex justify-between py-2 border-b border-walnut-200/40">
                  <span className="font-semibold text-walnut-900">Style:</span>
                  <span className="text-walnut-800">{product.style}</span>
                </div>
                <div className="flex justify-between py-2">
                  <span className="font-semibold text-walnut-900">Lead Time:</span>
                  <span className="text-walnut-800">{product.leadTime}</span>
                </div>
              </div>
            )}

            {activeTab === 'customization' && (
              <div className="space-y-3">
                <p className="text-walnut-900 mb-2">Need tailored dimensions or custom finish stains?</p>
                <ul className="list-disc pl-5 space-y-1 text-walnut-800">
                  <li>Custom wood species (Teak, Mahogany, Oak, Walnut)</li>
                  <li>Made-to-measure width/depth adjustments</li>
                  <li>Custom stain & protective oil finishes</li>
                </ul>
                <button
                  onClick={() => navigate('/custom-request')}
                  className="mt-3 text-gold-600 font-semibold text-xs sm:text-sm underline flex items-center gap-1"
                >
                  Submit Custom Specification Request →
                </button>
              </div>
            )}
          </div>
        </div>

        {/* BOTTOM SECTION: 4 Trust Value Badges (Matching Reference UI Theme) */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
          <div className="bg-[#F7F2EB] p-5 rounded-2xl border border-walnut-200/50 flex items-start gap-3.5">
            <Award className="w-6 h-6 text-gold-600 flex-shrink-0 mt-0.5" />
            <div>
              <h4 className="font-serif font-bold text-sm text-walnut-900 mb-0.5">High Quality Materials</h4>
              <p className="text-xs text-softgray leading-snug">Built to last with kiln-dried solid teak & walnut wood.</p>
            </div>
          </div>

          <div className="bg-[#F7F2EB] p-5 rounded-2xl border border-walnut-200/50 flex items-start gap-3.5">
            <Sparkles className="w-6 h-6 text-gold-600 flex-shrink-0 mt-0.5" />
            <div>
              <h4 className="font-serif font-bold text-sm text-walnut-900 mb-0.5">Modern & Timeless Design</h4>
              <p className="text-xs text-softgray leading-snug">Handcrafted furniture that fits every space and aesthetic.</p>
            </div>
          </div>

          <div className="bg-[#F7F2EB] p-5 rounded-2xl border border-walnut-200/50 flex items-start gap-3.5">
            <Leaf className="w-6 h-6 text-gold-600 flex-shrink-0 mt-0.5" />
            <div>
              <h4 className="font-serif font-bold text-sm text-walnut-900 mb-0.5">Sustainable Sourcing</h4>
              <p className="text-xs text-softgray leading-snug">Eco-friendly responsibly harvested natural timber.</p>
            </div>
          </div>

          <div className="bg-[#F7F2EB] p-5 rounded-2xl border border-walnut-200/50 flex items-start gap-3.5">
            <HeartHandshake className="w-6 h-6 text-gold-600 flex-shrink-0 mt-0.5" />
            <div>
              <h4 className="font-serif font-bold text-sm text-walnut-900 mb-0.5">Customer Satisfaction</h4>
              <p className="text-xs text-softgray leading-snug">Trusted by thousands of happy home owners.</p>
            </div>
          </div>
        </div>

        {/* Similar & Matching Handcrafted Products Section */}
        {similarProducts.length > 0 && (
          <div className="pt-8 border-t border-walnut-200/60 space-y-6">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="font-serif font-bold text-xl md:text-2xl text-walnut-900">Similar & Matching Pieces</h3>
                <p className="text-xs text-softgray">Complements your {product.category.toLowerCase()} design</p>
              </div>
              <button onClick={() => navigate('/catalog')} className="text-xs font-semibold text-walnut-800 hover:text-gold-600 flex items-center gap-1">
                <Grid className="w-4 h-4" /> View Full Catalog
              </button>
            </div>

            <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-4 gap-5 md:gap-6">
              {similarProducts.slice(0, 4).map(rel => (
                <ProductCard key={rel.id} product={rel} layout="grid" />
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Fullscreen Image Viewer Modal */}
      <Modal
        isOpen={isFullImageModalOpen}
        onClose={() => setIsFullImageModalOpen(false)}
        title={product.name}
        position="center"
      >
        <div className="aspect-square w-full max-w-xl mx-auto overflow-hidden rounded-3xl bg-[#F2ECE4]">
          <img
            src={product.images[selectedImage] || product.images[0]}
            alt={product.name}
            className="w-full h-full object-cover"
          />
        </div>
      </Modal>
    </div>
  )
}
