import React from 'react'
import { useNavigate } from 'react-router-dom'
import Header from '../components/common/Header'
import Badge from '../components/common/Badge'
import Button from '../components/common/Button'
import { useAppStore } from '../store/useAppStore'
import { Hammer, Plus } from 'lucide-react'

export default function MyRequestsScreen() {
  const navigate = useNavigate()
  const { customRequests } = useAppStore()

  return (
    <div className="min-h-screen bg-cream-100 pb-28">
      <Header title="My Custom Requests" showBack={true} />

      <div className="px-5 py-4">
        {customRequests.length > 0 ? (
          <div className="space-y-3">
            {customRequests.map(req => (
              <div
                key={req.id}
                className="bg-white p-4 rounded-2xl border border-walnut-100 shadow-card flex flex-col justify-between"
              >
                <div className="flex items-center justify-between pb-2 border-b border-cream-200 mb-2">
                  <span className="font-mono font-bold text-xs text-walnut-800">#{req.id}</span>
                  <Badge variant="warning">{req.status}</Badge>
                </div>

                <h4 className="font-serif font-bold text-sm text-walnut-900 mb-1">{req.furnitureType}</h4>
                <p className="text-xs text-softgray mb-2">{req.description}</p>

                <div className="flex items-center justify-between text-[11px] pt-2 border-t border-cream-200 text-softgray">
                  <span>Wood: <strong className="text-walnut-800">{req.wood}</strong></span>
                  <span>Budget: <strong className="text-gold-600">{req.budget}</strong></span>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="py-16 text-center">
            <Hammer className="w-12 h-12 text-softgray mx-auto mb-2" />
            <h4 className="font-serif font-bold text-sm text-walnut-800">No custom furniture requests yet</h4>
            <p className="text-xs text-softgray mt-1 mb-4">Request a custom dining table, bed, or wardrobe handcrafted to your dimensions.</p>
            <Button
              variant="primary"
              size="md"
              onClick={() => navigate('/custom-request')}
              icon={Plus}
              className="mx-auto"
            >
              Request Custom Piece
            </Button>
          </div>
        )}
      </div>
    </div>
  )
}
