type Severity = "low" | "medium" | "high" | "critical"

export type Alert = {
    id: string;
    rule: string;
    severity: Severity;
    confidence?: number | null;
    source_ip?: string | null;
    event_time: string | null;
    received_at: string;
    description?: string | null;
}
