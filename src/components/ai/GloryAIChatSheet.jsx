import React, { useState, useEffect, useRef } from 'react'
import { X, Send, Sparkles, RefreshCw, ShoppingBag, Mic, PlusCircle } from 'lucide-react'
import { useAppStore } from '../../store/useAppStore'
import { aiService } from '../../services/aiService'
import { useNavigate } from 'react-router-dom'

export default function GloryAIChatSheet() {
  const navigate = useNavigate()
  const { isAIChatOpen, closeAIChat, aiChatContext, user } = useAppStore()
  const [messages, setMessages] = useState([])
  const [inputValue, setInputValue] = useState('')
  const [isTyping, setIsTyping] = useState(false)
  const [isListening, setIsListening] = useState(false)
  const chatEndRef = useRef(null)

  useEffect(() => {
    if (isAIChatOpen && messages.length === 0) {
      const initialGreeting = aiChatContext 
        ? `Hello! I see you are exploring **${aiChatContext.name || 'this piece'}**. How can I assist with dimensions, finish options, or styling recommendations?`
        : `Welcome to Glory Furniture Hub! I am **GloryAI**, your personal handcrafted furniture advisor. How can I help you customize your dream space today?`

      setMessages([
        {
          id: 'welcome',
          sender: 'ai',
          text: initialGreeting,
          timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
          suggestions: [
            'Recommend living room pieces',
            'What finishes are available?',
            'Help me request custom furniture',
            'What is within a $500 budget?'
          ]
        }
      ])
    }
  }, [isAIChatOpen, aiChatContext, messages.length])

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, isTyping])

  if (!isAIChatOpen) return null

  const handleNewChat = () => {
    setMessages([
      {
        id: Date.now().toString(),
        sender: 'ai',
        text: 'Started a fresh conversation! What furniture design or styling questions do you have?',
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        suggestions: [
          'Recommend living room pieces',
          'What finishes are available?',
          'Help me request custom furniture'
        ]
      }
    ])
  }

  const handleVoiceInput = () => {
    if (!('webkitSpeechRecognition' in window || 'SpeechRecognition' in window)) {
      alert('Speech recognition is not supported in this browser version.')
      return
    }

    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition
    const recognition = new SpeechRecognition()
    recognition.lang = 'en-US'

    recognition.onstart = () => setIsListening(true)
    recognition.onend = () => setIsListening(false)
    recognition.onresult = (event) => {
      const transcript = event.results[0][0].transcript
      setInputValue(transcript)
    }

    recognition.start()
  }

  const handleSend = async (textToSend = inputValue) => {
    const text = textToSend.trim()
    if (!text) return

    const userMsg = {
      id: Date.now().toString(),
      sender: 'user',
      text: text,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    }

    setMessages(prev => [...prev, userMsg])
    setInputValue('')
    setIsTyping(true)

    // Save user message to database if logged in
    if (user?.id) {
      aiService.saveChatMessage({ userId: user.id, sender: 'user', text })
    }

    // Format chat payload for service call
    const chatPayload = messages.concat(userMsg).map(m => ({
      role: m.sender === 'user' ? 'user' : 'assistant',
      content: m.text
    }))

    const { text: responseText, product: recommendedProduct } = await aiService.sendMessage({
      messages: chatPayload,
      productContext: aiChatContext,
      userPreferences: user
    })

    setIsTyping(false)

    const aiMsg = {
      id: (Date.now() + 1).toString(),
      sender: 'ai',
      text: responseText,
      product: recommendedProduct,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    }

    setMessages(prev => [...prev, aiMsg])

    // Save AI response to database if logged in
    if (user?.id) {
      aiService.saveChatMessage({ userId: user.id, sender: 'ai', text: responseText, productId: recommendedProduct?.id })
    }
  }

  return (
    <div className="fixed inset-0 z-50 flex flex-col justify-end bg-charcoal/60 backdrop-blur-sm animate-fade-in">
      <div className="w-full max-w-md mx-auto h-[88vh] bg-cream-100 rounded-t-3xl shadow-warm-lg flex flex-col overflow-hidden border-t border-walnut-200">
        
        {/* Header */}
        <div className="bg-walnut-500 text-white px-5 py-4 flex items-center justify-between shadow-md">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-full bg-gold-500 flex items-center justify-center text-white ring-2 ring-white/30">
              <Sparkles className="w-5 h-5 text-white" />
            </div>
            <div>
              <h3 className="font-sans font-bold text-base text-white tracking-wide">GloryAI Assistant</h3>
              <p className="text-[11px] text-cream-200 flex items-center gap-1">
                <span className="w-1.5 h-1.5 rounded-full bg-mutedgreen animate-pulse" /> Personal Furniture Advisor
              </p>
            </div>
          </div>
          
          <div className="flex items-center gap-2">
            <button
              onClick={handleNewChat}
              className="p-1.5 text-cream-200 hover:text-white rounded-full hover:bg-walnut-600 active-tap flex items-center gap-1 text-[11px] font-semibold"
              title="New Chat"
            >
              <PlusCircle className="w-4 h-4" /> New
            </button>
            <button
              onClick={closeAIChat}
              className="p-1.5 text-cream-200 hover:text-white rounded-full hover:bg-walnut-600 active-tap"
            >
              <X className="w-5 h-5" />
            </button>
          </div>
        </div>

        {/* Context Banner */}
        {aiChatContext && (
          <div className="bg-gold-500/10 border-b border-gold-500/20 px-4 py-2 text-xs text-walnut-700 flex items-center justify-between">
            <span>Discussing: <strong>{aiChatContext.name}</strong></span>
            <button 
              onClick={() => {
                closeAIChat()
                navigate(`/product/${aiChatContext.id}`)
              }}
              className="text-gold-600 font-semibold underline text-[11px]"
            >
              View Piece
            </button>
          </div>
        )}

        {/* Messages Body */}
        <div className="flex-1 overflow-y-auto p-4 space-y-4">
          {messages.map((msg) => (
            <div
              key={msg.id}
              className={`flex flex-col ${msg.sender === 'user' ? 'items-end' : 'items-start'}`}
            >
              <div
                className={`max-w-[84%] px-4 py-3 rounded-2xl text-xs leading-relaxed shadow-card ${
                  msg.sender === 'user'
                    ? 'bg-walnut-500 text-white rounded-tr-none'
                    : 'bg-white text-charcoal border border-walnut-100 rounded-tl-none'
                }`}
              >
                {msg.text}

                {/* Inline Product Card */}
                {msg.product && (
                  <div className="mt-3 p-2 bg-cream-100 rounded-xl border border-walnut-200 flex items-center gap-3">
                    <img 
                      src={msg.product.images[0]} 
                      alt={msg.product.name} 
                      className="w-12 h-12 rounded-lg object-cover"
                    />
                    <div className="flex-1 min-w-0">
                      <h5 className="font-sans font-bold text-xs text-walnut-800 truncate">{msg.product.name}</h5>
                      <p className="text-[11px] font-semibold text-gold-600">${msg.product.price}</p>
                    </div>
                    <button
                      onClick={() => {
                        closeAIChat()
                        navigate(`/product/${msg.product.id}`)
                      }}
                      className="p-1.5 bg-walnut-500 text-white rounded-lg active-tap text-[10px] font-medium"
                    >
                      View
                    </button>
                  </div>
                )}
              </div>
              
              <span className="text-[10px] text-softgray mt-1 px-1">{msg.timestamp}</span>

              {/* Suggested prompt chips */}
              {msg.suggestions && (
                <div className="mt-3 flex flex-wrap gap-1.5">
                  {msg.suggestions.map((s, i) => (
                    <button
                      key={i}
                      onClick={() => handleSend(s)}
                      className="text-[11px] bg-white hover:bg-cream-200 text-walnut-700 px-3 py-1.5 rounded-full border border-walnut-200 shadow-sm active-tap transition-colors"
                    >
                      {s}
                    </button>
                  ))}
                </div>
              )}
            </div>
          ))}

          {isTyping && (
            <div className="flex items-center gap-2 text-softgray text-xs bg-white py-2.5 px-4 rounded-full w-fit border border-walnut-100 shadow-sm">
              <RefreshCw className="w-3.5 h-3.5 animate-spin text-gold-500" />
              GloryAI is typing...
            </div>
          )}
          <div ref={chatEndRef} />
        </div>

        {/* Custom Request Shortcut */}
        <div className="px-4 py-2 bg-cream-200/50 border-t border-walnut-100 flex items-center justify-between">
          <span className="text-[11px] text-walnut-700">Need something totally unique?</span>
          <button
            onClick={() => {
              closeAIChat()
              navigate('/custom-request')
            }}
            className="text-[11px] font-semibold text-gold-600 hover:text-gold-500 flex items-center gap-1 active-tap"
          >
            <ShoppingBag className="w-3.5 h-3.5" /> Start Custom Request
          </button>
        </div>

        {/* Input Footer */}
        <div className="p-3 bg-white border-t border-walnut-100 flex items-center gap-2">
          <button
            onClick={handleVoiceInput}
            className={`p-3 rounded-full active-tap transition-colors ${
              isListening ? 'bg-dustyrose text-white animate-pulse' : 'bg-cream-100 text-walnut-700 hover:bg-cream-200'
            }`}
            title="Voice input"
          >
            <Mic className="w-4 h-4" />
          </button>

          <input
            type="text"
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && handleSend()}
            placeholder={isListening ? 'Listening to speech...' : 'Ask me anything about furniture...'}
            className="flex-1 text-xs px-4 py-3 rounded-full bg-cream-100 border border-walnut-200 focus:outline-none focus:ring-2 focus:ring-walnut-500 text-charcoal placeholder:text-softgray"
          />
          <button
            onClick={() => handleSend()}
            disabled={!inputValue.trim()}
            className="p-3 bg-walnut-500 text-gold-400 disabled:opacity-50 rounded-full active-tap shadow-sm"
          >
            <Send className="w-4 h-4" />
          </button>
        </div>

      </div>
    </div>
  )
}
