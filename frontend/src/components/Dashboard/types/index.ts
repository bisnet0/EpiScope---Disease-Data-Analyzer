export interface DashboardHeaderProps {
  periodFilter: string;
  setPeriodFilter: (v: string) => void;
  modelFilter: string;
  setModelFilter: (v: string) => void;
  onRefresh: () => void;
  loading: boolean;
}