import React, { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAppStore } from '../store/useAppStore'
import { authService } from '../services/authService'
import Input from '../components/common/Input'
import Button from '../components/common/Button'
import { ArrowRight, Mail, Lock } from 'lucide-react'

export default function LoginScreen() {
  const navigate = useNavigate()
  const setUser = useAppStore(state => state.setUser)

  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [errorMessage, setErrorMessage] = useState('')

  const handleLogin = async (e) => {
    e.preventDefault()
    setIsLoading(true)
    setErrorMessage('')

    const { user, error } = await authService.signInWithPassword({ email, password })

    setIsLoading(false)

    if (error) {
      setErrorMessage(error.message || 'Invalid email or password.')
      return
    }

    setUser(user)
    navigate(user.role === 'admin' ? '/admin' : '/home')
  }

  const handleGoogleSignIn = async () => {
    setIsLoading(true)
    setErrorMessage('')
    const { user, error } = await authService.signInWithGoogle()
    setIsLoading(false)
    if (error) {
      setErrorMessage(error.message || 'Google sign-in failed.')
      return
    }
    if (user) {
      setUser(user)
      navigate('/home')
    }
  }

  const handleQuickRoleLogin = (role) => {
    if (role === 'admin') {
      const adminUser = {
        id: 'admin-001',
        name: 'Master Studio Admin',
        email: 'admin@gloryfurniture.com',
        role: 'admin',
        phone: '+91 98765 43210'
      }
      setUser(adminUser)
      navigate('/admin')
    } else {
      const saved = localStorage.getItem('glory_user')
      let existing = null
      try { if (saved) existing = JSON.parse(saved) } catch (e) {}

      const customerUser = (existing && existing.role === 'customer' && existing.name)
        ? existing
        : {
            id: `cust-${Date.now().toString().slice(-4)}`,
            name: 'Glory Patron',
            email: 'customer@gloryfurniture.com',
            role: 'customer',
            phone: ''
          }
      setUser(customerUser)
      navigate('/home')
    }
  }

  return (
    <div className="min-h-screen bg-[#FDFBF7] flex flex-col justify-center py-10 px-4 sm:px-6 relative overflow-hidden">
      {/* Decorative background glow */}
      <div className="absolute top-1/4 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[500px] h-[500px] bg-gold-500/5 rounded-full blur-3xl pointer-events-none" />

      <div className="w-full max-w-lg mx-auto bg-white p-6 sm:p-9 rounded-3xl border border-walnut-200 shadow-warm-lg relative z-10">
        {/* Brand Header */}
        <div className="text-center mb-6">
          <div 
            onClick={() => navigate('/home')}
            className="w-16 h-16 rounded-2xl bg-walnut-900 text-gold-400 font-serif font-bold text-2xl flex items-center justify-center mx-auto mb-3 shadow-warm ring-4 ring-gold-500/20 cursor-pointer hover:scale-105 transition-transform"
          >
            G
          </div>
          <h1 className="font-serif font-bold text-2xl text-walnut-800 tracking-wide">Glory Furniture Hub</h1>
          <p className="text-xs text-softgray mt-1">Select your login role to continue</p>
        </div>

        {/* QUICK ROLE SELECTOR (1-Click Instant Login for Demo) */}
        <div className="mb-5 space-y-2.5">
          <div className="text-[11px] font-bold uppercase tracking-wider text-walnut-600 text-center">
            ⚡ Quick 1-Click Role Login
          </div>

          <div className="grid grid-cols-2 gap-2.5">
            {/* Customer Login Button */}
            <button
              type="button"
              onClick={() => handleQuickRoleLogin('customer')}
              className="p-3.5 rounded-2xl bg-[#FDFBF7] border-2 border-walnut-200 hover:border-walnut-800 hover:bg-cream-50 transition-all text-left shadow-sm active-tap flex flex-col justify-between group"
            >
              <div className="flex items-center justify-between mb-1.5">
                <span className="text-lg">🛍️</span>
                <span className="text-[10px] font-bold uppercase tracking-wide bg-cream-200 text-walnut-800 px-2 py-0.5 rounded-md">
                  Customer
                </span>
              </div>
              <div>
                <h4 className="font-serif font-bold text-xs text-walnut-900 group-hover:text-gold-600 transition-colors">
                  Login as User
                </h4>
                <p className="text-[10px] text-softgray mt-0.5 leading-tight">
                  Order & check personal booking details
                </p>
              </div>
            </button>

            {/* Admin Login Button */}
            <button
              type="button"
              onClick={() => handleQuickRoleLogin('admin')}
              className="p-3.5 rounded-2xl bg-walnut-900 border-2 border-walnut-900 hover:bg-walnut-800 transition-all text-left shadow-md active-tap flex flex-col justify-between group"
            >
              <div className="flex items-center justify-between mb-1.5">
                <span className="text-lg">👑</span>
                <span className="text-[10px] font-bold uppercase tracking-wide bg-gold-500/20 text-gold-400 px-2 py-0.5 rounded-md">
                  Admin
                </span>
              </div>
              <div>
                <h4 className="font-serif font-bold text-xs text-white group-hover:text-gold-400 transition-colors">
                  Login as Admin
                </h4>
                <p className="text-[10px] text-cream-200/70 mt-0.5 leading-tight">
                  Manage products, bed sizes & all orders
                </p>
              </div>
            </button>
          </div>
        </div>

        <div className="flex items-center my-3">
          <div className="flex-1 border-t border-walnut-200" />
          <span className="px-3 text-[10px] font-semibold text-softgray uppercase">or sign in with password</span>
          <div className="flex-1 border-t border-walnut-200" />
        </div>

        {errorMessage && (
          <div className="p-3 rounded-xl bg-red-50 border border-red-200 text-red-700 text-xs mb-4">
            {errorMessage}
          </div>
        )}

        {/* Login Form */}
        <form onSubmit={handleLogin} className="space-y-4">
          <Input
            label="Email Address"
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            placeholder="e.g. admin@gloryfurniture.com or user@gmail.com"
            icon={Mail}
            required
          />

          <div className="space-y-1">
            <Input
              label="Password"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="••••••••"
              icon={Lock}
              required
            />
            <div className="flex justify-end">
              <button
                type="button"
                onClick={() => navigate('/forgot-password')}
                className="text-[11px] font-semibold text-gold-600 hover:text-gold-700"
              >
                Forgot Password?
              </button>
            </div>
          </div>

          <Button
            type="submit"
            variant="primary"
            size="lg"
            isLoading={isLoading}
            className="w-full"
            icon={ArrowRight}
          >
            Sign In
          </Button>

          <div className="flex items-center my-3">
            <div className="flex-1 border-t border-walnut-200" />
            <span className="px-3 text-[10px] font-semibold text-softgray uppercase">or continue with</span>
            <div className="flex-1 border-t border-walnut-200" />
          </div>

          <button
            type="button"
            onClick={handleGoogleSignIn}
            disabled={isLoading}
            className="w-full flex items-center justify-center gap-2.5 py-3 px-4 bg-white border border-walnut-200 hover:border-walnut-400 hover:bg-cream-50 rounded-xl text-xs font-semibold text-walnut-900 transition-all shadow-2xs active:scale-[0.99]"
          >
            <svg className="w-4 h-4" viewBox="0 0 24 24">
              <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/>
              <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/>
              <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.06H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.94l2.85-2.22.81-.63z"/>
              <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.06l3.66 2.84c.87-2.6 3.3-4.52 6.16-4.52z"/>
            </svg>
            <span>Sign In with Google</span>
          </button>

          <div className="text-center text-[10px] text-softgray pt-1">
            Tip: Emails containing <code className="bg-cream-200 px-1 py-0.5 rounded text-walnut-800">admin</code> log in with full Admin capabilities.
          </div>
        </form>

        <div className="text-center mt-5 pt-4 border-t border-walnut-100 space-y-2">
          <p className="text-xs text-softgray">
            Don't have an account?{' '}
            <button onClick={() => navigate('/register')} className="text-gold-600 font-bold hover:underline">
              Register as Customer
            </button>
          </p>
          <div>
            <button onClick={() => navigate('/home')} className="text-xs text-walnut-600 hover:text-walnut-900 font-medium">
              ← Return to Main Website
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}
