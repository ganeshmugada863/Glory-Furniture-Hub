import React, { useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import Button from '../components/common/Button'
import Toast from '../components/common/Toast'
import { useAppStore } from '../store/useAppStore'
import { CheckCircle2, Copy, ArrowRight, Home, MapPin, Receipt, ShieldCheck, Truck, Phone } from 'lucide-react'

export default function BookingConfirmationScreen() {
  const { bookingId } = useParams()
  const navigate = useNavigate()
  const { userBookings } = useAppStore()
  const [toastMessage, setToastMessage] = useState('')

  const booking = userBookings.find(b => b.id === bookingId) || userBookings[0]

  const copyReference = () => {
    navigator.clipboard.writeText(bookingId)
    setToastMessage(`Booking reference #${bookingId} copied!`)
  }

  return (
    <div className="min-h-screen bg-[#FDFBF7] flex flex-col items-center justify-center p-4 sm:p-6 text-center max-w-xl mx-auto font-sans">
      <Toast message={toastMessage} onClose={() => setToastMessage('')} />

      {/* Animated Checkmark Badge */}
      <div className="w-20 h-20 rounded-full bg-emerald-100 text-emerald-700 flex items-center justify-center mb-4 ring-8 ring-emerald-500/20 shadow-sm">
        <CheckCircle2 className="w-10 h-10 text-emerald-700" />
      </div>

      <span className="text-xs font-bold uppercase tracking-widest text-gold-600 mb-1">
        Order & Reservation Confirmed!
      </span>

      <h2 className="font-sans font-bold text-2xl sm:text-3xl text-walnut-900 tracking-wide mb-2">
        Thank You for Your Order
      </h2>

      <p className="text-xs text-softgray max-w-md leading-relaxed mb-5">
        Your handcrafted furniture commission has been officially confirmed at Glory Furniture Hub. A commercial GST Tax Invoice and 15-Year Teak Warranty Certificate have been recorded.
      </p>

      {/* Order & Piece Summary Box */}
      <div className="bg-white p-5 rounded-3xl border border-walnut-200/80 shadow-card w-full mb-6 text-left space-y-4">
        
        {/* Header IDs */}
        <div className="flex items-center justify-between bg-cream-100 p-3 rounded-2xl border border-walnut-200/70">
          <div>
            <span className="text-[10px] uppercase font-bold text-softgray block">Order Reference ID</span>
            <span className="font-mono font-bold text-sm text-walnut-900">#{bookingId}</span>
          </div>

          <div className="text-right">
            <span className="text-[10px] uppercase font-bold text-softgray block">Tax Invoice Reference</span>
            <span className="font-mono font-bold text-xs text-gold-700">{booking?.invoiceId || 'INV-2026-001'}</span>
          </div>

          <button onClick={copyReference} className="p-2 text-walnut-700 hover:text-gold-700 active-tap cursor-pointer" title="Copy Order ID">
            <Copy className="w-4 h-4" />
          </button>
        </div>

        {/* Item Row if found */}
        {booking && (
          <div className="flex items-center gap-3.5 pt-1 border-b border-cream-200 pb-3">
            {booking.image && (
              <img
                src={booking.image}
                alt={booking.productName}
                className="w-16 h-16 rounded-xl object-cover bg-cream-200 border border-walnut-200 shrink-0"
              />
            )}
            <div className="flex-1 min-w-0 text-xs space-y-0.5">
              <strong className="font-sans font-bold text-sm text-walnut-900 block truncate">
                {booking.productName}
              </strong>
              <div className="text-softgray text-[11px]">
                {booking.bedSize ? `Size: ${booking.bedSize} • ` : ''}
                {booking.woodType || 'Solid Burma Teak Wood'}
              </div>
              <div className="text-[11px] font-bold text-walnut-900 pt-0.5">
                Qty: {booking.quantity} • Total: <span className="text-gold-700 font-sans">₹{Number(booking.price * booking.quantity).toLocaleString('en-IN')}</span>
              </div>
            </div>
          </div>
        )}

        {/* Delivery & Payment Specification */}
        <div className="space-y-2 text-xs">
          <div className="flex items-start gap-2 text-walnut-800">
            <MapPin className="w-4 h-4 text-gold-600 shrink-0 mt-0.5" />
            <div>
              <span className="text-softgray text-[11px] block">Delivering To:</span>
              <strong className="text-walnut-900">{booking?.fullName || 'Customer'}</strong>
              <p className="text-softgray text-[11px] mt-0.5">{booking?.deliveryAddress}</p>
            </div>
          </div>

          <div className="flex items-center justify-between pt-2 border-t border-cream-200 text-[11px]">
            <span className="text-softgray">Payment Method:</span>
            <strong className="text-walnut-900">{booking?.paymentMethod || 'Cash on Delivery'}</strong>
          </div>

          <div className="flex items-center justify-between text-[11px]">
            <span className="text-softgray">Estimated Delivery Date:</span>
            <strong className="text-emerald-700">{booking?.deliveryDate || '5 - 7 Business Days'}</strong>
          </div>
        </div>

        {/* What happens next */}
        <div className="pt-3 border-t border-cream-200 space-y-1.5 text-[11px] text-softgray">
          <span className="font-bold text-walnut-900 block">Next Steps:</span>
          <p>• Our studio supervisor will call {booking?.phone ? `at ${booking.phone}` : ''} to confirm delivery schedule.</p>
          <p>• 15-Year Solid Burma Teak Warranty certificate will be handed over during white-glove assembly.</p>
        </div>

      </div>

      {/* CTA Buttons */}
      <div className="w-full space-y-2.5">
        <Button
          variant="primary"
          size="lg"
          onClick={() => navigate(`/bookings/${bookingId}`)}
          className="w-full bg-walnut-900 text-gold-400 font-bold py-3.5"
          icon={ArrowRight}
        >
          Track My Order
        </Button>

        <Button
          variant="secondary"
          size="md"
          onClick={() => navigate('/home')}
          className="w-full"
          icon={Home}
        >
          Back to Catalog & Home
        </Button>
      </div>
    </div>
  )
}

