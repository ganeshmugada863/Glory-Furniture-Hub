import React, { useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import Header from '../components/common/Header'
import Badge from '../components/common/Badge'
import Button from '../components/common/Button'
import Toast from '../components/common/Toast'
import { useAppStore } from '../store/useAppStore'
import { CheckCircle2, Hammer, Truck, Package, MessageSquare, AlertTriangle } from 'lucide-react'

export default function BookingDetailScreen() {
  const { bookingId } = useParams()
  const navigate = useNavigate()
  const { userBookings, cancelBooking } = useAppStore()
  const [toastMessage, setToastMessage] = useState('')

  const booking = userBookings.find(b => b.id === bookingId) || (userBookings.length > 0 ? userBookings[0] : null)

  if (!booking) {
    return (
      <div className="min-h-screen bg-cream-100 flex flex-col items-center justify-center p-6 text-center">
        <Package className="w-12 h-12 text-softgray mb-3" />
        <h3 className="font-sans font-bold text-base text-walnut-900">No Booking Found</h3>
        <p className="text-xs text-softgray mt-1">This reservation reference does not exist or has been removed.</p>
        <Button onClick={() => navigate('/home')} variant="primary" size="sm" className="mt-4">Back to Home</Button>
      </div>
    )
  }

  const handleCancel = () => {
    if (confirm('Are you sure you want to cancel this pending booking?')) {
      cancelBooking(booking.id)
      setToastMessage('Reservation cancelled successfully.')
    }
  }

  const steps = [
    { title: 'Placed', icon: Package, done: true },
    { title: 'Confirmed', icon: CheckCircle2, done: booking?.status !== 'Pending' && booking?.status !== 'Cancelled' },
    { title: 'In Production', icon: Hammer, done: booking?.status === 'In Production' || booking?.status === 'Delivered' },
    { title: 'Delivered', icon: Truck, done: booking?.status === 'Delivered' }
  ]

  return (
    <div className="min-h-screen bg-cream-100 pb-28">
      <Header title={`Booking #${booking?.id || ''}`} showBack={true} />
      <Toast message={toastMessage} onClose={() => setToastMessage('')} />

      <div className="px-5 py-4 space-y-4 max-w-md mx-auto">
        {/* Status Tracker */}
        <div className="bg-white p-4 rounded-2xl border border-walnut-100 shadow-card">
          <div className="flex items-center justify-between mb-4">
            <span className="text-xs font-semibold text-softgray">Current Status:</span>
            <Badge variant={booking?.status === 'Delivered' ? 'success' : booking?.status === 'Cancelled' ? 'danger' : 'warning'}>
              {booking?.status}
            </Badge>
          </div>

          {/* Progress Step Bar */}
          {booking?.status !== 'Cancelled' ? (
            <div className="grid grid-cols-4 gap-1 text-center relative pt-2">
              {steps.map((st, idx) => {
                const Icon = st.icon
                return (
                  <div key={idx} className="flex flex-col items-center">
                    <div className={`w-8 h-8 rounded-full flex items-center justify-center mb-1 text-xs font-bold ${
                      st.done ? 'bg-walnut-500 text-gold-400 ring-2 ring-gold-500/30' : 'bg-cream-200 text-softgray'
                    }`}>
                      <Icon className="w-4 h-4" />
                    </div>
                    <span className={`text-[9px] font-semibold leading-tight ${st.done ? 'text-walnut-800' : 'text-softgray'}`}>
                      {st.title}
                    </span>
                  </div>
                )
              })}
            </div>
          ) : (
            <div className="p-3 bg-dustyrose/10 border border-dustyrose/30 rounded-xl text-center text-xs text-dustyrose font-semibold">
              This reservation has been cancelled.
            </div>
          )}
        </div>

        {/* Product Details */}
        <div className="bg-white p-4 rounded-2xl border border-walnut-100 shadow-card flex items-center gap-3">
          <img src={booking?.image} alt={booking?.productName} className="w-16 h-16 rounded-xl object-cover bg-cream-200" />
          <div className="flex-1 min-w-0">
            <h4 className="font-sans font-bold text-xs text-walnut-900 truncate">{booking?.productName}</h4>
            <span className="text-[11px] text-softgray block">Qty: {booking?.quantity}</span>
            <span className="font-sans font-bold text-xs text-gold-600 block mt-0.5">₹{Number(booking?.price || 0).toLocaleString('en-IN')}</span>
          </div>
        </div>

        {/* Delivery & Address Information */}
        <div className="bg-white p-4 rounded-2xl border border-walnut-100 shadow-card space-y-2 text-xs">
          <h4 className="font-sans font-bold text-xs text-walnut-800 uppercase tracking-wider mb-2">
            Delivery Specification
          </h4>
          <div className="flex justify-between border-b border-cream-200 py-1">
            <span className="text-softgray">Estimated Delivery:</span>
            <span className="font-bold text-walnut-900">{booking?.deliveryDate}</span>
          </div>
          <div className="flex justify-between border-b border-cream-200 py-1">
            <span className="text-softgray">Destination Address:</span>
            <span className="font-medium text-walnut-900 text-right max-w-[180px]">{booking?.deliveryAddress}</span>
          </div>
          {booking?.customizationNotes && (
            <div className="py-1">
              <span className="text-softgray block">Customization Notes:</span>
              <p className="text-walnut-800 font-medium mt-0.5">{booking.customizationNotes}</p>
            </div>
          )}
        </div>

        {/* WhatsApp Direct Studio Support */}
        <a
          href={`https://wa.me/?text=Hi%20Glory%20Furniture%20Studio,%20inquiring%20about%20booking%20%23${booking?.id}`}
          target="_blank"
          rel="noopener noreferrer"
          className="w-full py-3.5 bg-mutedgreen hover:bg-mutedgreen/90 text-white font-semibold text-xs rounded-2xl active-tap flex items-center justify-center gap-2 shadow-sm"
        >
          <MessageSquare className="w-4 h-4" /> Speak with Studio Master via WhatsApp
        </a>

        {/* Cancel Booking Option */}
        {booking?.status === 'Pending' && (
          <Button
            variant="outline"
            size="md"
            onClick={handleCancel}
            className="w-full border-dustyrose/40 text-dustyrose hover:bg-dustyrose/10"
            icon={AlertTriangle}
          >
            Cancel Reservation
          </Button>
        )}
      </div>
    </div>
  )
}
