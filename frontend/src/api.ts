import type {
  AlertPage,
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
  status?: string;
  sourceIp?: string;
}

function createQuery(
  parameters: Record<
    string,
    string | number | undefined
  >,
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

async function request<T>(url: string): Promise<T> {
  const response = await fetch(url, {
    headers: {
      Accept: "application/json",
    },
  });

  if (!response.ok) {
    throw new Error(
      `API request failed with status ${response.status}`,
    );
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
    status: filters.status,
    source_ip: filters.sourceIp,
  });

  return request<AlertPage>(
    `/api/alerts${query}`,
  );
}
