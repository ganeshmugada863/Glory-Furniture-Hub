import React, { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAppStore } from '../store/useAppStore'
import { authService } from '../services/authService'
import Input from '../components/common/Input'
import Button from '../components/common/Button'
import { ArrowRight, User, Mail, Lock, Phone } from 'lucide-react'

export default function RegisterScreen() {
  const navigate = useNavigate()
  const setUser = useAppStore(state => state.setUser)

  const [name, setName] = useState('')
  const [email, setEmail] = useState('')
  const [phone, setPhone] = useState('')
  const [password, setPassword] = useState('')
  const [confirmPassword, setConfirmPassword] = useState('')
  const [termsAccepted, setTermsAccepted] = useState(true)
  const [isLoading, setIsLoading] = useState(false)
  const [errorMessage, setErrorMessage] = useState('')

  const handleRegister = async (e) => {
    e.preventDefault()
    setErrorMessage('')

    if (password !== confirmPassword) {
      setErrorMessage('Passwords do not match.')
      return
    }

    if (!termsAccepted) {
      setErrorMessage('Please accept the Terms & Privacy Policy.')
      return
    }

    setIsLoading(true)

    const { user, error } = await authService.signUp({
      email,
      password,
      fullName: name,
      phone
    })

    setIsLoading(false)

    if (error) {
      setErrorMessage(error.message || 'Registration failed. Please try again.')
      return
    }

    setUser(user)
    navigate('/home')
  }

  const handleGoogleSignUp = async () => {
    setIsLoading(true)
    setErrorMessage('')
    const { user, error } = await authService.signInWithGoogle()
    setIsLoading(false)
    if (error) {
      setErrorMessage(error.message || 'Google sign-up failed.')
      return
    }
    if (user) {
      setUser(user)
      navigate('/home')
    }
  }

  return (
    <div className="min-h-screen bg-[#FDFBF7] flex flex-col justify-center py-10 px-4 sm:px-6 relative overflow-hidden">
      {/* Ambient background glow */}
      <div className="absolute top-1/4 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[500px] h-[500px] bg-gold-500/5 rounded-full blur-3xl pointer-events-none" />

      <div className="w-full max-w-lg mx-auto bg-white p-6 sm:p-9 rounded-3xl border border-walnut-200 shadow-warm-lg relative z-10">
        <div className="text-center mb-6">
          <div 
            onClick={() => navigate('/home')}
            className="w-16 h-16 rounded-2xl bg-walnut-900 text-gold-400 font-sans font-bold text-2xl flex items-center justify-center mx-auto mb-3 shadow-warm ring-4 ring-gold-500/20 cursor-pointer hover:scale-105 transition-transform"
          >
            G
          </div>
          <h1 className="font-sans font-bold text-2xl text-walnut-800 tracking-wide">Create Account</h1>
          <p className="text-xs text-softgray mt-1">Join Glory Furniture Hub for tailored craftsmanship & AI guidance.</p>
        </div>

        {errorMessage && (
          <div className="mb-4 p-3 bg-dustyrose/10 border border-dustyrose/30 text-dustyrose text-xs font-semibold rounded-xl text-center">
            {errorMessage}
          </div>
        )}

        <form onSubmit={handleRegister} className="space-y-3.5">
        <Input
          label="Full Name"
          type="text"
          required
          icon={User}
          value={name}
          onChange={(e) => setName(e.target.value)}
          placeholder="e.g. Suresh Nambiar"
        />

        <Input
          label="Email Address"
          type="email"
          required
          icon={Mail}
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          placeholder="e.g. suresh@example.com"
        />

        <Input
          label="Phone Number"
          type="tel"
          required
          icon={Phone}
          value={phone}
          onChange={(e) => setPhone(e.target.value)}
          placeholder="+91 98765 43210"
        />

        <Input
          label="Password"
          type="password"
          required
          icon={Lock}
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          placeholder="••••••••"
        />

        <Input
          label="Confirm Password"
          type="password"
          required
          icon={Lock}
          value={confirmPassword}
          onChange={(e) => setConfirmPassword(e.target.value)}
          placeholder="••••••••"
        />

        <div className="flex items-center gap-2 pt-1">
          <input
            type="checkbox"
            id="terms"
            checked={termsAccepted}
            onChange={(e) => setTermsAccepted(e.target.checked)}
            className="accent-walnut-500 rounded"
          />
          <label htmlFor="terms" className="text-[11px] text-softgray">
            I agree to the <span className="text-walnut-800 font-semibold underline">Terms of Service</span> & <span className="text-walnut-800 font-semibold underline">Privacy Policy</span>
          </label>
        </div>

        <Button
          type="submit"
          variant="primary"
          size="lg"
          isLoading={isLoading}
          className="w-full"
          icon={ArrowRight}
        >
          Complete Registration
        </Button>

        <div className="flex items-center my-3">
          <div className="flex-1 border-t border-cream-200" />
          <span className="px-3 text-[11px] text-softgray uppercase">or</span>
          <div className="flex-1 border-t border-cream-200" />
        </div>

        <Button
          type="button"
          variant="secondary"
          size="md"
          onClick={handleGoogleSignUp}
          className="w-full"
        >
          <svg className="w-4 h-4 mr-2" viewBox="0 0 24 24">
            <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/>
            <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/>
            <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.06H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.94l2.85-2.22.81-.63z"/>
            <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.06l3.66 2.84c.87-2.6 3.3-4.52 6.16-4.52z"/>
          </svg>
          Sign Up with Google OAuth
        </Button>
      </form>

        <div className="text-center mt-6 pt-4 border-t border-walnut-100 space-y-2">
          <p className="text-xs text-softgray">
            Already registered?{' '}
            <button onClick={() => navigate('/login')} className="text-gold-600 font-bold hover:underline">
              Sign In
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
