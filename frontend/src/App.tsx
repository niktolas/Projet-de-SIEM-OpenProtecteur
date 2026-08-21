import {
  useCallback,
  useEffect,
  useState,
} from "react";

import { getAlerts, getEvents } from "./api";

import type {
  Alert,
  AlertPage,
  SecurityEvent,
  SecurityEventPage,
  Severity,
} from "./types";

type View = "events" | "alerts";

const PAGE_SIZE = 10;

function formatDate(date: string): string {
  return new Intl.DateTimeFormat("fr-FR", {
    dateStyle: "short",
    timeStyle: "medium",
  }).format(new Date(date));
}

function SeverityBadge({
  severity,
}: {
  severity: Severity;
}) {
  return (
    <span className={`badge severity-${severity}`}>
      {severity}
    </span>
  );
}

function EventsTable({
  events,
}: {
  events: SecurityEvent[];
}) {
  if (events.length === 0) {
    return (
      <div className="empty-state">
        Aucun événement ne correspond aux filtres.
      </div>
    );
  }

  return (
    <div className="table-container">
      <table>
        <thead>
          <tr>
            <th>Date</th>
            <th>Machine</th>
            <th>Type</th>
            <th>Utilisateur</th>
            <th>Adresse IP</th>
            <th>Criticité</th>
          </tr>
        </thead>

        <tbody>
          {events.map((event) => (
            <tr key={event.id}>
              <td>{formatDate(event.timestamp)}</td>
              <td>{event.hostname}</td>
              <td>
                <code>{event.event_type}</code>
              </td>
              <td>{event.username ?? "Non renseigné"}</td>
              <td>
                <code>{event.source_ip ?? "Non renseignée"}</code>
              </td>
              <td>
                <SeverityBadge severity={event.severity} />
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

function AlertsTable({
  alerts,
}: {
  alerts: Alert[];
}) {
  if (alerts.length === 0) {
    return (
      <div className="empty-state">
        Aucune alerte ne correspond aux filtres.
      </div>
    );
  }

  return (
    <div className="table-container">
      <table>
        <thead>
          <tr>
            <th>Date</th>
            <th>Alerte</th>
            <th>Adresse IP</th>
            <th>Utilisateur</th>
            <th>Événements</th>
            <th>Criticité</th>
            <th>Statut</th>
          </tr>
        </thead>

        <tbody>
          {alerts.map((alert) => (
            <tr key={alert.id}>
              <td>{formatDate(alert.created_at)}</td>

              <td>
                <strong>{alert.title}</strong>
                <div className="secondary">
                  {alert.rule_name}
                </div>
              </td>

              <td>
                <code>{alert.source_ip ?? "Non renseignée"}</code>
              </td>

              <td>{alert.username ?? "Non renseigné"}</td>
              <td>{alert.event_count}</td>

              <td>
                <SeverityBadge severity={alert.severity} />
              </td>

              <td>
                <span className="badge status-badge">
                  {alert.status}
                </span>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

function App() {
  const [view, setView] = useState<View>("alerts");

  const [events, setEvents] =
    useState<SecurityEventPage | null>(null);

  const [alerts, setAlerts] =
    useState<AlertPage | null>(null);

  const [severity, setSeverity] =
    useState<Severity | "">("");

  const [sourceIp, setSourceIp] = useState("");
  const [offset, setOffset] = useState(0);

  const [loading, setLoading] = useState(true);
  const [error, setError] =
    useState<string | null>(null);

  const loadData = useCallback(async () => {
    setLoading(true);
    setError(null);

    try {
      if (view === "events") {
        const result = await getEvents({
          limit: PAGE_SIZE,
          offset,
          severity,
          sourceIp,
        });

        setEvents(result);
      } else {
        const result = await getAlerts({
          limit: PAGE_SIZE,
          offset,
          severity,
          sourceIp,
        });

        setAlerts(result);
      }
    } catch (requestError) {
      setError(
        requestError instanceof Error
          ? requestError.message
          : "Impossible de contacter OpenProtecteur.",
      );
    } finally {
      setLoading(false);
    }
  }, [view, offset, severity, sourceIp]);

  useEffect(() => {
    void loadData();
  }, [loadData]);

  function changeView(newView: View) {
    setView(newView);
    setOffset(0);
    setSeverity("");
    setSourceIp("");
  }

  const currentPage =
    view === "events" ? events : alerts;

  const total = currentPage?.total ?? 0;

  const canGoBack = offset > 0;
  const canGoForward = offset + PAGE_SIZE < total;

  return (
    <div className="application">
      <aside className="sidebar">
        <div>
          <div className="brand">
            <div className="brand-icon">OP</div>

            <div>
              <h1>OpenProtecteur</h1>
              <p>Security Operations Platform</p>
            </div>
          </div>

          <nav>
            <button
              className={
                view === "alerts" ? "active" : ""
              }
              onClick={() => changeView("alerts")}
            >
              Alertes
            </button>

            <button
              className={
                view === "events" ? "active" : ""
              }
              onClick={() => changeView("events")}
            >
              Événements
            </button>
          </nav>
        </div>

        <div className="api-status">
          <span className="status-dot" />
          API connectée
        </div>
      </aside>

      <main>
        <header className="page-header">
          <div>
            <p className="eyebrow">
              Centre des opérations de sécurité
            </p>

            <h2>
              {view === "alerts"
                ? "Alertes de sécurité"
                : "Événements collectés"}
            </h2>

            <p>
              {total} résultat{total > 1 ? "s" : ""}
            </p>
          </div>

          <button
            className="refresh-button"
            onClick={() => void loadData()}
            disabled={loading}
          >
            Actualiser
          </button>
        </header>

        <section className="filters">
          <label>
            Criticité
            <select
              value={severity}
              onChange={(event) => {
                setSeverity(
                  event.target.value as Severity | "",
                );
                setOffset(0);
              }}
            >
              <option value="">Toutes</option>
              <option value="informational">
                Informational
              </option>
              <option value="low">Low</option>
              <option value="medium">Medium</option>
              <option value="high">High</option>
              <option value="critical">Critical</option>
            </select>
          </label>

          <label>
            Adresse IP source
            <input
              type="text"
              placeholder="192.168.1.42"
              value={sourceIp}
              onChange={(event) => {
                setSourceIp(event.target.value);
                setOffset(0);
              }}
            />
          </label>
        </section>

        {error && (
          <div className="error-message">{error}</div>
        )}

        <section className="content-card">
          {loading ? (
            <div className="empty-state">
              Chargement...
            </div>
          ) : view === "events" ? (
            <EventsTable events={events?.items ?? []} />
          ) : (
            <AlertsTable alerts={alerts?.items ?? []} />
          )}

          <footer className="pagination">
            <span>
              Résultats {total === 0 ? 0 : offset + 1} à{" "}
              {Math.min(offset + PAGE_SIZE, total)} sur{" "}
              {total}
            </span>

            <div>
              <button
                disabled={!canGoBack || loading}
                onClick={() =>
                  setOffset(
                    Math.max(0, offset - PAGE_SIZE),
                  )
                }
              >
                Précédent
              </button>

              <button
                disabled={!canGoForward || loading}
                onClick={() =>
                  setOffset(offset + PAGE_SIZE)
                }
              >
                Suivant
              </button>
            </div>
          </footer>
        </section>
      </main>
    </div>
  );
}

export default App;
