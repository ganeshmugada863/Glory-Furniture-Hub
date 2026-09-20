# =====================================================================
# GLORY FURNITURE HUB — COMPLETE MASTER PRODUCTION SYSTEM PROMPT
# =====================================================================
# Single Source of Truth Specification for Recreating, Scaling, and
# Maintaining the Entire Glory Furniture Hub Luxury E-Commerce Platform.
# =====================================================================

## 1. PROJECT VISION & BRAND IDENTITY
- **Platform Name**: Glory Furniture Hub
- **Business Domain**: Luxury Handcrafted Burma Teak Wood Furniture e-Commerce, Custom Joinery Studio & Workshop Showroom.
- **Headquarters & Workshop**: Hyderabad, Telangana, India.
- **Brand Ethos**: 100% Seasoned Solid Burma Teak (Zero Engineered Wood / MDF / Particleboard), 10-Year Comprehensive Termite & Timber Warranty, Free White-Glove Doorstep Delivery in Hyderabad, Direct Artisan Workshop Pricing with Zero Middlemen.
- **Design Aesthetic**: High-end luxury timber studio aesthetic. Primary palette: Warm Teak (`#5C3D2E`), Deep Maroon/Oxblood (`#8B0000`), Cream/Linen Canvas (`#FAF7F4`), Obsidian Teak Bark (`#1b0e07`), Golden Amber Accent (`#F59E0B`, `#FFB703`), Emerald Guarantee Green (`#10B981`).

---

## 2. SYSTEM ARCHITECTURE & TECH STACK

### Backend Framework
- **Language**: Python 3.12+
- **Framework**: Django 5.x
- **WSGI / Web Server**: Gunicorn with Whitenoise for static file serving.
- **Architecture**: Modular Django architecture organized by domain:
  - `apps/core`: Storefront home, static pages, craft guide timeline, HTML5 geolocation reverse geocoding API, context processors.
  - `apps/store`: Product catalog, categories, search, filtering, product detail views, finish swatches.
  - `apps/bookings`: Direct checkout summary, order creation, order status history, tracking, booking confirmation, reschedule audits.
  - `apps/payments`: Cashfree SDK integration (v2023-08-01), 3 Equal Installments math engine, webhook receiver, UTR receipts, payment ledger.
  - `apps/accounts`: Customer authentication (Email/Password & Google OAuth), User Profile, delivery addresses, multi-tenant customer portal, Admin Studio dashboard, Website Settings CMS.
  - `apps/custom_orders`: Custom 3D Bespoke Furniture Request engine (room type, dimensions, wood choice, budget, inspiration uploads).

### Database & Storage
- **Production Database**: Managed PostgreSQL (Render / Neon serverless PostgreSQL via `DATABASE_URL`).
- **Development / Testing Database**: SQLite (`db.sqlite3`) for zero-dependency test suite execution.
- **Media & Image Storage**: Cloudinary persistent CDN storage (`CLOUDINARY_URL`), with graceful local media fallback.
- **Static Assets**: Tailwind CSS CDN, custom micro-interactions, responsive typography, FontAwesome/Heroicons SVGs.

### Third-Party Gateways & Integrations
- **Payment Gateway**: Cashfree Payments Production API (`https://api.cashfree.com/pg/orders`), Webhook signature verification via HMAC-SHA256.
- **Authentication**: Native Django Auth Backend + Google OAuth / Supabase Auth redirect flow.
- **Geolocation**: OpenStreetMap Nominatim Reverse Geocoding API with client-side HTML5 Geolocation permission handling and manual fallback.

---

## 3. DATABASE MODELS & SCHEMA SPECIFICATION

### A. `apps/store/models.py`
1. **`Category`**:
   - `name` (CharField, 100)
   - `slug` (SlugField, unique)
   - `image` (URLField / ImageField)
   - `order` (PositiveIntegerField, default=0)
   - `is_active` (BooleanField, default=True)
