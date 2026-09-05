import React from 'react'
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import AppLayout from './components/layout/AppLayout'

import SplashScreen from './pages/SplashScreen'
import OnboardingScreen from './pages/OnboardingScreen'
import LoginScreen from './pages/LoginScreen'
import RegisterScreen from './pages/RegisterScreen'
import ForgotPasswordScreen from './pages/ForgotPasswordScreen'

import HomeScreen from './pages/HomeScreen'
import CatalogScreen from './pages/CatalogScreen'
import ProductDetailScreen from './pages/ProductDetailScreen'
import SearchScreen from './pages/SearchScreen'
import WishlistScreen from './pages/WishlistScreen'

import BookingScreen from './pages/BookingScreen'
import BookingConfirmationScreen from './pages/BookingConfirmationScreen'
import CustomRequestScreen from './pages/CustomRequestScreen'
import CustomRequestConfirmationScreen from './pages/CustomRequestConfirmationScreen'

import MyBookingsScreen from './pages/MyBookingsScreen'
import BookingDetailScreen from './pages/BookingDetailScreen'

import ProfileScreen from './pages/ProfileScreen'
import EditProfileScreen from './pages/EditProfileScreen'
import MyRequestsScreen from './pages/MyRequestsScreen'
import NotificationsScreen from './pages/NotificationsScreen'

import AboutScreen from './pages/AboutScreen'
import ContactScreen from './pages/ContactScreen'
import FAQScreen from './pages/FAQScreen'

import AdminDashboardScreen from './pages/AdminDashboardScreen'
import AdminProductsScreen from './pages/AdminProductsScreen'
import AdminBookingsScreen from './pages/AdminBookingsScreen'
import AdminCustomRequestsScreen from './pages/AdminCustomRequestsScreen'
import ProtectedRoute from './components/common/ProtectedRoute'

export default function App() {
  return (
    <Router>
      <AppLayout>
        <Routes>
          <Route path="/" element={<SplashScreen />} />
          <Route path="/onboarding" element={<OnboardingScreen />} />
          <Route path="/login" element={<LoginScreen />} />
          <Route path="/register" element={<RegisterScreen />} />
          <Route path="/forgot-password" element={<ForgotPasswordScreen />} />

          <Route path="/home" element={<HomeScreen />} />
          <Route path="/catalog" element={<CatalogScreen />} />
          <Route path="/product/:id" element={<ProductDetailScreen />} />
          <Route path="/search" element={<SearchScreen />} />
          <Route path="/wishlist" element={<WishlistScreen />} />

          <Route path="/booking" element={<BookingScreen />} />
          <Route path="/booking-confirmation/:bookingId" element={<BookingConfirmationScreen />} />
          <Route path="/custom-request" element={<CustomRequestScreen />} />
          <Route path="/custom-request-confirmation" element={<CustomRequestConfirmationScreen />} />

          <Route path="/bookings" element={<MyBookingsScreen />} />
          <Route path="/bookings/:bookingId" element={<BookingDetailScreen />} />

          <Route path="/profile" element={<ProfileScreen />} />
          <Route path="/profile/edit" element={<EditProfileScreen />} />
          <Route path="/profile/requests" element={<MyRequestsScreen />} />
          <Route path="/notifications" element={<NotificationsScreen />} />

          <Route path="/about" element={<AboutScreen />} />
          <Route path="/contact" element={<ContactScreen />} />
          <Route path="/faq" element={<FAQScreen />} />

          {/* Role-Protected Admin Single Page Portal */}
          <Route path="/admin" element={<ProtectedRoute requiredRole="admin"><AdminDashboardScreen /></ProtectedRoute>} />
          <Route path="/admin/products" element={<Navigate to="/admin?tab=products" replace />} />
          <Route path="/admin/bookings" element={<Navigate to="/admin?tab=orders" replace />} />
          <Route path="/admin/custom-requests" element={<Navigate to="/admin?tab=custom-requests" replace />} />

          <Route path="*" element={<Navigate to="/home" replace />} />
        </Routes>
      </AppLayout>
    </Router>
  )
}
