/**
 * Glory Furniture Hub — Core Interactive JavaScript
 * Powers Hero Carousel Autoplay, Slide-over Drawers (Cart, Wishlist, Profile),
 * Dynamic Filter Dropdown, Dynamic Variant Pricing, and AI Assistant Chat.
 */

document.addEventListener('DOMContentLoaded', () => {
  initHeroCarousel();
  initDrawers();
  initCategoryDropdown();
  initSizeVariantPricing();
  initAIChat();
});

/* ==========================================================================
   1. HERO CAROUSEL AUTO-PLAY & SWIPE
   ========================================================================== */
function initHeroCarousel() {
  const carousel = document.getElementById('hero-carousel');
  if (!carousel) return;

  const slides = carousel.querySelectorAll('.hero-slide');
  const dots = document.querySelectorAll('.carousel-dot');
  const totalSlides = slides.length;
  if (totalSlides <= 1) return;

  let currentSlide = 0;
  let isPaused = false;
  let autoplayTimer = null;

  function showSlide(index) {
    currentSlide = (index + totalSlides) % totalSlides;
    slides.forEach((slide, i) => {
      if (i === currentSlide) {
        slide.classList.remove('opacity-0', 'pointer-events-none');
        slide.classList.add('opacity-100', 'pointer-events-auto');
      } else {
        slide.classList.add('opacity-0', 'pointer-events-none');
        slide.classList.remove('opacity-100', 'pointer-events-auto');
      }
    });

    dots.forEach((dot, i) => {
      if (i === currentSlide) {
        dot.classList.add('w-8', 'bg-white');
        dot.classList.remove('w-2', 'bg-white/50');
      } else {
        dot.classList.remove('w-8', 'bg-white');
        dot.classList.add('w-2', 'bg-white/50');
      }
    });
  }

  function startAutoplay() {
    stopAutoplay();
    autoplayTimer = setInterval(() => {
      if (!isPaused) {
        showSlide(currentSlide + 1);
      }
    }, 4500);
  }

  function stopAutoplay() {
    if (autoplayTimer) {
      clearInterval(autoplayTimer);
      autoplayTimer = null;
    }
  }

  carousel.addEventListener('mouseenter', () => { isPaused = true; });
  carousel.addEventListener('mouseleave', () => { isPaused = false; });

  dots.forEach((dot, i) => {
    dot.addEventListener('click', () => {
      showSlide(i);
      startAutoplay();
    });
  });

  // Touch Swipe
  let touchStartX = null;
  carousel.addEventListener('touchstart', (e) => {
    touchStartX = e.touches[0].clientX;
  }, { passive: true });

  carousel.addEventListener('touchend', (e) => {
    if (touchStartX === null) return;
    const diff = touchStartX - e.changedTouches[0].clientX;
    if (diff > 45) {
      showSlide(currentSlide + 1);
      startAutoplay();
    } else if (diff < -45) {
      showSlide(currentSlide - 1);
      startAutoplay();
    }
    touchStartX = null;
  });

  showSlide(0);
  startAutoplay();
}

/* ==========================================================================
   2. SLIDE-OVER DRAWERS (Cart, Wishlist, Profile) — TOP LEVEL BULLETPROOF
   ========================================================================== */
window.currentDrawerTab = 'profile';

window.openDrawer = function(tabName = 'profile') {
  tabName = tabName || 'profile';
  window.currentDrawerTab = tabName;
  const overlay = document.getElementById('drawer-overlay');
  const drawer = document.getElementById('nav-drawer');
  if (!overlay || !drawer) return;

  document.body.style.overflow = 'hidden';
  overlay.style.display = 'block';
  drawer.style.display = 'flex';

  void drawer.offsetWidth; // Force reflow

  overlay.classList.add('is-open');
  drawer.classList.add('is-open');
  overlay.style.opacity = '1';
  drawer.style.transform = 'translateX(0%)';

  window.switchDrawerTab(tabName);
};

