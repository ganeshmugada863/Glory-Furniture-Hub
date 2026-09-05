import React, { useState, useEffect } from 'react'
import { useNavigate, useSearchParams } from 'react-router-dom'
import Input from '../components/common/Input'
import Button from '../components/common/Button'
import Modal from '../components/common/Modal'
import Toast from '../components/common/Toast'
import { useAppStore } from '../store/useAppStore'
import { dataService } from '../services/dataService'
import { MOCK_PRODUCTS } from '../data/mockData'
import { 
  ShoppingBag, Package, Hammer, LayoutDashboard, Plus, Trash2, Check, 
  Upload, Loader2, X, Ruler, LogOut, Phone, MapPin, Calendar, 
  TrendingUp, RefreshCw, MessageSquare, AlertCircle, Shield, Search,
  Eye, CheckCircle2, Clock, Sparkles, User, Mail, ShieldCheck, Edit3,
  Activity, FileText, Award, Lock, Receipt, Printer, Download, CreditCard,
  Share2, ExternalLink
} from 'lucide-react'

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

function getStoredInvoices() {
  try {
    const saved = localStorage.getItem('glory_invoices')
    if (saved) {
      const parsed = JSON.parse(saved)
      if (Array.isArray(parsed)) return parsed
    }
  } catch (e) {}
  return []
}


