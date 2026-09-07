import React, { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { ArrowLeft, Heart, Search, ShoppingBag, User } from 'lucide-react'
import { useAppStore } from '../../store/useAppStore'

export default function Header({ title, showBack = false }) {
  const navigate = useNavigate()
    const { wishlist, userBookings, openNavDrawer } = useAppStore()
    const [searchQuery, setSearchQuery] = useState('')

    const cartCount = userBookings.length > 0 ? userBookings.length : 3

    const handleSearch = (e) => {
      e.preventDefault()
      if (searchQuery.trim()) {
        navigate(`/catalog?search=${encodeURIComponent(searchQuery.trim())}`)
      }
    }

    return (
      <header className="sticky top-0 z-50 bg-white text-gray-900 border-b border-gray-100 shadow-2xs w-full font-sans">
        <div className="w-full px-4 sm:px-6 lg:px-10">
          <div className="flex items-center justify-between h-16 sm:h-20 gap-4">
            
            {/* 1. BRAND LOGO (Left) */}
            <div className="flex items-center gap-3">
              {showBack && (
                <button
                  onClick={() => navigate(-1)}
                  className="p-1.5 rounded-full hover:bg-gray-100 text-gray-700 md:hidden"
                  aria-label="Go back"
                >
                  <ArrowLeft className="w-5 h-5" />
                </button>
              )}

              <div 
                onClick={() => navigate('/home')}
                className="flex items-center gap-2.5 cursor-pointer select-none group"
              >
                {/* Vertical Wood Slats Icon */}
                <div className="w-9 h-9 sm:w-10 sm:h-10 rounded-lg overflow-hidden flex-shrink-0 shadow-2xs border border-gray-200/80 group-hover:opacity-95 transition-opacity">
                  <img 
                    src="/images/logo_wood.jpg" 
                    alt="Glory Furniture" 
                    className="w-full h-full object-cover"
                  />
                </div>

                {/* Logo Typography */}
                <div className="flex flex-col">
                  <span className="font-sans font-black text-lg sm:text-xl text-gray-950 tracking-wider leading-none">
                    GLORY
                  </span>
                  <span className="text-[8px] sm:text-[9px] font-bold tracking-[0.2em] text-gray-500 uppercase mt-0.5 leading-tight">
                    FURNITURE HUB
                  </span>
                </div>
              </div>
            </div>

            {/* 2. CENTER - EMPTY (Per user request) */}
            <div className="flex-1" />

            {/* 3. RIGHT UTILITIES (Search Bar & Profile/Wishlist/Cart Icons) */}
            <div className="flex items-center gap-2.5 sm:gap-4 flex-shrink-0">
              
              {/* Pill Search Input */}
              <form 
                onSubmit={handleSearch}
                className="hidden sm:flex items-center border border-gray-200/90 hover:border-gray-400 focus-within:border-gray-900 rounded-full pl-4 pr-1.5 py-1 bg-white shadow-2xs transition-all w-52 md:w-60 lg:w-68"
              >
                <input
                  type="text"
                  placeholder="Search for luxury furniture..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="w-full text-xs text-gray-800 placeholder:text-gray-400 focus:outline-none bg-transparent"
                />
                <button
                  type="submit"
                  className="w-7 h-7 rounded-full bg-[#0B1728] hover:bg-[#152740] text-white flex items-center justify-center transition-colors flex-shrink-0 ml-1 active-tap"
                  title="Search"
                >
                  <Search className="w-3.5 h-3.5" />
                </button>
              </form>

              {/* User Profile Icon -> Opens Slide-over Sidebar Drawer */}
              <button
                onClick={() => openNavDrawer('profile')}
                className="p-2 rounded-full hover:bg-gray-100 text-gray-700 hover:text-gray-950 transition-colors active-tap"
                title="Account Profile Drawer"
                aria-label="Open profile drawer"
              >
                <User className="w-5 h-5 stroke-[1.75]" />
              </button>

              {/* Wishlist Heart Icon -> Opens Slide-over Sidebar Drawer */}
              <button
                onClick={() => openNavDrawer('favourite')}
                className="p-2 rounded-full hover:bg-gray-100 text-gray-700 hover:text-gray-950 relative transition-colors active-tap"
                title="Saved Wishlist Drawer"
                aria-label="Open wishlist drawer"
              >
                <Heart className="w-5 h-5 stroke-[1.75]" />
                {wishlist.length > 0 && (
                  <span className="absolute top-0.5 right-0.5 w-4 h-4 bg-red-600 text-white text-[8px] font-bold rounded-full flex items-center justify-center shadow-xs">
                    {wishlist.length}
                  </span>
                )}
              </button>

              {/* Shopping Cart / Bag Icon -> Opens Slide-over Sidebar Drawer */}
              <button
                onClick={() => openNavDrawer('cart')}
                className="p-2 rounded-full hover:bg-gray-100 text-gray-700 hover:text-gray-950 relative transition-colors active-tap"
                title="Shopping Cart & Orders Drawer"
                aria-label="Open cart drawer"
              >
                <ShoppingBag className="w-5 h-5 stroke-[1.75]" />
                <span className="absolute top-0.5 right-0.5 w-4 h-4 bg-gray-950 text-white text-[9px] font-bold rounded-full flex items-center justify-center shadow-xs">
                  {cartCount}
                </span>
              </button>
            </div>

        </div>

        {/* Mobile Search Bar Row (Visible only on small mobile screens) */}
        <div className="sm:hidden pb-3">
          <form 
            onSubmit={handleSearch}
            className="flex items-center border border-gray-200 rounded-full pl-3.5 pr-1.5 py-1 bg-gray-50/50 shadow-2xs w-full"
          >
            <input
              type="text"
              placeholder="Search for luxury furniture..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full text-xs text-gray-800 placeholder:text-gray-400 focus:outline-none bg-transparent"
            />
            <button
              type="submit"
              className="w-7 h-7 rounded-full bg-[#0B1728] text-white flex items-center justify-center flex-shrink-0 ml-1"
            >
              <Search className="w-3.5 h-3.5" />
            </button>
          </form>
        </div>

      </div>
    </header>
  )
}
