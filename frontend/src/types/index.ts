export interface User {
  id: number;
  email: string;
  name: string;
  role: 'admin' | 'safety_officer' | 'engineer' | 'viewer';
}

export interface LoginResponse {
  access_token: string;
  token_type: string;
  user: User;
}

export interface AIModel {
  id: number;
  name: string;
  version: string;
  description: string;
  team: string;
  risk_score: number;
  risk_level: string;
  status: string;
  created_by: number;
  created_at: string;
  updated_at: string;
  risk_categories?: RiskCategory[];
}

export interface RiskCategory {
  id: number;
  model_id: number;
  category: string;
  score: number;
}

export interface Incident {
  id: number;
  title: string;
  description: string;
  type: string;
  severity: string;
  model_id: number | null;
  status: string;
  assigned_to: number | null;
  reported_by: number;
  resolution_notes: string | null;
  created_at: string;
  updated_at: string;
  resolved_at: string | null;
}

export interface Policy {
  id: number;
  name: string;
  description: string;
  requirements: string;
  applicable_model_types: string[];
  created_at: string;
  updated_at: string;
}

export interface PolicyModelMapping {
  id: number;
  policy_id: number;
  model_id: number;
  compliance_status: string;
  reviewed_by: number | null;
  notes: string | null;
}

export interface AuditEntry {
  id: number;
  user_id: number;
  action: string;
  resource_type: string;
  resource_id: number | null;
  details: any;
  created_at: string;
}

export interface Alert {
  id: number;
  title: string;
  description: string;
  type: string;
  severity: string;
  model_id: number | null;
  status: string;
  assigned_to: number | null;
  created_at: string;
  updated_at: string;
  resolved_at: string | null;
}

export interface DashboardSummary {
  total_models: number;
  risk_distribution: {
    low: number;
    medium: number;
    high: number;
    critical: number;
  };
  total_incidents: number;
  open_incidents: number;
  compliance_score: number;
  total_policies: number;
  open_alerts: number;
  recent_incidents: Incident[];
  recent_audit: AuditEntry[];
}

export interface ComplianceMatrix {
  models: AIModel[];
  policies: Policy[];
  mappings: PolicyModelMapping[];
}
