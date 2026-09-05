import { supabase, isSupabaseConfigured } from '../lib/supabase'
import { MOCK_PRODUCTS } from '../data/mockData'

export const aiService = {
  // Send message to GloryAI assistant
  async sendMessage({ messages, productContext, userPreferences }) {
    if (isSupabaseConfigured) {
      try {
        const { data, error } = await supabase.functions.invoke('glory-ai-proxy', {
          body: { messages, productContext, userPreferences }
        })
        if (!error && data?.choices?.[0]?.message?.content) {
          return { text: data.choices[0].message.content, error: null }
        }
      } catch (err) {
        console.warn('Edge function invoke failed, utilizing local intelligent advice fallback.', err)
      }
    }

    // Local Intelligent Recommendation Fallback
    const lastUserMsg = messages[messages.length - 1]?.content || ''
    const lower = lastUserMsg.toLowerCase()

    let text = "That's a fantastic choice! Our studio craftsmen work primarily with premium kiln-dried American Walnut, Teak, and Honduran Mahogany. Would you like me to recommend specific matching pieces for your room?"
    let recommendedProduct = null

    if (lower.includes('living') || lower.includes('chair') || lower.includes('sofa')) {
      text = "For living room spaces, our **Artisan Linen Velvet Lounge Chair** ($640) paired with the **Minimalist Oak Credenza** creates a warm, opulent atmosphere."
      recommendedProduct = MOCK_PRODUCTS.find(p => p.id === 3)
    } else if (lower.includes('bed') || lower.includes('bedroom')) {
      text = "Our bestseller is the **Royal Walnut King Bed** ($1,250)! It features hand-carved solid walnut and posture slat support."
      recommendedProduct = MOCK_PRODUCTS.find(p => p.id === 1)
    } else if (lower.includes('dining') || lower.includes('table')) {
      text = "Our **Heritage Teak Dining Table** ($980) seats up to 8 guests and features natural oil-rich teak with mortise-and-tenon joinery."
      recommendedProduct = MOCK_PRODUCTS.find(p => p.id === 2)
    } else if (lower.includes('budget') || lower.includes('500') || lower.includes('price')) {
      text = "For under $500, check out the **Solstice Teak Outdoor Bench** ($420) or speak with us to craft a custom accent piece!"
      recommendedProduct = MOCK_PRODUCTS.find(p => p.id === 5)
    } else if (lower.includes('custom') || lower.includes('request') || lower.includes('design')) {
      text = "I can guide you step-by-step to design custom furniture! Tap below to open our Custom Furniture Request form with pre-filled specifications."
    }

    return { text, product: recommendedProduct, error: null }
  },

  // Save chat history for authenticated user
  async saveChatMessage({ userId, sender, text, productId }) {
    if (!isSupabaseConfigured || !userId) return

    await supabase.from('ai_chat_messages').insert([
      {
        user_id: userId,
        sender,
        text,
        product_id: productId || null
      }
    ])
  }
}