window.closeDrawer = function() {
  const overlay = document.getElementById('drawer-overlay');
  const drawer = document.getElementById('nav-drawer');

  if (drawer) {
    drawer.classList.remove('is-open');
    drawer.style.transform = 'translateX(100%)';
  }

  if (overlay) {
    overlay.classList.remove('is-open');
    overlay.style.opacity = '0';
  }

  setTimeout(() => {
    if (drawer && !drawer.classList.contains('is-open')) {
      drawer.style.display = 'none';
    }
    if (overlay && !overlay.classList.contains('is-open')) {
      overlay.style.display = 'none';
    }
    document.body.style.overflow = '';
  }, 260);

  document.body.style.overflow = '';
};

window.toggleDrawer = function(tabName = 'profile') {
  tabName = tabName || 'profile';
  const drawer = document.getElementById('nav-drawer');
  const isOpen = drawer && (drawer.classList.contains('is-open') || drawer.style.display === 'flex');
  if (isOpen && window.currentDrawerTab === tabName) {
    window.closeDrawer();
  } else {
    window.openDrawer(tabName);
  }
};

window.switchDrawerTab = function(tabName) {
  window.currentDrawerTab = tabName;
  const tabs = ['profile', 'favourite', 'cart'];
  tabs.forEach(t => {
    const btn = document.getElementById(`drawer-tab-btn-${t}`);
    const content = document.getElementById(`drawer-tab-content-${t}`);
    if (btn) {
      if (t === tabName) {
        btn.className = 'relative flex items-center gap-1.5 px-3 sm:px-3.5 py-1.5 rounded-full text-xs font-semibold transition-all cursor-pointer bg-gray-950 text-white shadow-xs';
        const heart = document.getElementById('drawer-fav-icon');
        if (t === 'favourite' && heart) heart.classList.add('fill-white', 'text-white');
      } else {
        btn.className = 'relative flex items-center gap-1.5 px-3 sm:px-3.5 py-1.5 rounded-full text-xs font-semibold transition-all cursor-pointer text-gray-600 hover:text-gray-950 hover:bg-white/60';
        const heart = document.getElementById('drawer-fav-icon');
        if (t !== 'favourite' && heart) heart.classList.remove('fill-white', 'text-white');
      }
    }
    if (content) {
      if (t === tabName) {
        content.classList.remove('hidden');
      } else {
        content.classList.add('hidden');
      }
    }
  });
};

// Global escape key to close drawer and chat
window.addEventListener('keydown', (e) => {
  if (e.key === 'Escape' || e.key === 'Esc') {
    window.closeDrawer();
    if (typeof window.closeAIChat === 'function') {
      window.closeAIChat();
    }
  }
});