2. **`Product`**:
   - `name` (CharField, 200)
   - `category` (ForeignKey -> Category)
   - `price` (DecimalField, 10 digits, 2 decimal places)
   - `mrp` (DecimalField, optional display original price)
   - `dimensions` (CharField, e.g. "72 x 78 inches")
   - `wood_type` (CharField, default="Burma Teak")
   - `finishes` (JSONField, e.g. `["Natural Teak", "Dark Walnut", "Rosewood Luster"]`)
   - `sizes` (JSONField, e.g. `["King Size (72x78)", "Queen Size (60x78)"]`)
   - `primary_image` (URLField / ImageField)
   - `gallery_images` (JSONField, list of URLs)
   - `description` (TextField)
   - `wood_grain_story` (TextField)
   - `care_guide` (TextField)
   - `featured` (BooleanField, default=False)
   - `in_stock` (BooleanField, default=True)
   - `created_at`, `updated_at` (DateTimeField)

### B. `apps/bookings/models.py`
1. **`Order`**:
   - `order_number` (CharField, unique, e.g. `ORD-F2E445`)
   - `user` (ForeignKey -> auth.User, null=True, blank=True, on_delete=SET_NULL)
   - `booking` (OneToOneField -> Booking, null=True, blank=True)
   - `customer_name` (CharField, 150)
   - `email` (EmailField)
   - `phone` (CharField, 15)
   - `shipping_address` (TextField)
   - `product` (ForeignKey -> Product, on_delete=PROTECT)
   - `product_name` (CharField, 200)
   - `selected_size` (CharField, 100)
   - `selected_wood` (CharField, 100)
   - `quantity` (PositiveIntegerField, default=1)
   - `unit_price` (DecimalField, max_digits=12, decimal_places=2)
   - `total_amount` (DecimalField, max_digits=12, decimal_places=2)
   - `paid_amount` (DecimalField, default=0.00)
   - `remaining_amount` (DecimalField)
   - `payment_plan` (CharField: `'FULL_PAYMENT'` or `'THREE_INSTALLMENTS'`)
   - `payment_status` (CharField: `'PENDING'`, `'PARTIALLY_PAID'`, `'FULLY_PAID'`, `'FAILED'`, `'REFUNDED'`)
   - `fulfillment_status` (CharField: `'CONFIRMED'`, `'IN_PRODUCTION'`, `'SHIPPED'`, `'OUT_FOR_DELIVERY'`, `'DELIVERED'`)
   - `order_status` (CharField: `'PENDING_PAYMENT'`, `'PROCESSING'`, `'COMPLETED'`, `'CANCELLED'`)
   - `created_at`, `updated_at` (DateTimeField)
   - **Methods**:
     - `recalculate_financials()`: Computes `paid_amount = SUM(payments.amount)`, updates `remaining_amount`, syncs `payment_status`.
     - `get_flipkart_timeline()`: Returns 5-stage progress objects with completed flags and artisan audit notes.
2. **`Installment`**:
   - `order` (ForeignKey -> Order, related_name='installments')
   - `installment_number` (IntegerField: 1, 2, or 3)
   - `title` (CharField, e.g. "Advance Timber Booking (Part 1)")
   - `amount` (DecimalField, max_digits=10, decimal_places=2)
   - `due_date` (DateField)
   - `status` (CharField: `'PENDING'`, `'PAID'`, `'OVERDUE'`)
   - `paid_at` (DateTimeField, null=True)
   - `payment_id` (CharField, null=True)
   - `is_eligible_for_payment` (Property: True for Part 1, or True for Part N only if Part N-1 is PAID).
3. **`Booking`**:
   - `booking_id` (CharField, unique, e.g. `GLORY-12345`)
   - `customer_name`, `email`, `phone`, `address`
   - `product_name`
   - `status` (CharField: `'Pending'`, `'Confirmed'`, `'Completed'`, `'Cancelled'`)
   - `created_at` (DateTimeField)
4. **`PaymentTransaction` / `OrderStatusHistory` / `OrderAdminAuditLog`**:
   - Full ledger audit trail for payment events, workshop status transitions, and admin overrides.

