import { supabase, isSupabaseConfigured } from '../lib/supabase'

export const authService = {
  // Sign up new user with email & password
  async signUp({ email, password, fullName, phone }) {
    if (!isSupabaseConfigured) {
      console.warn('Supabase credentials missing. Operating in offline demo session mode.')
      return {
        user: { id: 'demo-user-id', email, name: fullName, phone, role: 'customer' },
        error: null
      }
    }

    const { data, error } = await supabase.auth.signUp({
      email,
      password,
      options: {
        data: {
          full_name: fullName,
          phone: phone,
          role: 'customer'
        }
      }
    })

    if (error) return { user: null, error }

    if (data.user) {
      // Create user profile in profiles table
      await supabase.from('profiles').insert([
        {
          id: data.user.id,
          full_name: fullName,
          email: email,
          phone: phone,
          role: 'customer'
        }
      ])
    }

    return { user: data.user, error: null }
  },

  // Sign in with email & password
  async signInWithPassword({ email, password }) {
    if (!isSupabaseConfigured) {
      const isAdmin = email.toLowerCase().includes('admin')
      return {
        user: {
          id: isAdmin ? 'admin-id' : 'demo-user-id',
          email,
          name: isAdmin ? 'Master Artisan (Admin)' : (email.split('@')[0] || 'Glory Patron'),
          role: isAdmin ? 'admin' : 'customer'
        },
        error: null
      }
    }

    const { data, error } = await supabase.auth.signInWithPassword({
      email,
      password
    })

    if (error) return { user: null, error }

    // Fetch user profile role details
    const { data: profile } = await supabase
      .from('profiles')
      .select('*')
      .eq('id', data.user.id)
      .single()

    const formattedUser = {
      id: data.user.id,
      email: data.user.email,
      name: profile?.full_name || data.user.user_metadata?.full_name || 'Valued Patron',
      phone: profile?.phone || '',
      role: profile?.role || 'customer'
    }

    return { user: formattedUser, error: null }
  },

  // Sign in with Google OAuth
  async signInWithGoogle() {
    if (!isSupabaseConfigured) {
      const demoGoogleUser = {
        id: `google-user-${Date.now().toString().slice(-4)}`,
        email: 'google.patron@gmail.com',
        name: 'Google Patron',
        role: 'customer',
        phone: ''
      }
      return { user: demoGoogleUser, error: null }
    }

    const { data, error } = await supabase.auth.signInWithOAuth({
      provider: 'google',
      options: {
        redirectTo: `${window.location.origin}/home`
      }
    })

    return { data, error }
  },

  // Sign out user session
  async signOut() {
    if (isSupabaseConfigured) {
      await supabase.auth.signOut()
    }
    return { error: null }
  },

  // Listen to Auth State Changes
  onAuthStateChange(callback) {
    if (!isSupabaseConfigured) return () => {}

    const { data: { subscription } } = supabase.auth.onAuthStateChange(async (event, session) => {
      if (session?.user) {
        const { data: profile } = await supabase
          .from('profiles')
          .select('*')
          .eq('id', session.user.id)
          .single()

        callback({
          id: session.user.id,
          email: session.user.email,
          name: profile?.full_name || session.user.user_metadata?.full_name || 'Valued Patron',
          phone: profile?.phone || '',
          role: profile?.role || 'customer'
        })
      } else {
        callback(null)
      }
    })

    return () => subscription.unsubscribe()
  }
}
