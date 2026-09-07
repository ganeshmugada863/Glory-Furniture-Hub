import React, { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import Header from '../components/common/Header'
import Input from '../components/common/Input'
import Button from '../components/common/Button'
import { dataService } from '../services/dataService'
import { useAppStore } from '../store/useAppStore'
import { Sparkles, Upload, Check, ArrowRight, ArrowLeft, Ruler, Palette, DollarSign } from 'lucide-react'

export default function CustomRequestScreen() {
  const navigate = useNavigate()
  const { openAIChat, addCustomRequest, user } = useAppStore()

  const [step, setStep] = useState(1)
  const [unit, setUnit] = useState('cm') // cm or inches

  // Step 1 Form
  const [furnitureType, setFurnitureType] = useState('Dining Table')
  const [otherType, setOtherType] = useState('')
  const [room, setRoom] = useState('Dining Room')
  const [width, setWidth] = useState('200')
  const [depth, setDepth] = useState('100')
  const [height, setHeight] = useState('76')

  // Step 2 Form
  const [wood, setWood] = useState('Oak')
  const [finish, setFinish] = useState('Natural Honey Stain')
  const [style, setStyle] = useState('Modern Minimalist')
  const [notes, setNotes] = useState('')
  const [uploadedFiles, setUploadedFiles] = useState([])
  const [isUploading, setIsUploading] = useState(false)

  // Step 3 Form
  const [budget, setBudget] = useState('1000')
  const [requiredDate, setRequiredDate] = useState('2026-10-15')
  const [fullName, setFullName] = useState(user?.name || '')
  const [phone, setPhone] = useState(user?.phone || '')
  const [isSubmitting, setIsSubmitting] = useState(false)

  const handleFileUpload = async (e) => {
    const files = Array.from(e.target.files)
    if (files.length === 0) return

    setIsUploading(true)
    const uploadedUrls = []

    for (const file of files) {
      const { publicUrl } = await dataService.uploadReferenceImage(file)
      if (publicUrl) uploadedUrls.push(publicUrl)
    }

    setUploadedFiles(prev => [...prev, ...uploadedUrls].slice(0, 5))
    setIsUploading(false)
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setIsSubmitting(true)

    const reqId = `REQ-${Math.floor(1000 + Math.random() * 9000)}`

    const requestPayload = {
      id: reqId,
      furnitureType: furnitureType === 'Other' ? otherType : furnitureType,
      room,
      dimensions: `${width}${unit} W × ${depth}${unit} D × ${height}${unit} H`,
      wood,
      finish,
      style,
      budget: `$${budget}`,
      submittedDate: new Date().toISOString().split('T')[0],
      status: 'Under Review',
      referenceImages: uploadedFiles,
      description: notes || 'Custom specifications request'
    }

    const { data } = await dataService.createCustomRequest(requestPayload)

    setIsSubmitting(false)
    addCustomRequest(data || requestPayload)
    navigate('/custom-request-confirmation')
  }

  return (
    <div className="min-h-screen bg-cream-100 pb-28">
      <Header title="Custom Furniture Request" showBack={true} />

      {/* AI Assistant Callout Banner */}
      <div className="px-5 pt-3">
        <button
          onClick={() => openAIChat({ name: 'Custom Specification Assistant' })}
          className="w-full p-3 bg-gradient-to-r from-walnut-800 to-walnut-600 text-gold-400 font-semibold text-xs rounded-2xl shadow-sm flex items-center justify-between border border-gold-500/30 active-tap"
        >
          <div className="flex items-center gap-2">
            <Sparkles className="w-4 h-4 text-gold-400 animate-spin-slow" />
            <span className="text-white">Let GloryAI Help Design & Pre-fill Your Request</span>
          </div>
          <ArrowRight className="w-4 h-4 text-gold-400" />
        </button>
      </div>

      {/* Step Progress Bar */}
      <div className="px-5 my-4">
        <div className="flex items-center justify-between text-xs font-semibold text-walnut-800 mb-2">
          <span>Step {step} of 3</span>
          <span className="text-gold-600 font-bold">
            {step === 1 ? 'Dimensions & Room' : step === 2 ? 'Wood & Finish' : 'Budget & Contact'}
          </span>
        </div>
        <div className="w-full bg-cream-200 h-2 rounded-full overflow-hidden border border-walnut-200/50">
          <div
            className="bg-gold-500 h-full transition-all duration-300"
            style={{ width: `${(step / 3) * 100}%` }}
          />
        </div>
      </div>

      <form onSubmit={handleSubmit} className="px-5 space-y-4">
        {/* Step 1: Furniture & Dimensions */}
        {step === 1 && (
          <div className="bg-white p-4 rounded-2xl border border-walnut-100 shadow-card space-y-3 animate-fade-in">
            <h3 className="font-sans font-bold text-xs text-walnut-800 uppercase tracking-wider flex items-center gap-1.5">
              <Ruler className="w-3.5 h-3.5 text-gold-600" /> Furniture Type & Room
            </h3>

            <div>
              <label className="block text-[11px] font-semibold text-walnut-700 mb-1">Furniture Type</label>
              <select
                value={furnitureType}
                onChange={(e) => setFurnitureType(e.target.value)}
                className="w-full text-xs p-2.5 bg-cream-100 border border-walnut-200 rounded-xl"
              >
                <option value="Dining Table">Dining Table</option>
                <option value="Bed Frame">Bed Frame</option>
                <option value="Wardrobe & Armoire">Wardrobe & Armoire</option>
                <option value="Executive Desk">Executive Desk</option>
                <option value="Lounge Chair">Lounge Chair</option>
                <option value="Credenza & Buffet">Credenza & Buffet</option>
                <option value="Other">Other Custom Furniture</option>
              </select>
            </div>

            {furnitureType === 'Other' && (
              <Input
                label="Specify Custom Furniture"
                type="text"
                value={otherType}
                onChange={(e) => setOtherType(e.target.value)}
                placeholder="e.g. Spiral Wine Cabinet"
              />
            )}

            <div>
              <label className="block text-[11px] font-semibold text-walnut-700 mb-1">Target Room Space</label>
              <select
                value={room}
                onChange={(e) => setRoom(e.target.value)}
                className="w-full text-xs p-2.5 bg-cream-100 border border-walnut-200 rounded-xl"
              >
                <option value="Living Room">Living Room</option>
                <option value="Bedroom">Bedroom</option>
                <option value="Dining Room">Dining Room</option>
                <option value="Executive Office">Executive Office</option>
                <option value="Patio & Outdoor">Patio & Outdoor</option>
              </select>
            </div>

            <div className="pt-2">
              <div className="flex items-center justify-between mb-1.5">
                <label className="text-[11px] font-semibold text-walnut-700">Dimensions</label>
                <div className="flex items-center gap-1 text-[10px] bg-cream-200 p-0.5 rounded-lg border border-walnut-200">
                  <button
                    type="button"
                    onClick={() => setUnit('cm')}
                    className={`px-2 py-0.5 rounded-md font-bold ${unit === 'cm' ? 'bg-walnut-500 text-white' : 'text-softgray'}`}
                  >
                    cm
                  </button>
                  <button
                    type="button"
                    onClick={() => setUnit('in')}
                    className={`px-2 py-0.5 rounded-md font-bold ${unit === 'in' ? 'bg-walnut-500 text-white' : 'text-softgray'}`}
                  >
                    inches
                  </button>
                </div>
              </div>

              <div className="grid grid-cols-3 gap-2">
                <div>
                  <span className="text-[10px] text-softgray block">Width ({unit})</span>
                  <input
                    type="number"
                    value={width}
                    onChange={(e) => setWidth(e.target.value)}
                    className="w-full text-xs p-2 bg-cream-100 border border-walnut-200 rounded-xl text-center font-semibold"
                  />
                </div>
                <div>
                  <span className="text-[10px] text-softgray block">Depth ({unit})</span>
                  <input
                    type="number"
                    value={depth}
                    onChange={(e) => setDepth(e.target.value)}
                    className="w-full text-xs p-2 bg-cream-100 border border-walnut-200 rounded-xl text-center font-semibold"
                  />
                </div>
                <div>
                  <span className="text-[10px] text-softgray block">Height ({unit})</span>
                  <input
                    type="number"
                    value={height}
                    onChange={(e) => setHeight(e.target.value)}
                    className="w-full text-xs p-2 bg-cream-100 border border-walnut-200 rounded-xl text-center font-semibold"
                  />
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Step 2: Wood & Finish */}
        {step === 2 && (
          <div className="bg-white p-4 rounded-2xl border border-walnut-100 shadow-card space-y-3 animate-fade-in">
            <h3 className="font-sans font-bold text-xs text-walnut-800 uppercase tracking-wider flex items-center gap-1.5">
              <Palette className="w-3.5 h-3.5 text-gold-600" /> Wood Species & Styling
            </h3>

            <div>
              <label className="block text-[11px] font-semibold text-walnut-700 mb-1">Preferred Wood Species</label>
              <div className="grid grid-cols-2 gap-2">
                {['Mahogany', 'Teak', 'White Oak', 'American Walnut', 'Pine'].map(w => (
                  <button
                    key={w}
                    type="button"
                    onClick={() => setWood(w)}
                    className={`py-2 px-3 rounded-xl text-xs font-medium border text-left active-tap ${
                      wood === w ? 'bg-walnut-500 text-gold-400 border-walnut-500 font-semibold' : 'bg-cream-100 text-walnut-800 border-walnut-200'
                    }`}
                  >
                    {w}
                  </button>
                ))}
              </div>
            </div>

            <Input
              label="Finish / Stain Preference"
              type="text"
              value={finish}
              onChange={(e) => setFinish(e.target.value)}
              placeholder="e.g. Natural Honey, Dark Walnut Stain, Matte Clear"
            />

            <div>
              <label className="block text-[11px] font-semibold text-walnut-700 mb-1">Design Style</label>
              <select
                value={style}
                onChange={(e) => setStyle(e.target.value)}
                className="w-full text-xs p-2.5 bg-cream-100 border border-walnut-200 rounded-xl"
              >
                <option value="Modern Minimalist">Modern Minimalist</option>
                <option value="Classic Carved">Classic Carved</option>
                <option value="Rustic Farmhouse">Rustic Farmhouse</option>
                <option value="Mid-Century Modern">Mid-Century Modern</option>
              </select>
            </div>

            <div>
              <label className="block text-[11px] font-semibold text-walnut-700 mb-1">Upload Reference Photos (Up to 5)</label>
              <label className="border-2 border-dashed border-walnut-200 bg-cream-100 hover:bg-cream-200 p-4 rounded-2xl flex flex-col items-center justify-center cursor-pointer">
                <Upload className="w-6 h-6 text-gold-600 mb-1" />
                <span className="text-xs font-medium text-walnut-800">
                  {isUploading ? 'Uploading reference files...' : 'Tap to upload reference sketches or room photos'}
                </span>
                <input type="file" multiple accept="image/*" onChange={handleFileUpload} className="hidden" />
              </label>

              {uploadedFiles.length > 0 && (
                <div className="mt-2 flex flex-wrap gap-1">
                  {uploadedFiles.map((fn, idx) => (
                    <span key={idx} className="text-[10px] bg-walnut-500 text-gold-400 px-2 py-1 rounded-md font-medium truncate max-w-[120px]">
                      Photo #{idx + 1}
                    </span>
                  ))}
                </div>
              )}
            </div>

            <div>
              <label className="block text-[11px] font-semibold text-walnut-700 mb-1">Special Craftsmanship Notes</label>
              <textarea
                rows="2"
                value={notes}
                onChange={(e) => setNotes(e.target.value)}
                placeholder="Include custom drawer requirements, brass inlay preferences, or seating capacity."
                className="w-full text-xs p-2.5 bg-cream-100 border border-walnut-200 rounded-xl"
              />
            </div>
          </div>
        )}

        {/* Step 3: Budget & Contact */}
        {step === 3 && (
          <div className="bg-white p-4 rounded-2xl border border-walnut-100 shadow-card space-y-3 animate-fade-in">
            <h3 className="font-sans font-bold text-xs text-walnut-800 uppercase tracking-wider flex items-center gap-1.5">
              <DollarSign className="w-3.5 h-3.5 text-gold-600" /> Estimated Budget & Deadline
            </h3>

            <div>
              <div className="flex justify-between text-xs font-semibold text-walnut-800 mb-1">
                <span>Target Budget Estimate:</span>
                <span className="text-gold-600 font-bold">${budget}</span>
              </div>
              <input
                type="range"
                min="400"
                max="5000"
                step="100"
                value={budget}
                onChange={(e) => setBudget(e.target.value)}
                className="w-full accent-walnut-500"
              />
            </div>

            <div>
              <label className="block text-[11px] font-semibold text-walnut-700 mb-1">Required Completion Date</label>
              <input
                type="date"
                value={requiredDate}
                onChange={(e) => setRequiredDate(e.target.value)}
                className="w-full text-xs p-2.5 bg-cream-100 border border-walnut-200 rounded-xl"
              />
            </div>

            <div className="pt-2 border-t border-cream-200 space-y-2">
              <Input
                label="Full Name"
                type="text"
                required
                value={fullName}
                onChange={(e) => setFullName(e.target.value)}
                placeholder="Your full name"
              />

              <Input
                label="Phone / WhatsApp Number"
                type="tel"
                required
                value={phone}
                onChange={(e) => setPhone(e.target.value)}
                placeholder="+1 (555) 345-6789"
              />
            </div>
          </div>
        )}

        {/* Step Navigation Buttons */}
        <div className="flex items-center gap-3 pt-3">
          {step > 1 && (
            <Button
              type="button"
              variant="secondary"
              size="md"
              onClick={() => setStep(step - 1)}
              icon={ArrowLeft}
            >
              Back
            </Button>
          )}

          {step < 3 ? (
            <Button
              type="button"
              variant="primary"
              size="lg"
              onClick={() => setStep(step + 1)}
              className="flex-1"
              icon={ArrowRight}
            >
              Continue to Step {step + 1}
            </Button>
          ) : (
            <Button
              type="submit"
              variant="primary"
              size="lg"
              isLoading={isSubmitting}
              className="flex-1"
              icon={Check}
            >
              Submit Custom Request
            </Button>
          )}
        </div>
      </form>
    </div>
  )
}
