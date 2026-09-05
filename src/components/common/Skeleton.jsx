import React from 'react'

export function ProductCardSkeleton() {
  return (
    <div className="bg-white rounded-2xl p-3 shadow-card border border-walnut-100/80 animate-pulse">
      <div className="aspect-square rounded-xl bg-cream-200 mb-2.5" />
      <div className="h-3 bg-cream-300 rounded w-1/3 mb-2" />
      <div className="h-3.5 bg-cream-300 rounded w-3/4 mb-1" />
      <div className="h-2.5 bg-cream-200 rounded w-1/2 mb-3" />
      <div className="flex justify-between items-center pt-2 border-t border-cream-200">
        <div className="h-4 bg-cream-300 rounded w-1/3" />
        <div className="h-3 bg-cream-200 rounded-full w-1/4" />
      </div>
    </div>
  )
}

export function ProductGridSkeleton({ count = 4 }) {
  return (
    <div className="grid grid-cols-2 gap-3.5">
      {Array.from({ length: count }).map((_, i) => (
        <ProductCardSkeleton key={i} />
      ))}
    </div>
  )
}