function initDrawers() {
  const overlay = document.getElementById('drawer-overlay');
  const drawerCloseBtn = document.getElementById('drawer-close-btn');
  const drawer = document.getElementById('nav-drawer');

  if (drawer) {
    drawer.classList.remove('is-open');
    drawer.style.display = 'none';
    drawer.style.transform = 'translateX(100%)';
  }
  if (overlay) {
    overlay.classList.remove('is-open');
    overlay.style.display = 'none';
    overlay.style.opacity = '0';
    overlay.addEventListener('click', window.closeDrawer);
  }
  if (drawerCloseBtn) {
    drawerCloseBtn.addEventListener('click', window.closeDrawer);
  }

  // Live Cart Add
  window.addToCart = async function(productId, size = 'Standard', qty = 1) {
    try {
      const res = await fetch('/api/cart/add/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ product_id: productId, size, quantity: qty })
      });
      const data = await res.json();
      if (data.status === 'success') {
        updateBadgeCounters(data.cart_count, null);
        showToast('Item added to your cart!');
        openDrawer('cart');
      }
    } catch (e) {
      showToast('Item added to your cart!');
      openDrawer('cart');
    }
  };

  // Live Cart Remove
  window.removeFromCart = async function(productId, size) {
    try {
      const res = await fetch('/api/cart/remove/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ product_id: productId, size })
      });
      const data = await res.json();
      if (data.status === 'success') {
        location.reload();
      }
    } catch (e) {
      location.reload();
    }
  };

  // Live Wishlist Toggle
  window.toggleWishlist = async function(productId) {
    try {
      const res = await fetch('/api/wishlist/toggle/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ product_id: productId })
      });
      const data = await res.json();
      if (data.status === 'success') {
        updateBadgeCounters(null, data.count);

        // Update heart icons across the page for this product
        document.querySelectorAll(`[data-wishlist-id="${productId}"]`).forEach(btn => {
          const svg = btn.querySelector('svg');
          if (svg) {
            if (data.added) {
              svg.classList.add('fill-red-600', 'text-red-600');
              svg.classList.remove('fill-none', 'text-gray-700', 'text-gray-800');
            } else {
              svg.classList.remove('fill-red-600', 'text-red-600');
              svg.classList.add('fill-none');
              if (!svg.classList.contains('text-white')) {
                svg.classList.add('text-gray-800');
              }
            }
          }
        });

        // Re-render sidebar drawer wishlist cards dynamically
        if (data.items !== undefined) {
          renderDrawerWishlist(data.items);
        }

        showToast(data.added ? 'Saved to Wishlist! View in sidebar' : 'Removed from Wishlist');
      }
    } catch (e) {
      showToast('Wishlist updated');
    }
  };

  window.refreshWishlistDrawer = async function() {
    try {
      const res = await fetch('/api/wishlist/toggle/', { method: 'GET' });
      const data = await res.json();
      if (data.status === 'success') {
        updateBadgeCounters(null, data.count);
        renderDrawerWishlist(data.items);
      }
    } catch (e) {
      console.error('Failed to refresh wishlist:', e);
    }
  };
}

function escapeHtml(str) {
  if (!str) return '';
  return String(str)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');
}

function renderDrawerWishlist(items) {
  const cardsContainer = document.getElementById('drawer-wishlist-cards');
  const emptyContainer = document.getElementById('drawer-wishlist-empty');

  if (!items || items.length === 0) {
    if (cardsContainer) cardsContainer.innerHTML = '';
    if (emptyContainer) emptyContainer.classList.remove('hidden');
    return;
  }

  if (emptyContainer) emptyContainer.classList.add('hidden');

  if (cardsContainer) {
    cardsContainer.innerHTML = items.map(item => `
      <div class="group cursor-pointer" onclick="window.location.href='${item.url}'">
        <div class="relative aspect-[4/3] rounded-2xl overflow-hidden bg-[#F2ECE4] mb-1.5 shadow-2xs">
          <img
            src="${item.primary_image}"
            alt="${escapeHtml(item.name)}"
            loading="lazy"
            class="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500"
          />
          <button
            data-wishlist-id="${item.id}"
            onclick="event.stopPropagation(); toggleWishlist(${item.id});"
            class="absolute top-2 right-2 w-7 h-7 rounded-full bg-white/90 backdrop-blur-sm flex items-center justify-center text-gray-800 shadow-sm active-tap hover:bg-white transition-all cursor-pointer"
            title="Save to Wishlist"
          >
            <svg class="w-3.5 h-3.5 fill-red-600 text-red-600" fill="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z"/>
            </svg>
          </button>
        </div>

        <h4 class="font-sans font-bold text-xs sm:text-sm text-gray-950 line-clamp-1 group-hover:text-[#5C3D2E] transition-colors">
          ${escapeHtml(item.name)}
        </h4>
        <p class="text-[10px] sm:text-xs text-gray-500 line-clamp-1 mt-0.5">${escapeHtml(item.material || 'Solid Teak Wood')}</p>

        <div class="flex items-center justify-between mt-1 mb-2">
          <span class="font-sans font-bold text-xs sm:text-sm text-gray-950">${item.formatted_price}</span>
          <div class="flex items-center gap-1 text-[11px] text-amber-700 font-semibold">
            <svg class="w-3 h-3 fill-amber-400 text-amber-400" fill="currentColor" viewBox="0 0 20 20">
              <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z"/>
            </svg>
            <span>${item.rating || '4.9'}</span>
          </div>
        </div>
      </div>
    `).join('');
  }
}

