import React, { useState } from 'react'
import Header from '../components/common/Header'
import Button from '../components/common/Button'
import { ChevronDown, Sparkles } from 'lucide-react'
import { useAppStore } from '../store/useAppStore'

const FAQS = [
  {
    q: 'How does the booking reservation process work?',
    a: 'When you book a ready-made piece, you place an order reservation. Our studio master reviews your address and delivery date requirements and contacts you to confirm white-glove logistics.'
  },
  {
    q: 'Can I request custom wood species or dimensions?',
    a: 'Yes! Navigate to Custom Furniture Request, upload reference photos or dimensions, and our team will provide a 3D blueprint & price quote within 24 hours.'
  },
  {
    q: 'What wood species do you work with?',
    a: 'We work primarily with kiln-dried American Walnut, Grade-A Teak, White Oak, Honduran Mahogany, and Eastern Pine.'
  },
  {
    q: 'How does GloryAI help me?',
    a: 'GloryAI is your personal furniture advisor. It answers questions about durability, recommends pieces based on room dimensions, and helps you fill custom specs.'
  }
]

export default function FAQScreen() {
  const { openAIChat } = useAppStore()
  const [openIdx, setOpenIdx] = useState(0)

  return (
    <div className="min-h-screen bg-cream-100 pb-28">
      <Header title="Help & FAQ" showBack={true} />

      <div className="px-5 py-4 space-y-3 max-w-md mx-auto">
        {FAQS.map((faq, idx) => (
          <div key={idx} className="bg-white rounded-2xl border border-walnut-100 shadow-card overflow-hidden">
            <button
              onClick={() => setOpenIdx(openIdx === idx ? -1 : idx)}
              className="w-full p-4 flex items-center justify-between text-left font-serif font-bold text-xs text-walnut-900"
            >
              <span>{faq.q}</span>
              <ChevronDown className={`w-4 h-4 text-gold-600 transition-transform ${openIdx === idx ? 'rotate-180' : ''}`} />
            </button>
            {openIdx === idx && (
              <div className="px-4 pb-4 text-xs text-softgray border-t border-cream-200 pt-2 leading-relaxed">
                {faq.a}
              </div>
            )}
          </div>
        ))}

        <div className="pt-4 text-center space-y-2">
          <p className="text-xs text-softgray">Have a specific design question?</p>
          <Button
            variant="accent"
            size="md"
            onClick={() => openAIChat()}
            icon={Sparkles}
            className="mx-auto"
          >
            Ask GloryAI Furniture Advisor
          </Button>
        </div>
      </div>
    </div>
  )
}
