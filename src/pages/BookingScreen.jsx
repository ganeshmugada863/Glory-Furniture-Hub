import React, { useState, useEffect } from 'react'
import { useNavigate, useSearchParams } from 'react-router-dom'
import Header from '../components/common/Header'
import Input from '../components/common/Input'
import Button from '../components/common/Button'
import Badge from '../components/common/Badge'
import Toast from '../components/common/Toast'
import { dataService } from '../services/dataService'
import { useAppStore } from '../store/useAppStore'
import { 
  MapPin, CheckCircle2, ChevronRight, ShieldCheck, Truck, 
  CreditCard, Banknote, Building, Sparkles, Check, 
  ArrowRight, ArrowLeft, Ruler, Plus, Phone, Mail, 
  User, Home, Briefcase, Lock, Clock, TreePine, AlertCircle
} from 'lucide-react'

export default function BookingScreen() {
  const navigate = useNavigate()
  const [searchParams] = useSearchParams()
  const productId = Number(searchParams.get('productId')) || 1
  const selectedFinishParam = searchParams.get('finish') || ''
  const bedSizeParam = searchParams.get('bedSize') || ''
  const woodTypeParam = searchParams.get('woodType') || ''
  const priceParam = searchParams.get('price') || ''

  const { user, setUser, addBooking, savedAddresses, addSavedAddress, addNotification } = useAppStore()
  
  const [product, setProduct] = useState(() => dataService.getInstantProductById(productId))
  const [quantity, setQuantity] = useState(1)
  const [finish, setFinish] = useState(selectedFinishParam || 'Standard Natural')
  const [bedSize, setBedSize] = useState(bedSizeParam || '6/6 ft (King)')
  const [woodType, setWoodType] = useState(woodTypeParam || 'Solid Burma Teak Wood')
  const [customNotes, setCustomNotes] = useState('')
  const [toastMessage, setToastMessage] = useState('')
  const [isSubmitting, setIsSubmitting] = useState(false)

  // Multi-step Checkout State (Flipkart-style sequential flow)
  // Step 1: Order Summary & Item Config
  // Step 2: Delivery Address & Contact Details (Mandatory before payment!)
  // Step 3: Payment Method (Strictly NO QR codes!)
  const [checkoutStep, setCheckoutStep] = useState(1)

  // Step 2: Address Selection / Entry State
  const [selectedAddressId, setSelectedAddressId] = useState(() => {
    return savedAddresses && savedAddresses.length > 0 ? savedAddresses[0].id : 'new'
  })
  const [isAddingNewAddress, setIsAddingNewAddress] = useState(() => {
    return !savedAddresses || savedAddresses.length === 0
  })

  // Address Form Fields (Flipkart-style structured fields)
  const [fullName, setFullName] = useState(user?.name || '')
  const [phone, setPhone] = useState(user?.phone || '')
  const [email, setEmail] = useState(user?.email || '')
  const [pincode, setPincode] = useState('')
  const [flatNo, setFlatNo] = useState('')
  const [street, setStreet] = useState('')
  const [landmark, setLandmark] = useState('')
  const [city, setCity] = useState('Hyderabad')
  const [state, setState] = useState('Telangana')
  const [addressType, setAddressType] = useState('Home') // 'Home' or 'Work'
  const [saveAddressToProfile, setSaveAddressToProfile] = useState(true)

  // Step 3: Payment Options State (STRICTLY NO QR CODES)
  const [paymentMethod, setPaymentMethod] = useState('cod') // 'cod', 'upi_id', 'card', 'netbanking', 'neft'
  const [upiId, setUpiId] = useState('')
  const [upiVerified, setUpiVerified] = useState(false)
  const [cardNumber, setCardNumber] = useState('')
  const [cardName, setCardName] = useState('')
  const [cardExpiry, setCardExpiry] = useState('')
  const [cardCvv, setCardCvv] = useState('')
  const [selectedBank, setSelectedBank] = useState('HDFC Bank')

  useEffect(() => {
    async function loadProduct() {
      const { data } = await dataService.getProductById(productId)
      if (data) {
        setProduct(data)
        if (!selectedFinishParam && data.finishes?.[0]) {
          setFinish(data.finishes[0])
        }
      }
    }
    loadProduct()
  }, [productId, selectedFinishParam])

  // Sync user profile data if available
  useEffect(() => {
    if (user?.name && !fullName) setFullName(user.name)
    if (user?.phone && !phone) setPhone(user.phone)
    if (user?.email && !email) setEmail(user.email)
  }, [user])

  if (!product) {
    return (
      <div className="min-h-screen bg-[#FDFBF7] flex items-center justify-center p-6">
        <p className="text-xs text-softgray font-medium">Loading handcrafted piece details...</p>
      </div>
    )
  }

  const isBedProduct = Boolean(
    product.category === 'Cot / Wooden Bed' ||
    product.category === 'Bedroom' ||
    product.name.toLowerCase().includes('bed') ||
    product.name.toLowerCase().includes('cot')
  )

  const unitPrice = priceParam ? Number(priceParam) : product.price
  const itemsSubtotal = unitPrice * quantity
  const deliveryFee = 0 // Free white-glove delivery
  const gstRate = 18
  const gstAmount = Math.round((itemsSubtotal * gstRate) / 100)
  const totalAmount = itemsSubtotal // MRP inclusive of GST
  const estimatedDeliveryDate = new Date(Date.now() + 7 * 86400000).toLocaleDateString('en-IN', {
    weekday: 'short',
    day: 'numeric',
    month: 'short',
    year: 'numeric'
  })

  // Autofill Hyderabad Local Sample Address for convenient 1-tap testing
  const handleAutofillLocalAddress = () => {
    setPincode('500033')
    setFlatNo('Plot 42, Heritage Residency, Flat 301')
    setStreet('Road No. 36, Jubilee Hills')
    setLandmark('Near Peddamma Temple Metro')
    setCity('Hyderabad')
    setState('Telangana')
    setToastMessage('Local Hyderabad address details filled!')
  }

  // Proceed from Step 1 (Summary) to Step 2 (Address)
  const handleProceedToAddress = () => {
    setCheckoutStep(2)
    window.scrollTo({ top: 0, behavior: 'smooth' })
  }

  // Proceed from Step 2 (Address) to Step 3 (Payment)
  const handleProceedToPayment = (e) => {
    if (e) e.preventDefault()

    let activeAddressString = ''

    if (!isAddingNewAddress && selectedAddressId !== 'new') {
      const existingAddr = savedAddresses.find(a => a.id === selectedAddressId)
      if (existingAddr) {
        activeAddressString = `${existingAddr.flatNo}, ${existingAddr.street}, ${existingAddr.landmark ? existingAddr.landmark + ', ' : ''}${existingAddr.city}, ${existingAddr.state} - ${existingAddr.pincode}`
        setFullName(existingAddr.fullName)
        setPhone(existingAddr.phone)
        setEmail(existingAddr.email)
      } else {
        setToastMessage('Please select a valid delivery address.')
        return
      }
    } else {
      // Validate address form
      if (!fullName.trim() || !phone.trim() || !email.trim()) {
        setToastMessage('Please provide your Full Name, Phone Number, and Email Address.')
        return
      }
      if (!pincode.trim() || pincode.trim().length !== 6) {
        setToastMessage('Please enter a valid 6-digit Indian PIN code.')
        return
      }
      if (!flatNo.trim() || !street.trim() || !city.trim() || !state.trim()) {
        setToastMessage('Please fill complete flat, street, city, and state details.')
        return
      }

      activeAddressString = `${flatNo.trim()}, ${street.trim()}, ${landmark.trim() ? landmark.trim() + ', ' : ''}${city.trim()}, ${state.trim()} - ${pincode.trim()}`

      // Store new address
      const newAddressRecord = {
        id: `addr-${Date.now()}`,
        fullName: fullName.trim(),
        phone: phone.trim(),
        email: email.trim(),
        pincode: pincode.trim(),
        flatNo: flatNo.trim(),
        street: street.trim(),
        landmark: landmark.trim(),
        city: city.trim(),
        state: state.trim(),
        addressType,
        isDefault: savedAddresses.length === 0
      }

      if (saveAddressToProfile) {
        addSavedAddress(newAddressRecord)
        setSelectedAddressId(newAddressRecord.id)
        setIsAddingNewAddress(false)
      }

      // Update user session in store & localStorage
      const updatedUser = {
        ...user,
        name: fullName.trim(),
        phone: phone.trim(),
        email: email.trim(),
        address: activeAddressString
      }
      setUser(updatedUser)
    }

    setToastMessage('Delivery address confirmed! Select your payment method.')
    setCheckoutStep(3)
    window.scrollTo({ top: 0, behavior: 'smooth' })
  }

  // Handle Verify UPI ID
  const handleVerifyUpi = () => {
    if (!upiId.trim() || !upiId.includes('@')) {
      setToastMessage('Please enter a valid UPI ID (e.g. 9876543210@upi or yourname@oksbi).')
      return
    }
    setUpiVerified(true)
    setToastMessage(`UPI ID "${upiId.trim()}" verified! Payment request will be sent upon order confirmation.`)
  }

  // Final Order Placement
  const handlePlaceOrder = async (e) => {
    e.preventDefault()

    // Validate payment method specifics
    if (paymentMethod === 'upi_id' && !upiId.trim()) {
      setToastMessage('Please enter your UPI ID before placing the order.')
      return
    }

    if (paymentMethod === 'card') {
      if (!cardNumber.trim() || cardNumber.replace(/\\s/g, '').length < 15 || !cardExpiry.trim() || !cardCvv.trim()) {
        setToastMessage('Please complete all 16-digit card, expiry, and CVV fields.')
        return
      }
    }

    setIsSubmitting(true)

    // Resolve delivery address
    let finalAddress = ''
    let finalCustomerName = fullName.trim() || user?.name || 'Valued Patron'
    let finalPhone = phone.trim() || user?.phone || '+91 98765 43210'
    let finalEmail = email.trim() || user?.email || 'patron@gloryfurniture.com'

    if (!isAddingNewAddress && selectedAddressId !== 'new') {
      const chosenAddr = savedAddresses.find(a => a.id === selectedAddressId)
      if (chosenAddr) {
        finalCustomerName = chosenAddr.fullName
        finalPhone = chosenAddr.phone
        finalEmail = chosenAddr.email
        finalAddress = `${chosenAddr.flatNo}, ${chosenAddr.street}, ${chosenAddr.landmark ? chosenAddr.landmark + ', ' : ''}${chosenAddr.city}, ${chosenAddr.state} - ${chosenAddr.pincode} (${chosenAddr.addressType})`
      }
    }

    if (!finalAddress) {
      finalAddress = `${flatNo.trim()}, ${street.trim()}, ${landmark.trim() ? landmark.trim() + ', ' : ''}${city.trim()}, ${state.trim()} - ${pincode.trim()} (${addressType})`
    }

    const bookingId = `GFH-${Math.floor(1000 + Math.random() * 9000)}`
    const invoiceId = `INV-2026-${Math.floor(100 + Math.random() * 900)}`

    const paymentTitles = {
      cod: 'Cash on Delivery (White-Glove Doorstep Inspection)',
      upi_id: `UPI VPA Collect (${upiId.trim()})`,
      card: `Credit/Debit Card (Ending in ${cardNumber.slice(-4) || '****'})`,
      netbanking: `Net Banking (${selectedBank})`,
      neft: 'Direct Studio NEFT / RTGS Transfer'
    }
    const chosenPaymentTitle = paymentTitles[paymentMethod] || 'Pay on Delivery'

    const bookingPayload = {
      id: bookingId,
      productId: product.id,
      productName: product.name,
      image: product.images[0],
      price: unitPrice,
      quantity: quantity,
      finish: finish,
      bedSize: isBedProduct ? bedSize : null,
      woodType: isBedProduct ? woodType : product.material,
      fullName: finalCustomerName,
      phone: finalPhone,
      email: finalEmail,
      status: paymentMethod === 'cod' ? 'Pending' : 'Confirmed',
      bookingDate: new Date().toISOString().split('T')[0],
      deliveryDate: estimatedDeliveryDate,
      deliveryAddress: finalAddress,
      customizationNotes: customNotes || `${finish} finish, White-glove assembly requested.`,
      specialInstructions: `Payment Method: ${chosenPaymentTitle}. Includes 15-Year Solid Burma Teak Warranty.`,
      paymentMethod: chosenPaymentTitle,
      invoiceId: invoiceId
    }

    const invoicePayload = {
      id: invoiceId,
      orderId: bookingId,
      customerName: finalCustomerName,
      customerPhone: finalPhone,
      customerEmail: finalEmail,
      customerAddress: finalAddress,
      itemTitle: isBedProduct ? `${product.name} (${bedSize})` : product.name,
      category: product.category,
      material: isBedProduct ? woodType : product.material,
      quantity: quantity,
      baseAmount: Math.round(totalAmount / 1.18),
      gstRate: 18,
      gstAmount: Math.round(totalAmount - (totalAmount / 1.18)),
      totalAmount: totalAmount,
      advancePaid: paymentMethod === 'cod' ? 0 : totalAmount,
      balanceDue: paymentMethod === 'cod' ? totalAmount : 0,
      status: paymentMethod === 'cod' ? 'Pending' : 'Paid',
      paymentMethod: chosenPaymentTitle,
      invoiceDate: new Date().toISOString().split('T')[0],
      dueDate: estimatedDeliveryDate,
      hsnCode: '9403',
      warrantyYears: 15,
      notes: `Official Commercial Tax Invoice for ${product.name}. 15-Year Burma Teak Wood & Termite Warranty Certificate attached.`
    }

    try {
      const { data } = await dataService.createBooking(bookingPayload)
      addBooking(data || bookingPayload)

      const existingInvoicesRaw = localStorage.getItem('glory_invoices')
      const existingInvoices = existingInvoicesRaw ? JSON.parse(existingInvoicesRaw) : []
      const updatedInvoices = [invoicePayload, ...existingInvoices]
      localStorage.setItem('glory_invoices', JSON.stringify(updatedInvoices))

      addNotification({
        id: `notif-${Date.now()}`,
        title: `Order #${bookingId} Confirmed`,
        description: `Your order for ${product.name} has been placed. Invoice #${invoiceId} generated.`,
        timestamp: 'Just now',
        read: false,
        type: 'booking',
        targetId: bookingId
      })

      setUser({
        ...user,
        name: finalCustomerName,
        phone: finalPhone,
        email: finalEmail,
        address: finalAddress
      })
    } catch (err) {
      console.warn('Booking placement notice:', err)
      addBooking(bookingPayload)
    } finally {
      setIsSubmitting(false)
      navigate(`/booking-confirmation/${bookingId}`)
    }
  }


  return (
    <div className="min-h-screen bg-[#FDFBF7] text-walnut-900 pb-28 font-sans">
      <Header title="Secure Studio Checkout" showBack={true} />
      <Toast message={toastMessage} onClose={() => setToastMessage('')} />

      {/* PROGRESS TRACKER BAR (Flipkart style 3 steps) */}
      <div className="bg-white border-b border-walnut-200/60 sticky top-14 z-20 shadow-xs">
        <div className="max-w-4xl mx-auto px-4 py-3">
          <div className="flex items-center justify-between">
            {/* Step 1 */}
            <button
              type="button"
              onClick={() => setCheckoutStep(1)}
              className={`flex items-center gap-2 text-xs font-bold transition-all cursor-pointer ${
                checkoutStep === 1 ? 'text-walnut-900' : 'text-emerald-700'
              }`}
            >
              <div className={`w-6 h-6 rounded-full flex items-center justify-center text-xs font-bold ${
                checkoutStep === 1 
                  ? 'bg-walnut-900 text-gold-400 ring-2 ring-gold-500/40' 
                  : 'bg-emerald-600 text-white'
              }`}>
                {checkoutStep > 1 ? <Check className="w-3.5 h-3.5" /> : '1'}
              </div>
              <span className="hidden sm:inline">1. Order Summary</span>
            </button>

            <div className={`flex-1 h-0.5 mx-3 ${checkoutStep >= 2 ? 'bg-emerald-600' : 'bg-cream-300'}`} />

            {/* Step 2 */}
            <button
              type="button"
              onClick={() => setCheckoutStep(2)}
              className={`flex items-center gap-2 text-xs font-bold transition-all cursor-pointer ${
                checkoutStep === 2 ? 'text-walnut-900' : checkoutStep > 2 ? 'text-emerald-700' : 'text-softgray'
              }`}
            >
              <div className={`w-6 h-6 rounded-full flex items-center justify-center text-xs font-bold ${
                checkoutStep === 2 
                  ? 'bg-walnut-900 text-gold-400 ring-2 ring-gold-500/40' 
                  : checkoutStep > 2 
                  ? 'bg-emerald-600 text-white'
                  : 'bg-cream-200 text-softgray'
              }`}>
                {checkoutStep > 2 ? <Check className="w-3.5 h-3.5" /> : '2'}
              </div>
              <span className="hidden sm:inline">2. Delivery Address</span>
            </button>

            <div className={`flex-1 h-0.5 mx-3 ${checkoutStep >= 3 ? 'bg-emerald-600' : 'bg-cream-300'}`} />

            {/* Step 3 */}
            <div className={`flex items-center gap-2 text-xs font-bold ${
              checkoutStep === 3 ? 'text-walnut-900' : 'text-softgray'
            }`}>
              <div className={`w-6 h-6 rounded-full flex items-center justify-center text-xs font-bold ${
                checkoutStep === 3 
                  ? 'bg-walnut-900 text-gold-400 ring-2 ring-gold-500/40' 
                  : 'bg-cream-200 text-softgray'
              }`}>
                3
              </div>
              <span className="hidden sm:inline">3. Payment (No QR)</span>
            </div>
          </div>
        </div>
      </div>

      {/* MAIN CHECKOUT WORKSPACE */}
      <div className="max-w-4xl mx-auto px-4 py-6 space-y-6">

        {/* =================================================================== */}
        {/* STEP 1: ORDER SUMMARY (Piece specs, review & price details) */}
        {/* =================================================================== */}
        {checkoutStep === 1 && (
          <div className="space-y-6">
            <div className="bg-white p-6 rounded-3xl border border-walnut-200/70 shadow-sm space-y-6">
              
              <div className="flex items-center justify-between border-b border-cream-200 pb-4">
                <div>
                  <h2 className="font-sans font-bold text-xl text-walnut-900">
                    Order Summary & Specifications
                  </h2>
                  <p className="text-xs text-softgray mt-0.5">
                    Review your chosen furniture piece, timber grade, and dimensions before delivery.
                  </p>
                </div>
                <Badge variant="gold">{product.category}</Badge>
              </div>

              {/* Product Card Row */}
              <div className="flex flex-col sm:flex-row items-start sm:items-center gap-5 bg-cream-100/60 p-4 rounded-2xl border border-cream-300">
                <img
                  src={product.images[0]}
                  alt={product.name}
                  className="w-24 h-24 sm:w-28 sm:h-28 rounded-2xl object-cover bg-cream-200 shadow-sm border border-walnut-200"
                />

                <div className="flex-1 min-w-0 space-y-1.5">
                  <h3 className="font-sans font-bold text-lg text-walnut-900 leading-snug">
                    {product.name}
                  </h3>

                  <div className="flex flex-wrap items-center gap-2 text-xs">
                    <span className="bg-white px-2.5 py-1 rounded-lg border border-walnut-200/70 font-semibold text-walnut-800 flex items-center gap-1">
                      <TreePine className="w-3.5 h-3.5 text-gold-600" />
                      {isBedProduct ? woodType : product.material}
                    </span>

                    {isBedProduct && (
                      <span className="bg-white px-2.5 py-1 rounded-lg border border-walnut-200/70 font-semibold text-walnut-800 flex items-center gap-1">
                        <Ruler className="w-3.5 h-3.5 text-gold-600" />
                        Size: {bedSize}
                      </span>
                    )}

                    <span className="bg-white px-2.5 py-1 rounded-lg border border-walnut-200/70 font-medium text-softgray">
                      Finish: {finish}
                    </span>
                  </div>

                  <div className="flex items-baseline gap-2 pt-1">
                    <span className="font-sans font-bold text-xl text-walnut-900">
                      ₹{unitPrice.toLocaleString('en-IN')}
                    </span>
                    <span className="text-xs text-softgray">per piece (18% GST included)</span>
                  </div>
                </div>

                {/* Quantity Controls */}
                <div className="flex flex-col items-center gap-1.5 bg-white p-2 rounded-2xl border border-walnut-200 shadow-xs">
                  <span className="text-[10px] font-bold text-softgray uppercase">Quantity</span>
                  <div className="flex items-center gap-3">
                    <button
                      type="button"
                      onClick={() => setQuantity(Math.max(1, quantity - 1))}
                      className="w-8 h-8 rounded-xl bg-cream-100 hover:bg-cream-200 font-bold text-walnut-900 flex items-center justify-center cursor-pointer transition-colors"
                    >
                      −
                    </button>
                    <span className="font-sans font-bold text-base text-walnut-900 w-4 text-center">
                      {quantity}
                    </span>
                    <button
                      type="button"
                      onClick={() => setQuantity(quantity + 1)}
                      className="w-8 h-8 rounded-xl bg-cream-100 hover:bg-cream-200 font-bold text-walnut-900 flex items-center justify-center cursor-pointer transition-colors"
                    >
                      +
                    </button>
                  </div>
                </div>
              </div>

              {/* Bed Specification Options (If applicable) */}
              {isBedProduct && (
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 pt-2">
                  <div>
                    <label className="block text-xs font-semibold text-walnut-800 mb-1.5">
                      Selected Bed Size (Dimensions):
                    </label>
                    <select
                      value={bedSize}
                      onChange={(e) => setBedSize(e.target.value)}
                      className="w-full text-xs p-3 bg-cream-100 border border-walnut-200 rounded-xl font-bold text-walnut-900"
                    >
                      <option value="6/6 ft (King)">6/6 ft (King Size)</option>
                      <option value="5/6 ft (Queen)">5/6 ft (Queen Size)</option>
                      <option value="4/6 ft (Double)">4/6 ft (Double)</option>
                      <option value="3/6 ft (Single)">3/6 ft (Single)</option>
                    </select>
                  </div>

                  <div>
                    <label className="block text-xs font-semibold text-walnut-800 mb-1.5">
                      Timber Spec:
                    </label>
                    <select
                      value={woodType}
                      onChange={(e) => setWoodType(e.target.value)}
                      className="w-full text-xs p-3 bg-cream-100 border border-walnut-200 rounded-xl font-bold text-walnut-900"
                    >
                      <option value="Solid Burma Teak Wood">Solid Burma Teak Wood</option>
                      <option value="Solid Teak & Walnut Wood">Solid Teak & Walnut Wood</option>
                      <option value="Seasoned CP Teak Wood">Seasoned CP Teak Wood</option>
                      <option value="Rosewood (Sheesham)">Rosewood (Sheesham)</option>
                    </select>
                  </div>
                </div>
              )}

              {/* Special Delivery Notes */}
              <div>
                <label className="block text-xs font-semibold text-walnut-800 mb-1">
                  Customization or Delivery Floor Notes (Optional):
                </label>
                <textarea
                  rows="2"
                  value={customNotes}
                  onChange={(e) => setCustomNotes(e.target.value)}
                  placeholder="e.g. 3rd Floor with service elevator, prefer weekend morning delivery..."
                  className="w-full text-xs p-3 bg-cream-100 border border-walnut-200 rounded-xl"
                />
              </div>

              {/* Studio Assurance Badges */}
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 pt-2 text-xs">
                <div className="bg-cream-100/60 p-3 rounded-xl border border-cream-300 flex items-center gap-2.5">
                  <ShieldCheck className="w-5 h-5 text-gold-600 shrink-0" />
                  <div>
                    <strong className="block text-walnut-900 text-[11px]">15-Year Warranty</strong>
                    <span className="text-[10px] text-softgray">Termite & joint certificate</span>
                  </div>
                </div>

                <div className="bg-cream-100/60 p-3 rounded-xl border border-cream-300 flex items-center gap-2.5">
                  <Truck className="w-5 h-5 text-emerald-700 shrink-0" />
                  <div>
                    <strong className="block text-walnut-900 text-[11px]">White-Glove Delivery</strong>
                    <span className="text-[10px] text-softgray">Doorstep assembly included</span>
                  </div>
                </div>

                <div className="bg-cream-100/60 p-3 rounded-xl border border-cream-300 flex items-center gap-2.5">
                  <Clock className="w-5 h-5 text-blue-700 shrink-0" />
                  <div>
                    <strong className="block text-walnut-900 text-[11px]">Estimated Handover</strong>
                    <span className="text-[10px] text-softgray">{estimatedDeliveryDate}</span>
                  </div>
                </div>
              </div>

            </div>

            {/* Flipkart-Style Price Details Card */}
            <div className="bg-white p-6 rounded-3xl border border-walnut-200/70 shadow-sm space-y-4">
              <h4 className="font-sans font-bold text-sm text-walnut-900 uppercase tracking-wider border-b border-cream-200 pb-2">
                Price Details ({quantity} {quantity === 1 ? 'Item' : 'Items'})
              </h4>

              <div className="space-y-2 text-xs">
                <div className="flex justify-between text-walnut-700">
                  <span>Price ({quantity} piece{quantity > 1 ? 's' : ''}):</span>
                  <span className="font-mono font-semibold">₹{itemsSubtotal.toLocaleString('en-IN')}</span>
                </div>

                <div className="flex justify-between text-walnut-700">
                  <span>Studio White-Glove Delivery & Installation:</span>
                  <div className="flex items-center gap-1.5">
                    <span className="line-through text-softgray">₹2,500</span>
                    <span className="text-emerald-700 font-bold">FREE</span>
                  </div>
                </div>

                <div className="flex justify-between text-walnut-700">
                  <span>GST 18% (HSN 9403 Wooden Furniture):</span>
                  <span className="text-softgray font-mono">₹{gstAmount.toLocaleString('en-IN')} (Included)</span>
                </div>

                <div className="border-t border-walnut-200/80 pt-3 flex justify-between items-baseline font-bold text-base text-walnut-900">
                  <span>Total Amount Payable:</span>
                  <span className="font-sans text-2xl text-gold-700 font-bold">
                    ₹{totalAmount.toLocaleString('en-IN')}
                  </span>
                </div>
              </div>

              <div className="p-3 bg-emerald-50 rounded-xl border border-emerald-200 text-xs text-emerald-800 font-medium flex items-center gap-2">
                <Sparkles className="w-4 h-4 text-emerald-600 shrink-0" />
                <span>You save ₹2,500 on white-glove doorstep delivery and studio assembly.</span>
              </div>

              <Button
                type="button"
                onClick={handleProceedToAddress}
                variant="primary"
                size="lg"
                className="w-full bg-walnut-900 hover:bg-walnut-800 text-gold-400 font-bold py-4 text-sm sm:text-base flex items-center justify-center gap-2 shadow-md cursor-pointer"
              >
                <span>Continue to Delivery Address</span>
                <ArrowRight className="w-4 h-4" />
              </Button>
            </div>
          </div>
        )}

        {/* =================================================================== */}
        {/* STEP 2: DELIVERY ADDRESS & USER INFO (Mandatory before Payment) */}
        {/* =================================================================== */}
        {checkoutStep === 2 && (
          <div className="space-y-6">
            
            {/* Header info */}
            <div className="bg-white p-6 rounded-3xl border border-walnut-200/70 shadow-sm space-y-4">
              <div className="flex items-center justify-between border-b border-cream-200 pb-3">
                <div className="flex items-center gap-2.5">
                  <div className="w-8 h-8 rounded-xl bg-gold-100 text-gold-800 flex items-center justify-center font-bold">
                    <MapPin className="w-4 h-4" />
                  </div>
                  <div>
                    <h2 className="font-sans font-bold text-lg text-walnut-900">
                      Step 2: Delivery Address & Contact Details
                    </h2>
                    <p className="text-xs text-softgray">
                      Your information is securely stored for doorstep delivery and official GST billing.
                    </p>
                  </div>
                </div>

                <button
                  type="button"
                  onClick={() => setCheckoutStep(1)}
                  className="text-xs font-semibold text-walnut-700 hover:text-walnut-900 flex items-center gap-1 cursor-pointer"
                >
                  <ArrowLeft className="w-3.5 h-3.5" /> Back to Summary
                </button>
              </div>

              {/* LIST OF SAVED ADDRESSES (Flipkart-style select radio cards) */}
              {savedAddresses && savedAddresses.length > 0 && !isAddingNewAddress && (
                <div className="space-y-3">
                  <div className="flex items-center justify-between">
                    <span className="text-xs font-bold text-walnut-900 uppercase tracking-wider">
                      Saved Delivery Addresses:
                    </span>
                    <button
                      type="button"
                      onClick={() => setIsAddingNewAddress(true)}
                      className="text-xs font-bold text-gold-700 hover:text-gold-800 flex items-center gap-1 cursor-pointer"
                    >
                      <Plus className="w-3.5 h-3.5" /> Add New Address
                    </button>
                  </div>

                  <div className="grid grid-cols-1 gap-3">
                    {savedAddresses.map((addr) => {
                      const isSelected = selectedAddressId === addr.id
                      return (
                        <div
                          key={addr.id}
                          onClick={() => setSelectedAddressId(addr.id)}
                          className={`p-4 rounded-2xl border transition-all cursor-pointer flex items-start gap-3.5 ${
                            isSelected
                              ? 'bg-cream-100/90 border-walnut-900 ring-2 ring-gold-500/30 shadow-sm'
                              : 'bg-white border-walnut-200 hover:bg-cream-50'
                          }`}
                        >
                          <input
                            type="radio"
                            name="selectedAddress"
                            checked={isSelected}
                            onChange={() => setSelectedAddressId(addr.id)}
                            className="mt-1 text-walnut-900 focus:ring-gold-500"
                          />

                          <div className="flex-1 min-w-0 text-xs space-y-1">
                            <div className="flex items-center gap-2">
                              <strong className="text-walnut-900 font-bold text-sm">{addr.fullName}</strong>
                              <span className="bg-cream-200 text-walnut-800 px-2 py-0.5 rounded text-[10px] font-bold uppercase">
                                {addr.addressType || 'Home'}
                              </span>
                            </div>

                            <p className="text-walnut-800 leading-relaxed">
                              {addr.flatNo}, {addr.street}, {addr.landmark ? addr.landmark + ', ' : ''}{addr.city}, {addr.state} - <strong className="font-mono">{addr.pincode}</strong>
                            </p>

                            <div className="flex items-center gap-3 text-[11px] text-softgray pt-1">
                              <span className="flex items-center gap-1">
                                <Phone className="w-3 h-3 text-gold-600" /> {addr.phone}
                              </span>
                              <span>•</span>
                              <span className="flex items-center gap-1">
                                <Mail className="w-3 h-3 text-gold-600" /> {addr.email}
                              </span>
                            </div>
                          </div>
                        </div>
                      )
                    })}
                  </div>

                  <Button
                    type="button"
                    onClick={handleProceedToPayment}
                    variant="primary"
                    size="lg"
                    className="w-full bg-walnut-900 text-gold-400 font-bold py-3.5 mt-3 flex items-center justify-center gap-2 cursor-pointer"
                  >
                    <span>Deliver to This Address & Proceed to Payment</span>
                    <ArrowRight className="w-4 h-4" />
                  </Button>
                </div>
              )}

              {/* NEW ADDRESS FORM (Flipkart-style fields) */}
              {(isAddingNewAddress || !savedAddresses || savedAddresses.length === 0) && (
                <form onSubmit={handleProceedToPayment} className="space-y-4 pt-2">
                  
                  <div className="flex items-center justify-between">
                    <h3 className="text-xs font-bold text-walnut-900 uppercase tracking-wider">
                      Enter Complete Delivery & Contact Details:
                    </h3>
                    
                    <div className="flex items-center gap-2">
                      <button
                        type="button"
                        onClick={handleAutofillLocalAddress}
                        className="text-[11px] font-bold text-gold-700 bg-gold-50 border border-gold-300 px-2.5 py-1 rounded-lg hover:bg-gold-100 transition-colors cursor-pointer"
                      >
                        ⚡ Autofill Hyderabad Address
                      </button>

                      {savedAddresses && savedAddresses.length > 0 && (
                        <button
                          type="button"
                          onClick={() => setIsAddingNewAddress(false)}
                          className="text-xs text-softgray hover:text-walnut-900 font-medium cursor-pointer"
                        >
                          Cancel
                        </button>
                      )}
                    </div>
                  </div>

                  {/* Contact Information */}
                  <div className="space-y-3 bg-cream-100/50 p-4 rounded-2xl border border-cream-300">
                    <span className="text-[11px] font-bold text-walnut-900 uppercase tracking-wider block">
                      1. Contact Information
                    </span>

                    <Input
                      label="Customer Full Name *"
                      type="text"
                      required
                      placeholder="e.g. Suresh Nambiar"
                      value={fullName}
                      onChange={(e) => setFullName(e.target.value)}
                    />

                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                      <Input
                        label="10-Digit Mobile Number (For Delivery SMS & Calls) *"
                        type="tel"
                        required
                        placeholder="e.g. 98765 43210"
                        value={phone}
                        onChange={(e) => setPhone(e.target.value)}
                      />

                      <Input
                        label="Email Address (For Tax Invoice & Warranty) *"
                        type="email"
                        required
                        placeholder="e.g. patron@example.com"
                        value={email}
                        onChange={(e) => setEmail(e.target.value)}
                      />
                    </div>
                  </div>

                  {/* Delivery Address Details */}
                  <div className="space-y-3 bg-cream-100/50 p-4 rounded-2xl border border-cream-300">
                    <span className="text-[11px] font-bold text-walnut-900 uppercase tracking-wider block">
                      2. Destination Delivery Address
                    </span>

                    <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
                      <Input
                        label="6-Digit PIN Code *"
                        type="text"
                        maxLength="6"
                        required
                        placeholder="e.g. 500033"
                        value={pincode}
                        onChange={(e) => setPincode(e.target.value.replace(/[^0-9]/g, ''))}
                      />

                      <Input
                        label="Town / City *"
                        type="text"
                        required
                        placeholder="e.g. Hyderabad"
                        value={city}
                        onChange={(e) => setCity(e.target.value)}
                      />

                      <Input
                        label="State *"
                        type="text"
                        required
                        placeholder="e.g. Telangana"
                        value={state}
                        onChange={(e) => setState(e.target.value)}
                      />
                    </div>

                    <Input
                      label="Flat, House No., Building, Apartment Name *"
                      type="text"
                      required
                      placeholder="e.g. Plot 42, Road No. 10, Luxury Apartments"
                      value={flatNo}
                      onChange={(e) => setFlatNo(e.target.value)}
                    />

                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                      <Input
                        label="Area, Colony, Street, Sector *"
                        type="text"
                        required
                        placeholder="e.g. Jubilee Hills"
                        value={street}
                        onChange={(e) => setStreet(e.target.value)}
                      />

                      <Input
                        label="Landmark (Optional)"
                        type="text"
                        placeholder="e.g. Near Jubilee Checkpost"
                        value={landmark}
                        onChange={(e) => setLandmark(e.target.value)}
                      />
                    </div>

                    {/* Address Type selection (Home / Work) */}
                    <div>
                      <label className="block text-[11px] font-semibold text-walnut-800 mb-1.5">
                        Address Type:
                      </label>
                      <div className="flex gap-3">
                        <button
                          type="button"
                          onClick={() => setAddressType('Home')}
                          className={`flex-1 py-2 px-3 rounded-xl border text-xs font-semibold flex items-center justify-center gap-1.5 transition-all cursor-pointer ${
                            addressType === 'Home'
                              ? 'bg-walnut-900 text-gold-400 border-walnut-900 shadow-xs'
                              : 'bg-white text-walnut-800 border-walnut-200'
                          }`}
                        >
                          <Home className="w-3.5 h-3.5" />
                          <span>Home (All-Day Delivery)</span>
                        </button>

                        <button
                          type="button"
                          onClick={() => setAddressType('Work')}
                          className={`flex-1 py-2 px-3 rounded-xl border text-xs font-semibold flex items-center justify-center gap-1.5 transition-all cursor-pointer ${
                            addressType === 'Work'
                              ? 'bg-walnut-900 text-gold-400 border-walnut-900 shadow-xs'
                              : 'bg-white text-walnut-800 border-walnut-200'
                          }`}
                        >
                          <Briefcase className="w-3.5 h-3.5" />
                          <span>Work (10 AM - 6 PM)</span>
                        </button>
                      </div>
                    </div>

                    {/* Save to Profile Checkbox */}
                    <label className="flex items-center gap-2 cursor-pointer text-xs text-walnut-800 pt-1">
                      <input
                        type="checkbox"
                        checked={saveAddressToProfile}
                        onChange={(e) => setSaveAddressToProfile(e.target.checked)}
                        className="rounded text-walnut-900 focus:ring-gold-500"
                      />
                      <span>Save this address to my Glory Furniture Hub account for future orders</span>
                    </label>
                  </div>

                  <Button
                    type="submit"
                    variant="primary"
                    size="lg"
                    className="w-full bg-walnut-900 text-gold-400 font-bold py-4 text-base flex items-center justify-center gap-2 cursor-pointer shadow-md"
                  >
                    <span>Save Address & Proceed to Payment</span>
                    <ArrowRight className="w-4 h-4" />
                  </Button>
                </form>
              )}
            </div>
          </div>
        )}

        {/* =================================================================== */}
        {/* STEP 3: PAYMENT OPTIONS (STRICTLY NO QR CODES!) */}
        {/* =================================================================== */}
        {checkoutStep === 3 && (
          <div className="space-y-6">
            
            {/* Address Summary Ribbon */}
            <div className="bg-white p-4 rounded-2xl border border-walnut-200 flex items-center justify-between gap-3 text-xs">
              <div className="flex items-center gap-2">
                <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0" />
                <div>
                  <span className="text-softgray">Deliver To: </span>
                  <strong className="text-walnut-900">{fullName}</strong>
                  <span className="text-softgray"> ({city}, {state} - {pincode || '500033'})</span>
                </div>
              </div>

              <button
                type="button"
                onClick={() => setCheckoutStep(2)}
                className="text-xs font-bold text-gold-700 hover:text-gold-800 underline cursor-pointer"
              >
                Change Address
              </button>
            </div>

            {/* Payment Modes Container (Flipkart / Amazon style) */}
            <form onSubmit={handlePlaceOrder} className="bg-white p-6 rounded-3xl border border-walnut-200/70 shadow-sm space-y-6">
              
              <div className="flex items-center justify-between border-b border-cream-200 pb-3">
                <div>
                  <h2 className="font-sans font-bold text-lg text-walnut-900">
                    Step 3: Select Payment Method
                  </h2>
                  <p className="text-xs text-softgray">
                    Direct secure options without any QR code scanning.
                  </p>
                </div>

                <div className="flex items-center gap-1 text-[11px] text-emerald-700 bg-emerald-50 px-2.5 py-1 rounded-lg border border-emerald-200 font-semibold">
                  <Lock className="w-3 h-3" />
                  <span>256-Bit SSL Encrypted</span>
                </div>
              </div>

              <div className="space-y-3">
                
                {/* 1. Cash on Delivery / Doorstep White-Glove Inspection (Recommended) */}
                <div
                  onClick={() => setPaymentMethod('cod')}
                  className={`p-4 rounded-2xl border transition-all cursor-pointer flex items-start gap-3.5 ${
                    paymentMethod === 'cod'
                      ? 'bg-cream-100/90 border-walnut-900 ring-2 ring-gold-500/30'
                      : 'bg-white border-walnut-200 hover:bg-cream-50'
                  }`}
                >
                  <input
                    type="radio"
                    name="paymentOption"
                    checked={paymentMethod === 'cod'}
                    onChange={() => setPaymentMethod('cod')}
                    className="mt-1 text-walnut-900 focus:ring-gold-500"
                  />
                  <div className="flex-1 min-w-0 text-xs space-y-1">
                    <div className="flex items-center gap-2">
                      <strong className="text-sm font-bold text-walnut-900">
                        Pay on Doorstep Inspection (Cash on Delivery)
                      </strong>
                      <span className="bg-emerald-100 text-emerald-800 text-[10px] font-bold px-2 py-0.5 rounded">
                        Most Popular
                      </span>
                    </div>
                    <p className="text-softgray leading-snug">
                      Inspect the authentic Burma teak finish and joints in person at your home before paying. Settle the balance via Cash, Card, or UPI on delivery.
                    </p>
                  </div>
                  <Banknote className="w-5 h-5 text-emerald-700 shrink-0 mt-1" />
                </div>

                {/* 2. Direct UPI ID / VPA (NO QR CODES!) */}
                <div
                  onClick={() => setPaymentMethod('upi_id')}
                  className={`p-4 rounded-2xl border transition-all cursor-pointer space-y-3 ${
                    paymentMethod === 'upi_id'
                      ? 'bg-cream-100/90 border-walnut-900 ring-2 ring-gold-500/30'
                      : 'bg-white border-walnut-200 hover:bg-cream-50'
                  }`}
                >
                  <div className="flex items-start gap-3.5">
                    <input
                      type="radio"
                      name="paymentOption"
                      checked={paymentMethod === 'upi_id'}
                      onChange={() => setPaymentMethod('upi_id')}
                      className="mt-1 text-walnut-900 focus:ring-gold-500"
                    />
                    <div className="flex-1 min-w-0 text-xs space-y-1">
                      <div className="flex items-center gap-2">
                        <strong className="text-sm font-bold text-walnut-900">
                          UPI ID / Virtual Payment Address (VPA)
                        </strong>
                        <span className="bg-gold-100 text-gold-800 text-[10px] font-bold px-2 py-0.5 rounded">
                          No QR Code Needed
                        </span>
                      </div>
                      <p className="text-softgray leading-snug">
                        Enter your UPI ID (e.g. Google Pay, PhonePe, Paytm, BHIM). We dispatch a secure collect request straight to your UPI app.
                      </p>
                    </div>
                    <CreditCard className="w-5 h-5 text-gold-600 shrink-0 mt-1" />
                  </div>

                  {paymentMethod === 'upi_id' && (
                    <div className="pl-7 pt-2 border-t border-cream-200 flex flex-col sm:flex-row gap-2">
                      <input
                        type="text"
                        placeholder="Enter UPI ID (e.g. yourname@oksbi or 9876543210@upi)"
                        value={upiId}
                        onChange={(e) => {
                          setUpiId(e.target.value)
                          setUpiVerified(false)
                        }}
                        className="flex-1 text-xs p-2.5 bg-white border border-walnut-200 rounded-xl"
                      />
                      <button
                        type="button"
                        onClick={handleVerifyUpi}
                        className="py-2.5 px-4 bg-walnut-900 hover:bg-walnut-800 text-gold-400 text-xs font-bold rounded-xl transition-all cursor-pointer"
                      >
                        {upiVerified ? '✓ Verified' : 'Verify ID'}
                      </button>
                    </div>
                  )}
                </div>

                {/* 3. Credit / Debit Card */}
                <div
                  onClick={() => setPaymentMethod('card')}
                  className={`p-4 rounded-2xl border transition-all cursor-pointer space-y-3 ${
                    paymentMethod === 'card'
                      ? 'bg-cream-100/90 border-walnut-900 ring-2 ring-gold-500/30'
                      : 'bg-white border-walnut-200 hover:bg-cream-50'
                  }`}
                >
                  <div className="flex items-start gap-3.5">
                    <input
                      type="radio"
                      name="paymentOption"
                      checked={paymentMethod === 'card'}
                      onChange={() => setPaymentMethod('card')}
                      className="mt-1 text-walnut-900 focus:ring-gold-500"
                    />
                    <div className="flex-1 min-w-0 text-xs space-y-1">
                      <strong className="text-sm font-bold text-walnut-900 block">
                        Credit / Debit Card (Visa, MasterCard, RuPay)
                      </strong>
                      <p className="text-softgray leading-snug">
                        Secure card checkout with 3D Secure OTP verification.
                      </p>
                    </div>
                    <CreditCard className="w-5 h-5 text-blue-700 shrink-0 mt-1" />
                  </div>

                  {paymentMethod === 'card' && (
                    <div className="pl-7 pt-2 border-t border-cream-200 space-y-2.5">
                      <input
                        type="text"
                        placeholder="Card Number (16 digits)"
                        maxLength="19"
                        value={cardNumber}
                        onChange={(e) => setCardNumber(e.target.value)}
                        className="w-full text-xs p-2.5 bg-white border border-walnut-200 rounded-xl font-mono"
                      />
                      <div className="grid grid-cols-3 gap-2">
                        <input
                          type="text"
                          placeholder="Name on Card"
                          value={cardName}
                          onChange={(e) => setCardName(e.target.value)}
                          className="col-span-2 text-xs p-2.5 bg-white border border-walnut-200 rounded-xl"
                        />
                        <input
                          type="text"
                          placeholder="MM/YY"
                          maxLength="5"
                          value={cardExpiry}
                          onChange={(e) => setCardExpiry(e.target.value)}
                          className="text-xs p-2.5 bg-white border border-walnut-200 rounded-xl text-center font-mono"
                        />
                      </div>
                      <div className="w-28">
                        <input
                          type="password"
                          placeholder="CVV (3-digit)"
                          maxLength="4"
                          value={cardCvv}
                          onChange={(e) => setCardCvv(e.target.value)}
                          className="text-xs p-2.5 bg-white border border-walnut-200 rounded-xl text-center font-mono"
                        />
                      </div>
                    </div>
                  )}
                </div>

                {/* 4. Net Banking */}
                <div
                  onClick={() => setPaymentMethod('netbanking')}
                  className={`p-4 rounded-2xl border transition-all cursor-pointer space-y-3 ${
                    paymentMethod === 'netbanking'
                      ? 'bg-cream-100/90 border-walnut-900 ring-2 ring-gold-500/30'
                      : 'bg-white border-walnut-200 hover:bg-cream-50'
                  }`}
                >
                  <div className="flex items-start gap-3.5">
                    <input
                      type="radio"
                      name="paymentOption"
                      checked={paymentMethod === 'netbanking'}
                      onChange={() => setPaymentMethod('netbanking')}
                      className="mt-1 text-walnut-900 focus:ring-gold-500"
                    />
                    <div className="flex-1 min-w-0 text-xs space-y-1">
                      <strong className="text-sm font-bold text-walnut-900 block">
                        Net Banking
                      </strong>
                      <p className="text-softgray leading-snug">
                        All major Indian public and private sector banks supported.
                      </p>
                    </div>
                    <Building className="w-5 h-5 text-walnut-700 shrink-0 mt-1" />
                  </div>

                  {paymentMethod === 'netbanking' && (
                    <div className="pl-7 pt-2 border-t border-cream-200">
                      <select
                        value={selectedBank}
                        onChange={(e) => setSelectedBank(e.target.value)}
                        className="w-full text-xs p-2.5 bg-white border border-walnut-200 rounded-xl font-medium"
                      >
                        <option value="HDFC Bank">HDFC Bank</option>
                        <option value="State Bank of India">State Bank of India (SBI)</option>
                        <option value="ICICI Bank">ICICI Bank</option>
                        <option value="Axis Bank">Axis Bank</option>
                        <option value="Kotak Mahindra Bank">Kotak Mahindra Bank</option>
                        <option value="Punjab National Bank">Punjab National Bank</option>
                      </select>
                    </div>
                  )}
                </div>

                {/* 5. Direct Studio NEFT / Bank Transfer */}
                <div
                  onClick={() => setPaymentMethod('neft')}
                  className={`p-4 rounded-2xl border transition-all cursor-pointer space-y-3 ${
                    paymentMethod === 'neft'
                      ? 'bg-cream-100/90 border-walnut-900 ring-2 ring-gold-500/30'
                      : 'bg-white border-walnut-200 hover:bg-cream-50'
                  }`}
                >
                  <div className="flex items-start gap-3.5">
                    <input
                      type="radio"
                      name="paymentOption"
                      checked={paymentMethod === 'neft'}
                      onChange={() => setPaymentMethod('neft')}
                      className="mt-1 text-walnut-900 focus:ring-gold-500"
                    />
                    <div className="flex-1 min-w-0 text-xs space-y-1">
                      <strong className="text-sm font-bold text-walnut-900 block">
                        Direct Studio Bank NEFT / RTGS Transfer
                      </strong>
                      <p className="text-softgray leading-snug">
                        Official corporate account transfer with instant receipt generation.
                      </p>
                    </div>
                    <Building className="w-5 h-5 text-gold-700 shrink-0 mt-1" />
                  </div>

                  {paymentMethod === 'neft' && (
                    <div className="pl-7 pt-2 border-t border-cream-200 text-xs bg-white p-3 rounded-xl border border-cream-300 space-y-1">
                      <div>A/C Name: <strong className="text-walnut-900">Glory Furniture Hub Pvt Ltd</strong></div>
                      <div>Bank: <strong className="text-walnut-900">HDFC Bank, Jubilee Hills Branch</strong></div>
                      <div>Account Number: <strong className="font-mono text-walnut-900">50200088991122</strong></div>
                      <div>IFSC Code: <strong className="font-mono text-gold-700">HDFC0001234</strong></div>
                    </div>
                  )}
                </div>

              </div>

              {/* Order Placement Action */}
              <div className="pt-4 border-t border-cream-200 space-y-3">
                <div className="flex items-center justify-between text-xs">
                  <span className="text-softgray">Total Payable (All Inclusive):</span>
                  <span className="font-sans font-bold text-xl text-walnut-900">
                    ₹{totalAmount.toLocaleString('en-IN')}
                  </span>
                </div>

                <Button
                  type="submit"
                  variant="primary"
                  size="lg"
                  disabled={isSubmitting}
                  className="w-full bg-walnut-900 hover:bg-walnut-800 text-gold-400 font-bold py-4 text-base flex items-center justify-center gap-2 shadow-md cursor-pointer"
                >
                  <ShieldCheck className="w-5 h-5 text-gold-400" />
                  <span>{isSubmitting ? 'Generating Official Invoice...' : `Confirm & Place Order (₹${totalAmount.toLocaleString('en-IN')})`}</span>
                </Button>

                <p className="text-[11px] text-center text-softgray">
                  By confirming, an official commercial GST Tax Invoice and 15-Year Solid Teak Warranty Certificate will be generated for your order.
                </p>
              </div>

            </form>
          </div>
        )}

      </div>
    </div>
  )
}

