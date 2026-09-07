import React, { useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { 
  X, ArrowLeft, User, Heart, ShoppingBag, Maximize2, Trash2, 
  ArrowRight, MapPin, Bell, HelpCircle, LogOut, LogIn, ChevronRight, 
  Hammer, Package
} from 'lucide-react'
import { useAppStore } from '../../store/useAppStore'
import { MOCK_PRODUCTS } from '../../data/mockData'

export default function NavSidebarDrawer(props = {}) {
  const navigate = useNavigate()
  const store = useAppStore()

  const isOpen = props.isOpen !== undefined ? props.isOpen : store.isNavDrawerOpen
  const onClose = props.onClose || store.closeNavDrawer
  const activeTab = props.activeTab || store.navDrawerTab
  const setActiveTab = props.setActiveTab || store.switchNavDrawerTab
  const onGoBack = props.onGoBack || store.goBackNavDrawer
  const previousTab = props.previousTab !== undefined 
    ? props.previousTab 
    : (store.navDrawerHistory && store.navDrawerHistory.length > 0 
        ? store.navDrawerHistory[store.navDrawerHistory.length - 1] 
        : null)

  const { 
    user, 
    setUser, 
    wishlist = [], 
    toggleWishlist, 
    userBookings = [], 
    customRequests = [],
    notifications = []
  } = store

  // Prevent background scrolling when sidebar is open
  useEffect(() => {
    if (isOpen) {
      document.body.style.overflow = 'hidden'
    } else {
      document.body.style.overflow = 'unset'
    }
    return () => {
      document.body.style.overflow = 'unset'
    }
  }, [isOpen])

  // Handle Escape key to close
  useEffect(() => {
    const handleKeyDown = (e) => {
      if (e.key === 'Escape' && isOpen) {
        onClose()
      }
    }
    window.addEventListener('keydown', handleKeyDown)
    return () => window.removeEventListener('keydown', handleKeyDown)
  }, [isOpen, onClose])

  if (!isOpen) return null

  // Normalize wishlist items
  const savedItems = wishlist.map(item => {
    if (typeof item === 'object' && item !== null) return item
    return MOCK_PRODUCTS.find(p => p.id === item)
  }).filter(Boolean)

  const cartCount = userBookings.length > 0 ? userBookings.length : 3
  const unreadNotifs = notifications.filter(n => !n.read).length

  // Destination URLs for "Make Full Tab"
  const getFullTabRoute = () => {
    switch (activeTab) {
      case 'profile': return '/profile'
      case 'favourite': return '/wishlist'
      case 'cart': return '/bookings'
      default: return '/home'
    }
  }

  const getFullTabTitle = () => {
    switch (activeTab) {
      case 'profile': return 'Open Profile in Full Tab'
      case 'favourite': return 'Open Wishlist in Full Tab'
      case 'cart': return 'Open Cart & Orders in Full Tab'
      default: return 'Open in Full Tab'
    }
  }

  const handleMakeFullTab = () => {
    onClose()
    navigate(getFullTabRoute())
  }

  const handleSignOut = () => {
    if (window.confirm('Are you sure you want to sign out?')) {
      setUser(null)
      localStorage.removeItem('glory_user')
      onClose()
      navigate('/login')
    }
  }

  return (
    <div className="fixed inset-0 z-50 overflow-hidden font-sans">
      {/* 1. Backdrop Overlay */}
      <div 
        onClick={onClose}
        className="fixed inset-0 bg-black/60 backdrop-blur-xs transition-opacity animate-in fade-in duration-300"
        aria-hidden="true"
      />

      {/* 2. Slide-over Right Drawer Container */}
      <div className="fixed inset-y-0 right-0 max-w-full flex pl-4 sm:pl-10">
        <aside className="w-screen max-w-md sm:max-w-lg bg-white shadow-2xl flex flex-col justify-between h-full border-l border-gray-100 transform transition-transform ease-in-out duration-300">
          
          {/* ======================================================== */}
          {/* HEADER: Back Button | 3 Tab Icons | Close Button */}
          {/* ======================================================== */}
          <div className="p-3.5 sm:p-4 border-b border-gray-100 bg-white/95 backdrop-blur-md sticky top-0 z-20 flex items-center justify-between gap-2">
            
            {/* Redirect to Previous Tab / Back Button */}
            <button
              onClick={onGoBack}
              className="p-2 rounded-full hover:bg-gray-100 text-gray-700 hover:text-gray-950 transition-colors flex items-center gap-1 active-tap"
              title={previousTab ? `Back to ${previousTab} tab` : "Close sidebar"}
              aria-label="Back to previous tab"
            >
              <ArrowLeft className="w-5 h-5 stroke-[2]" />
            </button>

            {/* 3 Icons Bar (Profile, Favourite, Cart) */}
            <div className="flex items-center bg-gray-100/90 p-1 rounded-full border border-gray-200/70 shadow-2xs">
              
              {/* Profile Icon */}
              <button
                onClick={() => setActiveTab('profile')}
                className={`relative flex items-center gap-1.5 px-3 sm:px-3.5 py-1.5 rounded-full text-xs font-semibold transition-all active-tap ${
                  activeTab === 'profile'
                    ? 'bg-gray-950 text-white shadow-xs'
                    : 'text-gray-600 hover:text-gray-950 hover:bg-white/60'
                }`}
                title="Profile Tab"
              >
                <User className="w-4 h-4" />
                <span className="hidden xs:inline text-[11px]">Profile</span>
              </button>

              {/* Favourite (Wishlist) Icon */}
              <button
                onClick={() => setActiveTab('favourite')}
                className={`relative flex items-center gap-1.5 px-3 sm:px-3.5 py-1.5 rounded-full text-xs font-semibold transition-all active-tap ${
                  activeTab === 'favourite'
                    ? 'bg-gray-950 text-white shadow-xs'
                    : 'text-gray-600 hover:text-gray-950 hover:bg-white/60'
                }`}
                title="Favourites / Wishlist Tab"
              >
                <Heart className={`w-4 h-4 ${activeTab === 'favourite' ? 'fill-white text-white' : ''}`} />
                <span className="hidden xs:inline text-[11px]">Favourites</span>
                {savedItems.length > 0 && (
                  <span className={`w-4 h-4 text-[9px] font-bold rounded-full flex items-center justify-center ${
                    activeTab === 'favourite' ? 'bg-red-500 text-white' : 'bg-red-600 text-white'
                  }`}>
                    {savedItems.length}
                  </span>
                )}
              </button>

              {/* Cart / Bookings Icon */}
              <button
                onClick={() => setActiveTab('cart')}
                className={`relative flex items-center gap-1.5 px-3 sm:px-3.5 py-1.5 rounded-full text-xs font-semibold transition-all active-tap ${
                  activeTab === 'cart'
                    ? 'bg-gray-950 text-white shadow-xs'
                    : 'text-gray-600 hover:text-gray-950 hover:bg-white/60'
                }`}
                title="Cart & Orders Tab"
              >
                <ShoppingBag className="w-4 h-4" />
                <span className="hidden xs:inline text-[11px]">Cart</span>
                <span className={`w-4 h-4 text-[9px] font-bold rounded-full flex items-center justify-center ${
                  activeTab === 'cart' ? 'bg-amber-400 text-gray-950' : 'bg-gray-900 text-white'
                }`}>
                  {cartCount}
                </span>
              </button>
            </div>

            {/* Close Sidebar Icon Button */}
            <button
              onClick={onClose}
              className="p-2 rounded-full hover:bg-gray-100 text-gray-600 hover:text-gray-950 transition-colors active-tap"
              title="Close drawer"
              aria-label="Close"
            >
              <X className="w-5 h-5 stroke-[2]" />
            </button>
          </div>

          {/* ======================================================== */}
          {/* BODY CONTENT: DYNAMIC ACCORDING TO ACTIVE TAB */}
          {/* ======================================================== */}
          <div className="flex-1 overflow-y-auto px-4 sm:px-6 py-4 space-y-4">
            
            {/* ------------------------------------------------------ */}
            {/* TAB 1: PROFILE TAB */}
            {/* ------------------------------------------------------ */}
            {activeTab === 'profile' && (
              <div className="space-y-4 animate-in fade-in duration-200">
                {/* User Card */}
                <div className="bg-gradient-to-br from-gray-900 via-gray-950 to-[#0F1E36] text-white p-4 sm:p-5 rounded-2xl shadow-sm relative overflow-hidden">
                  <div className="relative z-10 flex items-center gap-3.5">
                    <div className="w-12 h-12 rounded-full bg-white/10 border-2 border-white/20 flex items-center justify-center text-amber-400 font-bold text-xl shadow-xs">
                      {user?.name ? user.name.charAt(0).toUpperCase() : <User className="w-6 h-6 text-white/90" />}
                    </div>
                    <div className="min-w-0 flex-1">
                      <div className="flex items-center gap-2">
                        <h4 className="font-bold text-sm sm:text-base text-white truncate">
                          {user?.name || 'Valued Guest'}
                        </h4>
                        <span className="px-2 py-0.5 rounded-full text-[9px] font-semibold bg-amber-400/20 text-amber-300 border border-amber-400/30">
                          {user?.role === 'admin' ? 'Studio Admin' : 'Patron'}
                        </span>
                      </div>
                      <p className="text-xs text-gray-300 truncate mt-0.5">
                        {user?.email || 'Sign in to sync your bespoke orders'}
                      </p>
                    </div>
                  </div>

                  {!user?.email && (
                    <div className="mt-4 pt-3 border-t border-white/10 flex items-center gap-2">
                      <button
                        onClick={() => { onClose(); navigate('/login') }}
                        className="flex-1 py-2 px-3 rounded-xl bg-amber-400 hover:bg-amber-500 text-gray-950 font-bold text-xs flex items-center justify-center gap-1.5 transition-colors shadow-xs"
                      >
                        <LogIn className="w-3.5 h-3.5" />
                        <span>Sign In</span>
                      </button>
                      <button
                        onClick={() => { onClose(); navigate('/register') }}
                        className="flex-1 py-2 px-3 rounded-xl bg-white/10 hover:bg-white/20 text-white font-semibold text-xs transition-colors"
                      >
                        Register
                      </button>
                    </div>
                  )}
                </div>

                {/* Quick Numbers Rail */}
                <div className="grid grid-cols-3 gap-2">
                  <div 
                    onClick={() => setActiveTab('favourite')}
                    className="bg-gray-50 hover:bg-gray-100 p-3 rounded-xl border border-gray-100 text-center cursor-pointer transition-colors"
                  >
                    <span className="block text-lg font-bold text-gray-950">{savedItems.length}</span>
                    <span className="text-[10px] text-gray-500 font-medium">Wishlist</span>
                  </div>
                  <div 
                    onClick={() => setActiveTab('cart')}
                    className="bg-gray-50 hover:bg-gray-100 p-3 rounded-xl border border-gray-100 text-center cursor-pointer transition-colors"
                  >
                    <span className="block text-lg font-bold text-gray-950">{userBookings.length}</span>
                    <span className="text-[10px] text-gray-500 font-medium">Orders</span>
                  </div>
                  <div 
                    onClick={() => { onClose(); navigate('/profile/requests') }}
                    className="bg-gray-50 hover:bg-gray-100 p-3 rounded-xl border border-gray-100 text-center cursor-pointer transition-colors"
                  >
                    <span className="block text-lg font-bold text-gray-950">{customRequests.length}</span>
                    <span className="text-[10px] text-gray-500 font-medium">Custom</span>
                  </div>
                </div>

                {/* Account Navigation List */}
                <div className="bg-white rounded-2xl border border-gray-100 divide-y divide-gray-100 overflow-hidden shadow-2xs">
                  <button
                    onClick={() => { onClose(); navigate('/profile/edit') }}
                    className="w-full p-3.5 flex items-center justify-between hover:bg-gray-50 text-left transition-colors group"
                  >
                    <div className="flex items-center gap-3">
                      <div className="w-8 h-8 rounded-lg bg-gray-100 text-gray-700 flex items-center justify-center">
                        <MapPin className="w-4 h-4" />
                      </div>
                      <div>
                        <span className="block text-xs font-bold text-gray-900">Personal & Delivery Address</span>
                        <span className="text-[10px] text-gray-500">Manage shipping addresses</span>
                      </div>
                    </div>
                    <ChevronRight className="w-4 h-4 text-gray-400 group-hover:translate-x-0.5 transition-transform" />
                  </button>

                  <button
                    onClick={() => { onClose(); navigate('/profile/requests') }}
                    className="w-full p-3.5 flex items-center justify-between hover:bg-gray-50 text-left transition-colors group"
                  >
                    <div className="flex items-center gap-3">
                      <div className="w-8 h-8 rounded-lg bg-gray-100 text-gray-700 flex items-center justify-center">
                        <Hammer className="w-4 h-4" />
                      </div>
                      <div>
                        <span className="block text-xs font-bold text-gray-900">Custom Furniture Inquiries</span>
                        <span className="text-[10px] text-gray-500">Track bespoke woodwork</span>
                      </div>
                    </div>
                    <ChevronRight className="w-4 h-4 text-gray-400 group-hover:translate-x-0.5 transition-transform" />
                  </button>

                  <button
                    onClick={() => { onClose(); navigate('/notifications') }}
                    className="w-full p-3.5 flex items-center justify-between hover:bg-gray-50 text-left transition-colors group"
                  >
                    <div className="flex items-center gap-3">
                      <div className="w-8 h-8 rounded-lg bg-gray-100 text-gray-700 flex items-center justify-center relative">
                        <Bell className="w-4 h-4" />
                        {unreadNotifs > 0 && (
                          <span className="absolute -top-1 -right-1 w-2.5 h-2.5 bg-red-600 rounded-full" />
                        )}
                      </div>
                      <div>
                        <span className="block text-xs font-bold text-gray-900">Studio Notifications</span>
                        <span className="text-[10px] text-gray-500">{unreadNotifs} unread updates</span>
                      </div>
                    </div>
                    <ChevronRight className="w-4 h-4 text-gray-400 group-hover:translate-x-0.5 transition-transform" />
                  </button>

                  <button
                    onClick={() => { onClose(); navigate('/faq') }}
                    className="w-full p-3.5 flex items-center justify-between hover:bg-gray-50 text-left transition-colors group"
                  >
                    <div className="flex items-center gap-3">
                      <div className="w-8 h-8 rounded-lg bg-gray-100 text-gray-700 flex items-center justify-center">
                        <HelpCircle className="w-4 h-4" />
                      </div>
                      <div>
                        <span className="block text-xs font-bold text-gray-900">Care Guide & FAQs</span>
                        <span className="text-[10px] text-gray-500">Solid wood maintenance & support</span>
                      </div>
                    </div>
                    <ChevronRight className="w-4 h-4 text-gray-400 group-hover:translate-x-0.5 transition-transform" />
                  </button>
                </div>

                {/* Sign Out (if logged in) */}
                {user?.email && (
                  <button
                    onClick={handleSignOut}
                    className="w-full py-2.5 px-4 rounded-xl border border-red-200 text-red-600 hover:bg-red-50 text-xs font-semibold flex items-center justify-center gap-2 transition-colors"
                  >
                    <LogOut className="w-3.5 h-3.5" />
                    <span>Sign Out from Glory Hub</span>
                  </button>
                )}
              </div>
            )}


            {/* ------------------------------------------------------ */}
            {/* TAB 2: FAVOURITE (WISHLIST) TAB */}
            {/* ------------------------------------------------------ */}
            {activeTab === 'favourite' && (
              <div className="space-y-4 animate-in fade-in duration-200">
                <div className="flex items-center justify-between pb-1">
                  <h3 className="text-xs font-bold text-gray-900 uppercase tracking-wider">
                    Saved Pieces ({savedItems.length})
                  </h3>
                  {savedItems.length > 0 && (
                    <button
                      onClick={() => { onClose(); navigate('/catalog') }}
                      className="text-xs font-semibold text-gray-600 hover:text-gray-950 flex items-center gap-1"
                    >
                      <span>Explore More</span>
                      <ArrowRight className="w-3.5 h-3.5" />
                    </button>
                  )}
                </div>

                {savedItems.length === 0 ? (
                  <div className="text-center py-12 px-4 space-y-3 bg-gray-50 rounded-2xl border border-dashed border-gray-200">
                    <div className="w-12 h-12 rounded-full bg-red-50 text-red-500 flex items-center justify-center mx-auto">
                      <Heart className="w-6 h-6" />
                    </div>
                    <h4 className="font-bold text-sm text-gray-900">Your Wishlist is Empty</h4>
                    <p className="text-xs text-gray-500 max-w-xs mx-auto leading-relaxed">
                      Tap the heart icon on any solid teak furniture piece to save it here for later.
                    </p>
                    <div className="pt-2">
                      <button
                        onClick={() => { onClose(); navigate('/catalog') }}
                        className="px-5 py-2.5 rounded-full bg-gray-950 hover:bg-gray-800 text-white text-xs font-semibold shadow-xs transition-colors inline-flex items-center gap-2"
                      >
                        <span>Browse Collections</span>
                        <ArrowRight className="w-3.5 h-3.5" />
                      </button>
                    </div>
                  </div>
                ) : (
                  <div className="space-y-3">
                    {savedItems.map((item) => (
                      <div
                        key={item.id}
                        className="bg-white p-3 rounded-2xl border border-gray-100 shadow-2xs hover:shadow-sm transition-all flex items-center gap-3"
                      >
                        <img
                          src={item.images?.[0] || '/images/hero_epoxy_teak.jpg'}
                          alt={item.name}
                          onClick={() => { onClose(); navigate(`/product/${item.id}`) }}
                          className="w-18 h-18 rounded-xl object-cover bg-gray-50 cursor-pointer flex-shrink-0"
                        />
                        <div className="flex-1 min-w-0">
                          <span className="text-[10px] font-bold text-gray-500 uppercase tracking-wider">
                            {item.category || 'Teak Wood'}
                          </span>
                          <h4
                            onClick={() => { onClose(); navigate(`/product/${item.id}`) }}
                            className="font-bold text-xs text-gray-950 truncate cursor-pointer hover:text-amber-700 transition-colors"
                          >
                            {item.name}
                          </h4>
                          <p className="text-[11px] font-bold text-gray-950 mt-1">
                            ₹{Number(item.price || 0).toLocaleString('en-IN')}
                          </p>
                          <div className="flex items-center gap-2 mt-2">
                            <button
                              onClick={() => { onClose(); navigate(`/booking?productId=${item.id}`) }}
                              className="px-3 py-1 rounded-full bg-gray-950 hover:bg-gray-800 text-white text-[11px] font-semibold transition-colors"
                            >
                              Book Now
                            </button>
                            <button
                              onClick={() => toggleWishlist(item)}
                              className="p-1 text-gray-400 hover:text-red-500 transition-colors"
                              title="Remove from saved"
                            >
                              <Trash2 className="w-4 h-4" />
                            </button>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            )}


            {/* ------------------------------------------------------ */}
            {/* TAB 3: CART & ORDERS TAB */}
            {/* ------------------------------------------------------ */}
            {activeTab === 'cart' && (
              <div className="space-y-4 animate-in fade-in duration-200">
                <div className="flex items-center justify-between pb-1">
                  <h3 className="text-xs font-bold text-gray-900 uppercase tracking-wider">
                    My Cart & Studio Orders ({userBookings.length})
                  </h3>
                  <button
                    onClick={() => { onClose(); navigate('/catalog') }}
                    className="text-xs font-semibold text-gray-600 hover:text-gray-950 flex items-center gap-1"
                  >
                    <span>Add More</span>
                    <ArrowRight className="w-3.5 h-3.5" />
                  </button>
                </div>

                {userBookings.length === 0 ? (
                  <div className="text-center py-12 px-4 space-y-3 bg-gray-50 rounded-2xl border border-dashed border-gray-200">
                    <div className="w-12 h-12 rounded-full bg-amber-50 text-amber-700 flex items-center justify-center mx-auto">
                      <ShoppingBag className="w-6 h-6" />
                    </div>
                    <h4 className="font-bold text-sm text-gray-900">No Orders in Cart</h4>
                    <p className="text-xs text-gray-500 max-w-xs mx-auto leading-relaxed">
                      You don't have any pending furniture bookings. Explore handcrafted collections to begin your order.
                    </p>
                    <div className="pt-2">
                      <button
                        onClick={() => { onClose(); navigate('/catalog') }}
                        className="px-5 py-2.5 rounded-full bg-gray-950 hover:bg-gray-800 text-white text-xs font-semibold shadow-xs transition-colors inline-flex items-center gap-2"
                      >
                        <span>Start Shopping</span>
                        <ArrowRight className="w-3.5 h-3.5" />
                      </button>
                    </div>
                  </div>
                ) : (
                  <div className="space-y-3">
                    {userBookings.map((booking) => (
                      <div
                        key={booking.id}
                        onClick={() => { onClose(); navigate(`/bookings/${booking.id}`) }}
                        className="bg-white p-3.5 rounded-2xl border border-gray-100 shadow-2xs hover:shadow-sm cursor-pointer transition-all flex items-start gap-3"
                      >
                        <div className="w-16 h-16 rounded-xl overflow-hidden bg-gray-50 flex-shrink-0">
                          <img
                            src={booking.productImage || '/images/hero_epoxy_teak.jpg'}
                            alt={booking.productName}
                            className="w-full h-full object-cover"
                          />
                        </div>
                        <div className="flex-1 min-w-0">
                          <div className="flex items-center justify-between gap-1">
                            <span className="text-[10px] font-bold text-gray-500 uppercase tracking-wider">
                              #{booking.id}
                            </span>
                            <span className="px-2 py-0.5 rounded-full text-[9px] font-bold bg-amber-100 text-amber-900">
                              {booking.status || 'Confirmed'}
                            </span>
                          </div>
                          <h4 className="font-bold text-xs text-gray-950 truncate mt-0.5">
                            {booking.productName}
                          </h4>
                          <p className="text-[11px] text-gray-500 mt-0.5">
                            Qty: {booking.quantity || 1} • {booking.wood || 'Burma Teak'}
                          </p>
                          <div className="flex items-center justify-between mt-2 pt-1 border-t border-gray-50">
                            <span className="font-bold text-xs text-gray-950">
                              ₹{Number((booking.price || 0) * (booking.quantity || 1)).toLocaleString('en-IN')}
                            </span>
                            <span className="text-[10px] font-semibold text-amber-700 hover:text-amber-800 flex items-center gap-0.5">
                              <span>Track Order</span>
                              <ChevronRight className="w-3 h-3" />
                            </span>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            )}

          </div>


          {/* ======================================================== */}
          {/* BOTTOM BAR: "MAKE TAB FOR FULL TAB" (User Requirement) */}
          {/* ======================================================== */}
          <div className="p-4 border-t border-gray-100 bg-white shadow-lg space-y-2 sticky bottom-0 z-20">
            {/* Primary Action Button: Make Full Tab */}
            <button
              onClick={handleMakeFullTab}
              className="w-full py-3 px-4 rounded-full bg-gray-950 hover:bg-gray-800 text-white font-bold text-xs sm:text-sm shadow-md flex items-center justify-center gap-2 transition-all active-tap group"
            >
              <span>{getFullTabTitle()}</span>
              <Maximize2 className="w-4 h-4 group-hover:scale-110 transition-transform" />
            </button>

            {/* Clear explicit clickable text per user instruction: "provide text for make tab for full tab" */}
            <div className="text-center">
              <button
                onClick={handleMakeFullTab}
                className="text-[11px] text-gray-500 hover:text-gray-900 font-medium transition-colors inline-flex items-center gap-1"
              >
                <span>Click here to make tab for full tab view</span>
                <ArrowRight className="w-3 h-3" />
              </button>
            </div>
          </div>

        </aside>
      </div>
    </div>
  )
}