### C. `apps/payments/models.py`
1. **`Payment`**:
   - `payment_id` (CharField, unique, e.g. `PAY-UUID`)
   - `order` (ForeignKey -> Order, related_name='payments')
   - `customer` (ForeignKey -> auth.User, null=True, blank=True)
   - `installment` (ForeignKey -> Installment, null=True, blank=True)
   - `payment_type` (CharField: `'FULL'` or `'INSTALLMENT'`)
   - `amount` (DecimalField)
   - `gateway` (CharField, default='Cashfree')
   - `gateway_order_id` (CharField, e.g. `CF_ORDER_123`)
   - `gateway_payment_id` (CharField, null=True)
   - `payment_session_id` (TextField, null=True)
   - `payment_method` (CharField, e.g. `UPI`, `CARD`, `NETBANKING`)
   - `status` (CharField: `'PENDING'`, `'PAID'`, `'FAILED'`)
   - `verification_status` (CharField: `'UNVERIFIED'`, `'VERIFIED'`)
   - `paid_at` (DateTimeField, null=True)
2. **`WebhookEvent`**:
   - `event_id`, `event_type`, `payload`, `processed` (BooleanField), `created_at`.

### D. `apps/accounts/models.py`
1. **`UserProfile`**:
   - `user` (OneToOneField -> auth.User, related_name='profile')
   - `full_name` (CharField, 150)
   - `phone` (CharField, 15, blank=True)
   - `role` (CharField: `'customer'` or `'admin'`, default='customer')
   - `auth_provider` (CharField: `'email'` or `'google'`)
   - `google_id` (CharField, blank=True)
   - `avatar_url` (URLField, blank=True)
   - `saved_addresses` (JSONField, default=list)
   - `cart_items` (JSONField, default=list)
   - `wishlist_ids` (JSONField, default=list)
   - `created_at`, `updated_at` (DateTimeField)

### E. `apps/core/models.py`
1. **`WebsiteSettings` (Singleton / Key-Value CMS)**:
   - `website_name` (CharField, default="Glory Furniture Hub")
   - `tagline` (CharField)
   - `contact_email` (EmailField)
   - `contact_phone` (CharField)
   - `whatsapp_number` (CharField)
   - `address` (TextField)
   - `copyright_text` (CharField)
   - `facebook_url`, `instagram_url`, `youtube_url`, `maps_url` (URLField)
   - `footer_about_text` (TextField)

---

## 4. MULTI-TENANT CUSTOMER DATA ISOLATION & ZERO DATA LOSS

### Critical Security Engine (`apps/bookings/services.py` -> `OrderAccessControl`)
Under NO circumstances may Customer A see, copy, share, export, or access Customer B's order records, personal details, delivery addresses, phone numbers, or payment transactions.

```python
class OrderAccessControl:
    @staticmethod
    def check_order_access(request, order):
        if not order:
            return False

        # 1. Staff & Superusers & Studio Admin role
        if request.user.is_authenticated and (request.user.is_staff or request.user.is_superuser or (getattr(request.user, 'profile', None) and request.user.profile.is_admin)):
            return True
        if request.session.get('glory_role') == 'admin':
            return True

        # 2. Authenticated Customer: strict ownership
        if request.user.is_authenticated:
            if order.user_id:
                return order.user_id == request.user.id
            # Auto-claim unassigned order placed with this verified email
            if request.user.email and order.email and request.user.email.strip().lower() == order.email.strip().lower():
                order.user = request.user
                order.save(update_fields=['user'])
                return True
            return False

        # 3. Unauthenticated / Guest: strictly forbidden from accessing registered user orders
        if order.user_id is not None:
            return False

        # Guest order must be tracked in active session AND match email
        tracked_orders = request.session.get('glory_customer_order_ids', [])
        session_email = request.session.get('glory_user_email')
        if order.id in tracked_orders:
            if session_email and order.email:
                return session_email.strip().lower() == order.email.strip().lower()
            return True

        return False
```

### Zero Data Loss & Auto-Claiming (`sync_user_session`)
When a customer logs in or registers:
1. `Order.objects.filter(user__isnull=True, email__iexact=user.email.strip()).update(user=user)` links any guest orders placed with that email.
2. `request.session['glory_customer_order_ids'] = list(Order.objects.filter(user=user).values_list('id', flat=True))` ensures the session strictly contains ONLY this customer's orders.
3. On logout: `request.session.flush()` immediately purges all cookies and session keys so shared computers cannot leak data.

### Elimination of Unwanted Fallbacks
- In `customer_orders_view` and `customer_home_view`: **NEVER** fall back to `Order.objects.all()` or `Order.objects.first()` or `Booking.objects.all()`.
- If an account has 0 orders, it MUST render the clean empty state ("No Orders Placed Yet") with `total_orders = 0` and `latest_order = None`.

