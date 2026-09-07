import React from 'react'
import { useNavigate } from 'react-router-dom'
import { Phone, Mail, MapPin, ShieldCheck, Truck, Award, Sparkles } from 'lucide-react'

export default function Footer() {
  const navigate = useNavigate()

  return (
    <footer className="w-full bg-white text-gray-800 border-t border-gray-200/80 mt-12 sm:mt-16 font-sans">
      
      {/* Top Value Badges Bar */}
      <div className="border-b border-gray-100 bg-[#FAFAFA] py-5 px-4 sm:px-6 lg:px-10">
        <div className="max-w-7xl mx-auto grid grid-cols-2 md:grid-cols-4 gap-4 sm:gap-6">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-lg bg-gray-900 text-white flex items-center justify-center flex-shrink-0">
              <Award className="w-4 h-4" />
            </div>
            <div>
              <h5 className="text-xs font-bold text-gray-950">100% Solid Timber</h5>
              <p className="text-[10px] text-gray-500">Pure Teak & Sheesham</p>
            </div>
          </div>

          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-lg bg-gray-900 text-white flex items-center justify-center flex-shrink-0">
              <ShieldCheck className="w-4 h-4" />
            </div>
            <div>
              <h5 className="text-xs font-bold text-gray-950">10-Year Warranty</h5>
              <p className="text-[10px] text-gray-500">Termite & Joint Protection</p>
            </div>
          </div>

          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-lg bg-gray-900 text-white flex items-center justify-center flex-shrink-0">
              <Truck className="w-4 h-4" />
            </div>
            <div>
              <h5 className="text-xs font-bold text-gray-950">Free White-Glove Setup</h5>
              <p className="text-[10px] text-gray-500">Direct In-Home Assembly</p>
            </div>
          </div>

          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-lg bg-gray-900 text-white flex items-center justify-center flex-shrink-0">
              <Sparkles className="w-4 h-4" />
            </div>
            <div>
              <h5 className="text-xs font-bold text-gray-950">Custom Dimensions</h5>
              <p className="text-[10px] text-gray-500">Tailored to Room Size</p>
            </div>
          </div>
        </div>
      </div>

      {/* Main Footer Links Container */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-10 py-10 sm:py-12">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-8 lg:gap-10">
          
          {/* Brand Info (2 Cols) */}
          <div className="lg:col-span-2 space-y-4">
            <div 
              onClick={() => navigate('/home')}
              className="flex items-center gap-2.5 cursor-pointer select-none"
            >
              <div className="w-10 h-10 rounded-lg overflow-hidden flex-shrink-0 shadow-2xs border border-gray-200">
                <img 
                  src="/images/logo_wood.jpg" 
                  alt="Glory Furniture" 
                  className="w-full h-full object-cover"
                />
              </div>
              <div className="flex flex-col">
                <span className="font-serif font-black text-xl text-gray-950 tracking-wider leading-none">
                  GLORY
                </span>
                <span className="text-[9px] font-bold tracking-[0.2em] text-gray-500 uppercase mt-0.5 leading-tight">
                  FURNITURE HUB
                </span>
              </div>
            </div>

            <p className="text-xs text-gray-600 leading-relaxed max-w-sm">
              Hyderabad's trusted solid wood studio crafting heirloom furniture from seasoned Burma teak, natural rosewood, and epoxy resin slabs. Built to last generations with traditional mortise-and-tenon joinery.
            </p>

            <div className="space-y-2 pt-1 text-xs text-gray-600">
              <div className="flex items-center gap-2">
                <Phone className="w-3.5 h-3.5 text-gray-900 flex-shrink-0" />
                <span>+91 98765 43210</span>
              </div>
              <div className="flex items-center gap-2">
                <Mail className="w-3.5 h-3.5 text-gray-900 flex-shrink-0" />
                <span>support@gloryfurniture.com</span>
              </div>
              <div className="flex items-center gap-2">
                <MapPin className="w-3.5 h-3.5 text-gray-900 flex-shrink-0" />
                <span>Banjara Hills & Jubilee Hills, Hyderabad, Telangana</span>
              </div>
            </div>
          </div>

          {/* Categories */}
          <div className="space-y-3">
            <h4 className="font-bold text-xs uppercase tracking-wider text-gray-950">Categories</h4>
            <ul className="space-y-2 text-xs text-gray-600">
              <li>
                <button onClick={() => navigate('/catalog?category=Cot%20%2F%20Wooden%20Bed')} className="hover:text-gray-950 transition-colors">
                  Beds & Cots
                </button>
              </li>
              <li>
                <button onClick={() => navigate('/catalog?category=Sofa%20Set')} className="hover:text-gray-950 transition-colors">
                  Sofa Sets & Diwans
                </button>
              </li>
              <li>
                <button onClick={() => navigate('/catalog?category=Dining%20Table')} className="hover:text-gray-950 transition-colors">
                  Dining Tables & Sets
                </button>
              </li>
              <li>
                <button onClick={() => navigate('/catalog?category=Dressing%20Table')} className="hover:text-gray-950 transition-colors">
                  Dressing Tables
                </button>
              </li>
              <li>
                <button onClick={() => navigate('/catalog?category=Dining%20Chairs')} className="hover:text-gray-950 transition-colors">
                  Dining Chairs
                </button>
              </li>
              <li>
                <button onClick={() => navigate('/catalog?category=Pooja%20Mandir')} className="hover:text-gray-950 transition-colors">
                  Pooja Mandir
                </button>
              </li>
            </ul>
          </div>

          {/* Customer Services */}
          <div className="space-y-3">
            <h4 className="font-bold text-xs uppercase tracking-wider text-gray-950">Customer Care</h4>
            <ul className="space-y-2 text-xs text-gray-600">
              <li>
                <button onClick={() => navigate('/custom-request')} className="hover:text-gray-950 transition-colors">
                  Custom Furniture Request
                </button>
              </li>
              <li>
                <button onClick={() => navigate('/bookings')} className="hover:text-gray-950 transition-colors">
                  Track Your Booking
                </button>
              </li>
              <li>
                <button onClick={() => navigate('/wishlist')} className="hover:text-gray-950 transition-colors">
                  Saved Wishlist
                </button>
              </li>
              <li>
                <button onClick={() => navigate('/profile')} className="hover:text-gray-950 transition-colors">
                  My Profile & Orders
                </button>
              </li>
              <li>
                <button onClick={() => navigate('/contact')} className="hover:text-gray-950 transition-colors">
                  Help & Consultation
                </button>
              </li>
            </ul>
          </div>

          {/* Quick Links */}
          <div className="space-y-3">
            <h4 className="font-bold text-xs uppercase tracking-wider text-gray-950">Studio</h4>
            <ul className="space-y-2 text-xs text-gray-600">
              <li>
                <button onClick={() => navigate('/home')} className="hover:text-gray-950 transition-colors">
                  Home
                </button>
              </li>
              <li>
                <button onClick={() => navigate('/catalog')} className="hover:text-gray-950 transition-colors">
                  Full Catalog
                </button>
              </li>
              <li>
                <button onClick={() => navigate('/custom-request')} className="hover:text-gray-950 transition-colors">
                  Bespoke Carpentry
                </button>
              </li>
              <li>
                <button onClick={() => navigate('/contact')} className="hover:text-gray-950 transition-colors">
                  Contact Workshop
                </button>
              </li>
            </ul>
          </div>

        </div>

        {/* Bottom Legal Bar */}
        <div className="mt-10 pt-6 border-t border-gray-100 flex flex-col sm:flex-row items-center justify-between gap-3 text-[11px] text-gray-500">
          <p>© 2026 Glory Furniture Hub. Handcrafted in Hyderabad, India.</p>
          <div className="flex items-center gap-4">
            <span className="hover:text-gray-800 cursor-pointer">Privacy Policy</span>
            <span>•</span>
            <span className="hover:text-gray-800 cursor-pointer">Terms of Service</span>
            <span>•</span>
            <span className="hover:text-gray-800 cursor-pointer">Warranty Policy</span>
          </div>
        </div>
      </div>

    </footer>
  )
}
