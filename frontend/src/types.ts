export interface User {
  id: number;
  full_name: string;
  email: string;
  farm_location?: string;
  created_at: string;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
  user: User;
}

export interface Plant {
  id: number;
  common_name: string;
  scientific_name: string;
  family?: string;
  category?: string;
  description: string;
  sunlight: string;
  watering: string;
  soil_requirements: string;
  climate: string;
  temperature_range?: string;
  fertilizer?: string;
  season?: string;
  growing_conditions: string;
  common_diseases?: string;
  common_pests?: string;
  prevention_treatment?: string;
  facts?: string;
  image_url?: string;
  source_type: 'curated_local' | 'external_api';
  data_source?: string;
  external_api_id?: string;
  created_at?: string;
  updated_at?: string;
  is_bookmarked: boolean;
}

export interface PlantSearchResponse {
  items: Plant[];
  total: number;
  query?: string;
  api_source: string;
  page?: number;
  page_size?: number;
}

export interface AssistantMessage {
  id: number;
  conversation_id: number;
  role: 'user' | 'assistant' | 'system';
  content: string;
  model_metadata?: string;
  created_at: string;
}

export interface ConversationSummary {
  id: number;
  title: string;
  plant_id?: number;
  plant_common_name?: string;
  created_at: string;
  updated_at: string;
  message_count: number;
  last_message?: string;
}

export interface ConversationDetail {
  id: number;
  title: string;
  plant_id?: number;
  plant?: Plant;
  created_at: string;
  updated_at: string;
  messages: AssistantMessage[];
}

export interface ChatResponse {
  conversation_id: number;
  title: string;
  plant_id?: number;
  plant_common_name?: string;
  message: AssistantMessage;
  grounding_sources: string[];
  model: string;
  is_fallback: boolean;
}

export interface RecentBookmark {
  plant_id: number;
  common_name: string;
  scientific_name: string;
  image_url?: string;
  bookmarked_at: string;
}

export interface DashboardSummary {
  user_name: string;
  total_saved_plants: number;
  recent_bookmarks: RecentBookmark[];
  quick_tips: string[];
  system_status: string;
}

export interface DemoStore {
  id: string;
  name: string;
  category: string;
  address: string;
  phone: string;
  sample_products: string[];
  operating_hours: string;
  is_demo: boolean;
}

export interface TopClassProbability {
  label: string;
  confidence: number;
  probability: number;
}

export interface DiseaseInfo {
  crop: string;
  scientific_name: string;
  is_healthy: boolean;
  description: string;
  precautions: string[];
  expert_note: string;
  plantopedia_crop?: string;
}

export interface DiseaseDetectionResult {
  id: number;
  selected_crop: string;
  predicted_label: string;
  confidence: number;
  is_healthy: boolean;
  model_version: string;
  created_at: string;
  image_reference?: string;
  crop?: string;
  crop_mismatch: boolean;
  top_classes?: TopClassProbability[];
  disease_info?: DiseaseInfo;
  plantopedia_plant_id?: number;
}

export interface DiseaseHistoryItem {
  id: number;
  selected_crop: string;
  predicted_label: string;
  confidence: number;
  is_healthy: boolean;
  model_version: string;
  status: string;
  image_reference?: string;
  created_at: string;
}

export interface DiseaseModelStatus {
  is_configured: boolean;
  model_version: string;
  supported_crops: string[];
  supported_classes: string[];
  total_classes: number;
}
