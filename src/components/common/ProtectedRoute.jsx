import React from 'react'
import { useNavigate } from 'react-router-dom'
import { useAppStore } from '../../store/useAppStore'
import Button from './Button'
import { ShieldAlert, ArrowLeft, KeyRound, UserCheck } from 'lucide-react'

export default function ProtectedRoute({ children, requiredRole = 'admin' }) {
  const navigate = useNavigate()
  const { user, switchRole } = useAppStore()

  // 1. If not logged in at all
  if (!user) {
    return (
      <div className="min-h-screen bg-[#FDFBF7] flex flex-col items-center justify-center p-6 text-center">
        <div className="w-16 h-16 rounded-3xl bg-walnut-100 text-walnut-800 flex items-center justify-center mx-auto mb-4 shadow-sm">
          <KeyRound className="w-8 h-8" />
        </div>
        <h2 className="font-serif font-bold text-2xl text-walnut-900 mb-2">Sign In Required</h2>
        <p className="text-xs text-softgray max-w-sm mb-6">
          Please sign in to your account to view this page.
        </p>
        <Button variant="primary" size="md" onClick={() => navigate('/login')}>
          Go to Sign In
        </Button>
      </div>
    )
  }

  // 2. If logged in as customer trying to access admin portal
  if (requiredRole === 'admin' && user.role !== 'admin') {
    const handleQuickAdminLogin = () => {
      switchRole('admin')
      window.location.reload()
    }

    return (
      <div className="min-h-screen bg-[#FAF6F0] flex flex-col items-center justify-center p-6 text-center max-w-lg mx-auto">
        <div className="w-20 h-20 rounded-3xl bg-dustyrose/10 text-dustyrose flex items-center justify-center mx-auto mb-4 border border-dustyrose/20 shadow-sm">
          <ShieldAlert className="w-10 h-10" />
        </div>

        <span className="text-[11px] font-bold uppercase tracking-widest text-dustyrose bg-dustyrose/10 px-3 py-1 rounded-full mb-3 inline-block">
          Restricted Portal
        </span>

        <h2 className="font-serif font-bold text-2xl sm:text-3xl text-walnut-900 mb-2">
          Administrator Access Only
        </h2>

        <p className="text-xs text-softgray leading-relaxed mb-6 max-w-md">
          You are currently logged in with a Customer account (<strong>{user.name}</strong>). 
          Adding products, managing orders, and catalog operations are strictly reserved for <strong>Studio Admin</strong>.
        </p>

        <div className="bg-white p-4 rounded-2xl border border-walnut-200/80 shadow-sm w-full mb-6 space-y-2 text-left">
          <div className="flex items-center justify-between text-xs pb-2 border-b border-cream-200">
            <span className="text-softgray">Current Logged In User:</span>
            <span className="font-bold text-walnut-900">{user.name}</span>
          </div>
          <div className="flex items-center justify-between text-xs pb-2 border-b border-cream-200">
            <span className="text-softgray">Your Current Role:</span>
            <span className="font-bold uppercase tracking-wider text-dustyrose bg-dustyrose/10 px-2 py-0.5 rounded text-[10px]">
              Customer Account
            </span>
          </div>
          <div className="flex items-center justify-between text-xs">
            <span className="text-softgray">Customer Capabilities:</span>
            <span className="text-walnut-700 font-medium text-[11px]">Orders, Custom Specs, Wishlist</span>
          </div>
        </div>

        <div className="flex flex-col sm:flex-row gap-3 w-full">
          <Button
            variant="secondary"
            size="md"
            className="flex-1"
            icon={ArrowLeft}
            onClick={() => navigate('/home')}
          >
            Go to Store
          </Button>

          <Button
            variant="primary"
            size="md"
            className="flex-1 bg-walnut-900 hover:bg-walnut-800 text-gold-400 font-bold"
            icon={UserCheck}
            onClick={handleQuickAdminLogin}
          >
            Switch to Admin
          </Button>
        </div>
      </div>
    )
  }

  // 3. Authorized
  return children
}
