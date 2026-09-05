import React from 'react'
import Header from '../components/common/Header'
import { Sparkles, ShieldCheck, Heart, Award } from 'lucide-react'

export default function AboutScreen() {
  return (
    <div className="min-h-screen bg-cream-100 pb-28">
      <Header title="Our Story & Craft" showBack={true} />

      <div className="px-5 py-4 space-y-4 max-w-md mx-auto">
        <div className="relative rounded-3xl overflow-hidden aspect-video shadow-warm border border-walnut-200">
          <img
            src="https://images.unsplash.com/photo-1581092160607-ee22621dd758?auto=format&fit=crop&w=800&q=80"
            alt="Craftsman Studio"
            className="w-full h-full object-cover"
          />
          <div className="absolute inset-0 bg-gradient-to-t from-walnut-900/80 to-transparent flex items-end p-4">
            <span className="text-white font-serif font-bold text-lg">Three Generations of Master Woodworking</span>
          </div>
        </div>

        <div className="bg-white p-5 rounded-3xl border border-walnut-100 shadow-card space-y-3">
          <h3 className="font-serif font-bold text-lg text-walnut-800">Our Craftsmanship Philosophy</h3>
          <p className="text-xs text-softgray leading-relaxed">
            Founded as a family workshop, <strong>Glory Furniture Hub</strong> blends traditional hand-carving techniques with modern ergonomic design. We sustainably harvest native hardwoods—Walnut, Teak, Mahogany, and Oak—hand-finishing each piece with non-toxic organic oils.
          </p>
        </div>

        <div className="grid grid-cols-2 gap-3">
          <div className="bg-white p-4 rounded-2xl border border-walnut-100 text-center">
            <ShieldCheck className="w-6 h-6 text-gold-600 mx-auto mb-1" />
            <h4 className="font-serif font-bold text-xs text-walnut-800">100% Solid Wood</h4>
            <p className="text-[10px] text-softgray">Zero particle board</p>
          </div>
          <div className="bg-white p-4 rounded-2xl border border-walnut-100 text-center">
            <Award className="w-6 h-6 text-gold-600 mx-auto mb-1" />
            <h4 className="font-serif font-bold text-xs text-walnut-800">Master Joinery</h4>
            <p className="text-[10px] text-softgray">Mortise & Tenon</p>
          </div>
        </div>
      </div>
    </div>
  )
}
