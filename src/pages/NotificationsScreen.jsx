import React from 'react'
import { useNavigate } from 'react-router-dom'
import Header from '../components/common/Header'
import Badge from '../components/common/Badge'
import { useAppStore } from '../store/useAppStore'
import { Bell, CheckCheck, Package, Hammer } from 'lucide-react'

export default function NotificationsScreen() {
  const navigate = useNavigate()
  const { notifications, markNotificationAsRead, markAllNotificationsRead } = useAppStore()

  return (
    <div className="min-h-screen bg-cream-100 pb-28">
      <Header title="Notifications" showBack={true} />

      <div className="px-5 py-3 flex justify-between items-center bg-white border-b border-walnut-100">
        <span className="text-xs text-softgray">Stay updated on studio activities</span>
        <button
          onClick={markAllNotificationsRead}
          className="text-xs font-semibold text-gold-600 hover:underline flex items-center gap-1 active-tap"
        >
          <CheckCheck className="w-3.5 h-3.5" /> Mark all read
        </button>
      </div>

      <div className="px-5 py-4 space-y-3 max-w-md mx-auto">
        {notifications.length > 0 ? (
          notifications.map(n => (
            <div
              key={n.id}
              onClick={() => {
                markNotificationAsRead(n.id)
                if (n.type === 'booking') navigate(`/bookings/${n.targetId}`)
                if (n.type === 'request') navigate('/profile/requests')
              }}
              className={`p-4 rounded-2xl border shadow-card cursor-pointer transition-all active-tap ${
                n.read ? 'bg-white border-walnut-100' : 'bg-cream-200/90 border-gold-500/40 ring-1 ring-gold-500/20'
              }`}
            >
              <div className="flex items-start justify-between">
                <div className="flex items-center gap-2">
                  {n.type === 'booking' ? (
                    <Package className="w-4 h-4 text-walnut-600" />
                  ) : (
                    <Hammer className="w-4 h-4 text-gold-600" />
                  )}
                  <h4 className="font-sans font-bold text-xs text-walnut-900">{n.title}</h4>
                </div>
                <div className="flex items-center gap-1.5">
                  {!n.read && <Badge variant="warning">New</Badge>}
                  <span className="text-[10px] text-softgray">{n.timestamp}</span>
                </div>
              </div>
              <p className="text-xs text-softgray mt-1.5 leading-relaxed">{n.description}</p>
            </div>
          ))
        ) : (
          <div className="py-16 text-center">
            <Bell className="w-12 h-12 text-softgray mx-auto mb-2" />
            <h4 className="font-sans font-bold text-sm text-walnut-800">No notifications yet</h4>
          </div>
        )}
      </div>
    </div>
  )
}
