import {
  useCallback,
  useEffect,
  useState,
} from "react";

import {
  getAlert,
  getAlerts,
  getEvents,
  updateAlertStatus,
} from "./api";

import type {
  Alert,
  AlertPage,
  AlertStatus,
  SecurityEvent,
  SecurityEventPage,
  Severity,
} from "./types";

type View = "events" | "alerts";

const PAGE_SIZE = 10;

const statusLabels: Record<AlertStatus, string> = {
  open: "Ouverte",
  investigating: "En investigation",
  resolved: "Résolue",
  false_positive: "Faux positif",
};

const severityLabels: Record<Severity, string> = {
  informational: "Informationnelle",
  low: "Faible",
  medium: "Moyenne",
  high: "Élevée",
  critical: "Critique",
};

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
      {severityLabels[severity]}
    </span>
  );
}

function StatusBadge({
  status,
}: {
  status: AlertStatus;
}) {
  return (
    <span className={`badge status-${status}`}>
      {statusLabels[status]}
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
                <code>
                  {event.source_ip ?? "Non renseignée"}
                </code>
              </td>

              <td>
                <SeverityBadge
                  severity={event.severity}
                />
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
  onSelectAlert,
}: {
  alerts: Alert[];
  onSelectAlert: (alertId: string) => void;
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
            <tr
              key={alert.id}
              className="clickable-row"
              tabIndex={0}
              onClick={() => onSelectAlert(alert.id)}
              onKeyDown={(event) => {
                if (
                  event.key === "Enter" ||
                  event.key === " "
                ) {
                  onSelectAlert(alert.id);
                }
              }}
            >
              <td>{formatDate(alert.created_at)}</td>

              <td>
                <strong>{alert.title}</strong>

                <div className="secondary">
                  {alert.rule_name}
                </div>
              </td>

              <td>
                <code>
                  {alert.source_ip ?? "Non renseignée"}
                </code>
              </td>

              <td>
                {alert.username ?? "Non renseigné"}
              </td>

              <td>{alert.event_count}</td>

              <td>
                <SeverityBadge
                  severity={alert.severity}
                />
              </td>

              <td>
                <StatusBadge status={alert.status} />
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

function AlertDetailPanel({
  alert,
  loading,
  updating,
  error,
  onClose,
  onUpdateStatus,
}: {
  alert: Alert | null;
  loading: boolean;
  updating: boolean;
  error: string | null;
  onClose: () => void;
  onUpdateStatus: (status: AlertStatus) => void;
}) {
  return (
    <div
      className="drawer-overlay"
      onMouseDown={(event) => {
        if (event.target === event.currentTarget) {
          onClose();
        }
      }}
    >
      <aside
        className="alert-drawer"
        role="dialog"
        aria-modal="true"
        aria-label="Détail de l'alerte"
      >
        <header className="drawer-header">
          <div>
            <p className="eyebrow">
              Investigation
            </p>

            <h3>Détail de l’alerte</h3>
          </div>

          <button
            className="close-button"
            type="button"
            onClick={onClose}
            aria-label="Fermer"
          >
            ×
          </button>
        </header>

        {loading && (
          <div className="drawer-message">
            Chargement de l’alerte...
          </div>
        )}

        {error && (
          <div className="error-message">
            {error}
          </div>
        )}

        {!loading && alert && (
          <>
            <section className="alert-summary">
              <div className="summary-title">
                <h4>{alert.title}</h4>
                <SeverityBadge
                  severity={alert.severity}
                />
              </div>

              <p>{alert.description}</p>

              <StatusBadge status={alert.status} />
            </section>

            <section className="detail-section">
              <h4>Informations principales</h4>

              <dl className="detail-grid">
                <div>
                  <dt>Règle</dt>
                  <dd>
                    <code>{alert.rule_name}</code>
                  </dd>
                </div>

                <div>
                  <dt>Machine</dt>
                  <dd>
                    {alert.hostname ?? "Non renseignée"}
                  </dd>
                </div>

                <div>
                  <dt>Utilisateur</dt>
                  <dd>
                    {alert.username ?? "Non renseigné"}
                  </dd>
                </div>

                <div>
                  <dt>Adresse IP source</dt>
                  <dd>
                    <code>
                      {alert.source_ip ??
                        "Non renseignée"}
                    </code>
                  </dd>
                </div>

                <div>
                  <dt>Nombre d’événements</dt>
                  <dd>{alert.event_count}</dd>
                </div>

                <div>
                  <dt>Créée le</dt>
                  <dd>{formatDate(alert.created_at)}</dd>
                </div>
              </dl>
            </section>

            <section className="detail-section">
              <h4>Fenêtre de détection</h4>

              <div className="timeline">
                <div>
                  <span>Début</span>
                  <strong>
                    {formatDate(alert.window_start)}
                  </strong>
                </div>

                <div className="timeline-line" />

                <div>
                  <span>Fin</span>
                  <strong>
                    {formatDate(alert.window_end)}
                  </strong>
                </div>
              </div>
            </section>

            <section className="detail-section">
              <h4>Actions d’investigation</h4>

              <div className="action-buttons">
                {alert.status === "open" && (
                  <button
                    type="button"
                    className="primary-action"
                    disabled={updating}
                    onClick={() =>
                      onUpdateStatus("investigating")
                    }
                  >
                    Prendre en charge
                  </button>
                )}

                {alert.status === "investigating" && (
                  <>
                    <button
                      type="button"
                      className="success-action"
                      disabled={updating}
                      onClick={() =>
                        onUpdateStatus("resolved")
                      }
                    >
                      Résoudre
                    </button>

                    <button
                      type="button"
                      className="warning-action"
                      disabled={updating}
                      onClick={() =>
                        onUpdateStatus(
                          "false_positive",
                        )
                      }
                    >
                      Classer comme faux positif
                    </button>

                    <button
                      type="button"
                      className="secondary-action"
                      disabled={updating}
                      onClick={() =>
                        onUpdateStatus("open")
                      }
                    >
                      Remettre en attente
                    </button>
                  </>
                )}

                {(alert.status === "resolved" ||
                  alert.status ===
                    "false_positive") && (
                  <button
                    type="button"
                    className="primary-action"
                    disabled={updating}
                    onClick={() =>
                      onUpdateStatus("investigating")
                    }
                  >
                    Rouvrir l’investigation
                  </button>
                )}
              </div>

              {updating && (
                <p className="updating-message">
                  Mise à jour du statut...
                </p>
              )}
            </section>

            <footer className="drawer-footer">
              Identifiant : <code>{alert.id}</code>
            </footer>
          </>
        )}
      </aside>
    </div>
  );
}

function App() {
  const [view, setView] =
    useState<View>("alerts");

  const [events, setEvents] =
    useState<SecurityEventPage | null>(null);

  const [alerts, setAlerts] =
    useState<AlertPage | null>(null);

  const [severity, setSeverity] =
    useState<Severity | "">("");

  const [alertStatus, setAlertStatus] =
    useState<AlertStatus | "">("");

  const [sourceIp, setSourceIp] =
    useState("");

  const [offset, setOffset] =
    useState(0);

  const [loading, setLoading] =
    useState(true);

  const [error, setError] =
    useState<string | null>(null);

  const [selectedAlert, setSelectedAlert] =
    useState<Alert | null>(null);

  const [detailOpen, setDetailOpen] =
    useState(false);

  const [detailLoading, setDetailLoading] =
    useState(false);

  const [detailError, setDetailError] =
    useState<string | null>(null);

  const [statusUpdating, setStatusUpdating] =
    useState(false);

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
          status: alertStatus,
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
  }, [
    view,
    offset,
    severity,
    alertStatus,
    sourceIp,
  ]);

  useEffect(() => {
    void loadData();
  }, [loadData]);

  useEffect(() => {
    function closeWithEscape(
      event: KeyboardEvent,
    ) {
      if (event.key === "Escape") {
        setDetailOpen(false);
      }
    }

    window.addEventListener(
      "keydown",
      closeWithEscape,
    );

    return () => {
      window.removeEventListener(
        "keydown",
        closeWithEscape,
      );
    };
  }, []);

  function changeView(newView: View) {
    setView(newView);
    setOffset(0);
    setSeverity("");
    setAlertStatus("");
    setSourceIp("");
    setDetailOpen(false);
    setSelectedAlert(null);
  }

  async function openAlertDetail(
    alertId: string,
  ) {
    setDetailOpen(true);
    setDetailLoading(true);
    setDetailError(null);
    setSelectedAlert(null);

    try {
      const alert = await getAlert(alertId);
      setSelectedAlert(alert);
    } catch (requestError) {
      setDetailError(
        requestError instanceof Error
          ? requestError.message
          : "Impossible de charger l’alerte.",
      );
    } finally {
      setDetailLoading(false);
    }
  }

  async function changeAlertStatus(
    status: AlertStatus,
  ) {
    if (!selectedAlert) {
      return;
    }

    setStatusUpdating(true);
    setDetailError(null);

    try {
      const updatedAlert =
        await updateAlertStatus(
          selectedAlert.id,
          status,
        );

      setSelectedAlert(updatedAlert);

      setAlerts((currentAlerts) => {
        if (!currentAlerts) {
          return currentAlerts;
        }

        return {
          ...currentAlerts,
          items: currentAlerts.items.map((alert) =>
            alert.id === updatedAlert.id
              ? updatedAlert
              : alert,
          ),
        };
      });

      await loadData();
    } catch (requestError) {
      setDetailError(
        requestError instanceof Error
          ? requestError.message
          : "Impossible de modifier le statut.",
      );
    } finally {
      setStatusUpdating(false);
    }
  }

  const currentPage =
    view === "events" ? events : alerts;

  const total = currentPage?.total ?? 0;

  const canGoBack = offset > 0;
  const canGoForward =
    offset + PAGE_SIZE < total;

  return (
    <div className="application">
      <aside className="sidebar">
        <div>
          <div className="brand">
            <div className="brand-icon">
              OP
            </div>

            <div>
              <h1>OpenProtecteur</h1>
              <p>
                Security Operations Platform
              </p>
            </div>
          </div>

          <nav>
            <button
              className={
                view === "alerts"
                  ? "active"
                  : ""
              }
              onClick={() =>
                changeView("alerts")
              }
            >
              Alertes
            </button>

            <button
              className={
                view === "events"
                  ? "active"
                  : ""
              }
              onClick={() =>
                changeView("events")
              }
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
              {total} résultat
              {total > 1 ? "s" : ""}
            </p>
          </div>

          <button
            className="refresh-button"
            onClick={() =>
              void loadData()
            }
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
                  event.target.value as
                    | Severity
                    | "",
                );
                setOffset(0);
              }}
            >
              <option value="">
                Toutes
              </option>
              <option value="informational">
                Informationnelle
              </option>
              <option value="low">
                Faible
              </option>
              <option value="medium">
                Moyenne
              </option>
              <option value="high">
                Élevée
              </option>
              <option value="critical">
                Critique
              </option>
            </select>
          </label>

          {view === "alerts" && (
            <label>
              Statut

              <select
                value={alertStatus}
                onChange={(event) => {
                  setAlertStatus(
                    event.target.value as
                      | AlertStatus
                      | "",
                  );
                  setOffset(0);
                }}
              >
                <option value="">
                  Tous
                </option>
                <option value="open">
                  Ouverte
                </option>
                <option value="investigating">
                  En investigation
                </option>
                <option value="resolved">
                  Résolue
                </option>
                <option value="false_positive">
                  Faux positif
                </option>
              </select>
            </label>
          )}

          <label>
            Adresse IP source

            <input
              type="text"
              placeholder="192.168.1.42"
              value={sourceIp}
              onChange={(event) => {
                setSourceIp(
                  event.target.value,
                );
                setOffset(0);
              }}
            />
          </label>
        </section>

        {error && (
          <div className="error-message">
            {error}
          </div>
        )}

        <section className="content-card">
          {loading ? (
            <div className="empty-state">
              Chargement...
            </div>
          ) : view === "events" ? (
            <EventsTable
              events={events?.items ?? []}
            />
          ) : (
            <AlertsTable
              alerts={alerts?.items ?? []}
              onSelectAlert={
                openAlertDetail
              }
            />
          )}

          <footer className="pagination">
            <span>
              Résultats{" "}
              {total === 0 ? 0 : offset + 1} à{" "}
              {Math.min(
                offset + PAGE_SIZE,
                total,
              )}{" "}
              sur {total}
            </span>

            <div>
              <button
                disabled={
                  !canGoBack || loading
                }
                onClick={() =>
                  setOffset(
                    Math.max(
                      0,
                      offset - PAGE_SIZE,
                    ),
                  )
                }
              >
                Précédent
              </button>

              <button
                disabled={
                  !canGoForward || loading
                }
                onClick={() =>
                  setOffset(
                    offset + PAGE_SIZE,
                  )
                }
              >
                Suivant
              </button>
            </div>
          </footer>
        </section>
      </main>

      {detailOpen && (
        <AlertDetailPanel
          alert={selectedAlert}
          loading={detailLoading}
          updating={statusUpdating}
          error={detailError}
          onClose={() =>
            setDetailOpen(false)
          }
          onUpdateStatus={
            changeAlertStatus
          }
        />
      )}
    </div>
  );
}

export default App;
