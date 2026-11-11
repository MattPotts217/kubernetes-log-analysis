import { useEffect, useState } from 'react';
import './AlertsTable.scss';
import type { Alert } from '../../types/Alert';

const REFRESH_MS = 5000;

export default function AlertsTable() {
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let cancelled = false;

    async function load() {
      try {
        const res = await fetch('/alerts?limit=50');
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        const data: { alerts: Alert[] } = await res.json();
        if (!cancelled) {
          setAlerts(data.alerts);
          setError(null);
        }
      } catch {
        if (!cancelled) setError('Cannot reach storage. Retrying…');
      } finally {
        if (!cancelled) setLoading(false);
      }
    }

    load();
    const timer = setInterval(load, REFRESH_MS);
    return () => {
      cancelled = true;
      clearInterval(timer);
    };
  }, []);

  if (loading) return <p className="alerts-status">Loading alerts…</p>;

  return (
    <section className="alerts">
      {error && <p className="alerts-error">{error}</p>}
      {alerts.length === 0 ? (
        <p className="alerts-status">No alerts yet.</p>
      ) : (
        <table className="alerts-table">
          <thead>
            <tr>
              <th>Time</th>
              <th>Rule</th>
              <th>Severity</th>
              <th>Source IP</th>
              <th>Confidence</th>
              <th>Description</th>
            </tr>
          </thead>
          <tbody>
            {alerts.map((a) => (
              <tr key={a.id}>
                <td>{new Date(a.received_at).toLocaleString()}</td>
                <td>{a.rule.replace('_', ' ')}</td>
                <td>
                  <span className={`severity severity-${a.severity}`}>{a.severity}</span>
                </td>
                <td>{a.source_ip ?? '—'}</td>
                <td>{a.confidence != null ? `${Math.round(a.confidence * 100)}%` : '—'}</td>
                <td>{a.description ?? ''}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </section>
  );
}
