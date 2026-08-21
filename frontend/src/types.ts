export type Severity =
  | "informational"
  | "low"
  | "medium"
  | "high"
  | "critical";

export type AlertStatus =
  | "open"
  | "investigating"
  | "resolved"
  | "false_positive";

export interface SecurityEvent {
  id: string;
  timestamp: string;
  source: string;
  hostname: string;
  event_type: string;
  username: string | null;
  source_ip: string | null;
  severity: Severity;
  message: string | null;
  created_at: string;
}

export interface Alert {
  id: string;
  rule_name: string;
  title: string;
  description: string;
  severity: Severity;
  status: AlertStatus;
  source_ip: string | null;
  username: string | null;
  hostname: string | null;
  event_count: number;
  window_start: string;
  window_end: string;
  created_at: string;
}

export interface PaginatedResponse<T> {
  total: number;
  limit: number;
  offset: number;
  returned: number;
  items: T[];
}

export type SecurityEventPage =
  PaginatedResponse<SecurityEvent>;

export type AlertPage =
  PaginatedResponse<Alert>;
