export interface JitteredCircuitBreakerOptions {
  failureThreshold: number;
  baseRecoveryTimeoutMs: number;
  maxRecoveryTimeoutMs: number;
  requestTimeoutMs: number;
  successThreshold: number;
}

export type CircuitState = 'CLOSED' | 'OPEN' | 'HALF_OPEN';

export class CircuitBreakerError extends Error {
  constructor(public readonly breakerName: string, public readonly state: CircuitState) {
    super(`Circuit breaker "${breakerName}" is ${state}`);
    this.name = 'CircuitBreakerError';
  }
}

export class CircuitBreaker {
  private state: CircuitState = 'CLOSED';
  private failures = 0;
  private halfOpenSuccesses = 0;
  private openedAt = 0;
  private recoveryTimeoutMs: number;

  constructor(
    private readonly name: string,
    private readonly options: JitteredCircuitBreakerOptions,
  ) {
    this.recoveryTimeoutMs = options.baseRecoveryTimeoutMs;
  }

  async execute<T>(operation: (signal: AbortSignal) => Promise<T>): Promise<T> {
    const now = Date.now();
    if (this.state === 'OPEN') {
      if (now - this.openedAt < this.recoveryTimeoutMs) {
        throw new CircuitBreakerError(this.name, this.state);
      }
      this.state = 'HALF_OPEN';
      this.halfOpenSuccesses = 0;
    }

    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort(), this.options.requestTimeoutMs);
    try {
      const result = await operation(controller.signal);
      this.onSuccess();
      return result;
    } catch (error) {
      this.onFailure();
      throw error;
    } finally {
      clearTimeout(timeout);
    }
  }

  private onSuccess(): void {
    if (this.state === 'HALF_OPEN') {
      this.halfOpenSuccesses += 1;
      if (this.halfOpenSuccesses >= this.options.successThreshold) {
        this.state = 'CLOSED';
        this.failures = 0;
        this.recoveryTimeoutMs = this.options.baseRecoveryTimeoutMs;
      }
      return;
    }
    this.failures = 0;
  }

  private onFailure(): void {
    this.failures += 1;
    if (this.state === 'HALF_OPEN' || this.failures >= this.options.failureThreshold) {
      this.state = 'OPEN';
      this.openedAt = Date.now();
      const next = Math.min(this.options.maxRecoveryTimeoutMs, this.recoveryTimeoutMs * 2);
      this.recoveryTimeoutMs = Math.round(next * (0.75 + Math.random() * 0.5));
    }
  }

  getTelemetry() {
    return {
      name: this.name,
      state: this.state,
      failures: this.failures,
      recoveryTimeoutMs: this.recoveryTimeoutMs,
    };
  }
}
