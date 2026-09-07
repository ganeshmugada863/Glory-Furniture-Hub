import React, { useState } from 'react'
import Header from '../components/common/Header'
import Badge from '../components/common/Badge'
import Toast from '../components/common/Toast'
import { useAppStore } from '../store/useAppStore'
import { Package, MessageSquare, CheckCircle2 } from 'lucide-react'

export default function AdminBookingsScreen() {
  const { userBookings } = useAppStore()
  const [bookings, setBookings] = useState(userBookings)
  const [activeTab, setActiveTab] = useState('All')
  const [toastMessage, setToastMessage] = useState('')

  const statuses = ['All', 'Pending', 'Confirmed', 'In Production', 'Delivered', 'Cancelled']

  const handleStatusChange = (bookingId, newStatus) => {
    setBookings(prev => prev.map(b => b.id === bookingId ? { ...b, status: newStatus } : b))
    setToastMessage(`Booking #${bookingId} status updated to ${newStatus}.`)
  }

  const filteredBookings = activeTab === 'All'
    ? bookings
    : bookings.filter(b => b.status === activeTab)

  return (
    <div className="min-h-screen bg-cream-100 pb-28">
      <Header title="Manage Customer Bookings" showBack={true} />
      <Toast message={toastMessage} onClose={() => setToastMessage('')} />

      {/* Filter Tabs */}
      <div className="px-5 py-3 flex gap-2 overflow-x-auto no-scrollbar bg-white border-b border-walnut-100">
        {statuses.map(st => (
          <button
            key={st}
            onClick={() => setActiveTab(st)}
            className={`px-3 py-1.5 rounded-full text-xs font-medium whitespace-nowrap active-tap ${
              activeTab === st
                ? 'bg-walnut-500 text-gold-400 font-semibold shadow-sm'
                : 'bg-cream-100 text-walnut-700'
            }`}
          >
            {st}
          </button>
        ))}
      </div>

      <div className="px-5 py-4 space-y-3 max-w-md mx-auto">
        {filteredBookings.map(b => (
          <div key={b.id} className="bg-white p-4 rounded-2xl border border-walnut-100 shadow-card space-y-3">
            <div className="flex items-center justify-between border-b border-cream-200 pb-2">
              <span className="font-mono font-bold text-xs text-walnut-800">#{b.id}</span>
              <div className="flex items-center gap-2">
                <select
                  value={b.status}
                  onChange={(e) => handleStatusChange(b.id, e.target.value)}
                  className="text-xs font-bold bg-cream-100 border border-walnut-200 rounded-lg px-2 py-1 text-walnut-800"
                >
                  <option value="Pending">Pending</option>
                  <option value="Confirmed">Confirmed</option>
                  <option value="In Production">In Production</option>
                  <option value="Delivered">Delivered</option>
                  <option value="Cancelled">Cancelled</option>
                </select>
              </div>
            </div>

            <div className="flex items-center gap-3">
              <img src={b.image} alt="" className="w-16 h-16 rounded-xl object-cover bg-cream-200 border border-walnut-100" />
              <div className="flex-1 min-w-0">
                <h5 className="font-sans font-bold text-xs text-walnut-900 truncate">{b.productName}</h5>
                {b.bedSize && (
                  <span className="text-[11px] font-semibold text-walnut-800 bg-cream-100 px-2 py-0.5 rounded inline-block mt-0.5">
                    Size: {b.bedSize}
                  </span>
                )}
                <span className="text-[11px] text-softgray block mt-0.5">
                  Delivery Date: <strong className="text-walnut-800">{b.deliveryDate}</strong>
                </span>
                <span className="font-sans font-bold text-xs text-gold-600 block mt-0.5">
                  ₹{Number(b.price).toLocaleString('en-IN')}
                </span>
              </div>
            </div>

            <div className="pt-2 border-t border-cream-200 space-y-1 text-xs">
              <div className="flex items-center justify-between">
                <span className="text-softgray">Customer:</span>
                <span className="font-bold text-walnut-900">{b.fullName || 'Customer Order'}</span>
              </div>
              {b.phone && (
                <div className="flex items-center justify-between">
                  <span className="text-softgray">Phone:</span>
                  <span className="font-medium text-walnut-800">{b.phone}</span>
                </div>
              )}
              <div className="flex items-center justify-between">
                <span className="text-softgray">Delivery Address:</span>
                <span className="font-medium text-walnut-800 text-right truncate max-w-[200px]">{b.deliveryAddress}</span>
              </div>
            </div>

            <div className="pt-1 flex items-center justify-end gap-2">
              <a
                href={`https://wa.me/?text=Hi%20there,%20contacting%20regarding%20Glory%20Furniture%20booking%20%23${b.id}`}
                target="_blank"
                rel="noopener noreferrer"
                className="py-1.5 px-3 bg-mutedgreen text-white text-[11px] font-semibold rounded-xl flex items-center gap-1 active-tap"
              >
                <MessageSquare className="w-3.5 h-3.5" /> WhatsApp Customer
              </a>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
