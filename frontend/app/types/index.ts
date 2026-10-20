export interface Material {
  id: number; name: string; slug: string; description: string; applications: string;
  advantages: string; limitations: string; properties: string; seo_title: string; seo_description: string;
}
export interface Service {
  id: number; title: string; slug: string; summary: string; description: string; applications: string;
  materials: Material[]; faq: { question: string; answer: string }[]; seo_title: string; seo_description: string;
}
export interface Category { id: number; name: string; slug: string }
export interface ProjectImage { id: number; image: string; thumbnail: string; caption: string; role: string }
export interface Project {
  id: number; title: string; slug: string; summary: string; description: string; problem: string;
  solution: string; result: string; category: Category; material: Material | null; technology: string;
  cover: string; thumbnail: string; completed_at: string | null; is_demo: boolean; featured: boolean;
  images: ProjectImage[]; services: Service[]; video_url: string; model_url: string | null;
  model_format: 'stl' | 'glb' | null; seo_title: string; seo_description: string;
}
export interface Paginated<T> { count: number; next: string | null; previous: string | null; results: T[] }
export interface SiteSettings {
  company_name: string; logo: string; hero_title: string; hero_subtitle: string; phone: string;
  email: string; telegram: string; max_url: string; address: string; hours: string; legal_details: string;
  map_url: string; region: string; seo_title: string; seo_description: string;
  process: { title: string; text: string }[]; advantages: { title: string; text: string }[];
  business_text: string; privacy_text: string; consent_text: string; consent_version: string; legal_reviewed: boolean; accept_leads: boolean;
}
