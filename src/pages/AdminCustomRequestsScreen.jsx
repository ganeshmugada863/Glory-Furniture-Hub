import React, { useState } from 'react'
import Header from '../components/common/Header'
import Badge from '../components/common/Badge'
import Toast from '../components/common/Toast'
import { useAppStore } from '../store/useAppStore'
import { Hammer, MessageSquare, Send } from 'lucide-react'

export default function AdminCustomRequestsScreen() {
  const { customRequests } = useAppStore()
  const [requests, setRequests] = useState(customRequests)
  const [adminNote, setAdminNote] = useState('')
  const [toastMessage, setToastMessage] = useState('')

  const handleStatusChange = (reqId, newStatus) => {
    setRequests(prev => prev.map(r => r.id === reqId ? { ...r, status: newStatus } : r))
    setToastMessage(`Request #${reqId} status updated to ${newStatus}.`)
  }

  return (
    <div className="min-h-screen bg-cream-100 pb-28">
      <Header title="Manage Custom Requests" showBack={true} />
      <Toast message={toastMessage} onClose={() => setToastMessage('')} />

      <div className="px-5 py-4 space-y-3 max-w-md mx-auto">
        {requests.map(r => (
          <div key={r.id} className="bg-white p-4 rounded-2xl border border-walnut-100 shadow-card space-y-3">
            <div className="flex items-center justify-between border-b border-cream-200 pb-2">
              <span className="font-mono font-bold text-xs text-walnut-800">#{r.id}</span>
              <select
                value={r.status}
                onChange={(e) => handleStatusChange(r.id, e.target.value)}
                className="text-xs font-bold bg-cream-100 border border-walnut-200 rounded-lg px-2 py-1 text-walnut-800"
              >
                <option value="Under Review">Under Review</option>
                <option value="Quoted">Quoted</option>
                <option value="In Production">In Production</option>
                <option value="Completed">Completed</option>
              </select>
            </div>

            <div>
              <h4 className="font-sans font-bold text-sm text-walnut-900">{r.furnitureType} ({r.wood})</h4>
              <p className="text-xs text-softgray mt-0.5">{r.description}</p>
              <span className="text-xs font-bold text-gold-600 block mt-1">Dimensions: {r.dimensions}</span>
            </div>

            {/* Reference Photos if uploaded */}
            {r.referenceImages && r.referenceImages.length > 0 && (
              <div className="flex gap-2 overflow-x-auto py-1">
                {r.referenceImages.map((img, idx) => (
                  <img key={idx} src={img} alt="Ref photo" className="w-14 h-14 object-cover rounded-lg border border-walnut-100" />
                ))}
              </div>
            )}

            <div className="pt-2 border-t border-cream-200 flex items-center justify-between text-xs">
              <span className="text-softgray">Target Budget: <strong className="text-walnut-800">{r.budget}</strong></span>
              <a
                href={`https://wa.me/?text=Hi%20there,%20providing%20craftsman%20quote%20for%20Glory%20Furniture%20custom%20spec%20%23${r.id}`}
                target="_blank"
                rel="noopener noreferrer"
                className="py-1.5 px-3 bg-mutedgreen text-white text-[11px] font-semibold rounded-xl flex items-center gap-1 active-tap"
              >
                <MessageSquare className="w-3.5 h-3.5" /> Quote via WhatsApp
              </a>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
