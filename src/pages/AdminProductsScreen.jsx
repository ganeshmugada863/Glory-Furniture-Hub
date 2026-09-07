import React, { useState, useEffect } from 'react'
import Header from '../components/common/Header'
import Input from '../components/common/Input'
import Button from '../components/common/Button'
import Modal from '../components/common/Modal'
import Toast from '../components/common/Toast'
import { MOCK_PRODUCTS } from '../data/mockData'
import { dataService } from '../services/dataService'
import { Plus, Trash2, Check, Upload, Loader2, X, Ruler } from 'lucide-react'

const PRODUCT_TYPES = [
  { id: 'Cot / Wooden Bed', label: 'Cot / Wooden Bed', defaultCategory: 'Cot / Wooden Bed', defaultMaterial: 'Solid Teak Wood' },
  { id: 'Dressing Table', label: 'Dressing Table', defaultCategory: 'Dressing Table', defaultMaterial: 'Solid Teak Wood & Mirror' },
  { id: 'Sofa Set', label: 'Sofa Set', defaultCategory: 'Sofa Set', defaultMaterial: 'Solid Teak Frame & Cushions' },
  { id: 'Headboard', label: 'Headboard', defaultCategory: 'Headboard', defaultMaterial: 'Solid Carved Teak Wood' },
  { id: 'Dining Table', label: 'Dining Table', defaultCategory: 'Dining Table', defaultMaterial: 'Solid Teak Wood' },
  { id: 'Dining Chairs', label: 'Dining Chairs', defaultCategory: 'Dining Chairs', defaultMaterial: 'Solid Teak & Cane' },
  { id: 'Pooja Mandir', label: 'Pooja Mandir', defaultCategory: 'Pooja Mandir', defaultMaterial: 'Pure Burma Teak Wood' },
  { id: 'Podimes', label: 'Podimes (Traditional Low Bench / Stool)', defaultCategory: 'Podimes', defaultMaterial: 'Solid Burma Teak Wood' },
]

