import React, { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import Header from '../components/common/Header'
import Modal from '../components/common/Modal'
import Toast from '../components/common/Toast'
import Button from '../components/common/Button'
import { useAppStore } from '../store/useAppStore'
import { MOCK_PRODUCTS } from '../data/mockData'
import { 
  Package, Heart, Hammer, Bell, Info, Phone, HelpCircle, LogOut, 
  ChevronRight, Edit3, MapPin, ShieldCheck, Sparkles, Truck, 
  CheckCircle2, Droplets, Sun, Feather, Wrench, ArrowRight,
  Clock, Award, MessageSquare, Star, ShoppingBag, Compass, UserCheck, LogIn
} from 'lucide-react'

export default function ProfileScreen() {
  const navigate = useNavigate()
  const { user, setUser, wishlist = [], toggleWishlist, userBookings = [], customRequests = [], notifications = [], savedAddresses = [], addSavedAddress } = useAppStore()

  const [toastMessage, setToastMessage] = useState('')
  const [isCareGuideOpen, setIsCareGuideOpen] = useState(false)
  const [isAddressModalOpen, setIsAddressModalOpen] = useState(false)
  
  const getInitialAddress = () => {
    if (user?.address) return user.address
    if (savedAddresses && savedAddresses.length > 0) {
      const a = savedAddresses[0]
      return `${a.flatNo || ''}, ${a.street || ''}, ${a.landmark ? a.landmark + ', ' : ''}${a.city || ''}, ${a.state || ''} - ${a.pincode || ''}`
    }
    return ''
  }

  const [deliveryAddress, setDeliveryAddress] = useState(getInitialAddress)
  const [tempAddress, setTempAddress] = useState(deliveryAddress)

  useEffect(() => {
    const current = getInitialAddress()
    setDeliveryAddress(current)
    setTempAddress(current)
  }, [user, savedAddresses])

  const unreadCount = (notifications || []).filter(n => !n.read).length
  const latestBooking = userBookings && userBookings.length > 0 ? userBookings[0] : null

  const handleSignOut = () => {
    if (window.confirm('Are you sure you want to sign out from your account?')) {
      setUser(null)
      localStorage.removeItem('glory_user')
      navigate('/login', { replace: true })
    }
  }

  const handleSaveAddress = (e) => {
    e.preventDefault()
    setDeliveryAddress(tempAddress.trim())
    if (user) {
      setUser({ ...user, address: tempAddress.trim() })
    }
    setIsAddressModalOpen(false)
    setToastMessage('Delivery address updated successfully!')
  }

  // Recommended products if wishlist is empty
  const showcaseProducts = wishlist.length > 0 ? wishlist : MOCK_PRODUCTS.slice(0, 4)

  return (
    <div className="min-h-screen bg-[#FDFBF7] text-walnut-900 pb-24 md:pb-16 w-full font-sans">
      <Header title="My Studio Account" showBack={false} />
      <Toast message={toastMessage} onClose={() => setToastMessage('')} />

      {/* EXPANDED FULL-WIDTH DESKTOP CONTAINER (Fills widescreen beautifully) */}
      <div className="w-full px-4 sm:px-8 lg:px-12 max-w-7xl mx-auto py-6 space-y-6">
        
        {/* 1. LUXURY HERO PATRON BANNER (Wide Grand Header) */}
        <div className="bg-gradient-to-br from-[#231B15] via-[#2D231B] to-[#1A1410] text-white p-6 sm:p-8 lg:p-10 rounded-3xl border border-walnut-800 shadow-xl relative overflow-hidden">
          {/* Subtle Golden Ambient Glows */}
          <div className="absolute top-0 right-0 w-96 h-96 bg-gold-500/10 rounded-full blur-3xl -mr-20 -mt-20 pointer-events-none" />
          <div className="absolute bottom-0 left-1/3 w-64 h-64 bg-gold-600/5 rounded-full blur-2xl pointer-events-none" />

          <div className="relative z-10 flex flex-col md:flex-row items-start md:items-center justify-between gap-6">
            
            {/* Left: Avatar & Identity */}
            <div className="flex items-center gap-4 sm:gap-6">
              {/* Grand Monogram Avatar */}
              <div className="relative">
                <div className="w-16 sm:w-20 h-16 sm:h-20 rounded-2xl bg-[#17120E] text-gold-400 font-serif font-bold text-2xl sm:text-3xl flex items-center justify-center shadow-lg border-2 border-gold-500/50">
                  {user?.name ? user.name.charAt(0).toUpperCase() : 'G'}
                </div>
                <div className="absolute -bottom-1 -right-1 w-6 h-6 bg-gold-500 text-walnut-900 rounded-full flex items-center justify-center shadow-md">
                  <Sparkles className="w-3.5 h-3.5 fill-walnut-900 text-walnut-900" />
                </div>
              </div>

              <div>
                <div className="flex flex-wrap items-center gap-2">
                  <h1 className="font-serif font-bold text-xl sm:text-2xl lg:text-3xl text-cream-100 leading-tight">
                    {user?.name || 'Valued Patron'}
                  </h1>
                  <span className="bg-gold-500/20 text-gold-400 border border-gold-500/40 text-[10px] sm:text-xs font-bold px-2.5 py-0.5 rounded-full uppercase tracking-wider">
                    ★ Glory Heritage Patron
                  </span>
                </div>

                <p className="text-xs sm:text-sm text-cream-300 mt-1">{user?.email || 'Email not registered'}</p>

                <div className="flex flex-wrap items-center gap-4 mt-2 text-xs text-cream-300">
                  <span className="flex items-center gap-1">
                    <Phone className="w-3.5 h-3.5 text-gold-400" />
                    <span>{user?.phone || 'Phone not added'}</span>
                  </span>
                  <span className="text-cream-400/60 hidden sm:inline">•</span>
                  <span className="flex items-center gap-1 text-cream-300">
                    <Award className="w-3.5 h-3.5 text-gold-400" />
                    <span>Member ID: #GLR-{user?.id ? String(user.id).slice(-4) : '7892'}</span>
                  </span>
                </div>
              </div>
            </div>

            {/* Right: Quick Edit & Fast Actions */}
            <div className="flex flex-wrap items-center gap-2.5 w-full md:w-auto justify-start md:justify-end">
              {user?.name || user?.email ? (
                <>
                  <button
                    onClick={() => navigate('/profile/edit')}
                    className="flex items-center gap-1.5 text-xs font-bold bg-white/10 hover:bg-white/20 text-white border border-white/20 px-4 py-2.5 rounded-xl transition-all active-tap shadow-sm"
                  >
                    <Edit3 className="w-3.5 h-3.5 text-gold-400" />
                    <span>Edit Profile</span>
                  </button>

                  <button
                    onClick={handleSignOut}
                    className="flex items-center gap-1.5 text-xs font-bold bg-dustyrose/20 hover:bg-dustyrose/30 text-red-200 border border-dustyrose/40 px-3.5 py-2.5 rounded-xl transition-all active-tap shadow-sm"
                    title="Sign Out"
                  >
                    <LogOut className="w-3.5 h-3.5" />
                    <span className="hidden sm:inline">Sign Out</span>
                  </button>
                </>
              ) : (
                <>
                  <button
                    onClick={() => navigate('/login')}
                    className="flex items-center gap-1.5 text-xs font-bold bg-gold-500 hover:bg-gold-600 text-walnut-900 px-4 py-2.5 rounded-xl transition-all active-tap shadow-sm"
                  >
                    <LogIn className="w-3.5 h-3.5" />
                    <span>Sign In</span>
                  </button>

                  <button
                    onClick={() => navigate('/register')}
                    className="flex items-center gap-1.5 text-xs font-bold bg-white/10 hover:bg-white/20 text-white border border-white/20 px-4 py-2.5 rounded-xl transition-all active-tap shadow-sm"
                  >
                    <span>Create Account</span>
                  </button>

                  <button
                    onClick={() => navigate('/profile/edit')}
                    className="flex items-center gap-1.5 text-xs font-bold bg-white/5 hover:bg-white/10 text-cream-200 border border-white/10 px-3 py-2.5 rounded-xl transition-all active-tap"
                  >
                    <Edit3 className="w-3.5 h-3.5 text-gold-400" />
                    <span>Set Name</span>
                  </button>
                </>
              )}
            </div>

          </div>

          {/* Bottom Patron Benefits Strip */}
          <div className="mt-6 pt-4 border-t border-walnut-700/60 grid grid-cols-2 sm:grid-cols-4 gap-3 text-xs text-cream-200">
            <div className="flex items-center gap-2">
              <ShieldCheck className="w-4 h-4 text-gold-400 flex-shrink-0" />
              <span className="text-[11px] font-medium">10-Yr Timber Warranty</span>
            </div>
            <div className="flex items-center gap-2">
              <Truck className="w-4 h-4 text-gold-400 flex-shrink-0" />
              <span className="text-[11px] font-medium">White-Glove Delivery</span>
            </div>
            <div className="flex items-center gap-2">
              <Hammer className="w-4 h-4 text-gold-400 flex-shrink-0" />
              <span className="text-[11px] font-medium">Master Artisan Support</span>
            </div>
            <div className="flex items-center gap-2">
              <Wrench className="w-4 h-4 text-gold-400 flex-shrink-0" />
              <span className="text-[11px] font-medium">Free Wood Polishing Care</span>
            </div>
          </div>
        </div>

        {/* 2. MAIN 2-COLUMN LUXURY DASHBOARD LAYOUT */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
          
          {/* ================================================================= */}
          {/* LEFT COLUMN: QUICK CARDS, ADDRESS, CARE GUIDE & CONCIERGE (4 COLS) */}
          {/* ================================================================= */}
          <div className="lg:col-span-4 space-y-5">
            
            {/* Key Stat Cards (Vertical / Compact Grid) */}
            <div className="grid grid-cols-3 gap-2.5">
              <div
                onClick={() => navigate('/bookings')}
                className="bg-white p-3.5 rounded-2xl border border-walnut-200/70 shadow-2xs hover:shadow-sm text-center cursor-pointer transition-all active-tap group"
              >
                <div className="w-8 h-8 rounded-xl bg-cream-100 text-walnut-900 flex items-center justify-center mx-auto mb-1.5 group-hover:bg-walnut-900 group-hover:text-gold-400 transition-colors">
                  <Package className="w-4 h-4" />
                </div>
                <span className="font-serif font-bold text-lg text-walnut-900 block leading-none">
                  {userBookings.length}
                </span>
                <span className="text-[10px] text-softgray font-medium mt-1 block">My Orders</span>
              </div>

              <div
                onClick={() => navigate('/wishlist')}
                className="bg-white p-3.5 rounded-2xl border border-walnut-200/70 shadow-2xs hover:shadow-sm text-center cursor-pointer transition-all active-tap group"
              >
                <div className="w-8 h-8 rounded-xl bg-cream-100 text-walnut-900 flex items-center justify-center mx-auto mb-1.5 group-hover:bg-walnut-900 group-hover:text-gold-400 transition-colors">
                  <Heart className="w-4 h-4" />
                </div>
                <span className="font-serif font-bold text-lg text-walnut-900 block leading-none">
                  {wishlist.length}
                </span>
                <span className="text-[10px] text-softgray font-medium mt-1 block">Saved Pieces</span>
              </div>

              <div
                onClick={() => navigate('/profile/requests')}
                className="bg-white p-3.5 rounded-2xl border border-walnut-200/70 shadow-2xs hover:shadow-sm text-center cursor-pointer transition-all active-tap group"
              >
                <div className="w-8 h-8 rounded-xl bg-cream-100 text-walnut-900 flex items-center justify-center mx-auto mb-1.5 group-hover:bg-walnut-900 group-hover:text-gold-400 transition-colors">
                  <Hammer className="w-4 h-4" />
                </div>
                <span className="font-serif font-bold text-lg text-walnut-900 block leading-none">
                  {customRequests.length}
                </span>
                <span className="text-[10px] text-softgray font-medium mt-1 block">Custom Specs</span>
              </div>
            </div>

            {/* Saved Delivery Address Card */}
            <div className="bg-white p-5 rounded-2xl border border-walnut-200/70 shadow-2xs space-y-3">
              <div className="flex items-center justify-between border-b border-cream-200 pb-2.5">
                <div className="flex items-center gap-2">
                  <MapPin className="w-4 h-4 text-gold-600" />
                  <h3 className="font-serif font-bold text-xs sm:text-sm text-walnut-900">Delivery Residence</h3>
                </div>
                <button
                  onClick={() => setIsAddressModalOpen(true)}
                  className="text-[11px] font-bold text-gold-700 hover:text-walnut-900 underline"
                >
                  Edit
                </button>
              </div>

              <div className="text-xs text-walnut-800 space-y-1">
                <span className="text-[10px] font-bold text-softgray uppercase tracking-wider block">Primary Address:</span>
                {deliveryAddress ? (
                  <p className="font-medium text-walnut-900 leading-relaxed">{deliveryAddress}</p>
                ) : (
                  <p className="text-softgray italic">No delivery address saved yet. Tap edit to add your residence address.</p>
                )}
                <span className="text-[10px] text-green-700 font-semibold block pt-1">
                  ✓ Eligible for Free White-Glove Unpacking
                </span>
              </div>
            </div>

            {/* Solid Teak Wood Care & Maintenance Card */}
            <div className="bg-[#FAF7F2] p-5 rounded-2xl border border-walnut-200/80 shadow-2xs space-y-3">
              <div className="flex items-center gap-2.5">
                <div className="w-8 h-8 rounded-xl bg-gold-500/20 text-gold-700 flex items-center justify-center flex-shrink-0">
                  <ShieldCheck className="w-4 h-4" />
                </div>
                <div>
                  <h3 className="font-serif font-bold text-xs sm:text-sm text-walnut-900">Solid Teak Care Guide</h3>
                  <span className="text-[10px] text-softgray block">Lifetime heirloom preservation</span>
                </div>
              </div>

              <p className="text-[11px] text-softgray leading-relaxed">
                Handcrafted from pure kiln-dried timber. Learn how to clean, polish, and safeguard your wooden furniture for generations.
              </p>

              <button
                onClick={() => setIsCareGuideOpen(true)}
                className="w-full py-2 bg-white hover:bg-cream-100 text-walnut-900 font-bold text-xs rounded-xl border border-walnut-200/80 transition-all active-tap shadow-2xs flex items-center justify-center gap-1.5"
              >
                <span>Read Wood Care Recommendations</span>
                <ArrowRight className="w-3.5 h-3.5" />
              </button>
            </div>

            {/* Studio Concierge Hotline Card */}
            <div className="bg-white p-5 rounded-2xl border border-walnut-200/70 shadow-2xs space-y-3">
              <div className="flex items-center gap-2.5">
                <div className="w-8 h-8 rounded-xl bg-green-100 text-green-700 flex items-center justify-center flex-shrink-0">
                  <MessageSquare className="w-4 h-4" />
                </div>
                <div>
                  <h3 className="font-serif font-bold text-xs sm:text-sm text-walnut-900">Artisan Concierge</h3>
                  <span className="text-[10px] text-softgray block">Direct phone & WhatsApp assistance</span>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-2 pt-1">
                <a
                  href="https://wa.me/919876543210?text=Hello%20Glory%20Furniture%20Hub,%20I%20have%20an%20inquiry%20regarding%20my%20furniture."
                  target="_blank"
                  rel="noreferrer"
                  className="py-2 px-3 bg-green-700 hover:bg-green-800 text-white text-xs font-bold rounded-xl flex items-center justify-center gap-1.5 transition-all shadow-2xs text-center"
                >
                  <MessageSquare className="w-3.5 h-3.5" />
                  <span>WhatsApp</span>
                </a>

                <a
                  href="tel:+919876543210"
                  className="py-2 px-3 bg-walnut-900 hover:bg-walnut-800 text-gold-400 text-xs font-bold rounded-xl flex items-center justify-center gap-1.5 transition-all shadow-2xs text-center"
                >
                  <Phone className="w-3.5 h-3.5" />
                  <span>Call Studio</span>
                </a>
              </div>
            </div>

            {/* Navigation & Help Links */}
            <div className="bg-white rounded-2xl border border-walnut-200/70 shadow-2xs divide-y divide-cream-200 overflow-hidden text-xs font-semibold">
              <button
                onClick={() => navigate('/notifications')}
                className="w-full p-3.5 flex items-center justify-between text-left hover:bg-cream-50 transition-colors active-tap"
              >
                <div className="flex items-center gap-2.5">
                  <Bell className="w-4 h-4 text-walnut-700" />
                  <span>Notifications & Alerts</span>
                </div>
                {unreadCount > 0 ? (
                  <span className="text-[10px] bg-gold-500 text-walnut-900 font-bold px-2 py-0.5 rounded-full">
                    {unreadCount} New
                  </span>
                ) : (
                  <ChevronRight className="w-3.5 h-3.5 text-softgray" />
                )}
              </button>

              <button
                onClick={() => navigate('/about')}
                className="w-full p-3.5 flex items-center justify-between text-left hover:bg-cream-50 transition-colors active-tap"
              >
                <div className="flex items-center gap-2.5">
                  <Info className="w-4 h-4 text-walnut-700" />
                  <span>About Glory Studio Heritage</span>
                </div>
                <ChevronRight className="w-3.5 h-3.5 text-softgray" />
              </button>

              <button
                onClick={() => navigate('/faq')}
                className="w-full p-3.5 flex items-center justify-between text-left hover:bg-cream-50 transition-colors active-tap"
              >
                <div className="flex items-center gap-2.5">
                  <HelpCircle className="w-4 h-4 text-walnut-700" />
                  <span>Delivery & Payment FAQ</span>
                </div>
                <ChevronRight className="w-3.5 h-3.5 text-softgray" />
              </button>
            </div>

          </div>

          {/* ================================================================= */}
          {/* RIGHT COLUMN: ORDERS TRACKER, CUSTOM SPECS, WISHLIST (8 COLS) */}
          {/* ================================================================= */}
          <div className="lg:col-span-8 space-y-6">
            
            {/* 1. LIVE ORDER PROGRESS TRACKER SHOWCASE (Grand Visual Stepper) */}
            {latestBooking ? (
              <div className="bg-white p-5 sm:p-6 rounded-3xl border border-walnut-200/70 shadow-sm space-y-5">
                
                {/* Header */}
                <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-2 border-b border-cream-200 pb-3">
                  <div>
                    <div className="flex items-center gap-2">
                      <span className="text-xs font-bold text-gold-700 uppercase tracking-wider">Active Order Tracking</span>
                      <span className="bg-walnut-900 text-gold-400 text-[10px] font-bold px-2.5 py-0.5 rounded-full">
                        {latestBooking.status || 'In Production'}
                      </span>
                    </div>
                    <h3 className="font-serif font-bold text-base sm:text-lg text-walnut-900 mt-0.5">
                      {latestBooking.productName}
                    </h3>
                  </div>

                  <span className="font-mono text-xs font-bold text-walnut-800 bg-cream-100 px-3 py-1 rounded-lg border border-walnut-200/60">
                    #{latestBooking.id}
                  </span>
                </div>

                {/* Product Snapshot & Details */}
                <div className="flex flex-col sm:flex-row items-start sm:items-center gap-4 bg-cream-50/70 p-3.5 rounded-2xl border border-walnut-200/60">
                  <div className="w-20 h-20 rounded-xl overflow-hidden bg-white shadow-2xs flex-shrink-0">
                    <img 
                      src={latestBooking.image || 'https://images.unsplash.com/photo-1505693416388-ac5ce068fe85?auto=format&fit=crop&w=400&q=80'} 
                      alt="" 
                      className="w-full h-full object-cover" 
                    />
                  </div>

                  <div className="flex-1 min-w-0 space-y-1 text-xs">
                    <div className="flex flex-wrap items-center gap-x-4 gap-y-1">
                      <span>Amount: <strong className="text-walnut-900 font-bold">₹{Number(latestBooking.price || 0).toLocaleString('en-IN')}</strong></span>
                      {latestBooking.bedSize && (
                        <span className="bg-white px-2 py-0.5 rounded border border-walnut-200 font-semibold text-walnut-800 text-[11px]">
                          Size: {latestBooking.bedSize}
                        </span>
                      )}
                      {latestBooking.woodType && (
                        <span className="bg-white px-2 py-0.5 rounded border border-walnut-200 font-semibold text-walnut-800 text-[11px]">
                          Wood: {latestBooking.woodType}
                        </span>
                      )}
                    </div>
                    <p className="text-[11px] text-softgray flex items-center gap-1">
                      <Clock className="w-3 h-3 text-gold-600" />
                      <span>Estimated Completion & Delivery: <strong>{latestBooking.deliveryDate || '5 - 7 Business Days'}</strong></span>
                    </p>
                  </div>

                  <button
                    onClick={() => navigate(`/bookings/${latestBooking.id}`)}
                    className="self-end sm:self-center px-4 py-2 bg-walnut-900 hover:bg-walnut-800 text-gold-400 text-xs font-bold rounded-xl active-tap transition-all shadow-2xs whitespace-nowrap"
                  >
                    View Invoice
                  </button>
                </div>

                {/* 5-Stage Visual Progress Timeline */}
                <div className="space-y-2 pt-2">
                  <span className="text-[11px] font-bold text-walnut-800 uppercase tracking-wider block">
                    Handcrafting & Fulfillment Progress:
                  </span>
                  
                  <div className="grid grid-cols-5 gap-1.5 text-center text-[10px] font-semibold">
                    <div className="space-y-1">
                      <div className="h-2 rounded-full bg-green-600" />
                      <span className="text-walnut-900 block">Confirmed ✓</span>
                    </div>
                    <div className="space-y-1">
                      <div className="h-2 rounded-full bg-green-600" />
                      <span className="text-walnut-900 block">Wood Sourced ✓</span>
                    </div>
                    <div className="space-y-1">
                      <div className="h-2 rounded-full bg-gold-500 animate-pulse" />
                      <span className="text-gold-700 font-bold block">In Production 🔨</span>
                    </div>
                    <div className="space-y-1">
                      <div className="h-2 rounded-full bg-cream-300" />
                      <span className="text-softgray block">Polishing</span>
                    </div>
                    <div className="space-y-1">
                      <div className="h-2 rounded-full bg-cream-300" />
                      <span className="text-softgray block">Delivered</span>
                    </div>
                  </div>
                </div>

              </div>
            ) : (
              /* If No Active Order */
              <div className="bg-white p-6 rounded-3xl border border-walnut-200/70 shadow-sm flex flex-col sm:flex-row items-center justify-between gap-4">
                <div className="flex items-center gap-3.5 text-left">
                  <div className="w-12 h-12 rounded-2xl bg-cream-100 text-walnut-900 flex items-center justify-center flex-shrink-0">
                    <ShoppingBag className="w-6 h-6 text-gold-600" />
                  </div>
                  <div>
                    <h3 className="font-serif font-bold text-sm sm:text-base text-walnut-900">Explore Handcrafted Pieces</h3>
                    <p className="text-xs text-softgray">Solid teak wooden beds, dining tables, sofa sets crafted for lifetime beauty.</p>
                  </div>
                </div>
                <Button
                  variant="primary"
                  size="md"
                  onClick={() => navigate('/catalog')}
                  icon={Compass}
                  className="bg-walnut-900 text-gold-400 font-bold px-5 py-2.5 rounded-full text-xs shadow-sm whitespace-nowrap"
                >
                  Browse Catalog
                </Button>
              </div>
            )}

            {/* 2. CUSTOM FURNITURE INQUIRIES & SPECS (Interactive Section) */}
            <div className="bg-white p-5 sm:p-6 rounded-3xl border border-walnut-200/70 shadow-sm space-y-4">
              <div className="flex items-center justify-between border-b border-cream-200 pb-3">
                <div className="flex items-center gap-2">
                  <Hammer className="w-4 h-4 text-gold-600" />
                  <h3 className="font-serif font-bold text-sm sm:text-base text-walnut-900">
                    Bespoke Custom Furniture Requests
                  </h3>
                </div>
                <button
                  onClick={() => navigate('/custom-request')}
                  className="text-xs font-bold text-gold-700 hover:text-walnut-900 flex items-center gap-1"
                >
                  <span>+ New Custom Spec</span>
                  <ChevronRight className="w-3.5 h-3.5" />
                </button>
              </div>

              {customRequests.length > 0 ? (
                <div className="grid grid-cols-1 md:grid-cols-2 gap-3.5">
                  {customRequests.map(req => (
                    <div key={req.id} className="bg-cream-50/70 p-4 rounded-2xl border border-walnut-200/70 space-y-2.5">
                      <div className="flex items-center justify-between">
                        <span className="font-mono text-xs font-bold text-walnut-800">#{req.id}</span>
                        <span className="text-[10px] font-bold bg-gold-500/20 text-gold-800 border border-gold-500/30 px-2 py-0.5 rounded-full">
                          {req.status || 'Under Review'}
                        </span>
                      </div>

                      <div>
                        <h4 className="font-serif font-bold text-xs sm:text-sm text-walnut-900">
                          {req.furnitureType} ({req.wood})
                        </h4>
                        <p className="text-[11px] text-softgray line-clamp-2 mt-0.5">{req.description}</p>
                      </div>

                      <div className="pt-2 border-t border-walnut-200/50 flex items-center justify-between text-xs">
                        <span className="text-[11px] text-softgray">Budget: <strong className="text-walnut-900">{req.budget}</strong></span>
                        <a
                          href={`https://wa.me/919876543210?text=Hello%20Glory%20Studio,%20inquiring%20about%20my%20custom%20spec%20%23${req.id}`}
                          target="_blank"
                          rel="noreferrer"
                          className="text-[11px] font-bold text-green-700 hover:underline flex items-center gap-1"
                        >
                          <MessageSquare className="w-3 h-3" /> WhatsApp Quote
                        </a>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="py-6 text-center text-xs text-softgray bg-cream-50/50 rounded-2xl border border-dashed border-walnut-200">
                  <p>You have no pending bespoke furniture inquiries.</p>
                  <button
                    onClick={() => navigate('/custom-request')}
                    className="mt-2 text-xs font-bold text-walnut-900 underline"
                  >
                    Create a Custom Request (Room Dimensions & Wood Selection)
                  </button>
                </div>
              )}
            </div>

            {/* 3. SAVED PIECES WISHLIST SHOWCASE */}
            <div className="bg-white p-5 sm:p-6 rounded-3xl border border-walnut-200/70 shadow-sm space-y-4">
              <div className="flex items-center justify-between border-b border-cream-200 pb-3">
                <div className="flex items-center gap-2">
                  <Heart className="w-4 h-4 text-dustyrose" />
                  <h3 className="font-serif font-bold text-sm sm:text-base text-walnut-900">
                    {wishlist.length > 0 ? 'My Saved Wishlist Pieces' : 'Curated Studio Masterpieces'}
                  </h3>
                </div>

                <button
                  onClick={() => navigate(wishlist.length > 0 ? '/wishlist' : '/catalog')}
                  className="text-xs font-bold text-gold-700 hover:text-walnut-900 flex items-center gap-1"
                >
                  <span>{wishlist.length > 0 ? 'View All Wishlist' : 'Browse Full Catalog'}</span>
                  <ChevronRight className="w-3.5 h-3.5" />
                </button>
              </div>

              {/* Responsive Cards Grid (4 Columns) */}
              <div className="grid grid-cols-2 sm:grid-cols-2 md:grid-cols-4 gap-3.5">
                {showcaseProducts.map(p => (
                  <div
                    key={p.id}
                    onClick={() => navigate(`/product/${p.id}`)}
                    className="bg-[#F8F5F0] hover:bg-[#F2ECE2] p-2.5 rounded-2xl border border-walnut-200/60 shadow-2xs hover:shadow-xs transition-all cursor-pointer active-tap flex flex-col justify-between group"
                  >
                    <div>
                      <div className="relative aspect-[4/3] rounded-xl overflow-hidden bg-white mb-2 shadow-2xs">
                        <img 
                          src={p.images[0]} 
                          alt={p.name} 
                          className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300" 
                        />
                        <span className="absolute top-1.5 left-1.5 bg-walnut-900/80 text-gold-400 text-[9px] font-bold px-1.5 py-0.5 rounded">
                          {p.category}
                        </span>
                      </div>

                      <h4 className="font-serif font-bold text-xs text-walnut-900 line-clamp-1 group-hover:text-gold-700 transition-colors">
                        {p.name}
                      </h4>
                      <p className="text-[10px] text-softgray line-clamp-1 mt-0.5">{p.material}</p>
                    </div>

                    <div className="pt-2 mt-2 border-t border-walnut-200/50 flex items-center justify-between">
                      <span className="font-bold text-xs text-walnut-900">
                        ₹{Number(p.price || 0).toLocaleString('en-IN')}
                      </span>
                      <div className="flex items-center gap-0.5 text-[10px] font-bold text-walnut-800">
                        <Star className="w-3 h-3 fill-gold-500 text-gold-500" />
                        <span>{p.rating || 5.0}</span>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>

          </div>

        </div>

      </div>

      {/* ===================================================================== */}
      {/* MODAL 1: SOLID TEAK WOOD CARE & MAINTENANCE GUIDE */}
      {/* ===================================================================== */}
      <Modal
        isOpen={isCareGuideOpen}
        onClose={() => setIsCareGuideOpen(false)}
        title="Solid Wood Care & Maintenance Guide"
        position="center"
      >
        <div className="space-y-3.5 text-xs text-walnut-800 max-h-[75vh] overflow-y-auto pr-1">
          <p className="text-softgray text-[11px] leading-relaxed">
            Your furniture is sculpted from 100% seasoned solid teak and hardwoods. Follow these recommendations to keep it pristine for generations:
          </p>

          <div className="p-3 bg-cream-50 rounded-xl border border-walnut-200/60 flex items-start gap-3">
            <Feather className="w-4 h-4 text-gold-600 flex-shrink-0 mt-0.5" />
            <div>
              <h4 className="font-bold text-walnut-900 text-xs">Regular Dry Dusting</h4>
              <p className="text-[11px] text-softgray mt-0.5">Use a soft dry microfiber cloth along the wood grain weekly. Avoid synthetic chemical aerosols.</p>
            </div>
          </div>

          <div className="p-3 bg-cream-50 rounded-xl border border-walnut-200/60 flex items-start gap-3">
            <Droplets className="w-4 h-4 text-blue-600 flex-shrink-0 mt-0.5" />
            <div>
              <h4 className="font-bold text-walnut-900 text-xs">Moisture Protection</h4>
              <p className="text-[11px] text-softgray mt-0.5">Always use coasters under hot teacups or cold glasses. Clean spills immediately with a damp cloth.</p>
            </div>
          </div>

          <div className="p-3 bg-cream-50 rounded-xl border border-walnut-200/60 flex items-start gap-3">
            <Sun className="w-4 h-4 text-amber-600 flex-shrink-0 mt-0.5" />
            <div>
              <h4 className="font-bold text-walnut-900 text-xs">Sunlight & Humidity</h4>
              <p className="text-[11px] text-softgray mt-0.5">Keep furniture away from direct unrelenting sun or direct AC vents to prevent timber expansion or contraction.</p>
            </div>
          </div>

          <div className="p-3 bg-cream-50 rounded-xl border border-walnut-200/60 flex items-start gap-3">
            <Wrench className="w-4 h-4 text-green-600 flex-shrink-0 mt-0.5" />
            <div>
              <h4 className="font-bold text-walnut-900 text-xs">10-Year Structural Timber Warranty</h4>
              <p className="text-[11px] text-softgray mt-0.5">All Glory Furniture Hub solid wood mortise-and-tenon joints are protected with a 10-year termite & joint warranty.</p>
            </div>
          </div>

          <Button
            variant="primary"
            size="sm"
            className="w-full mt-2 bg-walnut-900 text-gold-400 font-bold"
            onClick={() => setIsCareGuideOpen(false)}
          >
            Understood
          </Button>
        </div>
      </Modal>

      {/* ===================================================================== */}
      {/* MODAL 2: EDIT DELIVERY ADDRESS */}
      {/* ===================================================================== */}
      <Modal
        isOpen={isAddressModalOpen}
        onClose={() => setIsAddressModalOpen(false)}
        title="Default Delivery Address"
        position="center"
      >
        <form onSubmit={handleSaveAddress} className="space-y-3.5 text-xs">
          <div>
            <label className="block text-xs font-bold text-walnut-900 mb-1">Residence Delivery Address</label>
            <textarea
              rows="3"
              required
              value={tempAddress}
              onChange={(e) => setTempAddress(e.target.value)}
              className="w-full text-xs p-2.5 bg-cream-50 border border-walnut-200 rounded-xl focus:outline-none focus:ring-1 focus:ring-walnut-500 text-walnut-900 font-medium"
              placeholder="House/Villa No, Street Name, Landmark, City, State, Pincode"
            />
          </div>

          <div className="flex items-center gap-2 pt-2">
            <Button
              type="button"
              variant="secondary"
              size="sm"
              className="flex-1"
              onClick={() => setIsAddressModalOpen(false)}
            >
              Cancel
            </Button>
            <Button
              type="submit"
              variant="primary"
              size="sm"
              className="flex-1 bg-walnut-900 text-gold-400 font-bold"
              icon={CheckCircle2}
            >
              Save Address
            </Button>
          </div>
        </form>
      </Modal>

    </div>
  )
}
