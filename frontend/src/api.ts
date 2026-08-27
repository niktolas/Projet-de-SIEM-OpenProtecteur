import {
  getAccessToken,
  removeAccessToken,
} from "./auth";

import type {
  Alert,
  AlertPage,
  AlertStatus,
  CurrentUserResponse,
  SecurityEventPage,
  Severity,
  TokenResponse,
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


export class ApiError extends Error {
  status: number;

  constructor(
    message: string,
    status: number,
  ) {
    super(message);
    this.name = "ApiError";
    this.status = status;
  }
}


function createQuery(
  parameters: Record<
    string,
    string | number | undefined
  >,
): string {
  const searchParameters =
    new URLSearchParams();

  Object.entries(parameters).forEach(
    ([key, value]) => {
      if (
        value !== undefined &&
        value !== ""
      ) {
        searchParameters.set(
          key,
          String(value),
        );
      }
    },
  );

  const query = searchParameters.toString();

  return query ? `?${query}` : "";
}


async function request<T>(
  url: string,
  options: RequestInit = {},
): Promise<T> {
  const token = getAccessToken();

  const headers = new Headers(
    options.headers,
  );

  headers.set(
    "Accept",
    "application/json",
  );

  if (options.body) {
    headers.set(
      "Content-Type",
      "application/json",
    );
  }

  if (token) {
    headers.set(
      "Authorization",
      `Bearer ${token}`,
    );
  }

  const response = await fetch(url, {
    ...options,
    headers,
  });

  if (!response.ok) {
    let detail = `Erreur API ${response.status}`;

    try {
      const body = (await response.json()) as {
        detail?: string;
      };

      if (body.detail) {
        detail = body.detail;
      }
    } catch {
      // Certaines réponses ne sont pas en JSON.
    }

    if (response.status === 401) {
      removeAccessToken();
    }

    throw new ApiError(
      detail,
      response.status,
    );
  }

  if (response.status === 204) {
    return undefined as T;
  }

  return response.json() as Promise<T>;
}


export async function login(
  username: string,
  password: string,
): Promise<TokenResponse> {
  const form = new URLSearchParams();

  form.set("username", username);
  form.set("password", password);

  const response = await fetch(
    "/api/auth/token",
    {
      method: "POST",
      headers: {
        Accept: "application/json",
        "Content-Type":
          "application/x-www-form-urlencoded",
      },
      body: form,
    },
  );

  if (!response.ok) {
    let detail =
      "Nom d’utilisateur ou mot de passe incorrect.";

    try {
      const body = (await response.json()) as {
        detail?: string;
      };

      if (body.detail) {
        detail = body.detail;
      }
    } catch {
      // La réponse ne contient pas de JSON.
    }

    throw new ApiError(
      detail,
      response.status,
    );
  }

  return response.json() as Promise<TokenResponse>;
}


export function getCurrentUser():
Promise<CurrentUserResponse> {
  return request<CurrentUserResponse>(
    "/api/auth/me",
  );
}


export function getEvents(
  filters: EventFilters = {},
): Promise<SecurityEventPage> {
  const query = createQuery({
    limit: filters.limit ?? 20,
    offset: filters.offset ?? 0,
    hostname: filters.hostname,
    event_type: filters.eventType,
    severity:
      filters.severity || undefined,
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
    severity:
      filters.severity || undefined,
    status:
      filters.status || undefined,
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
