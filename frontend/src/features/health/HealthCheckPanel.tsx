import { useState } from "react";

import { Button } from "../../shared/ui/Button";
import { ResultBox } from "../../shared/ui/ResultBox";
import { fetchBackendHealth, fetchDatabaseHealth } from "./healthApi";
import type { HealthApiResponse } from "./types";

type RequestName = "backend" | "database";

export function HealthCheckPanel() {
  const [loading, setLoading] = useState<RequestName | null>(null);
  const [result, setResult] = useState<HealthApiResponse | null>(null);

  async function runCheck(name: RequestName) {
    setLoading(name);
    try {
      const response =
        name === "backend" ? await fetchBackendHealth() : await fetchDatabaseHealth();
      setResult(response);
    } catch (error) {
      setResult({
        success: false,
        error: {
          code: "REQUEST_FAILED",
          message: error instanceof Error ? error.message : "Request failed",
        },
      });
    } finally {
      setLoading(null);
    }
  }

  return (
    <section className="health-panel" aria-label="Health checks">
      <div className="health-panel__actions">
        <Button disabled={loading !== null} onClick={() => runCheck("backend")}>
          {loading === "backend" ? "Checking..." : "Backend Health Check"}
        </Button>
        <Button disabled={loading !== null} onClick={() => runCheck("database")}>
          {loading === "database" ? "Checking..." : "DB Health Check"}
        </Button>
      </div>
      <ResultBox title="Response" value={result ?? "Click a button to run a check."} />
    </section>
  );
}
