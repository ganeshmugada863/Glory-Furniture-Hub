import React, { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import Header from '../components/common/Header'
import Input from '../components/common/Input'
import Button from '../components/common/Button'
import Toast from '../components/common/Toast'
import { useAppStore } from '../store/useAppStore'
import { Check, Camera, Phone, User, Mail } from 'lucide-react'

export default function EditProfileScreen() {
  const navigate = useNavigate()
  const { user, setUser } = useAppStore()

  const [name, setName] = useState(user?.name || '')
  const [phone, setPhone] = useState(user?.phone || '')
  const [email, setEmail] = useState(user?.email || '')
  const [toastMessage, setToastMessage] = useState('')

  const handleSave = (e) => {
    e.preventDefault()
    setUser({ ...user, name: name.trim(), phone: phone.trim(), email: email.trim() })
    setToastMessage('Profile details updated successfully!')
    setTimeout(() => {
      navigate('/profile')
    }, 800)
  }

  return (
    <div className="min-h-screen bg-cream-100 pb-28">
      <Header title="Edit Profile Details" showBack={true} />
      <Toast message={toastMessage} onClose={() => setToastMessage('')} />

      <form onSubmit={handleSave} className="px-5 py-4 space-y-4 max-w-md mx-auto">
        <div className="flex justify-center my-4">
          <div className="relative">
            <div className="w-24 h-24 rounded-3xl bg-walnut-500 text-gold-400 font-serif font-bold text-3xl flex items-center justify-center shadow-lg ring-4 ring-gold-500/20">
              {name ? name.charAt(0) : 'G'}
            </div>
            <button
              type="button"
              className="absolute -bottom-1 -right-1 p-2 bg-gold-500 text-white rounded-full shadow-md active-tap"
            >
              <Camera className="w-4 h-4" />
            </button>
          </div>
        </div>

        <div className="bg-white p-4 rounded-2xl border border-walnut-100 shadow-card space-y-3">
          <Input
            label="Full Name"
            type="text"
            required
            icon={User}
            value={name}
            onChange={(e) => setName(e.target.value)}
          />

          <Input
            label="Email Address"
            type="email"
            disabled
            icon={Mail}
            value={email}
            helperText="OAuth / Account email is managed by your provider."
          />

          <Input
            label="Phone Number"
            type="tel"
            icon={Phone}
            value={phone}
            onChange={(e) => setPhone(e.target.value)}
          />
        </div>

        <Button
          type="submit"
          variant="primary"
          size="lg"
          className="w-full"
          icon={Check}
        >
          Save Profile Changes
        </Button>
      </form>
    </div>
  )
}