### IDOR Route Protection
All endpoints accepting order or booking identifiers must strictly validate ownership and return `HttpResponseForbidden` (403) or redirect:
- `/customer/orders/<order_number>/` -> `OrderAccessControl.check_order_access`
- `/booking-confirmation/<booking_id>/` -> `OrderAccessControl.check_order_access`
- `/bookings/<booking_id>/` -> `OrderAccessControl.check_order_access`
- `/payments/checkout/<order_number>/` -> `OrderAccessControl.check_order_access`
- `/guide/?order=<order_id>` -> `OrderAccessControl.check_order_access` (if unauthorized, renders generic guide without leaking the order).

---

## 5. AUTHENTICATION & ROLE-BASED ACCESS CONTROL (RBAC)

### Middleware (`apps/accounts/middleware.py`)
- Unauthenticated visitors must start at `/register/` (or browse public storefront `/`, `/catalog`, `/product/*`, `/about`, `/contact`).
- Role segregation:
  - `role = 'customer'`: Permitted only on storefront and customer portal (`/customer/*`, `/orders/`, `/profile/`). Visiting `/admin/*` redirects to home with "Access Denied".
  - `role = 'admin'`: Dedicated studio admin console (`/admin/dashboard/`, `/admin/orders/`, `/admin/customers/`, `/admin/settings/`). If visiting `/admin/login/` while authenticated, redirects to dashboard. If visiting storefront `/`, redirects to `/admin/dashboard/`.
- Authenticated patrons are strictly forbidden from inheriting `role = 'admin'` via session bleed.

---

## 6. STOREFRONT & CUSTOMER SHOPPING EXPERIENCE

### Home Page (`/`)
- Hero Section: High-converting luxury Burma Teak Furniture headline, white-glove warranty badge, CTA to catalog.
- Category Grid: 5 Handcrafted Category Cards (Beds, Sofas, Dining Suites, Dressing Tables, Diwan Cots).
- Featured Pieces Carousel: Live products with direct wood type, MRP discount calculation, and Quick Order CTA.
- Timber Workshop Trust Badges: Seasoned timber moisture control (<12%), traditional mortise and tenon joinery seal, direct factory pricing.

### Product Catalog (`/catalog/`)
- Real-time search by piece title, wood type, and room category.
- Filters: Price range slider, wood finish swatches, size options.
- Zero fake products: Every item loads from the persistent PostgreSQL `Product` table.

### Product Detail View (`/product/<id>/`)
- High-resolution Cloudinary image gallery with thumbnail switcher.
- Interactive Wood Finish Selector (Natural Teak, Dark Walnut, Honey Teak).
- Bed / Table Size Selector (King Size, Queen Size, 6-Seater, 8-Seater) with dynamic price calculation.
- Primary CTA: "Direct White-Glove Booking" -> redirects to Checkout Summary (`/checkout/?product=<id>&wood=...&size=...&qty=1`).

---

## 7. CHECKOUT & ADDRESS ENGINE (`apps/bookings/views.py`)

### Luxury 3-Step Checkout Flow
- **Step 1: Delivery Address & Scheduling**:
  - Full Name, Phone (strictly sanitized 10-digit mobile, never fake defaults), Email.
  - Delivery Address: Flat/House No, Street, Landmark, City, State, Pincode.
  - **No Fake Default Address**: Never auto-populate fake strings (e.g. `Plot 42, Jubilee Hills`). Address is loaded strictly from authenticated `user.profile.saved_addresses` or left blank for new patrons.
  - **HTML5 Geolocation Permission Autofill**: Interactive "Detect My Location" button. Requests browser geolocation permissions cleanly, calls `/api/reverse-geocode/`, and populates city, state, pincode. Graceful fallback on permission denial.
  - Delivery Slot Preference (Immediate Dispatch, Weekend Delivery, Pre-Festival Booking).
- **Step 2: Transparent Price Breakdown**:
  - Item Subtotal, Guaranteed 30% Studio Direct Discount, Free Hyderabad Delivery (₹0), 18% Included GST, Final Payable Total.
