export interface StravaActivity {
  id: string;
  activity_id: string;
  name: string;
  type: string;
  distance_km: number;
  moving_time_min: number;
  avg_hr: number | null;
  max_hr: number | null;
  date: string;
}

export interface HealthStatsState {
  isConnected: boolean;
  activities: StravaActivity[];
  isLoading: boolean;
  error: string | null;
}

export interface HealthStatsPanelProps {
  // Props se necessário
}