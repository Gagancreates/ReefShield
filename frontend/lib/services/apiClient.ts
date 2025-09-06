/**
 * FastAPI Backend Client for ReefShield
 * Connects React frontend to Python FastAPI backend
 */

export interface BackendConfig {
  baseUrl: string;
  timeout: number;
  retryAttempts: number;
  retryDelay: number;
}

// API Response Types (matching FastAPI backend schemas)
export interface TemperatureReading {
  date: string;
  temperature: number;
  source: 'Historical' | 'Predicted' | 'Observed' | 'Forecast';
}

export interface LocationCoordinates {
  lat: number;
  lon: number;
}

export interface RiskAssessment {
  current_risk: 'low' | 'moderate' | 'high' | 'critical';
  trend: 'stable' | 'increasing' | 'decreasing';
  dhw: number | null;
  anomaly: number | null;
  bleaching_threshold?: number;
}

export interface ReefLocationData {
  location_name: string;
  coordinates: LocationCoordinates;
  last_updated: string;
  historical_data: TemperatureReading[];
  predictions: TemperatureReading[];
  risk_assessment: RiskAssessment;
}

export interface CombinedTemperatureData {
  location_name: string;
  coordinates: LocationCoordinates;
  last_updated: string;
  data: TemperatureReading[];
}

export interface ModelExecutionStatus {
  is_running: boolean;
  last_run: string | null;
  last_error: string | null;
  next_scheduled_run: string | null;
}

export interface SystemStatus {
  api_status: 'healthy' | 'degraded' | 'down';
  model_status: ModelExecutionStatus;
  data_files_status: Record<string, any>;
  last_data_update: string | null;
}

export interface HealthCheckResponse {
  status: 'healthy' | 'degraded' | 'down';
  service: string;
  version: string;
  timestamp: string;
}

export interface SchedulerStatus {
  status: string;
  scheduler: {
    is_running: boolean;
    jobs: Array<{
      id: string;
      name: string;
      next_run_time: string | null;
      trigger: string;
    }>;
    last_job_result: any;
    job_history_count: number;
  };
  timestamp: string;
}

export interface JobHistoryEntry {
  job_id: string;
  execution_id: string | null;
  start_time: string;
  end_time: string;
  success: boolean;
  message: string;
  trigger: 'scheduled' | 'manual';
  user_id?: string;
}

export interface ErrorStatistics {
  status: string;
  error_statistics: {
    error_counts: Record<string, number>;
    last_errors: Record<string, any>;
    total_errors: number;
  };
  timestamp: string;
}

export interface LoggingStatistics {
  status: string;
  logging_statistics: {
    logs_directory: string;
    initialized: boolean;
    loggers_count: number;
    log_files: Array<{
      name: string;
      size_bytes: number;
      size_mb: number;
      modified: string;
    }>;
  };
  timestamp: string;
}

// API Client Class
export class ReefShieldAPIClient {
  private config: BackendConfig;
  private abortController: AbortController | null = null;

  constructor(config: Partial<BackendConfig> = {}) {
    this.config = {
      baseUrl: config.baseUrl || 'http://localhost:8000',
      timeout: config.timeout || 10000,
      retryAttempts: config.retryAttempts || 3,
      retryDelay: config.retryDelay || 1000,
      ...config
    };
  }

  // Helper method for making HTTP requests with retry logic
  private async makeRequest<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const url = `${this.config.baseUrl}${endpoint}`;
    let lastError: Error = new Error('Unknown error');

    for (let attempt = 1; attempt <= this.config.retryAttempts; attempt++) {
      try {
        this.abortController = new AbortController();
        
        const timeoutId = setTimeout(() => {
          this.abortController?.abort();
        }, this.config.timeout);

        const response = await fetch(url, {
          ...options,
          signal: this.abortController.signal,
          headers: {
            'Content-Type': 'application/json',
            ...options.headers,
          },
        });

        clearTimeout(timeoutId);

        if (!response.ok) {
          throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }

        const data = await response.json();
        return data as T;

      } catch (error) {
        lastError = error as Error;
        
        if (error instanceof Error && error.name === 'AbortError') {
          throw new Error(`Request timeout after ${this.config.timeout}ms`);
        }

        if (attempt < this.config.retryAttempts) {
          console.warn(`API request attempt ${attempt} failed, retrying...`, error);
          await new Promise(resolve => setTimeout(resolve, this.config.retryDelay * attempt));
        }
      }
    }

