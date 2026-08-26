import type {
  Alert,
  AlertPage,
  AlertStatus,
  SecurityEventPage,
  Severity,
} from "./types";

interface EventFilters {
  limit?: number;
  offset?: number;
  hostname?: string;
  eventType?: string;
  severity?: Severity | "";
  sourceIp?: string;
}

interface AlertFilters {
  limit?: number;
  offset?: number;
  severity?: Severity | "";
  status?: AlertStatus | "";
  sourceIp?: string;
}

function createQuery(
  parameters: Record<string, string | number | undefined>,
): string {
  const searchParameters = new URLSearchParams();

  Object.entries(parameters).forEach(([key, value]) => {
    if (value !== undefined && value !== "") {
      searchParameters.set(key, String(value));
    }
  });

  const query = searchParameters.toString();

  return query ? `?${query}` : "";
}

async function request<T>(
  url: string,
  options?: RequestInit,
): Promise<T> {
  const response = await fetch(url, {
    ...options,
    headers: {
      Accept: "application/json",
      ...(options?.body
        ? { "Content-Type": "application/json" }
        : {}),
      ...options?.headers,
    },
  });

  if (!response.ok) {
    let detail = `Erreur API ${response.status}`;

    try {
      const errorBody = (await response.json()) as {
        detail?: string;
      };

      if (errorBody.detail) {
        detail = errorBody.detail;
      }
    } catch {
      // La réponse ne contient pas nécessairement du JSON.
    }

    throw new Error(detail);
  }

  if (response.status === 204) {
    return undefined as T;
  }

  return response.json() as Promise<T>;
}

export function getEvents(
  filters: EventFilters = {},
): Promise<SecurityEventPage> {
  const query = createQuery({
    limit: filters.limit ?? 20,
    offset: filters.offset ?? 0,
    hostname: filters.hostname,
    event_type: filters.eventType,
    severity: filters.severity || undefined,
    source_ip: filters.sourceIp,
  });

  return request<SecurityEventPage>(
    `/api/events${query}`,
  );
}

export function getAlerts(
  filters: AlertFilters = {},
): Promise<AlertPage> {
  const query = createQuery({
    limit: filters.limit ?? 20,
    offset: filters.offset ?? 0,
    severity: filters.severity || undefined,
    status: filters.status || undefined,
    source_ip: filters.sourceIp,
  });

  return request<AlertPage>(
    `/api/alerts${query}`,
  );
}

export function getAlert(
  alertId: string,
): Promise<Alert> {
  return request<Alert>(
    `/api/alerts/${alertId}`,
  );
}

export function updateAlertStatus(
  alertId: string,
  status: AlertStatus,
): Promise<Alert> {
  return request<Alert>(
    `/api/alerts/${alertId}/status`,
    {
      method: "PATCH",
      body: JSON.stringify({
        status,
      }),
    },
  );
}