- **Step 3: Direct Order Creation**:
  - Automatically creates permanent `Order` in database, initializes `OrderStatusHistory` with `fulfillment_status='CONFIRMED'`, clears cart, and redirects to `/payments/checkout/<order_number>/`.

---

## 8. PAYMENT ENGINE & CASHFREE INTEGRATION (`apps/payments`)

### Two Decoupled Payment Modes
1. **Full Payment (100% Upfront)**:
   - Full order amount payable immediately via Cashfree web checkout.
   - On payment verification: `order.payment_status = 'FULLY_PAID'`, `order.paid_amount = order.total_amount`.
2. **3 Equal Installments (Image 1 Luxury Engine)**:
   - Exact integer & paise division across 3 milestones:
     - Part 1 (33.33%): Advance Timber & Workshop Slot Confirmation (Payable immediately).
     - Part 2 (33.33%): Wood Carving & Framework Inspection Completion.
     - Part 3 (33.34% + Rounding Paise): Final Polish & Dispatch Authorization.
   - **Guaranteed Invariant**: `inst1.amount + inst2.amount + inst3.amount == order.total_amount` (zero float drift).
   - Strict chronological validation: Part 2 cannot be paid until Part 1 is verified.

### Cashfree Gateway Integration
- Endpoint: `https://api.cashfree.com/pg/orders` (or Sandbox if configured).
- Headers: `x-client-id`, `x-client-secret`, `x-api-version: 2023-08-01`.
- Payloads: Clean sanitized 10-digit customer phone (`CashfreeService.sanitize_phone`), order ID, currency INR, return URL (`/payments/return/?order_id={order_id}`), notify URL (`/webhook/cashfree/`).
- Webhook Handler: Computes HMAC-SHA256 signature using raw request body and verifies against `x-webhook-signature`. Idempotent processing guarantees transactions are never counted twice.
- Printable Luxury Invoice Receipt: `/receipt/<payment_id>/` with print-to-PDF formatting, GSTIN, Burma teak timber craftsmanship seal.

---

## 9. FLIPKART-STYLE 5-STAGE WORKSHOP TRACKING

### 5-Stage Stepper Workflow
1. **`CONFIRMED`**: Order Verified & Seasoned Burma Teak Selected.
2. **`IN_PRODUCTION`**: Master Carpenter Framework & Joinery in Progress.
3. **`SHIPPED`**: Quality Inspected, Moisture Sealed & Dispatched.
4. **`OUT_FOR_DELIVERY`**: White-Glove Van En Route with Assembly Technicians.
5. **`DELIVERED`**: Installed in Patron Residence & 10-Year Warranty Activated.

- Available on Customer Order Detail (`/customer/orders/<order_number>/`) with real timestamps, status history logs, and wood care guides.

---

## 10. CUSTOMER PROFILE PAGE & PATRON HUB

### Clean Layout Specification (`templates/accounts/profile.html`)
The customer profile page is built around two primary, non-duplicated visual cards:
1. **Top Luxury Patron Hero Card**:
   - Glowing initial avatar (`user_initial`), verified patron checkmark badge.
   - Customer Full Name, Email, Phone.
   - 10-Year Guarantee and White-Glove Delivery badges.
   - Primary action buttons: "✏️ Edit Profile" (`customer_edit_profile`) and "🚪 Sign Out" (`logout`).
   - 4 High-Contrast Stat Chips: `📦 Total Orders` (`orders_count`), `❤️ Wishlist Items` (`wishlist_count`), `👑 Teak Club Tier` (Gold), `🛡️ Wood Standard` (100% Teak).
2. **Patron Hub Navigation Card (Red-Circled Menu)**:
   - 📦 **My Orders** (`{% url 'orders' %}`) &mdash; Live production tracking with live badge count (`orders_count`)
   - ❤️ **Saved Wishlist** (`{% url 'wishlist' %}`) &mdash; Curated teak favorites with live badge count (`wishlist_count`)
   - 📍 **Delivery Addresses** (`{% url 'address' %}`) &mdash; Doorstep coordinates
   - 📐 **Custom 3D Designs** (`{% url 'custom_request' %}`) &mdash; Bespoke timber joinery
   - ✏️ **Account Settings** (`{% url 'customer_edit_profile' %}`) &mdash; Update name, phone & details
