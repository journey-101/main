import { HealthCheckPanel } from "../features/health/HealthCheckPanel";
import { RecommendationComponent } from "../features/recommendation/recommendationComponent";

export function HomePage() {
  return (
    <main className="page">
      <div className="page__inner">
        <h1 className="page__title">Journey101 Baseline</h1>
        <p className="page__subtitle">Hello World</p>
        <HealthCheckPanel />
        <RecommendationComponent />
      </div>
    </main>
  );
}