export default function AdminDashboardScreen() {
  const navigate = useNavigate()
  const [searchParams, setSearchParams] = useSearchParams()
  const tabParam = searchParams.get('tab') || 'products'

  const { user, setUser, userBookings, customRequests } = useAppStore()

  // Strict role security: Only admin can access this page
  useEffect(() => {
    if (!user || user.role !== 'admin') {
      navigate('/login', { replace: true })
    }
  }, [user, navigate])

  const [activeTab, setActiveTab] = useState(tabParam)
  const [toastMessage, setToastMessage] = useState('')

  // Sync tab with URL
  const handleTabChange = (tab) => {
    setActiveTab(tab)
    setSearchParams({ tab })
  }

  // =========================================================================
  // ADMIN PROFILE STATE & HANDLERS (DEDICATED FULL PAGE WORKSPACE)
  // =========================================================================
  const [isEditingAdminProfile, setIsEditingAdminProfile] = useState(false)
  const [adminName, setAdminName] = useState(user?.name || 'Master Studio Admin')
  const [adminPhone, setAdminPhone] = useState(user?.phone || '+91 98765 43210')
  const [adminEmail, setAdminEmail] = useState(user?.email || 'admin@gloryfurniture.com')
  const [adminStudioLocation, setAdminStudioLocation] = useState('Hyderabad Main Workshop & Studio, Jubilee Hills, Hyderabad')
  const [adminTitle, setAdminTitle] = useState('Master Craftsman & Studio Operations Director')
  const [adminBio, setAdminBio] = useState('Direct overseer of pure Burma teak procurement, traditional wood joinery, custom client commissions, and production quality control at Glory Furniture Hub.')
  const [adminHours, setAdminHours] = useState('Monday - Saturday: 9:30 AM - 8:30 PM | Sunday: By Appointment')

  // Inline edit state
  const [editAdminName, setEditAdminName] = useState(adminName)
  const [editAdminPhone, setEditAdminPhone] = useState(adminPhone)
  const [editAdminEmail, setEditAdminEmail] = useState(adminEmail)
  const [editAdminLocation, setEditAdminLocation] = useState(adminStudioLocation)
  const [editAdminTitle, setEditAdminTitle] = useState(adminTitle)
  const [editAdminBio, setEditAdminBio] = useState(adminBio)
  const [editAdminHours, setEditAdminHours] = useState(adminHours)

  useEffect(() => {
    if (user) {
      if (user.name) setAdminName(user.name)
      if (user.phone) setAdminPhone(user.phone)
      if (user.email) setAdminEmail(user.email)
    }
  }, [user])

  const handleStartEditProfile = () => {
    setEditAdminName(adminName)
    setEditAdminPhone(adminPhone)
    setEditAdminEmail(adminEmail)
    setEditAdminLocation(adminStudioLocation)
    setEditAdminTitle(adminTitle)
    setEditAdminBio(adminBio)
    setEditAdminHours(adminHours)
    setIsEditingAdminProfile(true)
  }

  const handleCancelEditProfile = () => {
    setIsEditingAdminProfile(false)
  }

  const handleSaveAdminProfile = (e) => {
    if (e) e.preventDefault()
    if (!editAdminName.trim()) {
      setToastMessage('Admin name cannot be empty')
      return
    }
    const updated = {
      ...user,
      name: editAdminName.trim(),
      phone: editAdminPhone.trim(),
      email: editAdminEmail.trim(),
    }
    setUser(updated)
    setAdminName(editAdminName.trim())
    setAdminPhone(editAdminPhone.trim())
    setAdminEmail(editAdminEmail.trim())
    setAdminStudioLocation(editAdminLocation.trim())
    setAdminTitle(editAdminTitle.trim())
    setAdminBio(editAdminBio.trim())
    setAdminHours(editAdminHours.trim())
    setIsEditingAdminProfile(false)
    setToastMessage('Admin Profile updated successfully!')
  }

  // =========================================================================
  // 1. PRODUCTS MANAGEMENT STATE & HANDLERS
  // =========================================================================
  const [products, setProducts] = useState(MOCK_PRODUCTS)
  const [isAddModalOpen, setIsAddModalOpen] = useState(false)
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
  const [productCategoryFilter, setProductCategoryFilter] = useState('All')
  const [productSearch, setProductSearch] = useState('')

  // Dynamic Bed Size & Price Variants (With '+' button to add more)
  const [bedVariants, setBedVariants] = useState([
    { size: '6/6 ft (King)', price: '99999' }
  ])

  useEffect(() => {
    async function loadAllProducts() {
      const { data } = await dataService.getProducts()
      if (data && data.length > 0) setProducts(data)
    }
    loadAllProducts()
  }, [])

  const handleProductTypeChange = (type) => {
    setSelectedProductType(type)
    const found = PRODUCT_TYPES.find(p => p.id === type)
    if (found) {
      setNewProductCategory(found.defaultCategory)
      setNewProductMaterial(found.defaultMaterial)
    }
  }

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

  const handleImageUpload = async (e) => {
    const file = e.target.files?.[0]
    if (!file) return
    setIsUploadingImage(true)
    try {
      const { publicUrl } = await dataService.uploadProductImage(file)
      if (publicUrl) {
        setUploadedImage(publicUrl)
        setToastMessage('Photo uploaded successfully!')
      } else {
        setToastMessage('Image upload failed.')
      }
    } catch (err) {
      console.error(err)
      setToastMessage('Could not upload image.')
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
      setToastMessage(`Product "${finalProduct.name}" published! Live on website.`)

      // Reset form
      setNewProductName('')
      setNewProductPrice('')
      setUploadedImage('')
      setNewProductDescription('')
      setBedVariants([{ size: '6/6 ft (King)', price: '99999' }])
    } catch (err) {
      console.error(err)
      setToastMessage('Failed to create product.')
    } finally {
      setIsSaving(false)
    }
  }

  const handleDeleteProduct = async (id, name) => {
    if (confirm(`Are you sure you want to delete "${name}" from the catalog?`)) {
      await dataService.deleteProduct(id)
      setProducts(prev => prev.filter(p => p.id !== id && String(p.id) !== String(id)))
      setToastMessage(`Product "${name}" removed.`)
    }
  }

  const filteredProducts = products.filter(p => {
    const matchesCat = productCategoryFilter === 'All' || p.category === productCategoryFilter
    const matchesSearch = !productSearch || p.name.toLowerCase().includes(productSearch.toLowerCase()) || (p.material && p.material.toLowerCase().includes(productSearch.toLowerCase()))
    return matchesCat && matchesSearch
  })

  // =========================================================================
  // 2. BOOKINGS & ORDERS STATE & HANDLERS
  // =========================================================================
  const [orders, setOrders] = useState(userBookings)
  const [orderStatusFilter, setOrderStatusFilter] = useState('All')

  const handleOrderStatusChange = (orderId, newStatus) => {
    setOrders(prev => prev.map(o => o.id === orderId ? { ...o, status: newStatus } : o))
    setToastMessage(`Order #${orderId} marked as ${newStatus}.`)
  }

  const filteredOrders = orderStatusFilter === 'All'
    ? orders
    : orders.filter(o => o.status === orderStatusFilter)

  // =========================================================================
  // 3. CUSTOM REQUESTS STATE & HANDLERS
  // =========================================================================
  const [requests, setRequests] = useState(customRequests)

  const handleRequestStatusChange = (reqId, newStatus) => {
    setRequests(prev => prev.map(r => r.id === reqId ? { ...r, status: newStatus } : r))
    setToastMessage(`Custom Spec #${reqId} updated to ${newStatus}.`)
  }

  // =========================================================================
  // 4. BILLING & INVOICE MANAGEMENT STATE & HANDLERS
  // =========================================================================
  const [invoices, setInvoices] = useState(getStoredInvoices)
  const [invoiceSearch, setInvoiceSearch] = useState('')
  const [invoiceStatusFilter, setInvoiceStatusFilter] = useState('All')
  const [isCreateInvoiceModalOpen, setIsCreateInvoiceModalOpen] = useState(false)
  const [selectedInvoiceForView, setSelectedInvoiceForView] = useState(null)

  // Keep orders synced with real user bookings from store
  useEffect(() => {
    setOrders(userBookings)
  }, [userBookings])

  // New Invoice Form State
  const [invCustomerName, setInvCustomerName] = useState('')
  const [invCustomerPhone, setInvCustomerPhone] = useState('')
  const [invCustomerEmail, setInvCustomerEmail] = useState('')
  const [invCustomerAddress, setInvCustomerAddress] = useState('')
  const [invItemTitle, setInvItemTitle] = useState('Royal Burma Teak King Cot (6x6 ft)')
  const [invCategory, setInvCategory] = useState('Cot / Wooden Bed')
  const [invMaterial, setInvMaterial] = useState('Solid Burma Teak Wood')
  const [invBaseAmount, setInvBaseAmount] = useState('95000')
  const [invGstRate, setInvGstRate] = useState(18)
  const [invAdvancePaid, setInvAdvancePaid] = useState('50000')
  const [invPaymentMethod, setInvPaymentMethod] = useState('UPI (GPay)')
  const [invNotes, setInvNotes] = useState('Includes 15-Year Burma Teak Wood & Termite Warranty.')

  const handleCreateInvoice = (e) => {
    e.preventDefault()
    if (!invCustomerName.trim() || !invItemTitle.trim() || !invBaseAmount) {
      setToastMessage('Please enter Customer Name, Item Title, and Base Price.')
      return
    }

    const base = Number(invBaseAmount) || 0
    const gstRate = Number(invGstRate) || 18
    const gstAmount = Math.round((base * gstRate) / 100)
    const totalAmount = base + gstAmount
    const advancePaid = Number(invAdvancePaid) || 0
    const balanceDue = Math.max(0, totalAmount - advancePaid)
    const status = balanceDue === 0 ? 'Paid' : advancePaid > 0 ? 'Partial' : 'Pending'

    const newInv = {
      id: `INV-2026-00${invoices.length + 1}`,
      orderId: `ORD-${8830 + invoices.length}`,
      customerName: invCustomerName.trim(),
      customerPhone: invCustomerPhone.trim() || '+91 98765 43210',
      customerEmail: invCustomerEmail.trim() || 'client@gloryfurniture.com',
      customerAddress: invCustomerAddress.trim() || 'Hyderabad Studio Delivery, Jubilee Hills',
      itemTitle: invItemTitle.trim(),
      category: invCategory,
      material: invMaterial,
      quantity: 1,
      baseAmount: base,
      gstRate,
      gstAmount,
      totalAmount,
      advancePaid,
      balanceDue,
      status,
      paymentMethod: invPaymentMethod,
      invoiceDate: new Date().toISOString().split('T')[0],
      dueDate: new Date(Date.now() + 14 * 86400000).toISOString().split('T')[0],
      hsnCode: '9403',
      warrantyYears: 15,
      notes: invNotes.trim()
    }

    const updatedInvoices = [newInv, ...invoices]
    setInvoices(updatedInvoices)
    try { localStorage.setItem('glory_invoices', JSON.stringify(updatedInvoices)) } catch (e) {}
    setIsCreateInvoiceModalOpen(false)
    setToastMessage(`Tax Invoice #${newInv.id} created successfully!`)

    // Reset form
    setInvCustomerName('')
    setInvCustomerPhone('')
    setInvCustomerEmail('')
    setInvCustomerAddress('')
    setInvItemTitle('')
    setInvBaseAmount('')
    setInvAdvancePaid('')
  }

  const handleMarkInvoicePaid = (invId) => {
    const updatedInvoices = invoices.map(inv => {
      if (inv.id === invId) {
        return {
          ...inv,
          status: 'Paid',
          advancePaid: inv.totalAmount,
          balanceDue: 0,
          notes: `${inv.notes} | Full settlement receipt logged on ${new Date().toLocaleDateString('en-GB')}`
        }
      }
      return inv
    })
    setInvoices(updatedInvoices)
    try { localStorage.setItem('glory_invoices', JSON.stringify(updatedInvoices)) } catch (e) {}
    setToastMessage(`Invoice #${invId} marked as fully Paid!`)
  }

  const handleDeleteInvoice = (invId) => {
    if (confirm(`Are you sure you want to delete Invoice #${invId}?`)) {
      const updatedInvoices = invoices.filter(inv => inv.id !== invId)
      setInvoices(updatedInvoices)
      try { localStorage.setItem('glory_invoices', JSON.stringify(updatedInvoices)) } catch (e) {}
      setToastMessage(`Invoice #${invId} deleted.`)
    }
  }

  const totalInvoiced = invoices.reduce((sum, inv) => sum + (Number(inv.totalAmount) || 0), 0)
  const totalCollected = invoices.reduce((sum, inv) => sum + (Number(inv.advancePaid) || 0), 0)
  const totalDue = invoices.reduce((sum, inv) => sum + (Number(inv.balanceDue) || 0), 0)
  const totalGstCollected = invoices.reduce((sum, inv) => sum + (Number(inv.gstAmount) || 0), 0)

  const filteredInvoices = invoices.filter(inv => {
    const matchesStatus = invoiceStatusFilter === 'All' || inv.status === invoiceStatusFilter
    const q = invoiceSearch.toLowerCase()
    const matchesSearch = !q ||
      inv.id.toLowerCase().includes(q) ||
      inv.customerName.toLowerCase().includes(q) ||
      inv.customerPhone.toLowerCase().includes(q) ||
      inv.itemTitle.toLowerCase().includes(q)
    return matchesStatus && matchesSearch
  })

  // =========================================================================
  // 4. LOGOUT ACTION
  // =========================================================================
  const handleAdminLogout = () => {
    if (confirm('Are you sure you want to log out from the Admin Console?')) {
      setUser(null)
      localStorage.removeItem('glory_user')
      navigate('/login', { replace: true })
    }
  }

  const totalEstimatedRevenue = orders.reduce((sum, o) => sum + (Number(o.price) || 0) * (o.quantity || 1), 0)

  return (
    <div className="min-h-screen bg-[#F0F2F5] text-walnut-900 font-sans pb-16 w-full">
      <Toast message={toastMessage} onClose={() => setToastMessage('')} />

      {/* DEDICATED STANDALONE ADMIN HEADER (Completely separated from customer website) */}
      <header className="sticky top-0 z-40 bg-walnut-900 text-white shadow-md border-b border-walnut-800">
        <div className="w-full px-4 sm:px-8 py-3 flex items-center justify-between">
          
          {/* Admin Identity */}
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-xl bg-gold-500 text-walnut-900 font-serif font-bold text-lg flex items-center justify-center shadow-sm">
              👑
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h1 className="font-serif font-bold text-base sm:text-lg text-cream-100 tracking-wide">
                  Glory Furniture Hub
                </h1>
                <span className="bg-gold-500/20 text-gold-400 border border-gold-500/40 text-[10px] font-bold px-2 py-0.5 rounded-full uppercase tracking-wider">
                  Admin Console
                </span>
              </div>
              <span className="text-[11px] text-cream-300 block">
                Master Studio Operational Workspace
              </span>
            </div>
          </div>

          {/* Admin Profile & Logout */}
          <div className="flex items-center gap-2 sm:gap-3">
            {/* Dedicated Admin Profile Button */}
            <button
              onClick={() => handleTabChange('profile')}
              className={`flex items-center gap-2 sm:gap-2.5 px-2.5 sm:px-3.5 py-1.5 rounded-xl text-xs transition-all active-tap group shadow-sm cursor-pointer border ${
                activeTab === 'profile'
                  ? 'bg-gold-500/20 border-gold-400 text-gold-300'
                  : 'bg-walnut-800 hover:bg-walnut-750 border-gold-500/50 hover:border-gold-400 text-cream-100'
              }`}
              title="Click to view full Admin Profile Workspace"
            >
              <div className="w-7 h-7 sm:w-8 sm:h-8 rounded-lg bg-gradient-to-br from-gold-400 to-gold-600 text-walnut-950 flex items-center justify-center font-bold shadow-xs group-hover:scale-105 transition-transform">
                <User className="w-4 h-4 text-walnut-950 stroke-[2.5]" />
              </div>
              <div className="text-left">
                <div className="flex items-center gap-1.5">
                  <span className="font-bold text-cream-100 group-hover:text-gold-300 text-xs sm:text-sm leading-tight transition-colors">
                    {adminName || 'Master Admin'}
                  </span>
                  <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" title="Admin Active"></span>
                </div>
                <span className="text-[10px] text-gold-400 font-medium block leading-none mt-0.5">
                  Super Admin Profile
                </span>
              </div>
            </button>

            {/* Logout Action */}
            <button
              onClick={handleAdminLogout}
              className="flex items-center gap-1.5 text-xs font-semibold bg-dustyrose/20 hover:bg-dustyrose/30 text-red-200 border border-dustyrose/40 px-3 py-2 rounded-xl transition-all active-tap cursor-pointer"
              title="Log Out from Admin Console"
            >
              <LogOut className="w-3.5 h-3.5" />
              <span className="hidden sm:inline">Log Out</span>
            </button>
          </div>

        </div>

        {/* ADMIN TAB NAVIGATION BAR */}
        <div className="w-full px-4 sm:px-8 bg-walnut-800 border-t border-walnut-700/80 flex items-center gap-2 overflow-x-auto no-scrollbar py-1">
          <button
            onClick={() => handleTabChange('products')}
            className={`flex items-center gap-2 px-4 py-2 rounded-xl text-xs font-bold transition-all whitespace-nowrap active-tap cursor-pointer ${
              activeTab === 'products'
                ? 'bg-gold-500 text-walnut-900 shadow-sm'
                : 'text-cream-200 hover:text-white hover:bg-walnut-700'
            }`}
          >
            <ShoppingBag className="w-3.5 h-3.5" />
            <span>Products ({products.length})</span>
          </button>

          <button
            onClick={() => handleTabChange('orders')}
            className={`flex items-center gap-2 px-4 py-2 rounded-xl text-xs font-bold transition-all whitespace-nowrap active-tap cursor-pointer ${
              activeTab === 'orders'
                ? 'bg-gold-500 text-walnut-900 shadow-sm'
                : 'text-cream-200 hover:text-white hover:bg-walnut-700'
            }`}
          >
            <Package className="w-3.5 h-3.5" />
            <span>Orders ({orders.length})</span>
          </button>

          <button
            onClick={() => handleTabChange('custom-requests')}
            className={`flex items-center gap-2 px-4 py-2 rounded-xl text-xs font-bold transition-all whitespace-nowrap active-tap cursor-pointer ${
              activeTab === 'custom-requests'
                ? 'bg-gold-500 text-walnut-900 shadow-sm'
                : 'text-cream-200 hover:text-white hover:bg-walnut-700'
            }`}
          >
            <Hammer className="w-3.5 h-3.5" />
            <span>Custom Specs ({requests.length})</span>
          </button>

          <button
            onClick={() => handleTabChange('billing')}
            className={`flex items-center gap-2 px-4 py-2 rounded-xl text-xs font-bold transition-all whitespace-nowrap active-tap cursor-pointer ${
              activeTab === 'billing'
                ? 'bg-gold-500 text-walnut-900 shadow-sm'
                : 'text-cream-200 hover:text-white hover:bg-walnut-700'
            }`}
          >
            <Receipt className="w-3.5 h-3.5" />
            <span>Billing & Invoices ({invoices.length})</span>
          </button>

          <button
            onClick={() => handleTabChange('overview')}
            className={`flex items-center gap-2 px-4 py-2 rounded-xl text-xs font-bold transition-all whitespace-nowrap active-tap cursor-pointer ${
              activeTab === 'overview'
                ? 'bg-gold-500 text-walnut-900 shadow-sm'
                : 'text-cream-200 hover:text-white hover:bg-walnut-700'
            }`}
          >
            <LayoutDashboard className="w-3.5 h-3.5" />
            <span>Analytics</span>
          </button>

          {/* Dedicated Full Page Profile Tab */}
          <button
            onClick={() => handleTabChange('profile')}
            className={`flex items-center gap-1.5 px-3.5 py-2 rounded-xl text-xs font-bold transition-all whitespace-nowrap active-tap ml-auto cursor-pointer ${
              activeTab === 'profile'
                ? 'bg-gold-500 text-walnut-900 shadow-sm'
                : 'text-gold-400 hover:text-gold-300 hover:bg-walnut-750 border border-gold-500/30'
            }`}
            title="Open Admin Profile Page"
          >
            <User className="w-3.5 h-3.5" />
            <span>Admin Profile</span>
          </button>
        </div>
      </header>

      {/* MAIN ADMIN WORKSPACE CONTAINER */}
      <main className="w-full px-4 sm:px-8 lg:px-12 py-6">

        {/* =================================================================== */}
        {/* TAB 1: PRODUCTS MANAGEMENT */}
        {/* =================================================================== */}
        {activeTab === 'products' && (
          <div className="space-y-4">
            
            {/* Action Bar: Search, Category Filter, and Add Button */}
            <div className="bg-white p-4 rounded-2xl border border-walnut-200/70 shadow-sm flex flex-col md:flex-row items-start md:items-center justify-between gap-3">
              <div className="flex items-center gap-3 w-full md:w-auto flex-1 max-w-md">
                <div className="relative w-full">
                  <Search className="w-3.5 h-3.5 text-softgray absolute left-3 top-2.5" />
                  <input
                    type="text"
                    value={productSearch}
                    onChange={(e) => setProductSearch(e.target.value)}
                    placeholder="Search products by title, species..."
                    className="w-full text-xs pl-8 pr-3 py-1.5 bg-cream-50 border border-walnut-200 rounded-xl focus:outline-none focus:ring-1 focus:ring-walnut-500 text-walnut-900"
                  />
                </div>
              </div>

              <div className="flex items-center gap-2 w-full md:w-auto justify-between md:justify-end">
                <span className="text-xs text-softgray">Total: <strong className="text-walnut-900">{filteredProducts.length}</strong></span>
                <Button
                  variant="primary"
                  size="sm"
                  onClick={() => setIsAddModalOpen(true)}
                  icon={Plus}
                  className="bg-walnut-900 hover:bg-walnut-800 text-gold-400 font-bold px-4 py-2 rounded-xl text-xs shadow-sm"
                >
                  + Add Furniture Piece
                </Button>
              </div>
            </div>

            {/* Category Filter Pills (8 Furniture Types) */}
            <div className="flex items-center gap-1.5 overflow-x-auto no-scrollbar py-1">
              {['All', ...PRODUCT_TYPES.map(p => p.id)].map(cat => (
                <button
                  key={cat}
                  onClick={() => setProductCategoryFilter(cat)}
                  className={`px-3 py-1 rounded-full text-xs font-semibold whitespace-nowrap transition-all active-tap ${
                    productCategoryFilter === cat
                      ? 'bg-walnut-900 text-gold-400 shadow-xs'
                      : 'bg-white text-walnut-800 border border-walnut-200 hover:bg-cream-100'
                  }`}
                >
                  {cat}
                </button>
              ))}
            </div>

            {/* Products Grid / Cards */}
            <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-3.5">
              {filteredProducts.map(p => (
                <div key={p.id} className="bg-white rounded-2xl border border-walnut-200/70 p-3 shadow-sm hover:shadow-md transition-all flex flex-col justify-between">
                  <div>
                    <div className="relative aspect-[4/3] rounded-xl overflow-hidden bg-cream-100 mb-2">
                      <img src={p.images[0]} alt={p.name} className="w-full h-full object-cover" />
                      <span className="absolute top-2 left-2 bg-walnut-900/80 backdrop-blur-sm text-gold-400 text-[10px] font-bold px-2 py-0.5 rounded-md">
                        {p.category}
                      </span>
                    </div>

                    <h3 className="font-serif font-bold text-xs sm:text-sm text-walnut-900 line-clamp-1">
                      {p.name}
                    </h3>
                    <p className="text-[11px] text-softgray line-clamp-1 mt-0.5">{p.material}</p>

                    {/* Price & Size Variants Badge */}
                    <div className="mt-2 pt-2 border-t border-cream-200">
                      {p.sizeVariants && p.sizeVariants.length > 0 ? (
                        <div className="space-y-1">
                          <span className="text-[10px] text-gold-700 font-bold uppercase tracking-wider block">
                            Sizes ({p.sizeVariants.length} Variants):
                          </span>
                          <div className="flex flex-wrap gap-1">
                            {p.sizeVariants.map((v, i) => (
                              <span key={i} className="text-[10px] bg-cream-100 px-1.5 py-0.5 rounded border border-walnut-200/60 text-walnut-800 font-medium">
                                {v.size}: ₹{Number(v.price).toLocaleString('en-IN')}
                              </span>
                            ))}
                          </div>
                        </div>
                      ) : (
                        <span className="text-xs sm:text-sm font-bold text-walnut-900">
                          ₹{Number(p.price).toLocaleString('en-IN')}
                        </span>
                      )}
                    </div>
                  </div>

                  <div className="pt-3 mt-3 border-t border-cream-200 flex items-center justify-between">
                    <span className="text-[10px] text-softgray">{p.dimensions || 'Standard'}</span>
                    <button
                      onClick={() => handleDeleteProduct(p.id, p.name)}
                      className="p-1 text-softgray hover:text-dustyrose rounded-md transition-colors"
                      title="Delete Product"
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>
                  </div>
                </div>
              ))}
            </div>

          </div>
        )}

        {/* =================================================================== */}
        {/* TAB 2: CUSTOMER ORDERS & BOOKINGS */}
        {/* =================================================================== */}
        {activeTab === 'orders' && (
          <div className="space-y-4">
            
            {/* Status Tabs Filter */}
            <div className="bg-white p-3 rounded-2xl border border-walnut-200/70 shadow-sm flex items-center gap-2 overflow-x-auto no-scrollbar">
              <span className="text-xs font-bold text-softgray uppercase tracking-wider pl-1">Status:</span>
              {['All', 'Pending', 'Confirmed', 'In Production', 'Delivered', 'Cancelled'].map(st => (
                <button
                  key={st}
                  onClick={() => setOrderStatusFilter(st)}
                  className={`px-3 py-1 rounded-full text-xs font-bold transition-all active-tap whitespace-nowrap ${
                    orderStatusFilter === st
                      ? 'bg-walnut-900 text-gold-400 shadow-xs'
                      : 'bg-cream-100 text-walnut-800 hover:bg-cream-200'
                  }`}
                >
                  {st}
                </button>
              ))}
            </div>

            {/* Orders List */}
            {filteredOrders.length > 0 ? (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {filteredOrders.map(order => (
                  <div key={order.id} className="bg-white p-4 rounded-2xl border border-walnut-200/70 shadow-sm space-y-3">
                    
                    <div className="flex items-center justify-between border-b border-cream-200 pb-2">
                      <span className="font-mono font-bold text-xs text-walnut-800">Order #{order.id}</span>
                      
                      {/* Real-time Status Selector */}
                      <select
                        value={order.status || 'Pending'}
                        onChange={(e) => handleOrderStatusChange(order.id, e.target.value)}
                        className={`text-xs font-bold px-2.5 py-1 rounded-lg border focus:outline-none cursor-pointer ${
                          order.status === 'Delivered' ? 'bg-green-100 text-green-800 border-green-300' :
                          order.status === 'Confirmed' ? 'bg-blue-100 text-blue-800 border-blue-300' :
                          order.status === 'In Production' ? 'bg-amber-100 text-amber-800 border-amber-300' :
                          order.status === 'Cancelled' ? 'bg-red-100 text-red-800 border-red-300' :
                          'bg-cream-100 text-walnut-800 border-walnut-200'
                        }`}
                      >
                        <option value="Pending">Pending</option>
                        <option value="Confirmed">Confirmed</option>
                        <option value="In Production">In Production</option>
                        <option value="Delivered">Delivered</option>
                        <option value="Cancelled">Cancelled</option>
                      </select>
                    </div>

                    <div>
                      <h4 className="font-serif font-bold text-sm text-walnut-900">{order.productName}</h4>
                      <div className="flex items-center gap-2 mt-1 text-xs text-softgray">
                        <span>Price: <strong className="text-walnut-900 font-bold">₹{Number(order.price || 0).toLocaleString('en-IN')}</strong></span>
                        {order.bedSize && (
                          <span className="bg-cream-100 px-2 py-0.5 rounded text-[11px] font-semibold text-walnut-800">
                            Size: {order.bedSize}
                          </span>
                        )}
                        {order.woodType && (
                          <span className="bg-cream-100 px-2 py-0.5 rounded text-[11px] font-semibold text-walnut-800">
                            Wood: {order.woodType}
                          </span>
                        )}
                      </div>
                    </div>

                    {/* Customer Contact Details */}
                    <div className="p-2.5 bg-cream-50 rounded-xl border border-walnut-200/50 space-y-1.5 text-xs text-walnut-800">
                      <div className="font-bold flex items-center justify-between">
                        <span>{order.customerName || 'Customer'}</span>
                        <a
                          href={`tel:${order.customerPhone}`}
                          className="flex items-center gap-1 text-gold-700 hover:text-walnut-900 font-semibold"
                        >
                          <Phone className="w-3 h-3" /> {order.customerPhone || 'N/A'}
                        </a>
                      </div>
                      <p className="text-[11px] text-softgray flex items-start gap-1">
                        <MapPin className="w-3 h-3 flex-shrink-0 mt-0.5 text-softgray" />
                        <span>{order.address || 'Standard Delivery Address'}</span>
                      </p>
                    </div>

                    <div className="flex items-center justify-between text-[11px] text-softgray pt-1">
                      <span className="flex items-center gap-1">
                        <Calendar className="w-3 h-3" /> {order.date || 'Recent'}
                      </span>
                      {order.customerPhone && (
                        <a
                          href={`https://wa.me/${String(order.customerPhone).replace(/\D/g, '')}?text=Hello%20from%20Glory%20Furniture%20regarding%20your%20order%20%23${order.id}`}
                          target="_blank"
                          rel="noreferrer"
                          className="text-green-700 font-semibold hover:underline flex items-center gap-1"
                        >
                          <MessageSquare className="w-3 h-3" /> WhatsApp
                        </a>
                      )}
                    </div>

                  </div>
                ))}
              </div>
            ) : (
              <div className="p-8 text-center bg-white rounded-2xl border border-walnut-200 text-softgray text-xs">
                No orders match the selected status.
              </div>
            )}

          </div>
        )}

        {/* =================================================================== */}
        {/* TAB 3: CUSTOM SPECIFICATION REQUESTS */}
        {/* =================================================================== */}
        {activeTab === 'custom-requests' && (
          <div className="space-y-4">
            <div className="bg-white p-4 rounded-2xl border border-walnut-200/70 shadow-sm flex items-center justify-between">
              <div>
                <h3 className="font-serif font-bold text-sm text-walnut-900">Custom Furniture Inquiries</h3>
                <p className="text-xs text-softgray">Review customer dimensions, wood species, and send quotes</p>
              </div>
              <span className="text-xs font-bold text-walnut-900 bg-cream-100 px-3 py-1 rounded-full border border-walnut-200">
                {requests.length} Requests
              </span>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {requests.map(req => (
                <div key={req.id} className="bg-white p-4 rounded-2xl border border-walnut-200/70 shadow-sm space-y-3">
                  <div className="flex items-center justify-between border-b border-cream-200 pb-2">
                    <span className="font-mono font-bold text-xs text-walnut-800">Req #{req.id}</span>
                    <select
                      value={req.status}
                      onChange={(e) => handleRequestStatusChange(req.id, e.target.value)}
                      className="text-xs font-bold bg-cream-100 border border-walnut-200 rounded-lg px-2 py-1 text-walnut-800"
                    >
                      <option value="Under Review">Under Review</option>
                      <option value="Quoted">Quoted</option>
                      <option value="In Production">In Production</option>
                      <option value="Completed">Completed</option>
                    </select>
                  </div>

                  <div>
                    <h4 className="font-serif font-bold text-sm text-walnut-900">{req.furnitureType} ({req.wood})</h4>
                    <p className="text-xs text-softgray mt-1 leading-snug">{req.description}</p>
                    <span className="text-xs font-bold text-gold-700 block mt-1.5">Dimensions: {req.dimensions}</span>
                  </div>

                  <div className="pt-2 border-t border-cream-200 flex items-center justify-between text-xs">
                    <span className="text-softgray">Budget: <strong className="text-walnut-900">{req.budget}</strong></span>
                    <a
                      href={`https://wa.me/?text=Hi,%20this%20is%20Glory%20Furniture%20Hub%20regarding%20your%20custom%20spec%20%23${req.id}`}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="py-1 px-2.5 bg-green-700 hover:bg-green-800 text-white text-[11px] font-semibold rounded-lg flex items-center gap-1 transition-all"
                    >
                      <MessageSquare className="w-3 h-3" /> WhatsApp Quote
                    </a>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* =================================================================== */}
        {/* TAB: BILLING & INVOICE MANAGEMENT */}
        {/* =================================================================== */}
        {activeTab === 'billing' && (
          <div className="space-y-6">
            {/* Top Action Bar & Summary */}
            <div className="bg-white p-5 rounded-2xl border border-walnut-200/70 shadow-sm flex flex-col lg:flex-row items-start lg:items-center justify-between gap-4">
              <div>
                <div className="flex items-center gap-2">
                  <h2 className="text-xl font-serif font-bold text-walnut-900">Studio Billing & Tax Invoices</h2>
                  <span className="bg-gold-100 text-gold-800 text-[11px] font-bold px-2 py-0.5 rounded-full border border-gold-300">
                    GST Compliant
                  </span>
                </div>
                <p className="text-xs text-softgray mt-1">
                  Manage commercial furniture invoices, advance settlements, GST 18% filing logs, and printable receipts.
                </p>
              </div>

              <div className="flex flex-wrap items-center gap-3 w-full lg:w-auto">
                <div className="relative flex-1 sm:w-64">
                  <Search className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-softgray" />
                  <input
                    type="text"
                    placeholder="Search invoice, customer, phone..."
                    value={invoiceSearch}
                    onChange={(e) => setInvoiceSearch(e.target.value)}
                    className="w-full pl-9 pr-3 py-2 text-xs bg-cream-100/70 border border-walnut-200 rounded-xl focus:bg-white focus:border-gold-500 transition-all"
                  />
                  {invoiceSearch && (
                    <button 
                      onClick={() => setInvoiceSearch('')} 
                      className="absolute right-2.5 top-1/2 -translate-y-1/2 text-softgray hover:text-walnut-900 text-xs"
                    >
                      ✕
                    </button>
                  )}
                </div>

                <Button
                  onClick={() => setIsCreateInvoiceModalOpen(true)}
                  variant="primary"
                  size="sm"
                  className="bg-walnut-900 text-gold-400 hover:bg-walnut-800 flex items-center gap-1.5 shadow-sm"
                  icon={Plus}
                >
                  Generate Tax Invoice
                </Button>
              </div>
            </div>

            {/* Financial KPI Cards */}
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
              <div className="bg-white p-5 rounded-2xl border border-walnut-200/70 shadow-sm">
                <div className="flex items-center justify-between">
                  <span className="text-xs font-semibold text-softgray uppercase tracking-wider">Total Invoiced</span>
                  <div className="w-9 h-9 rounded-xl bg-gold-100 text-gold-700 flex items-center justify-center">
                    <Receipt className="w-4 h-4" />
                  </div>
                </div>
                <div className="mt-3">
                  <h3 className="text-2xl font-serif font-bold text-walnut-900">
                    ₹{totalInvoiced.toLocaleString('en-IN')}
                  </h3>
                  <p className="text-[11px] text-softgray mt-1">
                    Gross volume across {invoices.length} invoices
                  </p>
                </div>
              </div>

              <div className="bg-white p-5 rounded-2xl border border-walnut-200/70 shadow-sm">
                <div className="flex items-center justify-between">
                  <span className="text-xs font-semibold text-softgray uppercase tracking-wider">Payments Collected</span>
                  <div className="w-9 h-9 rounded-xl bg-emerald-100 text-emerald-700 flex items-center justify-center">
                    <CreditCard className="w-4 h-4" />
                  </div>
                </div>
                <div className="mt-3">
                  <h3 className="text-2xl font-serif font-bold text-emerald-700">
                    ₹{totalCollected.toLocaleString('en-IN')}
                  </h3>
                  <p className="text-[11px] text-softgray mt-1">
                    {Math.round((totalCollected / Math.max(1, totalInvoiced)) * 100)}% collection efficiency
                  </p>
                </div>
              </div>

              <div className="bg-white p-5 rounded-2xl border border-walnut-200/70 shadow-sm">
                <div className="flex items-center justify-between">
                  <span className="text-xs font-semibold text-softgray uppercase tracking-wider">Receivables Due</span>
                  <div className="w-9 h-9 rounded-xl bg-amber-100 text-amber-700 flex items-center justify-center">
                    <Clock className="w-4 h-4" />
                  </div>
                </div>
                <div className="mt-3">
                  <h3 className="text-2xl font-serif font-bold text-amber-700">
                    ₹{totalDue.toLocaleString('en-IN')}
                  </h3>
                  <p className="text-[11px] text-softgray mt-1">
                    {invoices.filter(i => i.balanceDue > 0).length} invoices pending settlement
                  </p>
                </div>
              </div>

              <div className="bg-white p-5 rounded-2xl border border-walnut-200/70 shadow-sm">
                <div className="flex items-center justify-between">
                  <span className="text-xs font-semibold text-softgray uppercase tracking-wider">GST 18% Recorded</span>
                  <div className="w-9 h-9 rounded-xl bg-blue-100 text-blue-700 flex items-center justify-center">
                    <ShieldCheck className="w-4 h-4" />
                  </div>
                </div>
                <div className="mt-3">
                  <h3 className="text-2xl font-serif font-bold text-blue-700">
                    ₹{totalGstCollected.toLocaleString('en-IN')}
                  </h3>
                  <p className="text-[11px] text-softgray mt-1">
                    HSN 9403 Teak Wood Tax Records
                  </p>
                </div>
              </div>
            </div>

            {/* Filter Tabs */}
            <div className="flex items-center justify-between flex-wrap gap-3">
              <div className="flex items-center gap-1.5 bg-cream-200/60 p-1 rounded-xl border border-walnut-200/70">
                {['All', 'Paid', 'Partial', 'Pending'].map((status) => (
                  <button
                    key={status}
                    onClick={() => setInvoiceStatusFilter(status)}
                    className={`px-3 py-1.5 rounded-lg text-xs font-bold transition-all cursor-pointer ${
                      invoiceStatusFilter === status
                        ? 'bg-walnut-900 text-gold-400 shadow-sm'
                        : 'text-walnut-700 hover:text-walnut-900 hover:bg-cream-100'
                    }`}
                  >
                    {status} ({status === 'All' ? invoices.length : invoices.filter(i => i.status === status).length})
                  </button>
                ))}
              </div>

              <span className="text-xs text-softgray">
                Showing <strong className="text-walnut-900">{filteredInvoices.length}</strong> of {invoices.length} Invoices
              </span>
            </div>

            {/* Invoices List / Table */}
            <div className="bg-white rounded-2xl border border-walnut-200/70 shadow-sm overflow-hidden">
              {filteredInvoices.length === 0 ? (
                <div className="text-center py-16 px-4">
                  <div className="w-14 h-14 mx-auto rounded-2xl bg-cream-200 flex items-center justify-center text-softgray mb-3">
                    <Receipt className="w-7 h-7" />
                  </div>
                  <h4 className="font-serif font-bold text-walnut-900 text-base">No Invoices Found</h4>
                  <p className="text-xs text-softgray mt-1 max-w-sm mx-auto">
                    No billing records matched your filter or search query. Click below to generate an invoice.
                  </p>
                  <Button
                    onClick={() => setIsCreateInvoiceModalOpen(true)}
                    variant="primary"
                    size="sm"
                    className="mt-4 bg-walnut-900 text-gold-400"
                    icon={Plus}
                  >
                    Create New Invoice
                  </Button>
                </div>
              ) : (
                <div className="overflow-x-auto">
                  <table className="w-full text-left border-collapse">
                    <thead>
                      <tr className="bg-cream-100/90 border-b border-walnut-200/70 text-[11px] font-bold text-walnut-700 uppercase tracking-wider">
                        <th className="py-3 px-4">Invoice & Date</th>
                        <th className="py-3 px-4">Customer</th>
                        <th className="py-3 px-4">Furniture Item</th>
                        <th className="py-3 px-4">Total (₹)</th>
                        <th className="py-3 px-4">Advance / Balance</th>
                        <th className="py-3 px-4">Status</th>
                        <th className="py-3 px-4 text-right">Actions</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-cream-200/80 text-xs">
                      {filteredInvoices.map((inv) => (
                        <tr key={inv.id} className="hover:bg-cream-100/50 transition-colors">
                          <td className="py-3.5 px-4">
                            <div className="flex items-center gap-2">
                              <span className="font-bold text-walnut-900 font-mono">{inv.id}</span>
                              <span className="text-[10px] bg-cream-200 text-walnut-700 px-1.5 py-0.5 rounded font-mono">{inv.orderId}</span>
                            </div>
                            <span className="text-[11px] text-softgray block mt-0.5">{inv.invoiceDate}</span>
                          </td>

                          <td className="py-3.5 px-4">
                            <strong className="text-walnut-900 block">{inv.customerName}</strong>
                            <div className="flex items-center gap-2 text-[11px] text-softgray mt-0.5">
                              <span className="flex items-center gap-1"><Phone className="w-3 h-3 text-gold-600" /> {inv.customerPhone}</span>
                            </div>
                          </td>

                          <td className="py-3.5 px-4 max-w-[220px]">
                            <span className="font-medium text-walnut-900 block truncate" title={inv.itemTitle}>
                              {inv.itemTitle}
                            </span>
                            <span className="text-[10px] text-gold-700 font-semibold block mt-0.5">
                              {inv.material}
                            </span>
                          </td>

                          <td className="py-3.5 px-4 font-serif font-bold text-walnut-900">
                            <div>₹{inv.totalAmount.toLocaleString('en-IN')}</div>
                            <span className="text-[10px] font-sans font-normal text-softgray block">
                              Base ₹{inv.baseAmount.toLocaleString('en-IN')} + 18% GST
                            </span>
                          </td>

                          <td className="py-3.5 px-4">
                            <div className="flex flex-col gap-0.5">
                              <span className="text-emerald-700 font-semibold text-[11px]">
                                Recv: ₹{inv.advancePaid.toLocaleString('en-IN')}
                              </span>
                              {inv.balanceDue > 0 ? (
                                <span className="text-rose-600 font-bold text-[11px]">
                                  Due: ₹{inv.balanceDue.toLocaleString('en-IN')}
                                </span>
                              ) : (
                                <span className="text-softgray text-[10px]">Settled in Full</span>
                              )}
                            </div>
                          </td>

                          <td className="py-3.5 px-4">
                            <span
                              className={`inline-flex items-center px-2 py-0.5 rounded-full text-[11px] font-bold ${
                                inv.status === 'Paid'
                                  ? 'bg-emerald-100 text-emerald-800 border border-emerald-300'
                                  : inv.status === 'Partial'
                                  ? 'bg-amber-100 text-amber-800 border border-amber-300'
                                  : 'bg-rose-100 text-rose-800 border border-rose-300'
                              }`}
                            >
                              {inv.status}
                            </span>
                            <span className="block text-[10px] text-softgray mt-1">{inv.paymentMethod}</span>
                          </td>

                          <td className="py-3.5 px-4 text-right">
                            <div className="flex items-center justify-end gap-1.5">
                              <button
                                onClick={() => setSelectedInvoiceForView(inv)}
                                title="View & Print Official Studio Invoice"
                                className="p-1.5 rounded-lg bg-cream-200 hover:bg-gold-500 hover:text-walnut-900 text-walnut-800 transition-colors cursor-pointer"
                              >
                                <Printer className="w-3.5 h-3.5" />
                              </button>

                              <a
                                href={`https://wa.me/${inv.customerPhone.replace(/[^0-9]/g, '')}?text=Dear%20${encodeURIComponent(inv.customerName)},%20here%20is%20your%20tax%20invoice%20${inv.id}%20from%20Glory%20Furniture%20Hub%20for%20${encodeURIComponent(inv.itemTitle)}.%20Total:%20INR%20${inv.totalAmount},%20Balance%20Due:%20INR%20${inv.balanceDue}.%20Thank%20you!`}
                                target="_blank"
                                rel="noopener noreferrer"
                                title="Share Invoice on WhatsApp"
                                className="p-1.5 rounded-lg bg-emerald-100 hover:bg-emerald-200 text-emerald-800 transition-colors cursor-pointer"
                              >
                                <Share2 className="w-3.5 h-3.5" />
                              </a>

                              {inv.balanceDue > 0 && (
                                <button
                                  onClick={() => handleMarkInvoicePaid(inv.id)}
                                  title="Mark Full Balance as Paid"
                                  className="p-1.5 rounded-lg bg-blue-100 hover:bg-blue-200 text-blue-800 transition-colors cursor-pointer"
                                >
                                  <Check className="w-3.5 h-3.5" />
                                </button>
                              )}

                              <button
                                onClick={() => handleDeleteInvoice(inv.id)}
                                title="Delete Invoice"
                                className="p-1.5 rounded-lg bg-cream-200 hover:bg-rose-100 text-softgray hover:text-rose-700 transition-colors cursor-pointer"
                              >
                                <Trash2 className="w-3.5 h-3.5" />
                              </button>
                            </div>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </div>

            {/* Studio Tax Compliance Footer Bar */}
            <div className="p-4 bg-walnut-900 text-cream-200 rounded-2xl border border-walnut-800 flex flex-col md:flex-row items-center justify-between gap-3 text-xs">
              <div className="flex items-center gap-3">
                <div className="w-8 h-8 rounded-lg bg-gold-500/20 text-gold-400 flex items-center justify-center font-bold">
                  <ShieldCheck className="w-4 h-4" />
                </div>
                <div>
                  <span className="font-bold text-white block">Official Studio GST Tax Documentation</span>
                  <span className="text-[11px] text-cream-300">
                    GSTIN: <strong className="text-gold-400 font-mono">36AAACG1234F1Z5</strong> | HSN Code: <strong className="text-gold-400 font-mono">9403</strong> (Wooden Furniture)
                  </span>
                </div>
              </div>

              <div className="text-[11px] text-cream-300 md:text-right">
                <span>Direct Studio Bank: <strong className="text-white">HDFC Bank, Jubilee Hills Branch</strong></span>
                <span className="block">All invoices automatically include 15-Year Solid Burma Teak Warranty</span>
              </div>
            </div>
          </div>
        )}

        {/* =================================================================== */}
        {/* TAB 4: OVERVIEW & ANALYTICS */}
        {/* =================================================================== */}
        {activeTab === 'overview' && (
          <div className="space-y-6">
            
            {/* KPI Stat Cards */}
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
              <div className="bg-white p-5 rounded-2xl border border-walnut-200/70 shadow-sm flex items-center gap-4">
                <div className="w-12 h-12 rounded-xl bg-gold-100 text-gold-700 flex items-center justify-center">
                  <ShoppingBag className="w-6 h-6" />
                </div>
                <div>
                  <span className="text-xs text-softgray block">Total Products</span>
                  <strong className="text-xl font-serif text-walnut-900">{products.length} Items</strong>
                </div>
              </div>

              <div className="bg-white p-5 rounded-2xl border border-walnut-200/70 shadow-sm flex items-center gap-4">
                <div className="w-12 h-12 rounded-xl bg-blue-100 text-blue-700 flex items-center justify-center">
                  <Package className="w-6 h-6" />
                </div>
                <div>
                  <span className="text-xs text-softgray block">Active Bookings</span>
                  <strong className="text-xl font-serif text-walnut-900">{orders.length} Orders</strong>
                </div>
              </div>

              <div className="bg-white p-5 rounded-2xl border border-walnut-200/70 shadow-sm flex items-center gap-4">
                <div className="w-12 h-12 rounded-xl bg-amber-100 text-amber-700 flex items-center justify-center">
                  <Hammer className="w-6 h-6" />
                </div>
                <div>
                  <span className="text-xs text-softgray block">Custom Specs</span>
                  <strong className="text-xl font-serif text-walnut-900">{requests.length} Inquiries</strong>
                </div>
              </div>

              <div className="bg-white p-5 rounded-2xl border border-walnut-200/70 shadow-sm flex items-center gap-4">
                <div className="w-12 h-12 rounded-xl bg-green-100 text-green-700 flex items-center justify-center">
                  <TrendingUp className="w-6 h-6" />
                </div>
                <div>
                  <span className="text-xs text-softgray block">Estimated Volume</span>
                  <strong className="text-xl font-serif text-walnut-900">₹{totalEstimatedRevenue.toLocaleString('en-IN')}</strong>
                </div>
              </div>
            </div>

            {/* Quick Actions Panel */}
            <div className="bg-white p-6 rounded-2xl border border-walnut-200/70 shadow-sm space-y-4">
              <h3 className="font-serif font-bold text-base text-walnut-900">Studio Management Shortcuts</h3>
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
                <button
                  onClick={() => { setActiveTab('products'); setIsAddModalOpen(true); }}
                  className="p-4 rounded-xl bg-cream-50 hover:bg-cream-100 border border-walnut-200 text-left transition-all active-tap"
                >
                  <Plus className="w-5 h-5 text-gold-600 mb-1" />
                  <h4 className="font-serif font-bold text-xs text-walnut-900">Add New Furniture</h4>
                  <p className="text-[11px] text-softgray mt-0.5">Upload photos & set bed sizes/prices</p>
                </button>

                <button
                  onClick={() => setActiveTab('orders')}
                  className="p-4 rounded-xl bg-cream-50 hover:bg-cream-100 border border-walnut-200 text-left transition-all active-tap"
                >
                  <Package className="w-5 h-5 text-blue-600 mb-1" />
                  <h4 className="font-serif font-bold text-xs text-walnut-900">Manage Customer Orders</h4>
                  <p className="text-[11px] text-softgray mt-0.5">Update fulfillment and delivery status</p>
                </button>

                <button
                  onClick={() => setActiveTab('custom-requests')}
                  className="p-4 rounded-xl bg-cream-50 hover:bg-cream-100 border border-walnut-200 text-left transition-all active-tap"
                >
                  <Hammer className="w-5 h-5 text-amber-600 mb-1" />
                  <h4 className="font-serif font-bold text-xs text-walnut-900">Review Custom Specs</h4>
                  <p className="text-[11px] text-softgray mt-0.5">Send custom WhatsApp quotes</p>
                </button>
              </div>
            </div>

          </div>
        )}

        {/* =================================================================== */}
        {/* TAB 5: DEDICATED FULL-PAGE ADMIN PROFILE (Not a small box!) */}
        {/* =================================================================== */}
        {activeTab === 'profile' && (
          <div className="space-y-6 max-w-6xl mx-auto animate-fade-in pb-8">

            {/* 1. EXECUTIVE HERO BANNER (Upgraded Luxury Palette & High Contrast) */}
            <div 
              className="relative overflow-hidden text-white rounded-3xl p-6 sm:p-8 border-2 border-gold-500/40 shadow-2xl"
              style={{ background: 'linear-gradient(135deg, #180F0A 0%, #291A11 50%, #150D08 100%)' }}
            >
              {/* Golden Ambient Glow Overlays */}
              <div className="absolute top-0 right-0 w-96 h-96 bg-gradient-to-b from-gold-500/20 via-gold-500/5 to-transparent rounded-full blur-3xl pointer-events-none"></div>
              <div className="absolute -bottom-10 -left-10 w-72 h-72 bg-amber-600/15 rounded-full blur-2xl pointer-events-none"></div>
              
              <div className="relative z-10 flex flex-col md:flex-row md:items-center justify-between gap-6">
                
                {/* Avatar & Title */}
                <div className="flex items-center gap-4 sm:gap-6">
                  <div className="relative">
                    <div className="w-20 h-20 sm:w-24 sm:h-24 rounded-2xl bg-gradient-to-br from-[#FFE494] via-[#D4AF37] to-[#8C5E1E] text-walnut-950 flex items-center justify-center font-serif font-black text-3xl sm:text-4xl shadow-xl border-2 border-[#FFF0B3] shrink-0 transform hover:scale-105 transition-transform">
                      👑
                    </div>
                    <span className="absolute -bottom-1 -right-1 bg-emerald-500 text-white p-1 rounded-full border-2 border-[#180F0A] shadow-md" title="Active Master Session">
                      <CheckCircle2 className="w-4 h-4 stroke-[2.5]" />
                    </span>
                  </div>

                  <div>
                    <div className="flex items-center gap-3 flex-wrap">
                      <h2 className="font-serif font-bold text-2xl sm:text-3xl text-white tracking-wide drop-shadow-sm">
                        {adminName}
                      </h2>
                      <span className="bg-gradient-to-r from-gold-400 via-gold-500 to-amber-600 text-walnut-950 text-[11px] sm:text-xs font-black px-3 py-1 rounded-full uppercase tracking-wider shadow-md border border-gold-300/80">
                        Super Administrator
                      </span>
                    </div>
                    <p className="text-sm font-semibold text-[#F3DFBF] mt-1 drop-shadow-xs">
                      {adminTitle || 'Master Craftsman & Studio Operations Director'}
                    </p>
                    <div className="flex items-center gap-3 text-xs mt-3 flex-wrap">
                      <span className="flex items-center gap-1.5 bg-white/10 px-3 py-1 rounded-xl border border-white/15 text-[#EFE7DE] backdrop-blur-xs">
                        <MapPin className="w-3.5 h-3.5 text-gold-400 shrink-0" />
                        <span>{adminStudioLocation}</span>
                      </span>
                      <span className="flex items-center gap-2 bg-[#0A3D22] px-3 py-1 rounded-xl border border-[#2BB865]/60 text-[#4EFA94] font-bold shadow-xs">
                        <span className="w-2 h-2 rounded-full bg-[#4EFA94] animate-pulse"></span>
                        <span>Full System Access (Root Privileges)</span>
                      </span>
                    </div>
                  </div>
                </div>

                {/* SMALL BUTTON FOR EDIT THE DETAILS */}
                <div className="flex items-center gap-2 self-start md:self-center">
                  {!isEditingAdminProfile ? (
                    <button
                      onClick={handleStartEditProfile}
                      className="px-4 py-2.5 bg-gradient-to-r from-gold-400 via-gold-500 to-amber-600 hover:from-gold-300 hover:to-gold-400 text-walnut-950 font-extrabold text-xs rounded-xl flex items-center gap-2 shadow-lg hover:shadow-gold-500/30 border border-gold-300/90 transition-all active-tap cursor-pointer shrink-0"
                      title="Edit Admin Details"
                    >
                      <Edit3 className="w-3.5 h-3.5 text-walnut-950 stroke-[2.5]" />
                      <span>Edit Details</span>
                    </button>
                  ) : (
                    <div className="flex items-center gap-2 shrink-0">
                      <button
                        onClick={handleCancelEditProfile}
                        className="px-3.5 py-2.5 bg-walnut-800 hover:bg-walnut-700 text-cream-200 border border-walnut-700 font-bold text-xs rounded-xl transition-all active-tap cursor-pointer"
                      >
                        Cancel
                      </button>
                      <button
                        onClick={handleSaveAdminProfile}
                        className="px-4 py-2.5 bg-gradient-to-r from-emerald-600 to-emerald-500 hover:from-emerald-500 hover:to-emerald-400 text-white font-extrabold text-xs rounded-xl flex items-center gap-1.5 shadow-md transition-all active-tap cursor-pointer"
                      >
                        <Check className="w-4 h-4 stroke-[3]" />
                        <span>Save Changes</span>
                      </button>
                    </div>
                  )}
                </div>

              </div>
            </div>

            {/* 2. EXECUTIVE STUDIO KPI METRIC STRIP */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div className="bg-white p-4 rounded-2xl border border-walnut-200/80 shadow-xs flex items-center gap-3">
                <div className="w-10 h-10 rounded-xl bg-gold-500/10 text-gold-600 flex items-center justify-center shrink-0">
                  <ShoppingBag className="w-5 h-5" />
                </div>
                <div>
                  <span className="text-base font-bold text-walnut-900 block leading-tight">{products.length}</span>
                  <span className="text-[11px] text-softgray block mt-0.5">Catalog Pieces</span>
                </div>
              </div>

              <div className="bg-white p-4 rounded-2xl border border-walnut-200/80 shadow-xs flex items-center gap-3">
                <div className="w-10 h-10 rounded-xl bg-blue-500/10 text-blue-600 flex items-center justify-center shrink-0">
                  <Package className="w-5 h-5" />
                </div>
                <div>
                  <span className="text-base font-bold text-walnut-900 block leading-tight">{orders.length}</span>
                  <span className="text-[11px] text-softgray block mt-0.5">Orders in Pipeline</span>
                </div>
              </div>

              <div className="bg-white p-4 rounded-2xl border border-walnut-200/80 shadow-xs flex items-center gap-3">
                <div className="w-10 h-10 rounded-xl bg-amber-500/10 text-amber-600 flex items-center justify-center shrink-0">
                  <Hammer className="w-5 h-5" />
                </div>
                <div>
                  <span className="text-base font-bold text-walnut-900 block leading-tight">{requests.length}</span>
                  <span className="text-[11px] text-softgray block mt-0.5">Custom Inquiries</span>
                </div>
              </div>

              <div className="bg-white p-4 rounded-2xl border border-walnut-200/80 shadow-xs flex items-center gap-3">
                <div className="w-10 h-10 rounded-xl bg-emerald-500/10 text-emerald-600 flex items-center justify-center shrink-0">
                  <TrendingUp className="w-5 h-5" />
                </div>
                <div>
                  <span className="text-base font-bold text-walnut-900 block leading-tight">₹{totalEstimatedRevenue.toLocaleString('en-IN')}</span>
                  <span className="text-[11px] text-softgray block mt-0.5">Est. Studio Volume</span>
                </div>
              </div>
            </div>

            {/* 3. MAIN DETAILS & CONTROLS GRID */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">

              {/* LEFT & CENTER (2 COLS): PROFILE DETAILS CARD (VIEW OR INLINE EDIT) */}
              <div className="lg:col-span-2 space-y-6">
                
                {/* Master Details Card */}
                <div className="bg-white rounded-3xl p-6 sm:p-8 border border-walnut-200/80 shadow-sm space-y-6">
                  <div className="flex items-center justify-between border-b border-walnut-100 pb-4">
                    <div className="flex items-center gap-2.5">
                      <div className="w-8 h-8 rounded-xl bg-gold-500/10 text-gold-600 flex items-center justify-center font-bold">
                        <User className="w-4 h-4" />
                      </div>
                      <div>
                        <h3 className="font-serif font-bold text-base text-walnut-900">
                          Admin Credentials & Studio Identity
                        </h3>
                        <p className="text-xs text-softgray">
                          {isEditingAdminProfile ? 'Update your master details directly in the fields below and click Save.' : 'Official administrative credentials for Glory Furniture Hub operations.'}
                        </p>
                      </div>
                    </div>

                    {/* Small edit button */}
                    {!isEditingAdminProfile && (
                      <button
                        onClick={handleStartEditProfile}
                        className="text-xs font-semibold text-gold-700 hover:text-gold-800 flex items-center gap-1 bg-gold-50 hover:bg-gold-100 px-3 py-1 rounded-lg transition-all border border-gold-200 cursor-pointer"
                        title="Edit Profile"
                      >
                        <Edit3 className="w-3 h-3" />
                        <span>Edit</span>
                      </button>
                    )}
                  </div>

                  {isEditingAdminProfile ? (
                    /* INLINE EDIT FORM DIRECTLY ON PAGE (No small box!) */
                    <form onSubmit={handleSaveAdminProfile} className="space-y-4">
                      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                        <div>
                          <label className="block text-xs font-bold text-walnut-800 mb-1">
                            Admin Full Name *
                          </label>
                          <div className="relative">
                            <User className="w-4 h-4 text-walnut-400 absolute left-3 top-3" />
                            <input
                              type="text"
                              required
                              value={editAdminName}
                              onChange={(e) => setEditAdminName(e.target.value)}
                              placeholder="Master Studio Admin"
                              className="w-full pl-9 pr-3 py-2 text-xs bg-cream-50 border border-walnut-300 rounded-xl focus:outline-none focus:ring-1 focus:ring-walnut-700 font-medium text-walnut-900"
                            />
                          </div>
                        </div>

                        <div>
                          <label className="block text-xs font-bold text-walnut-800 mb-1">
                            Operational Title
                          </label>
                          <div className="relative">
                            <ShieldCheck className="w-4 h-4 text-walnut-400 absolute left-3 top-3" />
                            <input
                              type="text"
                              value={editAdminTitle}
                              onChange={(e) => setEditAdminTitle(e.target.value)}
                              placeholder="Master Craftsman & Studio Operations Director"
                              className="w-full pl-9 pr-3 py-2 text-xs bg-cream-50 border border-walnut-300 rounded-xl focus:outline-none focus:ring-1 focus:ring-walnut-700 font-medium text-walnut-900"
                            />
                          </div>
                        </div>

                        <div>
                          <label className="block text-xs font-bold text-walnut-800 mb-1">
                            Phone / WhatsApp Hotline
                          </label>
                          <div className="relative">
                            <Phone className="w-4 h-4 text-walnut-400 absolute left-3 top-3" />
                            <input
                              type="tel"
                              value={editAdminPhone}
                              onChange={(e) => setEditAdminPhone(e.target.value)}
                              placeholder="+91 98765 43210"
                              className="w-full pl-9 pr-3 py-2 text-xs bg-cream-50 border border-walnut-300 rounded-xl focus:outline-none focus:ring-1 focus:ring-walnut-700 font-medium text-walnut-900"
                            />
                          </div>
                        </div>

                        <div>
                          <label className="block text-xs font-bold text-walnut-800 mb-1">
                            Official Email Address
                          </label>
                          <div className="relative">
                            <Mail className="w-4 h-4 text-walnut-400 absolute left-3 top-3" />
                            <input
                              type="email"
                              value={editAdminEmail}
                              onChange={(e) => setEditAdminEmail(e.target.value)}
                              placeholder="admin@gloryfurniture.com"
                              className="w-full pl-9 pr-3 py-2 text-xs bg-cream-50 border border-walnut-300 rounded-xl focus:outline-none focus:ring-1 focus:ring-walnut-700 font-medium text-walnut-900"
                            />
                          </div>
                        </div>
                      </div>

                      <div>
                        <label className="block text-xs font-bold text-walnut-800 mb-1">
                          Workshop / Studio Headquarters
                        </label>
                        <div className="relative">
                          <MapPin className="w-4 h-4 text-walnut-400 absolute left-3 top-3" />
                          <input
                            type="text"
                            value={editAdminLocation}
                            onChange={(e) => setEditAdminLocation(e.target.value)}
                            placeholder="Hyderabad Main Workshop & Studio, Jubilee Hills, Hyderabad"
                            className="w-full pl-9 pr-3 py-2 text-xs bg-cream-50 border border-walnut-300 rounded-xl focus:outline-none focus:ring-1 focus:ring-walnut-700 font-medium text-walnut-900"
                          />
                        </div>
                      </div>

                      <div>
                        <label className="block text-xs font-bold text-walnut-800 mb-1">
                          Studio Operating Hours
                        </label>
                        <div className="relative">
                          <Clock className="w-4 h-4 text-walnut-400 absolute left-3 top-3" />
                          <input
                            type="text"
                            value={editAdminHours}
                            onChange={(e) => setEditAdminHours(e.target.value)}
                            placeholder="Monday - Saturday: 9:30 AM - 8:30 PM | Sunday: By Appointment"
                            className="w-full pl-9 pr-3 py-2 text-xs bg-cream-50 border border-walnut-300 rounded-xl focus:outline-none focus:ring-1 focus:ring-walnut-700 font-medium text-walnut-900"
                          />
                        </div>
                      </div>

                      <div>
                        <label className="block text-xs font-bold text-walnut-800 mb-1">
                          Administrative Bio & Craftsmanship Mandate
                        </label>
                        <textarea
                          rows="3"
                          value={editAdminBio}
                          onChange={(e) => setEditAdminBio(e.target.value)}
                          placeholder="Overseeing timber procurement, artisan joinery, and custom luxury commissions..."
                          className="w-full p-3 text-xs bg-cream-50 border border-walnut-300 rounded-xl focus:outline-none focus:ring-1 focus:ring-walnut-700 font-medium text-walnut-900"
                        />
                      </div>

                      <div className="flex items-center gap-3 pt-3 border-t border-walnut-100">
                        <button
                          type="button"
                          onClick={handleCancelEditProfile}
                          className="px-4 py-2 text-xs font-bold text-walnut-700 bg-cream-100 hover:bg-cream-200 rounded-xl transition-all cursor-pointer"
                        >
                          Cancel
                        </button>
                        <button
                          type="submit"
                          className="px-5 py-2 text-xs font-bold text-gold-400 bg-walnut-900 hover:bg-walnut-800 rounded-xl flex items-center gap-2 shadow-sm transition-all cursor-pointer"
                        >
                          <Check className="w-3.5 h-3.5" />
                          <span>Save Profile Changes</span>
                        </button>
                      </div>
                    </form>
                  ) : (
                    /* VIEW MODE IN HIGH RESOLUTION */
                    <div className="space-y-4">
                      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                        
                        <div className="p-4 rounded-2xl bg-cream-50/70 border border-walnut-100">
                          <span className="text-[11px] font-semibold text-softgray block">Admin Name</span>
                          <span className="text-sm font-bold text-walnut-900 mt-1 block">{adminName}</span>
                        </div>

                        <div className="p-4 rounded-2xl bg-cream-50/70 border border-walnut-100">
                          <span className="text-[11px] font-semibold text-softgray block">Role & Authority</span>
                          <div className="flex items-center gap-2 mt-1">
                            <span className="text-sm font-bold text-walnut-900">Super Administrator</span>
                            <span className="bg-emerald-100 text-emerald-800 text-[10px] font-bold px-2 py-0.5 rounded-md">
                              Root Privileges
                            </span>
                          </div>
                        </div>

                        <div className="p-4 rounded-2xl bg-cream-50/70 border border-walnut-100">
                          <span className="text-[11px] font-semibold text-softgray block">Phone / WhatsApp Hotline</span>
                          <span className="text-sm font-bold text-walnut-900 mt-1 block flex items-center gap-1.5">
                            <Phone className="w-3.5 h-3.5 text-gold-600" />
                            {adminPhone}
                          </span>
                        </div>

                        <div className="p-4 rounded-2xl bg-cream-50/70 border border-walnut-100">
                          <span className="text-[11px] font-semibold text-softgray block">Official Email Address</span>
                          <span className="text-sm font-bold text-walnut-900 mt-1 block flex items-center gap-1.5">
                            <Mail className="w-3.5 h-3.5 text-gold-600" />
                            {adminEmail}
                          </span>
                        </div>

                      </div>

                      <div className="p-4 rounded-2xl bg-cream-50/70 border border-walnut-100">
                        <span className="text-[11px] font-semibold text-softgray block">Studio Workshop Location</span>
                        <span className="text-sm font-bold text-walnut-900 mt-1 block flex items-center gap-2">
                          <MapPin className="w-4 h-4 text-gold-600 shrink-0" />
                          {adminStudioLocation}
                        </span>
                      </div>

                      <div className="p-4 rounded-2xl bg-cream-50/70 border border-walnut-100">
                        <span className="text-[11px] font-semibold text-softgray block">Operating Schedule</span>
                        <span className="text-xs font-semibold text-walnut-800 mt-1 block flex items-center gap-2">
                          <Clock className="w-4 h-4 text-gold-600 shrink-0" />
                          {adminHours}
                        </span>
                      </div>

                      <div className="p-4 rounded-2xl bg-cream-50/70 border border-walnut-100">
                        <span className="text-[11px] font-semibold text-softgray block">Craftsmanship Mandate</span>
                        <p className="text-xs text-walnut-800 mt-1 leading-relaxed">
                          {adminBio}
                        </p>
                      </div>

                      {/* Small button to edit right below details */}
                      <div className="pt-2 flex justify-end">
                        <button
                          onClick={handleStartEditProfile}
                          className="px-3 py-1.5 bg-cream-100 hover:bg-gold-50 border border-walnut-200 hover:border-gold-400 text-walnut-800 text-xs font-bold rounded-xl flex items-center gap-1.5 transition-all cursor-pointer"
                        >
                          <Edit3 className="w-3 h-3 text-gold-600" />
                          <span>Edit Details</span>
                        </button>
                      </div>
                    </div>
                  )}
                </div>

                {/* Studio Quality & Operational Standards Card */}
                <div className="bg-white rounded-3xl p-6 border border-walnut-200/80 shadow-sm space-y-4">
                  <div className="flex items-center gap-2 text-walnut-900">
                    <Award className="w-5 h-5 text-gold-600" />
                    <h3 className="font-serif font-bold text-sm">Studio Quality & Sourcing Standards</h3>
                  </div>

                  <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 text-xs">
                    <div className="p-3.5 rounded-2xl bg-cream-50/80 border border-walnut-100 space-y-1">
                      <div className="font-bold text-walnut-900 flex items-center gap-1">
                        <span>🪵</span>
                        <span>100% Burma Teak</span>
                      </div>
                      <p className="text-[11px] text-softgray leading-relaxed">
                        Ethically procured first-grade timber seasoned to 8-12% moisture for heirloom durability.
                      </p>
                    </div>

                    <div className="p-3.5 rounded-2xl bg-cream-50/80 border border-walnut-100 space-y-1">
                      <div className="font-bold text-walnut-900 flex items-center gap-1">
                        <span>🔨</span>
                        <span>Mortise & Tenon Joinery</span>
                      </div>
                      <p className="text-[11px] text-softgray leading-relaxed">
                        Built without cheap fasteners to maintain structural integrity across decades of use.
                      </p>
                    </div>

                    <div className="p-3.5 rounded-2xl bg-cream-50/80 border border-walnut-100 space-y-1">
                      <div className="font-bold text-walnut-900 flex items-center gap-1">
                        <span>✨</span>
                        <span>Natural Wax Polish</span>
                      </div>
                      <p className="text-[11px] text-softgray leading-relaxed">
                        Hand-rubbed organic beeswax and oil finishes that enrich the natural wood grain.
                      </p>
                    </div>
                  </div>
                </div>

              </div>

              {/* RIGHT COLUMN (1 COL): PRIVILEGES & QUICK NAVIGATION */}
              <div className="space-y-6">
                
                {/* Privileges Card */}
                <div className="bg-white rounded-3xl p-6 border border-walnut-200/80 shadow-sm space-y-4">
                  <div className="flex items-center gap-2 text-walnut-900">
                    <ShieldCheck className="w-5 h-5 text-gold-600" />
                    <h3 className="font-serif font-bold text-sm">System Authority & Privileges</h3>
                  </div>

                  <div className="space-y-2.5 text-xs text-walnut-800">
                    <div className="flex items-start gap-2.5 p-2.5 rounded-xl bg-cream-50/80 border border-walnut-100">
                      <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0 mt-0.5" />
                      <div>
                        <strong className="block text-walnut-900">Products Catalog</strong>
                        <span className="text-[11px] text-softgray">Add pieces, update teak bed sizes & costs</span>
                      </div>
                    </div>

                    <div className="flex items-start gap-2.5 p-2.5 rounded-xl bg-cream-50/80 border border-walnut-100">
                      <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0 mt-0.5" />
                      <div>
                        <strong className="block text-walnut-900">Order Management</strong>
                        <span className="text-[11px] text-softgray">Advance live order tracking through 5 stages</span>
                      </div>
                    </div>

                    <div className="flex items-start gap-2.5 p-2.5 rounded-xl bg-cream-50/80 border border-walnut-100">
                      <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0 mt-0.5" />
                      <div>
                        <strong className="block text-walnut-900">Custom Teak Specs</strong>
                        <span className="text-[11px] text-softgray">Review customer dimensions & send WhatsApp quotes</span>
                      </div>
                    </div>

                    <div className="flex items-start gap-2.5 p-2.5 rounded-xl bg-cream-50/80 border border-walnut-100">
                      <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0 mt-0.5" />
                      <div>
                        <strong className="block text-walnut-900">Analytics & Turnover</strong>
                        <span className="text-[11px] text-softgray">Monitor studio sales & inventory velocity</span>
                      </div>
                    </div>
                  </div>
                </div>

                {/* Session Security Card */}
                <div className="bg-white rounded-3xl p-6 border border-walnut-200/80 shadow-sm space-y-3">
                  <div className="flex items-center gap-2 text-walnut-900">
                    <Lock className="w-4 h-4 text-gold-600" />
                    <h3 className="font-serif font-bold text-xs uppercase tracking-wider text-walnut-800">Security Clearance</h3>
                  </div>

                  <div className="space-y-2 text-[11px] text-walnut-700 bg-cream-50/70 p-3 rounded-xl border border-walnut-100">
                    <div className="flex items-center justify-between">
                      <span className="text-softgray">Security Protocol:</span>
                      <span className="font-bold text-emerald-700">TLS 1.3 End-to-End</span>
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-softgray">Session Access:</span>
                      <span className="font-bold text-walnut-900">Master Console Active</span>
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-softgray">Multi-Factor Status:</span>
                      <span className="font-bold text-emerald-700">Verified Root</span>
                    </div>
                  </div>
                </div>

                {/* Quick Navigation Panel */}
                <div className="bg-walnut-900 text-cream-100 rounded-3xl p-6 border border-walnut-800 shadow-sm space-y-3">
                  <h4 className="font-serif font-bold text-xs text-gold-400 uppercase tracking-wider">
                    Quick Studio Navigation
                  </h4>
                  <div className="grid grid-cols-2 gap-2 text-xs">
                    <button
                      onClick={() => handleTabChange('products')}
                      className="p-2.5 bg-walnut-800 hover:bg-walnut-700 rounded-xl text-left font-semibold text-cream-100 border border-walnut-700 transition-all cursor-pointer"
                    >
                      📦 Products ({products.length})
                    </button>
                    <button
                      onClick={() => handleTabChange('orders')}
                      className="p-2.5 bg-walnut-800 hover:bg-walnut-700 rounded-xl text-left font-semibold text-cream-100 border border-walnut-700 transition-all cursor-pointer"
                    >
                      🚚 Orders ({orders.length})
                    </button>
                    <button
                      onClick={() => handleTabChange('custom-requests')}
                      className="p-2.5 bg-walnut-800 hover:bg-walnut-700 rounded-xl text-left font-semibold text-cream-100 border border-walnut-700 transition-all cursor-pointer"
                    >
                      🔨 Custom Specs
                    </button>
                    <button
                      onClick={() => handleTabChange('overview')}
                      className="p-2.5 bg-walnut-800 hover:bg-walnut-700 rounded-xl text-left font-semibold text-cream-100 border border-walnut-700 transition-all cursor-pointer"
                    >
                      📊 Analytics
                    </button>
                  </div>

                  <div className="pt-2">
                    <button
                      onClick={handleAdminLogout}
                      className="w-full py-2 bg-dustyrose/20 hover:bg-dustyrose/30 text-red-200 border border-dustyrose/40 rounded-xl font-bold text-xs flex items-center justify-center gap-1.5 transition-all cursor-pointer"
                    >
                      <LogOut className="w-3.5 h-3.5" />
                      <span>Log Out from Workspace</span>
                    </button>
                  </div>
                </div>

              </div>

            </div>

          </div>
        )}

      </main>

      {/* =================================================================== */}
      {/* ADD PRODUCT MODAL (With Dynamic Bed Sizes/Prices '+' Feature) */}
      {/* =================================================================== */}
      <Modal
        isOpen={isAddModalOpen}
        onClose={() => setIsAddModalOpen(false)}
        title="Add New Handcrafted Furniture Piece"
        position="center"
      >
        <form onSubmit={handleAddProduct} className="space-y-3.5 text-xs max-h-[80vh] overflow-y-auto pr-1">
          
          {/* 1. SELECT PRODUCT TYPE */}
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
                
                {/* '+' Button to add new size/price rows */}
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
            /* 3. NON-BED ITEMS -> ONLY SINGLE PRICE */
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
            className="w-full mt-2 bg-walnut-900 text-gold-400 font-bold"
            disabled={isSaving || isUploadingImage}
            icon={isSaving ? Loader2 : Check}
          >
            {isSaving ? 'Publishing Piece...' : 'Save & Publish Listing'}
          </Button>
        </form>
      </Modal>

      {/* =================================================================== */}
      {/* MODAL: GENERATE STUDIO TAX INVOICE (GST 18%) */}
      {/* =================================================================== */}
      <Modal
        isOpen={isCreateInvoiceModalOpen}
        onClose={() => setIsCreateInvoiceModalOpen(false)}
        title="Generate Studio Tax Invoice (GST 18%)"
      >
        <form onSubmit={handleCreateInvoice} className="space-y-4 max-h-[78vh] overflow-y-auto pr-1">
          <div className="bg-cream-100 p-3 rounded-xl border border-walnut-200/60 text-xs">
            <span className="font-bold text-walnut-900 block">Glory Furniture Hub GST Billing Engine</span>
            <p className="text-softgray text-[11px] mt-0.5">
              Generates an official tax invoice with customer details, timber specifications, and automatic 18% GST calculation.
            </p>
          </div>

          <div className="space-y-3">
            <h4 className="text-xs font-bold text-walnut-900 uppercase tracking-wider border-b border-cream-200 pb-1">
              1. Customer Information
            </h4>
            
            <Input
              label="Customer Full Name *"
              placeholder="e.g. Suresh Nambiar"
              value={invCustomerName}
              onChange={(e) => setInvCustomerName(e.target.value)}
              required
            />

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
              <Input
                label="Customer Phone Number *"
                placeholder="+91 98765 43210"
                value={invCustomerPhone}
                onChange={(e) => setInvCustomerPhone(e.target.value)}
              />
              <Input
                label="Customer Email Address"
                placeholder="client@example.com"
                type="email"
                value={invCustomerEmail}
                onChange={(e) => setInvCustomerEmail(e.target.value)}
              />
            </div>

            <div>
              <label className="block text-[11px] font-semibold text-walnut-700 mb-1">
                Delivery / Site Address
              </label>
              <textarea
                rows="2"
                placeholder="Plot/Flat No, Street, Landmark, Hyderabad..."
                value={invCustomerAddress}
                onChange={(e) => setInvCustomerAddress(e.target.value)}
                className="w-full text-xs p-2.5 bg-cream-100 border border-walnut-200 rounded-xl focus:bg-white focus:border-gold-500"
              />
            </div>
          </div>

          <div className="space-y-3 pt-2">
            <h4 className="text-xs font-bold text-walnut-900 uppercase tracking-wider border-b border-cream-200 pb-1">
              2. Furniture Spec & Pricing
            </h4>

            <Input
              label="Furniture Item Title *"
              placeholder="e.g. Royal Burma Teak King Cot (6x6 ft)"
              value={invItemTitle}
              onChange={(e) => setInvItemTitle(e.target.value)}
              required
            />

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
              <div>
                <label className="block text-[11px] font-semibold text-walnut-700 mb-1">Category</label>
                <select
                  value={invCategory}
                  onChange={(e) => setInvCategory(e.target.value)}
                  className="w-full text-xs p-2.5 bg-cream-100 border border-walnut-200 rounded-xl focus:bg-white focus:border-gold-500"
                >
                  {PRODUCT_TYPES.map(pt => (
                    <option key={pt.id} value={pt.id}>{pt.label}</option>
                  ))}
                </select>
              </div>

              <Input
                label="Timber Specification"
                placeholder="e.g. Pure Solid Burma Teak Wood"
                value={invMaterial}
                onChange={(e) => setInvMaterial(e.target.value)}
              />
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
              <Input
                label="Base Price (₹) *"
                type="number"
                placeholder="95000"
                value={invBaseAmount}
                onChange={(e) => setInvBaseAmount(e.target.value)}
                required
              />

              <div>
                <label className="block text-[11px] font-semibold text-walnut-700 mb-1">GST Rate (%)</label>
                <input
                  type="number"
                  readOnly
                  value={invGstRate}
                  className="w-full text-xs p-2.5 bg-cream-200 border border-walnut-200 rounded-xl text-walnut-700 font-semibold"
                />
              </div>

              <Input
                label="Advance Paid (₹)"
                type="number"
                placeholder="50000"
                value={invAdvancePaid}
                onChange={(e) => setInvAdvancePaid(e.target.value)}
              />
            </div>

            {/* Calculated Breakdown Card */}
            <div className="bg-walnut-900 text-white p-3.5 rounded-xl border border-walnut-800 space-y-1.5 text-xs">
              <div className="flex justify-between text-cream-300">
                <span>Base Subtotal:</span>
                <span>₹{(Number(invBaseAmount) || 0).toLocaleString('en-IN')}</span>
              </div>
              <div className="flex justify-between text-cream-300">
                <span>GST (18% HSN 9403):</span>
                <span>₹{Math.round(((Number(invBaseAmount) || 0) * (Number(invGstRate) || 18)) / 100).toLocaleString('en-IN')}</span>
              </div>
              <div className="flex justify-between font-bold text-gold-400 border-t border-walnut-800 pt-1.5 text-sm">
                <span>Total Invoice Value:</span>
                <span>
                  ₹{(
                    (Number(invBaseAmount) || 0) + 
                    Math.round(((Number(invBaseAmount) || 0) * (Number(invGstRate) || 18)) / 100)
                  ).toLocaleString('en-IN')}
                </span>
              </div>
              <div className="flex justify-between text-emerald-400 text-xs">
                <span>Advance Recorded:</span>
                <span>₹{(Number(invAdvancePaid) || 0).toLocaleString('en-IN')}</span>
              </div>
              <div className="flex justify-between font-bold text-rose-400 text-xs border-t border-walnut-800/80 pt-1">
                <span>Balance Due at Delivery:</span>
                <span>
                  ₹{Math.max(
                    0, 
                    ((Number(invBaseAmount) || 0) + Math.round(((Number(invBaseAmount) || 0) * (Number(invGstRate) || 18)) / 100)) - (Number(invAdvancePaid) || 0)
                  ).toLocaleString('en-IN')}
                </span>
              </div>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
              <div>
                <label className="block text-[11px] font-semibold text-walnut-700 mb-1">Payment Method</label>
                <select
                  value={invPaymentMethod}
                  onChange={(e) => setInvPaymentMethod(e.target.value)}
                  className="w-full text-xs p-2.5 bg-cream-100 border border-walnut-200 rounded-xl"
                >
                  <option value="UPI (GPay)">UPI (Google Pay)</option>
                  <option value="UPI (PhonePe)">UPI (PhonePe)</option>
                  <option value="NEFT / Bank Transfer">NEFT / RTGS Bank Transfer</option>
                  <option value="Credit Card">Credit / Debit Card</option>
                  <option value="Cash at Studio">Cash at Studio</option>
                  <option value="Cheque">Account Payee Cheque</option>
                </select>
              </div>

              <div>
                <label className="block text-[11px] font-semibold text-walnut-700 mb-1">Warranty & Notes</label>
                <input
                  type="text"
                  value={invNotes}
                  onChange={(e) => setInvNotes(e.target.value)}
                  placeholder="e.g. Includes 15-Year Burma Teak Warranty"
                  className="w-full text-xs p-2.5 bg-cream-100 border border-walnut-200 rounded-xl"
                />
              </div>
            </div>
          </div>

          <div className="pt-2 flex items-center justify-end gap-2">
            <Button
              type="button"
              variant="outline"
              size="sm"
              onClick={() => setIsCreateInvoiceModalOpen(false)}
            >
              Cancel
            </Button>
            <Button
              type="submit"
              variant="primary"
              size="sm"
              className="bg-walnut-900 text-gold-400 font-bold"
              icon={Check}
            >
              Save & Generate Invoice
            </Button>
          </div>
        </form>
      </Modal>

      {/* =================================================================== */}
      {/* MODAL: PRINTABLE LUXURY TAX INVOICE */}
      {/* =================================================================== */}
      <Modal
        isOpen={Boolean(selectedInvoiceForView)}
        onClose={() => setSelectedInvoiceForView(null)}
        title="Commercial Tax Invoice Viewer"
      >
        {selectedInvoiceForView && (
          <div className="space-y-4">
            {/* Action Bar */}
            <div className="flex items-center justify-between bg-cream-100 p-2.5 rounded-xl border border-walnut-200/60">
              <span className="text-xs font-semibold text-walnut-800">
                Official Studio Record: <strong className="font-mono text-walnut-900">{selectedInvoiceForView.id}</strong>
              </span>
              <div className="flex items-center gap-2">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => window.print()}
                  icon={Printer}
                  className="text-xs"
                >
                  Print / Save PDF
                </Button>
                <a
                  href={`https://wa.me/${selectedInvoiceForView.customerPhone.replace(/[^0-9]/g, '')}?text=Dear%20${encodeURIComponent(selectedInvoiceForView.customerName)},%20here%20is%20your%20tax%20invoice%20${selectedInvoiceForView.id}%20from%20Glory%20Furniture%20Hub%20for%20${encodeURIComponent(selectedInvoiceForView.itemTitle)}.%20Total:%20INR%20${selectedInvoiceForView.totalAmount},%20Balance%20Due:%20INR%20${selectedInvoiceForView.balanceDue}.%20Thank%20you!`}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="py-1.5 px-3 bg-emerald-700 hover:bg-emerald-800 text-white text-xs font-semibold rounded-lg flex items-center gap-1.5 transition-all"
                >
                  <Share2 className="w-3.5 h-3.5" /> WhatsApp Invoice
                </a>
              </div>
            </div>

            {/* Printable Tax Invoice Sheet */}
            <div className="bg-white p-6 sm:p-8 rounded-2xl border border-walnut-200 shadow-sm text-walnut-900">
              
              {/* Studio Header */}
              <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between pb-6 border-b-2 border-walnut-900/80 gap-4">
                <div>
                  <div className="flex items-center gap-2">
                    <span className="text-2xl">👑</span>
                    <h2 className="font-serif font-bold text-2xl tracking-wider text-walnut-900 uppercase">
                      Glory Furniture Hub
                    </h2>
                  </div>
                  <p className="text-xs font-serif text-gold-700 tracking-wider mt-0.5">
                    Master Craftsmen • Handcrafted Pure Burma Teak Wood Furniture
                  </p>
                  <p className="text-[11px] text-softgray mt-1 leading-snug">
                    Plot 14, Luxury Furniture Street, Road No. 36, Jubilee Hills, Hyderabad, Telangana 500033<br />
                    Phone: +91 98765 43210 | contact@gloryfurniture.com
                  </p>
                </div>

                <div className="sm:text-right bg-cream-100 p-3 rounded-xl border border-cream-300">
                  <span className="text-[10px] font-bold uppercase tracking-wider text-softgray block">TAX INVOICE</span>
                  <strong className="text-lg font-mono text-walnut-900 block mt-0.5">{selectedInvoiceForView.id}</strong>
                  <span className="text-[11px] text-softgray block">Date: {selectedInvoiceForView.invoiceDate}</span>
                  <span className="text-[11px] font-bold text-walnut-800 block mt-1">
                    GSTIN: <span className="font-mono text-gold-700">36AAACG1234F1Z5</span>
                  </span>
                </div>
              </div>

              {/* Invoice Meta Grid */}
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 py-4 border-b border-cream-200 text-xs">
                <div>
                  <span className="text-[10px] font-bold uppercase tracking-wider text-softgray block mb-1">
                    Billed & Delivered To:
                  </span>
                  <strong className="text-sm text-walnut-900 block">{selectedInvoiceForView.customerName}</strong>
                  <p className="text-softgray mt-0.5">{selectedInvoiceForView.customerAddress}</p>
                  <p className="text-softgray mt-1">
                    Phone: <strong className="text-walnut-800">{selectedInvoiceForView.customerPhone}</strong> | Email: {selectedInvoiceForView.customerEmail}
                  </p>
                </div>

                <div className="sm:text-right space-y-1">
                  <div>
                    <span className="text-softgray">Associated Order: </span>
                    <strong className="font-mono text-walnut-900">{selectedInvoiceForView.orderId}</strong>
                  </div>
                  <div>
                    <span className="text-softgray">Payment Terms: </span>
                    <strong className="text-walnut-900">{selectedInvoiceForView.paymentMethod}</strong>
                  </div>
                  <div>
                    <span className="text-softgray">Warranty Certificate: </span>
                    <strong className="text-gold-700 font-bold">{selectedInvoiceForView.warrantyYears}-Year Teak Guarantee</strong>
                  </div>
                  <div>
                    <span className="text-softgray">Payment Status: </span>
                    <span
                      className={`inline-block px-2 py-0.5 rounded text-[10px] font-bold uppercase ${
                        selectedInvoiceForView.status === 'Paid'
                          ? 'bg-emerald-100 text-emerald-800'
                          : selectedInvoiceForView.status === 'Partial'
                          ? 'bg-amber-100 text-amber-800'
                          : 'bg-rose-100 text-rose-800'
                      }`}
                    >
                      {selectedInvoiceForView.status}
                    </span>
                  </div>
                </div>
              </div>

              {/* Itemized Line Items Table */}
              <div className="py-4">
                <table className="w-full text-left border-collapse text-xs">
                  <thead>
                    <tr className="bg-cream-100 border-y border-walnut-200 text-walnut-800 font-bold text-[11px]">
                      <th className="py-2.5 px-3">#</th>
                      <th className="py-2.5 px-3">Description of Goods</th>
                      <th className="py-2.5 px-3">HSN Code</th>
                      <th className="py-2.5 px-3">Wood Specification</th>
                      <th className="py-2.5 px-3 text-center">Qty</th>
                      <th className="py-2.5 px-3 text-right">Rate (₹)</th>
                      <th className="py-2.5 px-3 text-right">Amount (₹)</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-cream-200">
                    <tr>
                      <td className="py-3 px-3 text-softgray font-mono">1</td>
                      <td className="py-3 px-3">
                        <strong className="text-walnut-900 block">{selectedInvoiceForView.itemTitle}</strong>
                        <span className="text-[11px] text-softgray">{selectedInvoiceForView.category}</span>
                      </td>
                      <td className="py-3 px-3 font-mono text-softgray">{selectedInvoiceForView.hsnCode}</td>
                      <td className="py-3 px-3 text-gold-700 font-medium">{selectedInvoiceForView.material}</td>
                      <td className="py-3 px-3 text-center font-bold">{selectedInvoiceForView.quantity}</td>
                      <td className="py-3 px-3 text-right font-mono">₹{selectedInvoiceForView.baseAmount.toLocaleString('en-IN')}</td>
                      <td className="py-3 px-3 text-right font-mono font-bold">₹{selectedInvoiceForView.baseAmount.toLocaleString('en-IN')}</td>
                    </tr>
                  </tbody>
                </table>
              </div>

              {/* Calculation Breakdown & Taxes */}
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-6 pt-4 border-t border-cream-200 text-xs">
                <div className="space-y-2 bg-cream-100/60 p-3.5 rounded-xl border border-cream-200">
                  <span className="text-[11px] font-bold text-walnut-900 block">Notes & Studio Declaration</span>
                  <p className="text-[11px] text-softgray leading-relaxed">
                    {selectedInvoiceForView.notes}
                  </p>
                  <p className="text-[10px] text-softgray mt-1 leading-snug">
                    * 15-year guarantee protects against termite infestation and structural joint cleavage. Crafted from ethically seasoned solid timber.
                  </p>
                </div>

                <div className="space-y-2">
                  <div className="flex justify-between text-softgray">
                    <span>Taxable Base Value:</span>
                    <span className="font-mono text-walnut-900">₹{selectedInvoiceForView.baseAmount.toLocaleString('en-IN')}</span>
                  </div>
                  <div className="flex justify-between text-softgray">
                    <span>Central GST (CGST 9%):</span>
                    <span className="font-mono text-walnut-900">₹{Math.round(selectedInvoiceForView.gstAmount / 2).toLocaleString('en-IN')}</span>
                  </div>
                  <div className="flex justify-between text-softgray">
                    <span>State GST (SGST 9%):</span>
                    <span className="font-mono text-walnut-900">₹{Math.round(selectedInvoiceForView.gstAmount / 2).toLocaleString('en-IN')}</span>
                  </div>
                  <div className="flex justify-between font-bold text-walnut-900 pt-2 border-t border-walnut-200 text-sm">
                    <span>Gross Invoice Total:</span>
                    <span className="font-serif text-walnut-900">₹{selectedInvoiceForView.totalAmount.toLocaleString('en-IN')}</span>
                  </div>
                  <div className="flex justify-between text-emerald-700 font-semibold">
                    <span>Advance Received ({selectedInvoiceForView.paymentMethod}):</span>
                    <span className="font-mono">₹{selectedInvoiceForView.advancePaid.toLocaleString('en-IN')}</span>
                  </div>
                  <div className="flex justify-between font-bold text-rose-600 pt-1 border-t border-dashed border-walnut-200 text-sm">
                    <span>Net Balance Payable:</span>
                    <span className="font-serif">₹{selectedInvoiceForView.balanceDue.toLocaleString('en-IN')}</span>
                  </div>
                </div>
              </div>

              {/* Signature / Authorization Stamp */}
              <div className="pt-8 mt-6 border-t border-cream-200 flex flex-col sm:flex-row items-center justify-between gap-4 text-xs text-softgray">
                <div>
                  <span className="block font-semibold text-walnut-900">Glory Furniture Hub Studio Seal</span>
                  <span className="text-[10px]">Verified Certified Burma Teak Timber</span>
                </div>
                <div className="text-center sm:text-right">
                  <div className="w-36 h-0.5 bg-walnut-300 mx-auto sm:ml-auto mb-1"></div>
                  <strong className="text-walnut-900 block">Authorized Studio Signatory</strong>
                  <span className="text-[10px]">Master Craftsman & Operations Director</span>
                </div>
              </div>

            </div>

            {/* Modal Bottom Close */}
            <div className="flex justify-end gap-2 pt-2">
              <Button
                variant="outline"
                size="sm"
                onClick={() => setSelectedInvoiceForView(null)}
              >
                Close Invoice Viewer
              </Button>
            </div>
          </div>
        )}
      </Modal>

    </div>
  )
}