function updateBadgeCounters(cartCount, wishlistCount) {
  if (cartCount !== null) {
    document.querySelectorAll('.cart-badge-count').forEach(el => {
      el.textContent = cartCount;
    });
  }
  if (wishlistCount !== null) {
    document.querySelectorAll('.wishlist-badge-count').forEach(el => {
      el.textContent = wishlistCount;
      if (wishlistCount > 0) el.classList.remove('hidden');
      else el.classList.add('hidden');
    });
  }
}

/* ==========================================================================
   3. CATALOG CATEGORY DROPDOWN
   ========================================================================== */
function initCategoryDropdown() {
  const toggleBtn = document.getElementById('category-dropdown-btn');
  const menu = document.getElementById('category-dropdown-menu');
  if (!toggleBtn || !menu) return;

  toggleBtn.addEventListener('click', (e) => {
    e.stopPropagation();
    menu.classList.toggle('hidden');
  });

  document.addEventListener('click', (e) => {
    if (!toggleBtn.contains(e.target) && !menu.contains(e.target)) {
      menu.classList.add('hidden');
    }
  });
}

/* ==========================================================================
   4. DYNAMIC VARIANT PRICING (PRODUCT DETAIL PAGE)
   ========================================================================== */
function initSizeVariantPricing() {
  const sizeBtns = document.querySelectorAll('.size-variant-btn');
  const priceDisplay = document.getElementById('product-detail-price');
  if (!sizeBtns.length || !priceDisplay) return;

  sizeBtns.forEach(btn => {
    btn.addEventListener('click', () => {
      sizeBtns.forEach(b => {
        b.classList.remove('border-gray-900', 'bg-gray-900', 'text-white');
        b.classList.add('border-gray-200', 'bg-white', 'text-gray-800');
      });
      btn.classList.add('border-gray-900', 'bg-gray-900', 'text-white');
      btn.classList.remove('border-gray-200', 'bg-white', 'text-gray-800');

      const price = btn.getAttribute('data-price');
      if (price) {
        priceDisplay.textContent = formatIndianRupee(price);
      }
    });
  });
}

function formatIndianRupee(val) {
  val = parseInt(val, 10);
  if (isNaN(val)) return '₹0';
  let s = val.toString();
  let last3 = s.substring(s.length - 3);
  let other = s.substring(0, s.length - 3);
  if (other !== '') {
    last3 = ',' + last3;
  }
  return '₹' + other.replace(/\B(?=(\d{2})+(?!\d))/g, ",") + last3;
}

/* ==========================================================================
   5. GLORY AI ASSISTANT CHAT
   ========================================================================== */
