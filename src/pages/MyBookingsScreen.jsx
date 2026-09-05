import React, { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import Header from '../components/common/Header'
import Badge from '../components/common/Badge'
import { useAppStore } from '../store/useAppStore'
import { Package, ChevronRight, Clock, CheckCircle2, Hammer, Truck } from 'lucide-react'

export default function MyBookingsScreen() {
  const navigate = useNavigate()
  const { userBookings } = useAppStore()
  const [activeStatusTab, setActiveStatusTab] = useState('All')

  const statuses = ['All', 'Pending', 'Confirmed', 'In Production', 'Delivered']

  const filteredBookings = activeStatusTab === 'All'
    ? userBookings
    : userBookings.filter(b => b.status === activeStatusTab)

  const getStatusBadge = (status) => {
    switch (status) {
      case 'In Production':
        return <Badge variant="warning" icon={Hammer}>In Production</Badge>
      case 'Delivered':
        return <Badge variant="success" icon={CheckCircle2}>Delivered</Badge>
      case 'Confirmed':
        return <Badge variant="info" icon={Truck}>Confirmed</Badge>
      default:
        return <Badge variant="default" icon={Clock}>Pending</Badge>
    }
  }

  return (
    <div className="min-h-screen bg-cream-100 pb-28">
      <Header title="My Bookings" showBack={true} />

      {/* Filter Tabs */}
      <div className="px-5 py-3 flex gap-2 overflow-x-auto no-scrollbar bg-white border-b border-walnut-100">
        {statuses.map(st => (
          <button
            key={st}
            onClick={() => setActiveStatusTab(st)}
            className={`px-3 py-1.5 rounded-full text-xs font-medium whitespace-nowrap active-tap ${
              activeStatusTab === st
                ? 'bg-walnut-500 text-gold-400 font-semibold shadow-sm'
                : 'bg-cream-100 text-walnut-700'
            }`}
          >
            {st}
          </button>
        ))}
      </div>

      <div className="px-5 py-4">
        {filteredBookings.length > 0 ? (
          <div className="space-y-3">
            {filteredBookings.map(b => (
              <div
                key={b.id}
                onClick={() => navigate(`/bookings/${b.id}`)}
                className="bg-white p-4 rounded-2xl border border-walnut-100 shadow-card cursor-pointer hover:shadow-warm active-tap transition-all"
              >
                <div className="flex items-center justify-between pb-2 border-b border-cream-200 mb-3">
                  <span className="font-mono font-bold text-xs text-walnut-800">#{b.id}</span>
                  {getStatusBadge(b.status)}
                </div>

                <div className="flex items-center gap-3">
                  <img src={b.image} alt={b.productName} className="w-16 h-16 rounded-xl object-cover bg-cream-200" />
                  <div className="flex-1 min-w-0">
                    <h4 className="font-serif font-bold text-xs text-walnut-900 truncate">{b.productName}</h4>
                    <p className="text-[11px] text-softgray">Est. Delivery: {b.deliveryDate}</p>
                    <span className="font-sans font-bold text-xs text-gold-600 block mt-1">₹{Number(b.price || 0).toLocaleString('en-IN')}</span>
                  </div>
                  <ChevronRight className="w-4 h-4 text-softgray" />
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="py-16 text-center">
            <Package className="w-12 h-12 text-softgray mx-auto mb-2" />
            <h4 className="font-serif font-bold text-sm text-walnut-800">No bookings in this category</h4>
            <p className="text-xs text-softgray mt-1">Book ready-made furniture or check your custom request quotes.</p>
          </div>
        )}
      </div>
    </div>
  )
}
