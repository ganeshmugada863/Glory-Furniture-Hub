import React, { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import Input from '../components/common/Input'
import Button from '../components/common/Button'
import { ArrowLeft, Mail, CheckCircle2 } from 'lucide-react'

export default function ForgotPasswordScreen() {
  const navigate = useNavigate()
  const [email, setEmail] = useState('')
  const [sent, setSent] = useState(false)

  const handleSubmit = (e) => {
    e.preventDefault()
    setSent(true)
  }

  return (
    <div className="min-h-screen bg-cream-100 flex flex-col justify-center p-6 max-w-md mx-auto">
      <button onClick={() => navigate('/login')} className="p-2 text-walnut-700 w-fit mb-4 active-tap">
        <ArrowLeft className="w-5 h-5" />
      </button>

      <div className="bg-white p-6 rounded-3xl border border-walnut-100 shadow-card">
        {!sent ? (
          <>
            <h2 className="font-sans font-bold text-xl text-walnut-800 mb-1">Reset Your Password</h2>
            <p className="text-xs text-softgray mb-4">Enter your registered email and we will send you a password reset link.</p>

            <form onSubmit={handleSubmit} className="space-y-4">
              <Input
                label="Email Address"
                type="email"
                required
                icon={Mail}
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="client@example.com"
              />

              <Button
                type="submit"
                variant="primary"
                size="md"
                className="w-full"
              >
                Send Reset Link
              </Button>
            </form>
          </>
        ) : (
          <div className="text-center py-4">
            <CheckCircle2 className="w-12 h-12 text-mutedgreen mx-auto mb-2" />
            <h3 className="font-sans font-bold text-base text-walnut-800">Reset Email Sent!</h3>
            <p className="text-xs text-softgray my-2">Please check your inbox for instructions to set a new password.</p>
            <Button
              variant="primary"
              size="md"
              onClick={() => navigate('/login')}
              className="mt-4"
            >
              Back to Login
            </Button>
          </div>
        )}
      </div>
    </div>
  )
}