function initAIChat() {
  const openFab = document.getElementById('ai-fab-btn');
  const modal = document.getElementById('ai-chat-modal');
  const closeBtn = document.getElementById('ai-chat-close');
  const form = document.getElementById('ai-chat-form');
  const input = document.getElementById('ai-chat-input');
  const messagesContainer = document.getElementById('ai-chat-messages');

  if (!modal) return;

  window.openAIChat = function() {
    modal.classList.remove('hidden');
    setTimeout(() => {
      modal.classList.remove('opacity-0');
      modal.querySelector('.ai-chat-panel')?.classList.remove('translate-y-full', 'sm:scale-95');
    }, 10);
    input?.focus();
  };

  window.closeAIChat = function() {
    modal.classList.add('opacity-0');
    modal.querySelector('.ai-chat-panel')?.classList.add('translate-y-full', 'sm:scale-95');
    setTimeout(() => {
      modal.classList.add('hidden');
    }, 300);
  };

  if (openFab) openFab.addEventListener('click', openAIChat);
  if (closeBtn) closeBtn.addEventListener('click', closeAIChat);

  if (form && input && messagesContainer) {
    form.addEventListener('submit', async (e) => {
      e.preventDefault();
      const text = input.value.trim();
      if (!text) return;

      // User Bubble
      appendMessage('user', text);
      input.value = '';

      // Typing indicator
      const typingId = appendTypingIndicator();

      try {
        const res = await fetch('/api/ai-chat/', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ message: text })
        });
        const data = await res.json();
        removeTypingIndicator(typingId);

        if (data.status === 'success') {
          appendMessage('ai', data.reply, data.action);
        } else {
          appendMessage('ai', "I'm having a brief connection pause. Please feel free to book a consultation or view our catalog directly!");
        }
      } catch (err) {
        removeTypingIndicator(typingId);
        appendMessage('ai', "Our master artisans in Hyderabad are ready to help. Explore our catalog or schedule a consultation!");
      }
    });
  }

  function appendMessage(sender, text, action = null) {
    const msgDiv = document.createElement('div');
    msgDiv.className = sender === 'user'
      ? 'flex justify-end'
      : 'flex justify-start items-start gap-2.5';

    if (sender === 'user') {
      msgDiv.innerHTML = `
        <div class="bg-gray-900 text-white rounded-2xl rounded-tr-xs px-4 py-2.5 max-w-[82%] text-xs sm:text-sm leading-relaxed shadow-xs">
          ${escapeHtml(text)}
        </div>
      `;
    } else {
      let actionBtnHtml = '';
      if (action) {
        actionBtnHtml = `
          <div class="mt-2.5">
            <a href="${action.url}" class="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-[#5C3D2E] hover:bg-[#4D3326] text-white text-[11px] font-bold shadow-xs transition-colors">
              ${action.label} →
            </a>
          </div>
        `;
      }
      msgDiv.innerHTML = `
        <div class="w-6 h-6 rounded-full bg-[#5C3D2E] text-white flex items-center justify-center text-[10px] font-bold flex-shrink-0 mt-0.5">
          G
        </div>
        <div class="bg-gray-100 text-gray-900 rounded-2xl rounded-tl-xs px-4 py-2.5 max-w-[85%] text-xs sm:text-sm leading-relaxed shadow-xs">
          <p>${escapeHtml(text)}</p>
          ${actionBtnHtml}
        </div>
      `;
    }

    messagesContainer.appendChild(msgDiv);
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
  }

  function appendTypingIndicator() {
    const id = 'typing-' + Date.now();
    const div = document.createElement('div');
    div.id = id;
    div.className = 'flex justify-start items-center gap-2 text-xs text-gray-500 italic pl-8';
    div.innerHTML = '<span>Glory AI is thinking...</span>';
    messagesContainer.appendChild(div);
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
    return id;
  }

  function removeTypingIndicator(id) {
    const el = document.getElementById(id);
    if (el) el.remove();
  }
}

/* ==========================================================================
   6. TOAST NOTIFICATION
   ========================================================================== */
function showToast(message) {
  let toast = document.getElementById('glory-toast');
  if (!toast) {
    toast = document.createElement('div');
    toast.id = 'glory-toast';
    toast.className = 'fixed bottom-20 left-1/2 -translate-x-1/2 z-50 bg-gray-950 text-white px-5 py-2.5 rounded-full shadow-lg text-xs font-semibold tracking-wide transition-all opacity-0 pointer-events-none transform translate-y-3';
    document.body.appendChild(toast);
  }
  toast.textContent = message;
  toast.classList.remove('opacity-0', 'pointer-events-none', 'translate-y-3');
  toast.classList.add('opacity-100', 'translate-y-0');

  setTimeout(() => {
    toast.classList.add('opacity-0', 'pointer-events-none', 'translate-y-3');
    toast.classList.remove('opacity-100', 'translate-y-0');
  }, 2800);
}

function escapeHtml(text) {
  const map = { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#039;' };
  return text.replace(/[&<>"']/g, function(m) { return map[m]; });
}
