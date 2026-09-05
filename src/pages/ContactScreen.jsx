import React from 'react'
import Header from '../components/common/Header'
import Button from '../components/common/Button'
import { Phone, Mail, MapPin, MessageSquare, Clock } from 'lucide-react'

export default function ContactScreen() {
  return (
    <div className="min-h-screen bg-cream-100 pb-28">
      <Header title="Contact Studio" showBack={true} />

      <div className="px-5 py-4 space-y-4 max-w-md mx-auto">
        <div className="bg-white p-5 rounded-3xl border border-walnut-100 shadow-card space-y-3">
          <h3 className="font-serif font-bold text-base text-walnut-800">Glory Furniture Workshop</h3>
          
          <div className="flex items-center gap-3 text-xs text-softgray">
            <Phone className="w-4 h-4 text-gold-600" />
            <a href="tel:+15552345678" className="text-walnut-800 font-semibold hover:underline">+1 (555) 234-5678</a>
          </div>

          <div className="flex items-center gap-3 text-xs text-softgray">
            <Mail className="w-4 h-4 text-gold-600" />
            <a href="mailto:craftsmen@gloryfurniture.com" className="text-walnut-800 font-semibold hover:underline">craftsmen@gloryfurniture.com</a>
          </div>

          <div className="flex items-center gap-3 text-xs text-softgray">
            <MapPin className="w-4 h-4 text-gold-600" />
            <span>124 Heritage Artisan Way, Studio 4, NY 10001</span>
          </div>

          <div className="flex items-center gap-3 text-xs text-softgray">
            <Clock className="w-4 h-4 text-gold-600" />
            <span>Mon - Sat: 9:00 AM - 6:00 PM EST</span>
          </div>
        </div>

        {/* Embedded Google Maps Location Frame */}
        <div className="bg-white rounded-3xl border border-walnut-100 shadow-card overflow-hidden aspect-video">
          <iframe
            title="Workshop Location"
            src="https://maps.google.com/maps?q=New%20York&t=&z=13&ie=UTF8&iwloc=&output=embed"
            className="w-full h-full border-0"
            allowFullScreen=""
            loading="lazy"
          />
        </div>

        {/* WhatsApp direct click to chat */}
        <a
          href="https://wa.me/?text=Hello%20Glory%20Furniture%20Studio,%20inquiring%20about%20handcrafted%20pieces."
          target="_blank"
          rel="noopener noreferrer"
          className="w-full py-4 bg-mutedgreen hover:bg-mutedgreen/90 text-white font-semibold text-xs rounded-2xl active-tap flex items-center justify-center gap-2 shadow-sm"
        >
          <MessageSquare className="w-4 h-4" /> Direct WhatsApp Chat with Craftsman
        </a>
      </div>
    </div>
  )
}
