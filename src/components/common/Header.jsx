import React, { useState } from 'react'
import { useNavigate, useLocation, Link } from 'react-router-dom'
import { ArrowLeft, Heart, Search, ShoppingBag, User, Menu, X } from 'lucide-react'
import { useAppStore } from '../../store/useAppStore'

export default function Header({ title, showBack = false }) {
  const navigate = useNavigate()
  const location = useLocation()
  const { wishlist, userBookings } = useAppStore()
  const [searchQuery, setSearchQuery] = useState('')
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false)

  const cartCount = userBookings.length > 0 ? userBookings.length : 3

  const navLinks = [
    { name: 'New Arrivals', path: '/catalog?filter=newArrival' },
    { name: 'Living Room', path: '/catalog?category=Sofa%20Set' },
    { name: 'Dining Room', path: '/catalog?category=Dining%20Table' },
    { name: 'Bedroom', path: '/catalog?category=Cot%20%2F%20Wooden%20Bed' },
    { name: 'About Us', path: '/custom-request' },
    { name: 'Contact', path: '/contact' },
  ]

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
                <span className="font-serif font-black text-lg sm:text-xl text-gray-950 tracking-wider leading-none">
                  GLORY
                </span>
                <span className="text-[8px] sm:text-[9px] font-bold tracking-[0.2em] text-gray-500 uppercase mt-0.5 leading-tight">
                  FURNITURE HUB
                </span>
              </div>
            </div>
          </div>

          {/* 2. NAVIGATION LINKS (Center - Desktop) */}
          <nav className="hidden lg:flex items-center gap-6 xl:gap-8">
            {navLinks.map((link) => {
              const isActive = location.pathname + location.search === link.path
              return (
                <Link
                  key={link.name}
                  to={link.path}
                  className={`text-xs xl:text-[13px] font-medium transition-colors whitespace-nowrap ${
                    isActive
                      ? 'text-gray-950 font-bold border-b-2 border-gray-950 pb-0.5'
                      : 'text-gray-700 hover:text-gray-950'
                  }`}
                >
                  {link.name}
                </Link>
              )
            })}
          </nav>

          {/* 3. RIGHT UTILITIES (Search Bar & Profile/Wishlist/Cart Icons) */}
          <div className="flex items-center gap-3 sm:gap-4 flex-shrink-0">
            
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

            {/* User Profile Icon */}
            <button
              onClick={() => navigate('/profile')}
              className="p-1.5 text-gray-700 hover:text-gray-950 transition-colors"
              title="My Account"
            >
              <User className="w-5 h-5 stroke-[1.75]" />
            </button>

            {/* Wishlist Heart Icon */}
            <button
              onClick={() => navigate('/wishlist')}
              className="p-1.5 text-gray-700 hover:text-gray-950 relative transition-colors"
              title="Saved Wishlist"
            >
              <Heart className="w-5 h-5 stroke-[1.75]" />
              {wishlist.length > 0 && (
                <span className="absolute -top-1 -right-1 w-4 h-4 bg-red-600 text-white text-[8px] font-bold rounded-full flex items-center justify-center shadow-xs">
                  {wishlist.length}
                </span>
              )}
            </button>

            {/* Shopping Cart / Bag Icon with Badge '3' matching image */}
            <button
              onClick={() => navigate('/bookings')}
              className="p-1.5 text-gray-700 hover:text-gray-950 relative transition-colors"
              title="Shopping Cart & Orders"
            >
              <ShoppingBag className="w-5 h-5 stroke-[1.75]" />
              <span className="absolute -top-1 -right-1 w-4 h-4 bg-gray-950 text-white text-[9px] font-bold rounded-full flex items-center justify-center shadow-xs">
                {cartCount}
              </span>
            </button>

            {/* Mobile Menu Toggle Button */}
            <button
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
              className="p-1.5 text-gray-700 hover:text-gray-950 lg:hidden"
              aria-label="Toggle Menu"
            >
              {mobileMenuOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
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

        {/* Mobile Navigation Drawer */}
        {mobileMenuOpen && (
          <div className="lg:hidden border-t border-gray-100 py-3 space-y-1 bg-white animate-fadeIn">
            {navLinks.map((link) => (
              <Link
                key={link.name}
                to={link.path}
                onClick={() => setMobileMenuOpen(false)}
                className="block px-3 py-2 rounded-lg text-xs font-semibold text-gray-800 hover:bg-gray-50 transition-colors"
              >
                {link.name}
              </Link>
            ))}
          </div>
        )}

      </div>
    </header>
  )
}
