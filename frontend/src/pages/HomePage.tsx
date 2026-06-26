import { HealthCheckPanel } from "../features/health/HealthCheckPanel";
import { MapComponent } from "../features/map/MapComponent";

export function HomePage() {
  return (
    <main className="page">
      <div className="page__inner">
        <h1 className="page__title">Journey101 Baseline</h1>
        <p className="page__subtitle">Hello World</p>
        <HealthCheckPanel />
        <MapComponent />
      </div>
    </main>
  );
}
