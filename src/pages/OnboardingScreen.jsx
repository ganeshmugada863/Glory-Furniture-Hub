import React, { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import Button from '../components/common/Button'
import { Sparkles, ArrowRight, ArrowLeft, Check, ShieldCheck, Truck, Award, Compass } from 'lucide-react'

const SLIDES = [
  {
    id: 1,
    title: 'Handcrafted Furniture, Built for You',
    subtitle: 'Explore custom and ready-made furniture handcrafted by master artisans in Hyderabad using premium, sustainably sourced solid woods.',
    image: 'https://images.unsplash.com/photo-1555041469-a586c61ea9bc?auto=format&fit=crop&w=1400&q=85',
    badge: 'Artisanal Quality',
    pill: 'Solid Teak & Sheesham Craftsmanship',
    stat1: { label: 'Solid Wood Guarantee', value: '10-Year' },
    stat2: { label: 'Artisan Workshop', value: 'Hyderabad' },
    stat3: { label: 'White-Glove Delivery', value: 'Included' },
    highlight: 'Masterfully joined using authentic mortise and tenon joinery for heirloom durability.'
  },
  {
    id: 2,
    title: 'Browse, Customize & Book Easily',
    subtitle: 'Tailor dimensions, wood species, and luxury upholstery to harmonize perfectly with your home. Order ready-made or submit bespoke designs.',
    image: 'https://images.unsplash.com/photo-1618221195710-dd6b41faaea6?auto=format&fit=crop&w=1400&q=85',
    badge: 'Seamless Customization',
    pill: 'Bespoke Sizing & Custom Finishes',
    stat1: { label: 'Custom Sizing', value: 'Built-to-Fit' },
    stat2: { label: 'Wood Finishes', value: 'Natural / Teak / Walnut' },
    stat3: { label: 'Pricing Model', value: 'Direct Studio' },
    highlight: 'Choose custom width, depth, and wood tone with live order summary and instant invoice generation.'
  },
  {
    id: 3,
    title: 'Your Personal AI Furniture Advisor',
    subtitle: 'Meet GloryAI! Receive personalized styling advice, timber recommendations, and step-by-step guidance for your living space anytime.',
    image: 'https://images.unsplash.com/photo-1616486338812-3dadae4b4ace?auto=format&fit=crop&w=1400&q=85',
    badge: 'GloryAI Assisted',
    pill: 'Intelligent Space Planning & Styling',
    stat1: { label: 'Design Guidance', value: '24/7 AI Advisor' },
    stat2: { label: 'Wood Selection', value: 'Smart Matching' },
    stat3: { label: 'Consultation Fee', value: '₹0 Free' },
    highlight: 'Our intelligent design advisor guides you through wood selection, room scale, and maintenance.'
  }
]

export default function OnboardingScreen() {
  const navigate = useNavigate()
  const [currentSlide, setCurrentSlide] = useState(0)

  const handleNext = () => {
    if (currentSlide < SLIDES.length - 1) {
      setCurrentSlide(prev => prev + 1)
    } else {
      finishOnboarding('/home')
    }
  }

  const handlePrev = () => {
    if (currentSlide > 0) {
      setCurrentSlide(prev => prev - 1)
    }
  }

  const finishOnboarding = (target = '/home') => {
    localStorage.setItem('hasSeenOnboarding', 'true')
    navigate(target)
  }

  const active = SLIDES[currentSlide]

  return (
    <div className="min-h-screen bg-[#FDFBF7] text-walnut-900 flex flex-col justify-between selection:bg-gold-500 selection:text-white relative overflow-x-hidden">
      
      {/* 1. TOP WEBSITE HEADER (Full Width Website Ratio) */}
      <header className="w-full border-b border-walnut-200/60 bg-[#FDFBF7]/90 backdrop-blur-md sticky top-0 z-30">
        <div className="max-w-7xl mx-auto px-4 sm:px-8 lg:px-12 py-3.5 sm:py-4 flex items-center justify-between">
          
          {/* Logo Brand */}
          <div 
            onClick={() => finishOnboarding('/home')}
            className="flex items-center gap-3 cursor-pointer group"
          >
            <div className="w-10 h-10 rounded-xl bg-walnut-900 text-gold-400 flex items-center justify-center font-serif font-bold text-xl shadow-md border border-gold-500/30 group-hover:scale-105 transition-transform">
              G
            </div>
            <div>
              <span className="font-serif font-bold text-lg sm:text-xl text-walnut-900 tracking-wide block leading-tight">
                Glory Furniture Hub
              </span>
              <span className="text-[10px] sm:text-[11px] font-medium tracking-widest text-gold-700 uppercase block">
                Artisanal Solid Wood Studio • Hyderabad
              </span>
            </div>
          </div>

          {/* Desktop Center Studio Credential */}
          <div className="hidden md:flex items-center gap-6 text-xs text-walnut-600 font-medium">
            <span className="flex items-center gap-1.5">
              <Award className="w-3.5 h-3.5 text-gold-600" />
              100% Solid Seasoned Wood
            </span>
            <span className="w-1 h-1 rounded-full bg-walnut-300" />
            <span className="flex items-center gap-1.5">
              <Truck className="w-3.5 h-3.5 text-gold-600" />
              White-Glove Direct Delivery
            </span>
          </div>

          {/* Action Navigation */}
          <div className="flex items-center gap-2.5 sm:gap-4">
            <button
              onClick={() => finishOnboarding('/login')}
              className="text-xs font-semibold text-walnut-800 hover:text-walnut-950 px-3 sm:px-4 py-2 rounded-lg hover:bg-walnut-100 transition-colors"
            >
              Sign In
            </button>

            <button
              onClick={() => finishOnboarding('/home')}
              className="inline-flex items-center gap-1.5 text-xs font-bold text-white bg-walnut-900 hover:bg-walnut-800 active:scale-95 px-4 sm:px-5 py-2 sm:py-2.5 rounded-full shadow-sm transition-all"
            >
              <span>Explore Website</span>
              <ArrowRight className="w-3.5 h-3.5 text-gold-400" />
            </button>
          </div>
        </div>
      </header>

      {/* 2. MAIN SHOWCASE HERO (Expansive 2-Column Website Ratio Layout) */}
      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-8 lg:px-12 py-6 sm:py-10 lg:py-12 flex flex-col justify-center">
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 lg:gap-14 items-center">
          
          {/* LEFT COLUMN: Editorial Content & Controls (Col span 6) */}
          <div className="lg:col-span-6 flex flex-col justify-center space-y-6 sm:space-y-7 order-2 lg:order-1">
            
            {/* Tag / Category Badge */}
            <div className="flex flex-wrap items-center gap-2.5">
              <span className="inline-flex items-center gap-1.5 bg-walnut-900 text-gold-400 text-xs font-semibold px-3.5 py-1.5 rounded-full shadow-xs border border-gold-500/30">
                <Sparkles className="w-3.5 h-3.5 text-gold-400" />
                {active.badge}
              </span>
              <span className="text-xs font-medium text-walnut-600 bg-cream-200/80 px-3 py-1.5 rounded-full border border-walnut-200">
                {active.pill}
              </span>
            </div>

            {/* Main Headline */}
            <div className="space-y-3">
              <h1 className="font-serif font-bold text-3xl sm:text-4xl lg:text-5xl text-walnut-900 leading-[1.16] tracking-tight">
                {active.title}
              </h1>
              <p className="text-sm sm:text-base lg:text-lg text-walnut-700/90 leading-relaxed max-w-xl">
                {active.subtitle}
              </p>
            </div>

            {/* 3 Metric / Feature Badges */}
            <div className="grid grid-cols-3 gap-2.5 sm:gap-4 pt-1">
              <div className="bg-[#F7F2EB] p-3 sm:p-4 rounded-2xl border border-walnut-200/70 shadow-2xs">
                <span className="text-[10px] sm:text-xs font-medium text-softgray block mb-1">
                  {active.stat1.label}
                </span>
                <span className="font-serif font-bold text-xs sm:text-sm md:text-base text-walnut-900 block truncate">
                  {active.stat1.value}
                </span>
              </div>

              <div className="bg-[#F7F2EB] p-3 sm:p-4 rounded-2xl border border-walnut-200/70 shadow-2xs">
                <span className="text-[10px] sm:text-xs font-medium text-softgray block mb-1">
                  {active.stat2.label}
                </span>
                <span className="font-serif font-bold text-xs sm:text-sm md:text-base text-walnut-900 block truncate">
                  {active.stat2.value}
                </span>
              </div>

              <div className="bg-[#F7F2EB] p-3 sm:p-4 rounded-2xl border border-walnut-200/70 shadow-2xs">
                <span className="text-[10px] sm:text-xs font-medium text-softgray block mb-1">
                  {active.stat3.label}
                </span>
                <span className="font-serif font-bold text-xs sm:text-sm md:text-base text-walnut-900 block truncate">
                  {active.stat3.value}
                </span>
              </div>
            </div>

            {/* Craftsmanship Note */}
            <div className="flex items-start gap-3 bg-white/80 p-3.5 rounded-xl border border-walnut-200/80 text-xs text-walnut-700">
              <ShieldCheck className="w-4 h-4 text-gold-600 flex-shrink-0 mt-0.5" />
              <span>{active.highlight}</span>
            </div>

            {/* Slide Navigation Tabs */}
            <div className="space-y-3 pt-2">
              <div className="flex items-center justify-between text-xs text-walnut-600 font-medium">
                <span>Step {currentSlide + 1} of {SLIDES.length}</span>
                <span className="text-gold-700 font-semibold">{SLIDES[currentSlide].badge}</span>
              </div>

              <div className="grid grid-cols-3 gap-2">
                {SLIDES.map((slide, idx) => (
                  <button
                    key={slide.id}
                    onClick={() => setCurrentSlide(idx)}
                    className={`h-2.5 rounded-full transition-all duration-300 ${
                      currentSlide === idx 
                        ? 'bg-gold-500 shadow-xs' 
                        : idx < currentSlide 
                          ? 'bg-walnut-400' 
                          : 'bg-walnut-200/80 hover:bg-walnut-300'
                    }`}
                    title={slide.title}
                  />
                ))}
              </div>
            </div>

            {/* Actions & Next Step Buttons */}
            <div className="pt-2 flex flex-col sm:flex-row items-stretch sm:items-center gap-3.5">
              {currentSlide > 0 && (
                <button
                  onClick={handlePrev}
                  className="px-4 py-3 rounded-xl border border-walnut-300 text-walnut-800 font-semibold text-xs sm:text-sm hover:bg-cream-200 flex items-center justify-center gap-1.5 transition-colors"
                >
                  <ArrowLeft className="w-4 h-4" />
                  <span>Previous</span>
                </button>
              )}

              <Button
                variant="primary"
                size="lg"
                onClick={handleNext}
                className="flex-1 bg-walnut-900 hover:bg-walnut-800 text-white py-3.5 px-6 rounded-xl font-bold shadow-warm flex items-center justify-center gap-2"
                icon={currentSlide === SLIDES.length - 1 ? Check : ArrowRight}
              >
                {currentSlide === SLIDES.length - 1 ? 'Enter Website & Explore Collection' : 'Next Step'}
              </Button>

              <button
                onClick={() => finishOnboarding('/catalog')}
                className="px-5 py-3.5 rounded-xl bg-white border border-walnut-200 text-walnut-900 font-semibold text-xs sm:text-sm hover:border-walnut-400 hover:bg-cream-50 transition-all text-center shadow-2xs"
              >
                Direct Catalog
              </button>
            </div>

            {/* Sign In Alternative */}
            <div className="pt-1 text-center sm:text-left text-xs text-walnut-600">
              Already a registered customer?{' '}
              <button
                onClick={() => finishOnboarding('/login')}
                className="text-gold-700 font-bold hover:text-gold-800 underline underline-offset-2 ml-1"
              >
                Sign In to Your Account
              </button>
            </div>

          </div>

          {/* RIGHT COLUMN: Expansive Widescreen Visual Hero (Col span 6) */}
          <div className="lg:col-span-6 order-1 lg:order-2">
            <div className="relative w-full">
              
              {/* Background ambient lighting glow */}
              <div className="absolute -inset-2 bg-gradient-to-tr from-gold-500/20 via-cream-300/40 to-walnut-300/30 rounded-3xl blur-2xl opacity-60 -z-10" />

              {/* Main Widescreen Image Canvas */}
              <div className="relative w-full aspect-[4/3] sm:aspect-[16/11] lg:aspect-[4/3] rounded-3xl overflow-hidden shadow-2xl border-2 border-walnut-200/90 bg-walnut-900">
                <img
                  src={active.image}
                  alt={active.title}
                  className="w-full h-full object-cover transition-all duration-700 ease-out transform hover:scale-105"
                />

                {/* Subtle vignette overlay */}
                <div className="absolute inset-0 bg-gradient-to-t from-walnut-950/80 via-transparent to-black/25 pointer-events-none" />

                {/* Top Badge Overlay */}
                <div className="absolute top-4 sm:top-6 left-4 sm:left-6 flex items-center gap-2">
                  <span className="bg-walnut-900/90 backdrop-blur-md text-gold-400 border border-gold-500/40 text-xs font-bold px-3.5 py-1.5 rounded-full shadow-lg flex items-center gap-2">
                    <Sparkles className="w-3.5 h-3.5 text-gold-400" />
                    {active.badge}
                  </span>
                </div>

                {/* Floating Studio Credential Glass Card */}
                <div className="absolute bottom-4 sm:bottom-6 left-4 sm:left-6 right-4 sm:right-6 bg-white/95 backdrop-blur-md p-4 sm:p-5 rounded-2xl border border-white/40 shadow-xl flex items-center justify-between gap-4">
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 rounded-xl bg-gold-500/15 border border-gold-500/30 flex items-center justify-center text-gold-700 flex-shrink-0">
                      <Compass className="w-5 h-5" />
                    </div>
                    <div>
                      <div className="text-xs sm:text-sm font-bold text-walnut-900 font-serif">
                        {active.pill}
                      </div>
                      <div className="text-[11px] text-softgray">
                        Authentic solid teak, seasoned sheesham & handcrafted finishes
                      </div>
                    </div>
                  </div>

                  <button
                    onClick={() => finishOnboarding('/catalog')}
                    className="hidden sm:inline-flex items-center gap-1 text-xs font-bold text-gold-700 hover:text-gold-800 uppercase tracking-wider flex-shrink-0"
                  >
                    <span>View</span>
                    <ArrowRight className="w-3.5 h-3.5" />
                  </button>
                </div>
              </div>

              {/* Slide Thumbnail Preview Bar underneath the image */}
              <div className="mt-4 grid grid-cols-3 gap-3">
                {SLIDES.map((slide, idx) => (
                  <button
                    key={slide.id}
                    onClick={() => setCurrentSlide(idx)}
                    className={`p-2 rounded-xl text-left border transition-all flex items-center gap-2.5 ${
                      currentSlide === idx 
                        ? 'bg-white border-gold-500 shadow-md ring-2 ring-gold-500/20' 
                        : 'bg-white/60 border-walnut-200 hover:bg-white hover:border-walnut-300'
                    }`}
                  >
                    <img 
                      src={slide.image} 
                      alt="" 
                      className="w-10 h-10 rounded-lg object-cover flex-shrink-0" 
                    />
                    <div className="min-w-0 flex-1 hidden sm:block">
                      <div className={`text-[11px] font-bold truncate ${currentSlide === idx ? 'text-walnut-900' : 'text-softgray'}`}>
                        {slide.badge}
                      </div>
                      <div className="text-[10px] text-softgray truncate">
                        Slide 0{idx + 1}
                      </div>
                    </div>
                  </button>
                ))}
              </div>

            </div>
          </div>

        </div>
      </main>

      {/* 3. BOTTOM WEBSITE FOOTER BAR (Full Website Ratio) */}
      <footer className="w-full border-t border-walnut-200/60 bg-[#F7F2EB] py-4 px-4 sm:px-8 lg:px-12 text-xs text-walnut-600">
        <div className="max-w-7xl mx-auto flex flex-col sm:flex-row items-center justify-between gap-3 text-center sm:text-left">
          <div>
            © {new Date().getFullYear()} Glory Furniture Hub • Master Solid Wood Studio, Jubilee Hills, Hyderabad.
          </div>

          <div className="flex items-center gap-4 text-walnut-700 font-medium">
            <button onClick={() => finishOnboarding('/catalog')} className="hover:text-walnut-950">
              Browse Collection
            </button>
            <span className="text-walnut-300">•</span>
            <button onClick={() => finishOnboarding('/custom-request')} className="hover:text-walnut-950">
              Custom Order
            </button>
            <span className="text-walnut-300">•</span>
            <button onClick={() => finishOnboarding('/admin')} className="hover:text-walnut-950 font-semibold text-gold-700">
              Admin Portal
            </button>
          </div>
        </div>
      </footer>

    </div>
  )
}
