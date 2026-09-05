import React from 'react'
import { useNavigate, useLocation, Link } from 'react-router-dom'
import { ArrowLeft, Bell, Heart, Search, Shield, User } from 'lucide-react'
import { useAppStore } from '../../store/useAppStore'

export default function Header({ title, showBack = false }) {
  const navigate = useNavigate()
  const location = useLocation()
  const { wishlist, notifications, user } = useAppStore()

  const unreadNotifications = notifications.filter(n => !n.read).length

  const navLinks = [
    { name: 'Home', path: '/home' },
    { name: 'Catalog', path: '/catalog' },
  ]

  return (
    <header className="sticky top-0 z-50 bg-[#F7F4EF] text-walnut-900 border-b border-walnut-200/60 shadow-sm w-full font-sans">
      
      {/* TOPMOST ANNOUNCEMENT BAR */}
      <div className="bg-[#EFEAE2] border-b border-walnut-200/50 py-1 px-4 text-[10px] font-medium text-walnut-800 flex justify-between items-center w-full">
        <div className="flex items-center gap-2 mx-auto sm:mx-0">
          <span>📦 Free White-Glove Delivery Consultation on All Orders</span>
        </div>
        <div className="hidden sm:flex items-center gap-4 text-softgray text-[10px]">
          <button onClick={() => navigate('/bookings')} className="hover:text-walnut-900 transition-colors">Track Order</button>
          <span>|</span>
          <button onClick={() => navigate('/contact')} className="hover:text-walnut-900 transition-colors">Help & Support</button>
        </div>
      </div>

      {/* MAIN HEADER CONTAINER */}
      <div className="w-full px-3 sm:px-6 lg:px-10">
        <div className="flex items-center justify-between h-14 sm:h-16">
          
          {/* MOBILE HEADER VIEW */}
          <div className="flex items-center gap-2.5 md:hidden">
            {showBack ? (
              <button
                onClick={() => navigate(-1)}
                className="p-1.5 rounded-full hover:bg-cream-200 text-walnut-900"
                aria-label="Go back"
              >
                <ArrowLeft className="w-4 h-4" />
              </button>
            ) : (
              <div 
                onClick={() => navigate('/home')} 
                className="w-8 h-8 rounded-lg bg-walnut-900 text-gold-400 flex items-center justify-center font-serif font-bold text-base shadow-2xs cursor-pointer"
              >
                G
              </div>
            )}
            
            <h1 className="font-serif font-bold text-sm text-walnut-900 truncate">
              {title || 'Glory Furniture Hub'}
            </h1>
          </div>

          {/* DESKTOP BRAND LOGO */}
          <div 
            className="hidden md:flex items-center gap-1.5 cursor-pointer hover:opacity-90 transition-opacity flex-shrink-0" 
            onClick={() => navigate('/home')}
          >
            <span className="font-serif font-bold text-xl lg:text-2xl text-walnut-900 tracking-tight">
              Glory<span className="text-gold-600 font-normal">.</span>
            </span>
          </div>

          {/* DESKTOP TEXT NAVIGATION LINKS */}
          <nav className="hidden md:flex items-center gap-5 lg:gap-7">
            {navLinks.map(link => {
              const isActive = location.pathname === link.path
              return (
                <Link
                  key={link.name}
                  to={link.path}
                  className={`text-xs font-medium transition-all relative py-1 ${
                    link.isAdminLink
                      ? 'text-gold-700 bg-gold-500/10 px-2.5 py-0.5 rounded-full font-bold border border-gold-500/40 hover:bg-gold-500/20 text-[11px]'
                      : isActive
                        ? 'text-walnut-900 font-bold border-b-2 border-walnut-900'
                        : 'text-walnut-700 hover:text-walnut-900'
                  }`}
                >
                  {link.name}
                </Link>
              )
            })}
          </nav>

          {/* DESKTOP RIGHT ICON UTILITIES */}
          <div className="flex items-center gap-2 sm:gap-3 flex-shrink-0">
            {/* Search Icon */}
            <button
              onClick={() => navigate('/catalog')}
              className="p-1.5 text-walnut-800 hover:text-walnut-900 transition-colors"
              title="Search Catalog"
            >
              <Search className="w-4 h-4" />
            </button>

            {/* Profile User Icon */}
            <button
              onClick={() => navigate('/profile')}
              className="p-1.5 text-walnut-800 hover:text-walnut-900 transition-colors"
              title="My Account"
            >
              <User className="w-4 h-4" />
            </button>



            {/* Saved Wishlist Icon with Centered Badge */}
            <button
              onClick={() => navigate('/wishlist')}
              className="p-1.5 text-walnut-800 hover:text-walnut-900 relative transition-colors"
              title="Saved Wishlist"
            >
              <Heart className="w-4 h-4" />
              {wishlist.length > 0 && (
                <span className="absolute -top-1 -right-1 w-4 h-4 bg-walnut-900 text-white text-[8px] font-bold rounded-full flex items-center justify-center shadow-xs">
                  {wishlist.length}
                </span>
              )}
            </button>

            {/* Notifications Icon with Centered Badge */}
            <button
              onClick={() => navigate('/notifications')}
              className="p-1.5 text-walnut-800 hover:text-walnut-900 relative transition-colors"
              title="Notifications"
            >
              <Bell className="w-4 h-4" />
              {unreadNotifications > 0 && (
                <span className="absolute -top-1 -right-1 w-4 h-4 bg-gold-600 text-white text-[8px] font-bold rounded-full flex items-center justify-center shadow-xs animate-pulse">
                  {unreadNotifications}
                </span>
              )}
            </button>
          </div>

        </div>
      </div>
    </header>
  )
}
