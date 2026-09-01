import { CircuitBreaker, JitteredCircuitBreakerOptions } from './CircuitBreaker';

export interface CacheEntry<T> {
  data: T;
  cachedAt: number;
  freshUntil: number;
  staleUntil: number;
}

export interface SwrExecutionResult<T> {
  data: T;
  isStale: boolean;
  fromFallback: boolean;
  ageMs: number;
}

export interface SwrBreakerOptions extends JitteredCircuitBreakerOptions {
  ttlMs: number;
  maxStaleMs: number;
  maxCacheEntries: number;
}

const DEFAULT_OPTIONS: SwrBreakerOptions = {
  failureThreshold: 3,
  baseRecoveryTimeoutMs: 1500,
  maxRecoveryTimeoutMs: 30000,
  requestTimeoutMs: 2500,
  successThreshold: 2,
  ttlMs: 30000,
  maxStaleMs: 3600000,
  maxCacheEntries: 1000,
};

export class CachedCircuitBreaker {
  private readonly breaker: CircuitBreaker;
  private readonly cache = new Map<string, CacheEntry<unknown>>();

  constructor(
    private readonly name: string,
    private readonly options: SwrBreakerOptions = DEFAULT_OPTIONS,
  ) {
    this.validateOptions(options);
    this.breaker = new CircuitBreaker(name, options);
  }

  async execute<T>(
    cacheKey: string,
    operation: (signal: AbortSignal) => Promise<T>,
  ): Promise<SwrExecutionResult<T>> {
    const cached = this.getValidCacheEntry<T>(cacheKey, Date.now());

    if (cached && Date.now() <= cached.freshUntil) {
      return this.result(cached, false, false);
    }

    try {
      const data = await this.breaker.execute(operation);
      this.setCache(cacheKey, data);
      return { data, isStale: false, fromFallback: false, ageMs: 0 };
    } catch (error: unknown) {
      const fallback = this.getValidCacheEntry<T>(cacheKey, Date.now());
      if (fallback) return this.result(fallback, true, true);
      throw error;
    }
  }

  private result<T>(
    entry: CacheEntry<T>,
    isStale: boolean,
    fromFallback: boolean,
  ): SwrExecutionResult<T> {
    return {
      data: entry.data,
      isStale,
      fromFallback,
      ageMs: Math.max(0, Date.now() - entry.cachedAt),
    };
  }

  private getValidCacheEntry<T>(key: string, now: number): CacheEntry<T> | null {
    const entry = this.cache.get(key) as CacheEntry<T> | undefined;
    if (!entry) return null;
    if (now > entry.staleUntil) {
      this.cache.delete(key);
      return null;
    }

    // Touch the entry so Map insertion order represents actual LRU order.
    this.cache.delete(key);
    this.cache.set(key, entry);
    return entry;
  }

  private setCache<T>(key: string, data: T): void {
    if (this.cache.has(key)) this.cache.delete(key);
    while (this.cache.size >= this.options.maxCacheEntries) {
      const lruKey = this.cache.keys().next().value as string | undefined;
      if (lruKey === undefined) break;
      this.cache.delete(lruKey);
    }

    const now = Date.now();
    this.cache.set(key, {
      data,
      cachedAt: now,
      freshUntil: now + this.options.ttlMs,
      staleUntil: now + this.options.maxStaleMs,
    });
  }

  invalidate(key: string): void {
    this.cache.delete(key);
  }

  clear(): void {
    this.cache.clear();
  }

  getTelemetry() {
    return { ...this.breaker.getTelemetry(), cacheSize: this.cache.size };
  }

  private validateOptions(options: SwrBreakerOptions): void {
    const positive = [
      options.failureThreshold,
      options.baseRecoveryTimeoutMs,
      options.maxRecoveryTimeoutMs,
      options.requestTimeoutMs,
      options.successThreshold,
      options.ttlMs,
      options.maxStaleMs,
      options.maxCacheEntries,
    ];
    if (positive.some((value) => !Number.isFinite(value) || value <= 0)) {
      throw new RangeError(`${this.name}: all breaker and cache limits must be positive`);
    }
    if (options.maxStaleMs < options.ttlMs) {
      throw new RangeError(`${this.name}: maxStaleMs must be >= ttlMs`);
    }
  }
}
