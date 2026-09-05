import { create } from 'zustand'

function getStoredUser() {
  try {
    const saved = localStorage.getItem('glory_user')
    if (saved) return JSON.parse(saved)
  } catch (e) {}
  return {
    id: `cust-${Date.now().toString().slice(-4)}`,
    name: '',
    email: '',
    role: 'customer',
    phone: '',
    address: ''
  }
}

function getStoredBookings() {
  try {
    const saved = localStorage.getItem('glory_user_bookings')
    if (saved) {
      const parsed = JSON.parse(saved)
      if (Array.isArray(parsed)) return parsed
    }
  } catch (e) {}
  return []
}

function getStoredCustomRequests() {
  try {
    const saved = localStorage.getItem('glory_custom_requests')
    if (saved) {
      const parsed = JSON.parse(saved)
      if (Array.isArray(parsed)) return parsed
    }
  } catch (e) {}
  return []
}

function getStoredAddresses() {
  try {
    const saved = localStorage.getItem('glory_saved_addresses')
    if (saved) {
      const parsed = JSON.parse(saved)
      if (Array.isArray(parsed)) return parsed
    }
  } catch (e) {}
  return []
}

function getStoredNotifications() {
  try {
    const saved = localStorage.getItem('glory_notifications')
    if (saved) {
      const parsed = JSON.parse(saved)
      if (Array.isArray(parsed)) return parsed
    }
  } catch (e) {}
  return [
    {
      id: 'notif-welcome',
      title: 'Welcome to Glory Furniture Hub',
      description: 'Explore certified pure Burma teak wood luxury furniture handcrafted in Hyderabad.',
      timestamp: 'Just now',
      read: false,
      type: 'general'
    }
  ]
}

export const useAppStore = create((set, get) => ({
  // User Session
  user: getStoredUser(),

  setUser: (user) => {
    if (user) {
      try { localStorage.setItem('glory_user', JSON.stringify(user)) } catch (e) {}
    } else {
      try { localStorage.removeItem('glory_user') } catch (e) {}
    }
    set({ user })
  },

  switchRole: (newRole) => {
    const targetUser = newRole === 'admin' 
      ? {
          id: 'admin-001',
          name: 'Master Studio Admin',
          email: 'admin@gloryfurniture.com',
          role: 'admin',
          phone: '+91 98765 43210'
        }
      : {
          id: `cust-${Date.now().toString().slice(-4)}`,
          name: get().user?.name || '',
          email: get().user?.email || '',
          role: 'customer',
          phone: get().user?.phone || '',
          address: get().user?.address || ''
        }
    try { localStorage.setItem('glory_user', JSON.stringify(targetUser)) } catch (e) {}
    set({ user: targetUser })
    return targetUser
  },

  // Wishlist
  wishlist: [],
  toggleWishlist: (product) => set((state) => {
    const exists = state.wishlist.some(p => p.id === product.id)
    return {
      wishlist: exists
        ? state.wishlist.filter(p => p.id !== product.id)
        : [...state.wishlist, product]
    }
  }),

  // AI Chat Overlay state
  isAIChatOpen: false,
  aiChatContext: null,
  openAIChat: (context = null) => set({ isAIChatOpen: true, aiChatContext: context }),
  closeAIChat: () => set({ isAIChatOpen: false, aiChatContext: null }),

  // Saved Delivery Addresses (Flipkart style storage)
  savedAddresses: getStoredAddresses(),
  addSavedAddress: (newAddr) => set((state) => {
    const updated = [newAddr, ...state.savedAddresses.filter(a => a.id !== newAddr.id)]
    try { localStorage.setItem('glory_saved_addresses', JSON.stringify(updated)) } catch (e) {}
    return { savedAddresses: updated }
  }),
  deleteSavedAddress: (id) => set((state) => {
    const updated = state.savedAddresses.filter(a => a.id !== id)
    try { localStorage.setItem('glory_saved_addresses', JSON.stringify(updated)) } catch (e) {}
    return { savedAddresses: updated }
  }),

  // Notifications
  notifications: getStoredNotifications(),
  addNotification: (notif) => set((state) => {
    const updated = [notif, ...state.notifications]
    try { localStorage.setItem('glory_notifications', JSON.stringify(updated)) } catch (e) {}
    return { notifications: updated }
  }),
  markNotificationAsRead: (id) => set((state) => {
    const updated = state.notifications.map(n => n.id === id ? { ...n, read: true } : n)
    try { localStorage.setItem('glory_notifications', JSON.stringify(updated)) } catch (e) {}
    return { notifications: updated }
  }),
  markAllNotificationsRead: () => set((state) => {
    const updated = state.notifications.map(n => ({ ...n, read: true }))
    try { localStorage.setItem('glory_notifications', JSON.stringify(updated)) } catch (e) {}
    return { notifications: updated }
  }),

  // Real User Bookings (Persistent, zero dummy data)
  userBookings: getStoredBookings(),
  addBooking: (newBooking) => set((state) => {
    const updated = [newBooking, ...state.userBookings]
    try { localStorage.setItem('glory_user_bookings', JSON.stringify(updated)) } catch (e) {}
    return { userBookings: updated }
  }),
  cancelBooking: (bookingId) => set((state) => {
    const updated = state.userBookings.map(b => b.id === bookingId ? { ...b, status: 'Cancelled' } : b)
    try { localStorage.setItem('glory_user_bookings', JSON.stringify(updated)) } catch (e) {}
    return { userBookings: updated }
  }),

  // Custom Requests (Persistent, zero dummy data)
  customRequests: getStoredCustomRequests(),
  addCustomRequest: (newReq) => set((state) => {
    const updated = [newReq, ...state.customRequests]
    try { localStorage.setItem('glory_custom_requests', JSON.stringify(updated)) } catch (e) {}
    return { customRequests: updated }
  })
}))

