import React, { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import Header from '../components/common/Header'
import Button from '../components/common/Button'
import Toast from '../components/common/Toast'
import { MOCK_PRODUCTS } from '../data/mockData'
import { useAppStore } from '../store/useAppStore'
import { Heart, Trash2, ArrowRight, ShoppingBag } from 'lucide-react'

export default function WishlistScreen() {
  const navigate = useNavigate()
  const { wishlist, toggleWishlist } = useAppStore()
  const [toastMessage, setToastMessage] = useState('')

  const savedProducts = MOCK_PRODUCTS.filter(p => wishlist.includes(p.id))

  const handleRemove = (id, name) => {
    toggleWishlist(id)
    setToastMessage(`Removed "${name}" from wishlist.`)
  }

  return (
    <div className="min-h-screen bg-cream-100 pb-28">
      <Header title="My Saved Wishlist" showBack={false} />
      <Toast message={toastMessage} onClose={() => setToastMessage('')} />

      <div className="px-5 py-4">
        {savedProducts.length > 0 ? (
          <>
            <p className="text-xs text-softgray mb-4">
              You have <strong className="text-walnut-800">{savedProducts.length}</strong> saved handcrafted pieces.
            </p>

            <div className="space-y-3">
              {savedProducts.map(product => (
                <div
                  key={product.id}
                  className="bg-white p-3.5 rounded-2xl border border-walnut-100 shadow-card flex items-center gap-3.5"
                >
                  <img
                    src={product.images[0]}
                    alt={product.name}
                    onClick={() => navigate(`/product/${product.id}`)}
                    className="w-20 h-20 object-cover rounded-xl bg-cream-200 cursor-pointer"
                  />

                  <div className="flex-1 min-w-0">
                    <span className="text-[10px] uppercase font-bold text-gold-600 tracking-wider">
                      {product.category}
                    </span>
                    <h4
                      onClick={() => navigate(`/product/${product.id}`)}
                      className="font-serif font-bold text-xs text-walnut-800 truncate cursor-pointer hover:text-gold-600"
                    >
                      {product.name}
                    </h4>
                    <p className="text-[11px] text-softgray">{product.material}</p>
                    <span className="font-sans font-bold text-sm text-walnut-900 mt-1 block">
                      ${product.price}
                    </span>
                  </div>

                  <div className="flex flex-col gap-2 items-end">
                    <button
                      onClick={() => handleRemove(product.id, product.name)}
                      className="p-1.5 text-softgray hover:text-dustyrose active-tap"
                      title="Remove"
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>
                    
                    <Button
                      variant="primary"
                      size="sm"
                      onClick={() => navigate(`/booking?productId=${product.id}`)}
                      icon={ArrowRight}
                    >
                      Book
                    </Button>
                  </div>
                </div>
              ))}
            </div>
          </>
        ) : (
          <div className="py-20 text-center">
            <div className="w-16 h-16 rounded-full bg-cream-200 flex items-center justify-center mx-auto mb-3 text-softgray">
              <Heart className="w-8 h-8" />
            </div>
            <h3 className="font-serif font-bold text-lg text-walnut-800 mb-1">Your wishlist is empty</h3>
            <p className="text-xs text-softgray mb-6">Explore our handcrafted catalog and tap the heart icon to save favorite pieces.</p>
            <Button
              variant="primary"
              size="lg"
              onClick={() => navigate('/catalog')}
              icon={ShoppingBag}
              className="mx-auto"
            >
              Explore Catalog
            </Button>
          </div>
        )}
      </div>
    </div>
  )
}