export default function AdminProductsScreen() {
  const [products, setProducts] = useState(MOCK_PRODUCTS)
  const [isAddModalOpen, setIsAddModalOpen] = useState(false)
  
  // Product Type selection
  const [selectedProductType, setSelectedProductType] = useState('Cot / Wooden Bed')
  const [newProductName, setNewProductName] = useState('')
  const [newProductPrice, setNewProductPrice] = useState('')
  const [newProductCategory, setNewProductCategory] = useState('Cot / Wooden Bed')
  const [newProductMaterial, setNewProductMaterial] = useState('Solid Teak Wood')
  const [newProductDimensions, setNewProductDimensions] = useState('210cm W × 220cm D × 140cm H')
  const [newProductDescription, setNewProductDescription] = useState('')
  const [uploadedImage, setUploadedImage] = useState('')
  const [isFeatured, setIsFeatured] = useState(true)
  const [isNewArrival, setIsNewArrival] = useState(true)
  const [isUploadingImage, setIsUploadingImage] = useState(false)
  const [isSaving, setIsSaving] = useState(false)
  const [toastMessage, setToastMessage] = useState('')

  // Dynamic Bed Size & Price Variants (First size and price present initially)
  const [bedVariants, setBedVariants] = useState([
    { size: '6/6 ft (King)', price: '99999' }
  ])

  useEffect(() => {
    async function loadProducts() {
      const { data } = await dataService.getProducts()
      if (data && data.length > 0) setProducts(data)
    }
    loadProducts()
  }, [])

  // When Product Type changes, sync category & defaults
  const handleProductTypeChange = (type) => {
    setSelectedProductType(type)
    const found = PRODUCT_TYPES.find(p => p.id === type)
    if (found) {
      setNewProductCategory(found.defaultCategory)
      setNewProductMaterial(found.defaultMaterial)
    }
  }

  // Bed Variant Handlers
  const handleAddBedVariant = () => {
    const nextIndex = bedVariants.length
    const defaultSizes = ['6/6 ft (King)', '5/6 ft (Queen)', '4/6 ft (Double)', '3/6 ft (Single)']
    const suggestedSize = defaultSizes[nextIndex] || `Size #${nextIndex + 1}`
    setBedVariants([...bedVariants, { size: suggestedSize, price: '' }])
  }

  const handleRemoveBedVariant = (index) => {
    if (bedVariants.length > 1) {
      setBedVariants(bedVariants.filter((_, idx) => idx !== index))
    }
  }

  const handleBedVariantChange = (index, field, value) => {
    const updated = [...bedVariants]
    updated[index][field] = value
    setBedVariants(updated)
  }

  const handleDeleteProduct = async (id, name) => {
    if (confirm(`Are you sure you want to delete "${name}" from the catalog?`)) {
      await dataService.deleteProduct(id)
      setProducts(prev => prev.filter(p => p.id !== id && String(p.id) !== String(id)))
      setToastMessage(`Product "${name}" removed.`)
    }
  }

  const handleImageUpload = async (e) => {
    const file = e.target.files?.[0]
    if (!file) return
    setIsUploadingImage(true)
    try {
      const { publicUrl } = await dataService.uploadProductImage(file)
      if (publicUrl) {
        setUploadedImage(publicUrl)
        setToastMessage('Photo selected & ready!')
      } else {
        setToastMessage('Could not upload image.')
      }
    } catch (err) {
      console.error(err)
      setToastMessage('Image upload failed.')
    } finally {
      setIsUploadingImage(false)
    }
  }

  const handleAddProduct = async (e) => {
    e.preventDefault()
    if (!newProductName.trim()) {
      setToastMessage('Please enter a product title.')
      return
    }

    let finalPrice = Number(newProductPrice) || 25000
    let finalDimensions = newProductDimensions || 'Standard Dimensions'
    let finalSizeVariants = []

    const isBedType = selectedProductType === 'Cot / Wooden Bed' || selectedProductType === 'Bed'

    if (isBedType) {
      finalSizeVariants = bedVariants
        .filter(v => v.size.trim())
        .map(v => ({ size: v.size.trim(), price: Number(v.price) || 0 }))

      if (finalSizeVariants.length === 0) {
        setToastMessage('Please enter at least one size and price for the bed.')
        return
      }

      // First size price becomes base product price
      finalPrice = finalSizeVariants[0].price
      finalDimensions = finalSizeVariants.map(v => v.size).join(', ')
    }

    setIsSaving(true)
    try {
      const newP = {
        name: newProductName.trim(),
        price: finalPrice,
        category: newProductCategory,
        roomType: newProductCategory,
        material: newProductMaterial || 'Solid Wood',
        style: 'Modern Minimalist',
        dimensions: finalDimensions,
        leadTime: '5 - 7 Days Delivery',
        description: newProductDescription || 'Masterfully carved handcrafted wooden furniture piece.',
        inStock: true,
        rating: 5.0,
        reviewCount: 1,
        featured: isFeatured,
        newArrival: isNewArrival,
        sizeVariants: finalSizeVariants,
        images: [
          uploadedImage || 
          (isBedType 
            ? 'https://images.unsplash.com/photo-1505693416388-ac5ce068fe85?auto=format&fit=crop&w=800&q=80'
            : 'https://images.unsplash.com/photo-1555041469-a586c61ea9bc?auto=format&fit=crop&w=800&q=80')
        ]
      }

      const { data: createdProduct } = await dataService.createProduct(newP)
      const finalProduct = createdProduct || { ...newP, id: Date.now() }

      setProducts(prev => [finalProduct, ...prev.filter(p => p.id !== finalProduct.id)])
      setIsAddModalOpen(false)
      setToastMessage(`Product "${finalProduct.name}" published! Live on website now.`)
      
      // Reset Form
      setNewProductName('')
      setNewProductPrice('')
      setUploadedImage('')
      setNewProductDescription('')
      setIsFeatured(true)
      setIsNewArrival(true)
      setBedVariants([{ size: '6/6 ft (King)', price: '99999' }])
    } catch (err) {
      console.error('Error creating product:', err)
      setToastMessage('Failed to save product.')
    } finally {
      setIsSaving(false)
    }
  }

  return (
    <div className="min-h-screen bg-cream-100 pb-28">
      <Header title="Manage Products" showBack={true} />
      <Toast message={toastMessage} onClose={() => setToastMessage('')} />

      <div className="px-5 py-3 flex items-center justify-between bg-white border-b border-walnut-100">
        <span className="text-xs text-softgray">Total Listings: <strong className="text-walnut-800">{products.length}</strong></span>
        <Button
          variant="accent"
          size="sm"
          onClick={() => setIsAddModalOpen(true)}
          icon={Plus}
        >
          Add New Piece
        </Button>
      </div>

      <div className="px-5 py-4 space-y-3 max-w-md mx-auto">
        {products.map(p => {
          const hasVariants = Array.isArray(p.sizeVariants) && p.sizeVariants.length > 0
          return (
            <div key={p.id} className="bg-white p-3.5 rounded-2xl border border-walnut-100 shadow-card flex items-center gap-3">
              <img 
                src={p.images && p.images[0] ? p.images[0] : 'https://images.unsplash.com/photo-1555041469-a586c61ea9bc?auto=format&fit=crop&w=800&q=80'} 
                alt={p.name} 
                className="w-14 h-14 object-cover rounded-xl bg-cream-200" 
              />
              <div className="flex-1 min-w-0">
                <h4 className="font-sans font-bold text-xs text-walnut-900 truncate">{p.name}</h4>
                <span className="text-[10px] text-softgray block truncate">
                  {p.category} • {p.material}
                  {hasVariants ? ` • ${p.sizeVariants.length} Sizes` : ''}
                </span>
                <span className="font-sans font-bold text-xs text-gold-600 block">
                  ₹{Number(p.price).toLocaleString('en-IN')}
                  {hasVariants ? <span className="text-[10px] text-softgray font-normal ml-1">(Starting)</span> : ''}
                </span>
              </div>
              <div className="flex items-center gap-1">
                <button
                  onClick={() => handleDeleteProduct(p.id, p.name)}
                  className="p-1.5 text-softgray hover:text-dustyrose active-tap"
                  title="Delete Product"
                >
                  <Trash2 className="w-4 h-4" />
                </button>
              </div>
            </div>
          )
        })}
      </div>

      {/* Add Product Modal */}
      <Modal
        isOpen={isAddModalOpen}
        onClose={() => setIsAddModalOpen(false)}
        title="Publish New Catalog Piece"
        position="bottom"
      >
        <form onSubmit={handleAddProduct} className="space-y-3.5 max-h-[82vh] overflow-y-auto pr-1">
          
          {/* 1. SELECT PRODUCT TYPE (Main requirement) */}
          <div>
            <label className="block text-[11px] font-bold text-walnut-900 mb-1">
              Select Product Type *
            </label>
            <select
              value={selectedProductType}
              onChange={(e) => handleProductTypeChange(e.target.value)}
              className="w-full text-xs p-2.5 bg-cream-100 border border-walnut-300 rounded-xl font-semibold text-walnut-900 focus:ring-2 focus:ring-walnut-500"
            >
              {PRODUCT_TYPES.map(pt => (
                <option key={pt.id} value={pt.id}>{pt.label}</option>
              ))}
            </select>
          </div>

          <Input
            label="Product Title *"
            type="text"
            required
            value={newProductName}
            onChange={(e) => setNewProductName(e.target.value)}
            placeholder={(selectedProductType === 'Cot / Wooden Bed' || selectedProductType === 'Bed') ? 'e.g. Royal Teak King Bed' : `e.g. Handcrafted ${selectedProductType}`}
          />

          {/* 2. BED SIZE & COST VARIANTS (Only when Cot / Wooden Bed is selected) */}
          {(selectedProductType === 'Cot / Wooden Bed' || selectedProductType === 'Bed') ? (
            <div className="bg-[#F8F4EC] p-3.5 rounded-2xl border border-walnut-200/80 space-y-3">
              <div className="flex items-center justify-between">
                <div>
                  <label className="text-xs font-bold text-walnut-900 flex items-center gap-1">
                    <Ruler className="w-3.5 h-3.5 text-gold-600" />
                    Bed Sizes & Prices
                  </label>
                  <span className="text-[10px] text-softgray block">
                    Click '+' to add another size variant and price
                  </span>
                </div>
                
                {/* '+' Symbol button next to Bed Size to add new rows */}
                <button
                  type="button"
                  onClick={handleAddBedVariant}
                  className="flex items-center gap-1 text-[11px] bg-walnut-900 hover:bg-walnut-800 text-gold-400 font-bold px-3 py-1.5 rounded-xl shadow-sm active-tap"
                  title="Add Another Bed Size & Price"
                >
                  <Plus className="w-3.5 h-3.5" />
                  <span>Add Size (+)</span>
                </button>
              </div>

              {/* Variant Rows with Size and Price */}
              <div className="space-y-2.5">
                {bedVariants.map((variant, index) => (
                  <div key={index} className="bg-white p-3 rounded-xl border border-walnut-200/70 shadow-sm space-y-2 relative">
                    <div className="flex items-center justify-between">
                      <span className="text-[10px] font-bold uppercase tracking-wider text-walnut-800 bg-cream-100 px-2 py-0.5 rounded">
                        Size Variant #{index + 1}
                      </span>
                      {bedVariants.length > 1 && (
                        <button
                          type="button"
                          onClick={() => handleRemoveBedVariant(index)}
                          className="p-1 text-softgray hover:text-dustyrose rounded-md transition-colors"
                          title="Remove this size"
                        >
                          <Trash2 className="w-3.5 h-3.5" />
                        </button>
                      )}
                    </div>

                    <div>
                      <label className="block text-[10px] font-semibold text-walnut-700 mb-0.5">
                        Bed Size *
                      </label>
                      <input
                        type="text"
                        required
                        value={variant.size}
                        onChange={(e) => handleBedVariantChange(index, 'size', e.target.value)}
                        placeholder={
                          index === 0 ? "6/6 ft (King)" : 
                          index === 1 ? "5/6 ft (Queen)" : 
                          index === 2 ? "4/6 ft (Double)" : "3/6 ft (Single)"
                        }
                        className="w-full text-xs p-2 bg-cream-50 border border-walnut-200 rounded-lg text-walnut-900 focus:outline-none focus:ring-1 focus:ring-walnut-500 font-medium"
                      />
                    </div>

                    <div>
                      <label className="block text-[10px] font-semibold text-walnut-700 mb-0.5">
                        Cost for {variant.size || `Size #${index + 1}`} (₹) *
                      </label>
                      <input
                        type="number"
                        required
                        value={variant.price}
                        onChange={(e) => handleBedVariantChange(index, 'price', e.target.value)}
                        placeholder={index === 0 ? "99999" : index === 1 ? "85000" : "72000"}
                        className="w-full text-xs p-2 bg-cream-50 border border-walnut-200 rounded-lg text-walnut-900 focus:outline-none focus:ring-1 focus:ring-walnut-500 font-medium"
                      />
                    </div>
                  </div>
                ))}
              </div>
            </div>
          ) : (
            /* 3. NON-BED ITEMS (Chair, Sofa, Dining Set, etc.) -> ONLY SINGLE PRICE */
            <Input
              label="Price (₹) *"
              type="number"
              required
              value={newProductPrice}
              onChange={(e) => setNewProductPrice(e.target.value)}
              placeholder="38000"
            />
          )}

          <div>
            <label className="block text-[11px] font-semibold text-walnut-700 mb-1">Furniture Category</label>
            <select
              value={newProductCategory}
              onChange={(e) => setNewProductCategory(e.target.value)}
              className="w-full text-xs p-2.5 bg-cream-100 border border-walnut-200 rounded-xl"
            >
              {PRODUCT_TYPES.map(pt => (
                <option key={pt.id} value={pt.id}>{pt.label}</option>
              ))}
            </select>
          </div>

          <Input
            label="Material & Wood Species"
            type="text"
            value={newProductMaterial}
            onChange={(e) => setNewProductMaterial(e.target.value)}
            placeholder="Solid Teak Wood"
          />

          {!(selectedProductType === 'Cot / Wooden Bed' || selectedProductType === 'Bed') && (
            <Input
              label="Dimensions"
              type="text"
              value={newProductDimensions}
              onChange={(e) => setNewProductDimensions(e.target.value)}
              placeholder="e.g. 150cm W × 80cm D × 75cm H"
            />
          )}

          {/* Image Upload Area with Live Preview */}
          <div>
            <label className="block text-[11px] font-semibold text-walnut-700 mb-1">Product Photo</label>
            {uploadedImage ? (
              <div className="relative border-2 border-solid border-walnut-300 rounded-xl overflow-hidden bg-cream-100 p-2 flex items-center gap-3">
                <img src={uploadedImage} alt="Preview" className="w-16 h-16 object-cover rounded-lg border border-walnut-200" />
                <div className="flex-1 min-w-0">
                  <span className="text-xs text-walnut-900 font-semibold block">Photo Ready ✓</span>
                  <span className="text-[10px] text-softgray block truncate">Ready to publish</span>
                </div>
                <button
                  type="button"
                  onClick={() => setUploadedImage('')}
                  className="p-1 text-softgray hover:text-dustyrose rounded-full hover:bg-cream-200 transition-colors"
                >
                  <X className="w-4 h-4" />
                </button>
              </div>
            ) : (
              <label className="border-2 border-dashed border-walnut-300 hover:border-walnut-500 bg-cream-100 p-4 rounded-xl flex flex-col items-center justify-center gap-1.5 cursor-pointer transition-colors">
                {isUploadingImage ? (
                  <Loader2 className="w-5 h-5 text-gold-600 animate-spin" />
                ) : (
                  <Upload className="w-5 h-5 text-gold-600" />
                )}
                <span className="text-xs text-walnut-800 font-medium">
                  {isUploadingImage ? 'Attaching photo...' : 'Click to upload image file'}
                </span>
                <span className="text-[10px] text-softgray">JPG, PNG, WebP supported</span>
                <input 
                  type="file" 
                  accept="image/*" 
                  onChange={handleImageUpload} 
                  disabled={isUploadingImage}
                  className="hidden" 
                />
              </label>
            )}
          </div>

          <div>
            <label className="block text-[11px] font-semibold text-walnut-700 mb-1">Craftsmanship Description</label>
            <textarea
              rows="2"
              value={newProductDescription}
              onChange={(e) => setNewProductDescription(e.target.value)}
              placeholder="Handcrafted details, joinery, finish..."
              className="w-full text-xs p-2.5 bg-cream-100 border border-walnut-200 rounded-xl"
            />
          </div>

          {/* Visibility Checkboxes */}
          <div className="bg-cream-200/50 p-3 rounded-xl space-y-2 border border-walnut-200/50">
            <label className="flex items-center gap-2 cursor-pointer text-xs text-walnut-800">
              <input
                type="checkbox"
                checked={isFeatured}
                onChange={(e) => setIsFeatured(e.target.checked)}
                className="rounded text-walnut-600 focus:ring-walnut-500"
              />
              <span className="font-semibold">Show on Home Screen (Featured)</span>
            </label>
            <label className="flex items-center gap-2 cursor-pointer text-xs text-walnut-800">
              <input
                type="checkbox"
                checked={isNewArrival}
                onChange={(e) => setIsNewArrival(e.target.checked)}
                className="rounded text-walnut-600 focus:ring-walnut-500"
              />
              <span>Mark as New Arrival</span>
            </label>
          </div>

          <Button
            type="submit"
            variant="primary"
            size="lg"
            className="w-full mt-2"
            disabled={isSaving || isUploadingImage}
            icon={isSaving ? Loader2 : Check}
          >
            {isSaving ? 'Publishing Piece...' : 'Save & Publish Listing'}
          </Button>
        </form>
      </Modal>
    </div>
  )
}
