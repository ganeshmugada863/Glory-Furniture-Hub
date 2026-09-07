import React from 'react'
import { useNavigate } from 'react-router-dom'
import Button from '../components/common/Button'
import { Sparkles, ArrowRight, Home } from 'lucide-react'

export default function CustomRequestConfirmationScreen() {
  const navigate = useNavigate()

  return (
    <div className="min-h-screen bg-cream-100 flex flex-col items-center justify-center p-6 text-center max-w-md mx-auto">
      <div className="w-20 h-20 rounded-full bg-gold-500/10 text-gold-600 flex items-center justify-center mb-4 ring-8 ring-gold-500/20">
        <Sparkles className="w-10 h-10 text-gold-600 animate-spin-slow" />
      </div>

      <span className="text-xs font-bold uppercase tracking-widest text-gold-600 mb-1">
        Bespoke Specification Submitted
      </span>

      <h2 className="font-sans font-bold text-2xl text-walnut-800 tracking-wide mb-2">
        Custom Request Received!
      </h2>

      <p className="text-xs text-softgray max-w-xs leading-relaxed mb-6">
        Our master craftsman is reviewing your wood species, dimensions, and styling notes. You will receive a quote & timeline within 24–48 hours.
      </p>

      <div className="w-full space-y-3">
        <Button
          variant="primary"
          size="lg"
          onClick={() => navigate('/profile/requests')}
          className="w-full"
          icon={ArrowRight}
        >
          View My Custom Requests
        </Button>

        <Button
          variant="secondary"
          size="md"
          onClick={() => navigate('/home')}
          className="w-full"
          icon={Home}
        >
          Back to Home
        </Button>
      </div>
    </div>
  )
}