3. **Strict Cleanliness Rules**:
   - Do NOT render horizontal pill buttons.
   - Do NOT render Workshop Production Activity cards on the profile page (all live tracking belongs in My Orders).
   - Do NOT render Carpenter Concierge banners on the profile page.
   - Do NOT duplicate the hero card or navigation menu.

---

## 11. BESPOKE 3D CUSTOM FURNITURE ENGINE (`apps/custom_orders`)
- Route: `/custom/` (`custom_request`)
- Custom design submission form: Room Category (Master Bedroom, Dining Hall, Living Room), Wood Grade (A-Grade Burma Teak, Royal Teak), Dimensions (L x W x H), Budget Brackets (₹25k-₹50k, ₹50k-₹1L, ₹1L-₹2L, ₹2L-₹5L, ₹5L+), Inspiration Blueprint Upload.
- Dedicated confirmation view with request ID.
- Strictly isolated to the submitting patron's verified email.

---

## 12. STUDIO ADMIN PORTAL & WEBSITE SETTINGS CMS (`apps/accounts`)

### Admin Sidebar Navigation
- **Executive Dashboard** (`/admin/dashboard/`): Revenue overview, active workshop pieces, customer metrics, recent payments.
- **Order Management** (`/admin/orders/`): Fulfillment status updater, workshop stage progression, customer tracking link generator.
- **Customer Directory** (`/admin/customers/`): Patron spending history, registered emails, verified phone numbers.
- **Product Catalog CMS** (`/admin/products/`): Add/edit timber items, upload images, set featured highlights.
- **Payment Analytics** (`/admin/payments/`): Full Cashfree transaction ledger with UTR numbers, payment method breakdown.
- **Website Settings & Footer CMS** (`/admin/settings/`):
  - Live editable Website Name and Tagline.
  - Live editable Official Studio Email(s).
  - Live editable Phone Number and WhatsApp Support Number.
  - Live editable Showroom Address.
  - Live editable Social Media Links (Instagram, Facebook, YouTube, Google Maps).
  - Live editable Footer Sections, About Text, and Copyright Notice.
  - **Zero Hardcoded Fake Strings**: Completely replaces any outdated phone numbers or placeholder addresses.

---

## 13. DEPLOYMENT & DEVOPS CONFIGURATION

### Production Environment (`Render.com`)
- **Service Type**: Web Service (`Python 3.12`)
- **Build Command**: `./build.sh`
  ```bash
  #!/usr/bin/env bash
  set -o errexit
  pip install --upgrade pip
  pip install -r requirements.txt
  python manage.py collectstatic --no-input
  python manage.py migrate
  ```
- **Start Command**: `gunicorn glory_furniture.wsgi:application --bind 0.0.0.0:$PORT --workers 3 --timeout 120`
- **Environment Variables**:
  - `DEBUG`: `False`
  - `SECRET_KEY`: High-entropy production string
  - `DATABASE_URL`: Managed PostgreSQL connection URI (`postgres://...`)
  - `CASHFREE_APP_ID`: Cashfree production Client ID
  - `CASHFREE_SECRET_KEY`: Cashfree production Secret Key
  - `CASHFREE_ENV`: `PROD` (or `TEST`)
  - `CLOUDINARY_URL`: `cloudinary://<api_key>:<api_secret>@<cloud_name>`
  - `ALLOWED_HOSTS`: `glory-furniture-hub.onrender.com,localhost,127.0.0.1`
  - `CSRF_TRUSTED_ORIGINS`: `https://glory-furniture-hub.onrender.com`

---

## 14. VERIFICATION & QUALITY ASSURANCE

### Automated Test Suite
- Run command: `python manage.py test`
- Must maintain **49/49 passing automated unit tests** covering:
  1. Cashfree signature verification & webhook idempotency.
  2. 3 Equal Installments math precision & sum invariant.
  3. Multi-tenant customer data isolation (Customer B 403 on Customer A checkout/order).
  4. IDOR defense on direct order URLs and booking confirmations.
  5. Empty state rendering for 0-order accounts.
  6. Auto-claim guest orders upon user login.
  7. Reschedule audit trails and workshop status transitions.

---
# END OF MASTER PROMPT