    throw lastError;
  }

  // Cancel ongoing requests
  public cancelRequests(): void {
    if (this.abortController) {
      this.abortController.abort();
      this.abortController = null;
    }
  }

  // Health and Status Endpoints
  async getHealth(): Promise<HealthCheckResponse> {
    return this.makeRequest<HealthCheckResponse>('/health');
  }

  async getDetailedHealth(): Promise<HealthCheckResponse> {
    return this.makeRequest<HealthCheckResponse>('/api/v1/health');
  }

  async getSystemStatus(): Promise<SystemStatus> {
    return this.makeRequest<SystemStatus>('/api/v1/status');
  }

  // Core Data Endpoints
  async getReefData(): Promise<ReefLocationData> {
    return this.makeRequest<ReefLocationData>('/api/v1/reef-data');
  }

  async getCombinedData(): Promise<CombinedTemperatureData> {
    return this.makeRequest<CombinedTemperatureData>('/api/v1/combined-data');
  }

  // Model Execution
  async triggerModelRun(force: boolean = false, notify: boolean = true): Promise<any> {
    return this.makeRequest('/api/v1/run-model', {
      method: 'POST',
      body: JSON.stringify({ force, notify }),
    });
  }

  // Scheduler Management
  async getSchedulerStatus(): Promise<SchedulerStatus> {
    return this.makeRequest<SchedulerStatus>('/api/v1/scheduler/status');
  }

  async getJobHistory(limit: number = 10): Promise<{ history: JobHistoryEntry[]; count: number }> {
    return this.makeRequest(`/api/v1/scheduler/history?limit=${limit}`);
  }

  async triggerImmediateRun(userId?: string): Promise<any> {
    const params = userId ? `?user_id=${encodeURIComponent(userId)}` : '';
    return this.makeRequest(`/api/v1/scheduler/trigger${params}`, {
      method: 'POST',
    });
  }

  async rescheduleDaily(hour: number, minute: number = 0): Promise<any> {
    return this.makeRequest(`/api/v1/scheduler/reschedule?hour=${hour}&minute=${minute}`, {
      method: 'POST',
    });
  }

  async pauseScheduler(): Promise<any> {
    return this.makeRequest('/api/v1/scheduler/pause', {
      method: 'POST',
    });
  }

  async resumeScheduler(): Promise<any> {
    return this.makeRequest('/api/v1/scheduler/resume', {
      method: 'POST',
    });
  }

  // Monitoring and Diagnostics
  async getErrorStatistics(): Promise<ErrorStatistics> {
    return this.makeRequest<ErrorStatistics>('/api/v1/errors/stats');
  }

  async getLoggingStatistics(): Promise<LoggingStatistics> {
    return this.makeRequest<LoggingStatistics>('/api/v1/logs/stats');
  }

  // Cache Management
  async getCacheInfo(): Promise<any> {
    return this.makeRequest('/api/v1/cache-info');
  }

  async clearCache(): Promise<any> {
    return this.makeRequest('/api/v1/clear-cache', {
      method: 'POST',
    });
  }

  // Utility Methods
  async checkConnection(): Promise<boolean> {
    try {
      await this.getHealth();
      return true;
    } catch {
      return false;
    }
  }

  updateConfig(newConfig: Partial<BackendConfig>): void {
    this.config = { ...this.config, ...newConfig };
  }

  getConfig(): BackendConfig {
    return { ...this.config };
  }
}

// Default client instance
export const apiClient = new ReefShieldAPIClient({
  baseUrl: process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000',
});

// Hook for API client configuration
export function useAPIClient(config?: Partial<BackendConfig>): ReefShieldAPIClient {
  if (config) {
    const client = new ReefShieldAPIClient(config);
    return client;
  }
  return apiClient;
}