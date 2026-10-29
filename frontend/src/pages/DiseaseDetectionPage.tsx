import React, { useState, useEffect, useRef } from 'react';
import { Link } from 'react-router-dom';
import { Layout } from '../components/Layout';
import { api } from '../services/api';
import type { 
  DiseaseDetectionResult, 
  DiseaseHistoryItem, 
  DiseaseModelStatus 
} from '../types';
import {
  UploadCloud,
  CheckCircle2,
  AlertTriangle,
  AlertCircle,
  RefreshCw,
  Trash2,
  ExternalLink,
  ShieldAlert,
  ShieldCheck,
  Clock,
  Sparkles,
  ChevronRight,
  Info,
  FileImage,
  Loader2,
  Activity
} from 'lucide-react';

const COMMON_CROPS = [
  'Tomato',
  'Potato',
  'Corn (Maize)',
  'Apple',
  'Grape',
  'Bell Pepper',
  'Strawberry',
  'Orange',
  'Peach',
  'Cherry',
  'Soybean',
  'Squash',
  'Blueberry',
  'Raspberry',
  'General / Other'
];

export const DiseaseDetectionPage: React.FC = () => {
  const [selectedCrop, setSelectedCrop] = useState('Tomato');
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);
  const [isDragging, setIsDragging] = useState(false);
  
  const [analyzing, setAnalyzing] = useState(false);
  const [currentResult, setCurrentResult] = useState<DiseaseDetectionResult | null>(null);
  const [error, setError] = useState<string | null>(null);
  
  const [modelStatus, setModelStatus] = useState<DiseaseModelStatus | null>(null);
  const [history, setHistory] = useState<DiseaseHistoryItem[]>([]);
  const [historyLoading, setHistoryLoading] = useState(true);
  const [selectedHistoryDetail, setSelectedHistoryDetail] = useState<DiseaseDetectionResult | null>(null);
  const [loadingDetailId, setLoadingDetailId] = useState<number | null>(null);
  const [deletingId, setDeletingId] = useState<number | null>(null);

  const fileInputRef = useRef<HTMLInputElement>(null);

  // Load Model Status and Detection History on mount
  useEffect(() => {
    loadModelStatus();
    loadHistory();
  }, []);

  // Cleanup object URLs to prevent memory leaks
  useEffect(() => {
    return () => {
      if (previewUrl && previewUrl.startsWith('blob:')) {
        URL.revokeObjectURL(previewUrl);
      }
    };
  }, [previewUrl]);

  const loadModelStatus = async () => {
    try {
      const status = await api.getModelStatus();
      setModelStatus(status);
    } catch {
      // Non-blocking status error
    }
  };

  const loadHistory = async () => {
    setHistoryLoading(true);
    try {
      const items = await api.getDetectionHistory(25, 0);
      setHistory(items);
    } catch (err: any) {
      console.error('Failed to load history', err);
    } finally {
      setHistoryLoading(false);
    }
  };

  const handleFileSelection = (file: File) => {
    setError(null);
    // Validate format
    const validTypes = ['image/jpeg', 'image/png', 'image/webp'];
    if (!validTypes.includes(file.type)) {
      setError('Please select a valid image file (JPG, PNG, or WebP).');
      return;
    }
    // Validate size (10 MB)
    if (file.size > 10 * 1024 * 1024) {
      setError('File size exceeds the 10 MB limit. Please choose a smaller image.');
      return;
    }

    if (previewUrl && previewUrl.startsWith('blob:')) {
      URL.revokeObjectURL(previewUrl);
    }

    setSelectedFile(file);
    setPreviewUrl(URL.createObjectURL(file));
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFileSelection(e.dataTransfer.files[0]);
    }
  };

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
  };

  const handleResetImage = () => {
    if (previewUrl && previewUrl.startsWith('blob:')) {
      URL.revokeObjectURL(previewUrl);
    }
    setSelectedFile(null);
    setPreviewUrl(null);
    setError(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  const handleAnalyze = async () => {
    if (!selectedFile) {
      setError('Please select or drop a crop leaf image to analyze.');
      return;
    }

    setAnalyzing(true);
    setError(null);
    setSelectedHistoryDetail(null);

    try {
      const result = await api.detectDisease(selectedCrop, selectedFile);
      setCurrentResult(result);
      // Reload history list so the new record appears immediately
      loadHistory();
      // Scroll smoothly to results
      setTimeout(() => {
        document.getElementById('analysis-results-section')?.scrollIntoView({ behavior: 'smooth' });
      }, 100);
    } catch (err: any) {
      setError(err.message || 'Analysis failed. Please try again.');
    } finally {
      setAnalyzing(false);
    }
  };

  const handleViewHistoryDetail = async (id: number) => {
    setLoadingDetailId(id);
    try {
      const detail = await api.getDetectionDetail(id);
      setSelectedHistoryDetail(detail);
      setCurrentResult(null); // Switch view to selected historical record
      setTimeout(() => {
        document.getElementById('analysis-results-section')?.scrollIntoView({ behavior: 'smooth' });
      }, 100);
    } catch (err: any) {
      setError(`Failed to retrieve record: ${err.message}`);
    } finally {
      setLoadingDetailId(null);
    }
  };

  const handleDeleteHistory = async (e: React.MouseEvent, id: number) => {
    e.stopPropagation();
    if (!window.confirm('Are you sure you want to delete this diagnosis record?')) {
      return;
    }

    setDeletingId(id);
    try {
      await api.deleteDetectionRecord(id);
      setHistory(prev => prev.filter(item => item.id !== id));
      if (currentResult?.id === id) {
        setCurrentResult(null);
      }
      if (selectedHistoryDetail?.id === id) {
        setSelectedHistoryDetail(null);
      }
    } catch (err: any) {
      alert(`Could not delete record: ${err.message}`);
    } finally {
      setDeletingId(null);
    }
  };

  const activeResult = selectedHistoryDetail || currentResult;

  return (
    <Layout activeTitle="Disease Detection">
      <div className="max-w-6xl mx-auto space-y-8 pb-12">
        {/* Page Header */}
        <div className="bg-white border border-[#e7ebe3] rounded-2xl p-6 md:p-8 shadow-xs">
          <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
            <div>
              <div className="flex items-center gap-2 text-[10px] font-bold text-[#8b958a] tracking-widest uppercase mb-1.5">
                <span className="w-2 h-2 rounded-full bg-[#37774b]"></span>
                CROP PATHOLOGY ENGINE
              </div>
              <h1 className="text-2xl md:text-3xl font-extrabold text-[#26332b] tracking-tight">
                Plant Disease Detection
              </h1>
              <p className="text-sm text-[#616e63] mt-2 max-w-2xl leading-relaxed">
                Upload clear photographs of crop leaves displaying lesions, discoloration, or wilt symptoms.
                CropGuard AI evaluates image characteristics through a fine-tuned MobileNetV2 neural vision classifier
                to suggest probable diagnostic matches alongside non-chemical management precautions.
              </p>
            </div>

            {/* Model Architecture Badge */}
            <div className="bg-[#f5f8f3] border border-[#dce6d5] rounded-xl p-3.5 flex flex-col gap-1 min-w-[210px]">
              <div className="flex items-center justify-between text-xs font-semibold text-[#26332b]">
                <span className="flex items-center gap-1.5">
                  <Activity className="w-3.5 h-3.5 text-[#37774b]" />
                  Active Model
                </span>
                <span className={`text-[10px] px-2 py-0.5 rounded-full font-bold ${
                  modelStatus?.is_configured 
                    ? 'bg-[#dcecc9] text-[#245c3a]' 
                    : 'bg-[#fee2e2] text-[#991b1b]'
                }`}>
                  {modelStatus?.is_configured ? 'CPU Ready' : 'Not Loaded'}
                </span>
              </div>
              <span className="text-[11px] text-[#707e72] font-mono">
                {modelStatus?.model_version || 'mobilenet_v2_plantvillage'}
              </span>
              <span className="text-[10px] text-[#869488]">
                {modelStatus?.total_classes || 38} disease & healthy classes supported
              </span>
            </div>
          </div>
        </div>

        {/* Global Error Banner */}
        {error && (
          <div className="bg-[#fef2f2] border border-[#fecaca] text-[#991b1b] rounded-xl p-4 flex items-start gap-3 text-sm animate-in fade-in">
            <AlertCircle className="w-5 h-5 shrink-0 mt-0.5" />
            <div className="flex-1">{error}</div>
            <button 
              onClick={() => setError(null)} 
              className="text-[#991b1b] hover:text-[#7f1d1d] text-xs font-bold uppercase tracking-wider"
            >
              Dismiss
            </button>
          </div>
        )}

        {/* Main Work Area: Upload Form & Live Results */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
          {/* Left Column: Upload & Parameters (5 cols) */}
          <div className="lg:col-span-5 space-y-6">
            <div className="bg-white border border-[#e7ebe3] rounded-2xl p-6 shadow-xs space-y-5">
              <h2 className="text-base font-bold text-[#26332b] flex items-center gap-2">
                <span>1. Select Crop & Image</span>
              </h2>

              {/* Crop Selection */}
              <div>
                <label className="block text-xs font-bold text-[#445046] mb-1.5 uppercase tracking-wider">
                  Target Crop Variety
                </label>
                <select
                  value={selectedCrop}
                  onChange={(e) => setSelectedCrop(e.target.value)}
                  className="w-full bg-[#f9faf7] border border-[#d6ddd1] text-[#26332b] text-sm rounded-xl px-3.5 py-2.5 focus:outline-hidden focus:ring-2 focus:ring-[#37774b] focus:border-transparent transition font-medium"
                >
                  {COMMON_CROPS.map((crop) => (
                    <option key={crop} value={crop}>{crop}</option>
                  ))}
                </select>
                <p className="text-[11px] text-[#78857a] mt-1.5">
                  Matching your photographed crop improves validation against the model's supported host catalog.
                </p>
              </div>

              {/* Drag and Drop Upload Area */}
              <div>
                <label className="block text-xs font-bold text-[#445046] mb-1.5 uppercase tracking-wider">
                  Leaf Photograph
                </label>

                {!previewUrl ? (
                  <div
                    onDrop={handleDrop}
                    onDragOver={handleDragOver}
                    onDragLeave={handleDragLeave}
                    onClick={() => fileInputRef.current?.click()}
                    className={`border-2 border-dashed rounded-2xl p-6 text-center cursor-pointer transition flex flex-col items-center justify-center gap-2 ${
                      isDragging 
                        ? 'border-[#37774b] bg-[#edf4e8]' 
                        : 'border-[#cfd8c9] bg-[#fafbf8] hover:border-[#37774b] hover:bg-[#f4f7f1]'
                    }`}
                  >
                    <div className="w-12 h-12 rounded-full bg-[#e6eee2] text-[#37774b] flex items-center justify-center mb-1">
                      <UploadCloud className="w-6 h-6" />
                    </div>
                    <div className="text-sm font-bold text-[#26332b]">
                      Click to upload or drag & drop
                    </div>
                    <p className="text-xs text-[#707e72]">
                      Supports JPG, JPEG, PNG, or WebP (max 10 MB)
                    </p>
                    <span className="text-[10px] text-[#8e9c8f] bg-white px-2.5 py-1 rounded-full border border-[#e1e7dc] mt-1">
                      Clear focus on affected leaf recommended
                    </span>
                  </div>
                ) : (
                  /* Image Preview Card */
                  <div className="relative rounded-2xl overflow-hidden border border-[#dce3d6] bg-[#1a201b] group">
                    <img
                      src={previewUrl}
                      alt="Crop leaf preview"
                      className="w-full h-64 object-contain bg-black/40"
                    />
                    <div className="absolute inset-0 bg-black/40 opacity-0 group-hover:opacity-100 transition flex items-center justify-center gap-3 backdrop-blur-xs">
                      <button
                        type="button"
                        onClick={() => fileInputRef.current?.click()}
                        className="px-3.5 py-1.5 bg-white text-[#26332b] rounded-lg text-xs font-bold shadow-md hover:bg-[#f0f4ee] flex items-center gap-1.5 cursor-pointer"
                      >
                        <RefreshCw className="w-3.5 h-3.5" /> Replace
                      </button>
                      <button
                        type="button"
                        onClick={handleResetImage}
                        className="px-3.5 py-1.5 bg-[#ef4444] text-white rounded-lg text-xs font-bold shadow-md hover:bg-[#dc2626] flex items-center gap-1.5 cursor-pointer"
                      >
                        <Trash2 className="w-3.5 h-3.5" /> Remove
                      </button>
                    </div>

                    <div className="absolute bottom-2 left-2 right-2 bg-black/70 backdrop-blur-xs text-white text-[11px] px-3 py-1.5 rounded-lg flex items-center justify-between">
                      <span className="truncate max-w-[180px]">{selectedFile?.name}</span>
                      <span>{selectedFile ? (selectedFile.size / (1024 * 1024)).toFixed(2) : 0} MB</span>
                    </div>
                  </div>
                )}

                <input
                  ref={fileInputRef}
                  type="file"
                  accept="image/jpeg,image/png,image/webp"
                  className="hidden"
                  onChange={(e) => {
                    if (e.target.files && e.target.files[0]) {
                      handleFileSelection(e.target.files[0]);
                    }
                  }}
                />
              </div>

              {/* Action Button */}
              <button
                type="button"
                disabled={!selectedFile || analyzing || (modelStatus !== null && !modelStatus.is_configured)}
                onClick={handleAnalyze}
                className={`w-full py-3.5 px-4 rounded-xl font-bold text-sm flex items-center justify-center gap-2 transition cursor-pointer shadow-md ${
                  !selectedFile || analyzing || (modelStatus !== null && !modelStatus.is_configured)
                    ? 'bg-[#c5cdc2] text-white cursor-not-allowed opacity-75 shadow-none'
                    : 'bg-[#245c3a] text-white hover:bg-[#1b462c] active:scale-[0.99]'
                }`}
              >
                {analyzing ? (
                  <>
                    <Loader2 className="w-4 h-4 animate-spin" />
                    <span>Analyzing Leaf Features with AI...</span>
                  </>
                ) : (
                  <>
                    <Sparkles className="w-4 h-4 text-[#ffd778]" />
                    <span>Analyze Image</span>
                  </>
                )}
              </button>

              {/* Quality & Methodology Note */}
              <div className="bg-[#f7f9f5] border border-[#e6ecdf] rounded-xl p-3 text-[11px] text-[#69756b] leading-relaxed flex items-start gap-2">
                <Info className="w-4 h-4 text-[#37774b] shrink-0 mt-0.5" />
                <span>
                  For highest diagnostic reliability, photograph a single leaf against a uniform, neutral background with diffuse daylight. Avoid extreme blur or shadows.
                </span>
              </div>
            </div>
          </div>

          {/* Right Column: Active Results (7 cols) */}
          <div className="lg:col-span-7 space-y-6" id="analysis-results-section">
            {activeResult ? (
              <div className="bg-white border border-[#e7ebe3] rounded-2xl p-6 md:p-8 shadow-xs space-y-6 animate-in fade-in">
                {/* Result Top Banner */}
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-5 border-b border-[#edf1e8]">
                  <div className="flex items-center gap-3">
                    <div className={`w-12 h-12 rounded-2xl flex items-center justify-center text-white ${
                      activeResult.is_healthy 
                        ? 'bg-[#2e7d32]' 
                        : 'bg-[#d97706]'
                    }`}>
                      {activeResult.is_healthy ? (
                        <ShieldCheck className="w-6 h-6" />
                      ) : (
                        <ShieldAlert className="w-6 h-6" />
                      )}
                    </div>
                    <div>
                      <div className="flex items-center gap-2">
                        <span className={`text-[10px] font-bold px-2 py-0.5 rounded-full uppercase tracking-wider ${
                          activeResult.is_healthy 
                            ? 'bg-[#e8f5e9] text-[#2e7d32]' 
                            : 'bg-[#fef3c7] text-[#b45309]'
                        }`}>
                          {activeResult.is_healthy ? 'Healthy Crop' : 'Pathology Identified'}
                        </span>
                        {selectedHistoryDetail && (
                          <span className="text-[10px] font-bold bg-[#edf2e8] text-[#556356] px-2 py-0.5 rounded-full">
                            Historical Record #{selectedHistoryDetail.id}
                          </span>
                        )}
                      </div>
                      <h2 className="text-xl md:text-2xl font-extrabold text-[#26332b] mt-0.5">
                        {activeResult.predicted_label}
                      </h2>
                    </div>
                  </div>

                  <div className="flex flex-col items-end">
                    <span className="text-xs text-[#808c81] font-medium">Confidence Score</span>
                    <div className="flex items-baseline gap-1">
                      <span className={`text-2xl font-black ${
                        activeResult.confidence >= 75 
                          ? 'text-[#245c3a]' 
                          : activeResult.confidence >= 50 
                            ? 'text-[#d97706]' 
                            : 'text-[#dc2626]'
                      }`}>
                        {activeResult.confidence}%
                      </span>
                    </div>
                  </div>
                </div>

                {/* Low Confidence or Crop Mismatch Warnings */}
                {activeResult.confidence < 60 && (
                  <div className="bg-[#fffbeb] border border-[#fef3c7] text-[#92400e] rounded-xl p-3.5 text-xs flex items-start gap-2.5">
                    <AlertTriangle className="w-4 h-4 shrink-0 mt-0.5 text-[#d97706]" />
                    <div>
                      <strong className="block font-bold mb-0.5">Moderate Inference Confidence</strong>
                      The model's confidence is below 60%. Visual leaf symptoms may be ambiguous or influenced by lighting. Please consult your local agronomy extension service before taking chemical action.
                    </div>
                  </div>
                )}

                {activeResult.crop_mismatch && (
                  <div className="bg-[#eff6ff] border border-[#dbeafe] text-[#1e40af] rounded-xl p-3.5 text-xs flex items-start gap-2.5">
                    <Info className="w-4 h-4 shrink-0 mt-0.5 text-[#3b82f6]" />
                    <div>
                      <strong className="block font-bold mb-0.5">Crop Category Notice</strong>
                      You selected <em>{activeResult.selected_crop}</em>, but the model identified symptoms typical of <em>{activeResult.crop}</em>. Please ensure the photographed leaf belongs to the chosen crop variety.
                    </div>
                  </div>
                )}

                {/* Top Probability Distribution */}
                {activeResult.top_classes && activeResult.top_classes.length > 0 && (
                  <div className="bg-[#f9faf7] border border-[#e8ede3] rounded-xl p-4 space-y-2.5">
                    <span className="text-xs font-bold text-[#4c584e] uppercase tracking-wider block">
                      Diagnostic Probability Ranking
                    </span>
                    <div className="space-y-2">
                      {activeResult.top_classes.map((cls, idx) => (
                        <div key={idx} className="space-y-1">
                          <div className="flex justify-between text-xs text-[#2b362d] font-medium">
                            <span className="truncate pr-2">{cls.label}</span>
                            <span className="font-bold text-[#37774b]">{cls.confidence}%</span>
                          </div>
                          <div className="w-full bg-[#e3e8de] h-1.5 rounded-full overflow-hidden">
                            <div 
                              className={`h-full rounded-full ${idx === 0 ? 'bg-[#37774b]' : 'bg-[#829987]'}`}
                              style={{ width: `${cls.confidence}%` }}
                            />
                          </div>
                        </div>
                      ))}
                    </div>
                    <p className="text-[10px] text-[#869287] mt-1 italic">
                      * Confidence scores reflect model pattern matches on training data, not an infallible diagnostic guarantee.
                    </p>
                  </div>
                )}

                {/* Reliable Reference Explanations */}
                {activeResult.disease_info && (
                  <div className="space-y-4">
                    <div>
                      <h3 className="text-xs font-bold text-[#738075] uppercase tracking-wider mb-1.5">
                        Botanical Explanation
                      </h3>
                      <p className="text-sm text-[#3b473d] leading-relaxed bg-[#fbfcf9] p-3.5 rounded-xl border border-[#edf1e8]">
                        {activeResult.disease_info.description}
                      </p>
                    </div>

                    {/* General Precautions and Next Steps */}
                    <div>
                      <h3 className="text-xs font-bold text-[#738075] uppercase tracking-wider mb-2">
                        Agronomic Precautions & Management Steps
                      </h3>
                      <ul className="space-y-2">
                        {activeResult.disease_info.precautions.map((prec, i) => (
                          <li key={i} className="text-xs text-[#313d33] flex items-start gap-2.5 bg-white border border-[#e7ebe2] p-2.5 rounded-xl">
                            <CheckCircle2 className="w-4 h-4 text-[#37774b] shrink-0 mt-0.5" />
                            <span className="leading-snug">{prec}</span>
                          </li>
                        ))}
                      </ul>
                    </div>

                    {/* Scientific Transparency Warning */}
                    <div className="bg-[#fafbf9] border border-[#e3ebd9] rounded-xl p-3.5 text-xs text-[#526054] space-y-1">
                      <strong className="block font-bold text-[#26332b]">Field Verification Note</strong>
                      <p className="leading-relaxed">
                        {activeResult.disease_info.expert_note}
                      </p>
                    </div>
                  </div>
                )}

                {/* Footer Metadata & Actions */}
                <div className="pt-4 border-t border-[#edf1e8] flex flex-col sm:flex-row sm:items-center justify-between gap-3 text-xs text-[#748275]">
                  <div className="flex items-center gap-1.5">
                    <Clock className="w-3.5 h-3.5" />
                    <span>Analyzed: {new Date(activeResult.created_at).toLocaleString()}</span>
                  </div>

                  <div className="flex items-center gap-2">
                    {/* Cross link to Plantopedia if available */}
                    {activeResult.plantopedia_plant_id && (
                      <Link
                        to={`/plantopedia?id=${activeResult.plantopedia_plant_id}`}
                        className="px-3 py-1.5 bg-[#edf4e8] text-[#245c3a] font-bold rounded-lg hover:bg-[#dfead7] transition flex items-center gap-1 text-xs"
                      >
                        <ExternalLink className="w-3.5 h-3.5" />
                        <span>View in Plantopedia</span>
                      </Link>
                    )}

                    <button
                      type="button"
                      onClick={handleResetImage}
                      className="px-3.5 py-1.5 bg-[#f4f6f1] text-[#26332b] font-bold rounded-lg hover:bg-[#e8ece3] transition text-xs cursor-pointer"
                    >
                      Analyze Another Leaf
                    </button>
                  </div>
                </div>
              </div>
            ) : (
              /* Empty State */
              <div className="bg-white border border-[#e7ebe3] rounded-2xl p-10 text-center shadow-xs flex flex-col items-center justify-center min-h-[380px]">
                <div className="w-16 h-16 rounded-3xl bg-[#f2f6ee] text-[#37774b] flex items-center justify-center mb-4">
                  <FileImage className="w-8 h-8 opacity-80" />
                </div>
                <h3 className="text-lg font-bold text-[#26332b]">
                  No Active Analysis
                </h3>
                <p className="text-xs text-[#758276] mt-1 max-w-sm leading-relaxed">
                  Upload an image of a diseased or suspected crop leaf on the left and click <strong>Analyze Image</strong> to generate an instant diagnosis.
                </p>
              </div>
            )}
          </div>
        </div>

        {/* Section 2: Detection History for Logged-In User */}
        <div className="bg-white border border-[#e7ebe3] rounded-2xl p-6 md:p-8 shadow-xs space-y-5">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 pb-4 border-b border-[#edf1e8]">
            <div>
              <h2 className="text-lg font-extrabold text-[#26332b] flex items-center gap-2">
                <span>Recent Disease Detections</span>
                <span className="text-xs font-bold bg-[#edf4e8] text-[#245c3a] px-2 py-0.5 rounded-full">
                  {history.length}
                </span>
              </h2>
              <p className="text-xs text-[#717e72] mt-0.5">
                Isolated diagnosis log linked securely to your CropGuard account.
              </p>
            </div>

            <button
              onClick={loadHistory}
              disabled={historyLoading}
              className="text-xs font-bold text-[#245c3a] hover:underline flex items-center gap-1.5 self-start cursor-pointer"
            >
              <RefreshCw className={`w-3.5 h-3.5 ${historyLoading ? 'animate-spin' : ''}`} />
              <span>Refresh History</span>
            </button>
          </div>

          {historyLoading ? (
            <div className="py-8 flex justify-center items-center gap-2 text-xs text-[#788579]">
              <Loader2 className="w-4 h-4 animate-spin text-[#37774b]" />
              <span>Loading historical diagnoses...</span>
            </div>
          ) : history.length === 0 ? (
            <div className="py-8 text-center text-xs text-[#828f83]">
              No previous detection records found. When you run leaf diagnostics, they will automatically be preserved here.
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-left border-collapse">
                <thead>
                  <tr className="border-b border-[#edf1e8] text-[11px] font-bold text-[#869287] uppercase tracking-wider">
                    <th className="py-3 px-3">Crop</th>
                    <th className="py-3 px-3">Predicted Label</th>
                    <th className="py-3 px-3">Status</th>
                    <th className="py-3 px-3">Confidence</th>
                    <th className="py-3 px-3">Date</th>
                    <th className="py-3 px-3 text-right">Actions</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-[#f2f5ee] text-xs">
                  {history.map((item) => (
                    <tr
                      key={item.id}
                      onClick={() => handleViewHistoryDetail(item.id)}
                      className={`hover:bg-[#f8faf6] transition cursor-pointer ${
                        selectedHistoryDetail?.id === item.id ? 'bg-[#edf4e8]/60 font-semibold' : ''
                      }`}
                    >
                      <td className="py-3 px-3 font-semibold text-[#26332b]">
                        {item.selected_crop}
                      </td>
                      <td className="py-3 px-3 text-[#313c32]">
                        {item.predicted_label}
                      </td>
                      <td className="py-3 px-3">
                        <span className={`text-[10px] font-bold px-2 py-0.5 rounded-full ${
                          item.is_healthy 
                            ? 'bg-[#e8f5e9] text-[#2e7d32]' 
                            : 'bg-[#fffbeb] text-[#b45309]'
                        }`}>
                          {item.is_healthy ? 'Healthy' : 'Diseased'}
                        </span>
                      </td>
                      <td className="py-3 px-3 font-bold text-[#26332b]">
                        {item.confidence}%
                      </td>
                      <td className="py-3 px-3 text-[#798579]">
                        {new Date(item.created_at).toLocaleDateString()}
                      </td>
                      <td className="py-3 px-3 text-right">
                        <div className="flex items-center justify-end gap-2">
                          <button
                            type="button"
                            onClick={(e) => {
                              e.stopPropagation();
                              handleViewHistoryDetail(item.id);
                            }}
                            disabled={loadingDetailId === item.id}
                            className="p-1.5 rounded-lg text-[#37774b] hover:bg-[#edf4e8] transition"
                            title="View diagnosis details"
                          >
                            {loadingDetailId === item.id ? (
                              <Loader2 className="w-3.5 h-3.5 animate-spin" />
                            ) : (
                              <ChevronRight className="w-3.5 h-3.5" />
                            )}
                          </button>
                          <button
                            type="button"
                            onClick={(e) => handleDeleteHistory(e, item.id)}
                            disabled={deletingId === item.id}
                            className="p-1.5 rounded-lg text-[#a8b3a7] hover:text-[#dc2626] hover:bg-[#fee2e2] transition"
                            title="Delete record"
                          >
                            {deletingId === item.id ? (
                              <Loader2 className="w-3.5 h-3.5 animate-spin text-[#dc2626]" />
                            ) : (
                              <Trash2 className="w-3.5 h-3.5" />
                            )}
                          </button>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>
    </Layout>
  );
};

export default DiseaseDetectionPage;
