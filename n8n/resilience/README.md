# SWR Cached Circuit Breaker for n8n

Reusable TypeScript resilience layer for n8n custom nodes, task runners, and gateway services.

## Integration

Copy or compile this directory into the custom-node/service package that performs the upstream request. Keep one `CachedCircuitBreaker` instance at module scope so cache and breaker state survive individual executions in the same worker process.

```ts
import { CachedCircuitBreaker } from './CachedCircuitBreaker';

interface MarketTicker {
  symbol: string;
  price: number;
  timestamp: string;
}

const marketData = new CachedCircuitBreaker('MarketDataGateway', {
  failureThreshold: 3,
  baseRecoveryTimeoutMs: 2000,
  maxRecoveryTimeoutMs: 60000,
  requestTimeoutMs: 1500,
  successThreshold: 2,
  ttlMs: 5000,
  maxStaleMs: 300000,
  maxCacheEntries: 500,
});

export async function getTicker(symbol: string) {
  return marketData.execute<MarketTicker>(`ticker:${symbol}`, async (signal) => {
    const response = await fetch(
      `https://api.exchange.com/v1/ticker/${encodeURIComponent(symbol)}`,
      { signal },
    );
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    return response.json() as Promise<MarketTicker>;
  });
}
```

Expose `fromFallback`, `isStale`, and `ageMs` in the n8n node output. Trading workflows should explicitly reject stale data older than their own safety threshold.

## Operational notes

- Cache is process-local and bounded by true LRU eviction.
- OPEN state fails fast without upstream I/O.
- Expired entries are removed on access.
- This is not shared state: multiple n8n workers maintain independent caches.
- For durable/shared fallback across workers, use Redis or another external cache.
