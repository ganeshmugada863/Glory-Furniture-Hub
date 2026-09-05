import React from 'react'
import { useNavigate } from 'react-router-dom'
import { Star, Heart, ShoppingBag } from 'lucide-react'
import { useAppStore } from '../../store/useAppStore'

export default function ProductCard({ product, layout = 'grid' }) {
  const navigate = useNavigate()
  const { wishlist, toggleWishlist } = useAppStore()
  const isWishlisted = wishlist.some(item => item.id === product.id)

  const handleBookClick = (e) => {
    e.stopPropagation()
    navigate(`/booking?productId=${product.id}`)
  }

  const handleWishlistClick = (e) => {
    e.stopPropagation()
    toggleWishlist(product)
  }

  const formattedPrice = `₹${product.price.toLocaleString('en-IN')}`

  if (layout === 'horizontal') {
    return (
      <div
        onClick={() => navigate(`/product/${product.id}`)}
        className="w-56 flex-shrink-0 bg-transparent cursor-pointer group flex flex-col justify-between"
      >
        <div>
          {/* Card Image Box matching reference UI */}
          <div className="relative aspect-square rounded-2xl overflow-hidden bg-[#F2ECE4] mb-3">
            <img
              src={product.images[0]}
              alt={product.name}
              loading="lazy"
              className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500"
            />
            {/* Wishlist Heart Icon (Top Right) */}
            <button
              onClick={handleWishlistClick}
              className="absolute top-3 right-3 w-8 h-8 rounded-full bg-white/90 backdrop-blur-sm flex items-center justify-center text-walnut-800 shadow-sm active-tap hover:bg-white transition-all"
            >
              <Heart className={`w-4 h-4 ${isWishlisted ? 'fill-dustyrose text-dustyrose' : 'text-walnut-700'}`} />
            </button>
          </div>

          <h4 className="font-serif font-bold text-sm text-walnut-900 line-clamp-1 group-hover:text-gold-600 transition-colors">
            {product.name}
          </h4>
          <p className="text-xs text-softgray line-clamp-1 mt-0.5">{product.material}</p>

          <div className="flex items-center justify-between mt-2 mb-3">
            <span className="font-sans font-bold text-sm text-walnut-900">{formattedPrice}</span>
            <div className="flex items-center gap-1 text-xs text-walnut-700 font-semibold">
              <Star className="w-3.5 h-3.5 fill-gold-500 text-gold-500" />
              <span>{product.rating}</span>
            </div>
          </div>
        </div>

        {/* Action Button: Book Now */}
        <button
          onClick={handleBookClick}
          className="w-full py-2.5 bg-walnut-900 hover:bg-walnut-800 text-white text-xs font-semibold rounded-xl active-tap flex items-center justify-center gap-1.5 shadow-sm transition-all"
        >
          <ShoppingBag className="w-3.5 h-3.5 text-gold-400" /> Book Now
        </button>
      </div>
    )
  }

  return (
    <div
      onClick={() => navigate(`/product/${product.id}`)}
      className="bg-transparent cursor-pointer group flex flex-col justify-between"
    >
      <div>
        {/* Compact Card Image Container */}
        <div className="relative aspect-[4/3] rounded-xl overflow-hidden bg-[#F2ECE4] mb-2 shadow-2xs">
          <img
            src={product.images[0]}
            alt={product.name}
            loading="lazy"
            className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500"
          />
          {/* Wishlist Heart Button */}
          <button
            onClick={handleWishlistClick}
            className="absolute top-2 right-2 w-7 h-7 rounded-full bg-white/90 backdrop-blur-sm flex items-center justify-center text-walnut-800 shadow-sm active-tap hover:bg-white transition-all"
          >
            <Heart className={`w-3.5 h-3.5 ${isWishlisted ? 'fill-dustyrose text-dustyrose' : 'text-walnut-700'}`} />
          </button>
        </div>

        <h4 className="font-serif font-bold text-xs sm:text-sm text-walnut-900 line-clamp-1 group-hover:text-gold-600 transition-colors">
          {product.name}
        </h4>
        <p className="text-[10px] sm:text-xs text-softgray line-clamp-1 mt-0.5">{product.material}</p>

        <div className="flex items-center justify-between mt-1 mb-2">
          <span className="font-sans font-bold text-xs sm:text-sm text-walnut-900">{formattedPrice}</span>
          <div className="flex items-center gap-1 text-[11px] text-walnut-700 font-semibold">
            <Star className="w-3 h-3 fill-gold-500 text-gold-500" />
            <span>{product.rating}</span>
          </div>
        </div>
      </div>

      {/* Action Button: Book Now */}
      <button
        onClick={handleBookClick}
        className="w-full py-1.5 sm:py-2 bg-walnut-900 hover:bg-walnut-800 text-white text-[11px] sm:text-xs font-semibold rounded-lg active-tap flex items-center justify-center gap-1.5 shadow-2xs transition-all"
      >
        <ShoppingBag className="w-3 h-3 text-gold-400" /> Book Now
      </button>
    </div>
  )
}
