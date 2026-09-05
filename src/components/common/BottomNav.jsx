import React from 'react'
import { useNavigate, useLocation } from 'react-router-dom'
import { Home, Grid, Hammer, Package, User, ShoppingBag, ShieldCheck } from 'lucide-react'
import { useAppStore } from '../../store/useAppStore'

export default function BottomNav() {
  const navigate = useNavigate()
  const location = useLocation()
  const { user } = useAppStore()

  const isAdmin = user?.role === 'admin'

  const tabs = isAdmin
    ? [
        { id: 'home', label: 'Store', icon: Home, path: '/home' },
        { id: 'catalog', label: 'Catalog', icon: Grid, path: '/catalog' },
        { id: 'admin-products', label: 'Products', icon: ShoppingBag, path: '/admin/products' },
        { id: 'admin-bookings', label: 'Orders', icon: Package, path: '/admin/bookings' },
        { id: 'admin-dash', label: 'Admin', icon: ShieldCheck, path: '/admin' },
      ]
    : [
        { id: 'home', label: 'Home', icon: Home, path: '/home' },
        { id: 'catalog', label: 'Catalog', icon: Grid, path: '/catalog' },
        { id: 'custom', label: 'Custom', icon: Hammer, path: '/custom-request' },
        { id: 'bookings', label: 'My Orders', icon: Package, path: '/bookings' },
        { id: 'profile', label: 'Profile', icon: User, path: '/profile' },
      ]

  return (
    <nav className="fixed bottom-0 left-0 right-0 z-40 bg-walnut-900 border-t border-walnut-700 shadow-warm-lg md:hidden">
      <div className="max-w-md mx-auto flex items-center justify-around py-2 px-1">
        {tabs.map((tab) => {
          const Icon = tab.icon
          const isActive = location.pathname === tab.path || (tab.path === '/home' && location.pathname === '/')
          return (
            <button
              key={tab.id}
              onClick={() => navigate(tab.path)}
              className={`flex flex-col items-center justify-center py-1 px-3 rounded-2xl transition-all active-tap ${
                isActive ? 'text-gold-400 font-bold scale-105' : 'text-cream-200 hover:text-white'
              }`}
            >
              <Icon className={`w-5 h-5 mb-0.5 ${isActive ? 'stroke-[2.5px]' : 'stroke-2'}`} />
              <span className="text-[10px] font-medium tracking-tight">{tab.label}</span>
            </button>
          )
        })}
      </div>
    </nav>
  )
}
