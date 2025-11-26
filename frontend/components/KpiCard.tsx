interface KpiCardProps {
  title: string;
  value: string | number;
  subValue?: string;
  trend?: string;
  trendUp?: boolean;
  icon?: React.ReactNode;
  className?: string;
}

export function KpiCard({ title, value, subValue, trend, trendUp, icon, className = "" }: KpiCardProps) {
  return (
    <div className={`card bg-base-100 shadow-sm border border-base-200 ${className}`}>
      <div className="card-body p-4">
        <div className="flex justify-between items-start">
          <div>
            <h3 className="text-xs font-bold text-base-content/60 uppercase tracking-wider">{title}</h3>
            <div className="text-2xl font-bold mt-1">{value}</div>
            {subValue && <div className="text-sm text-base-content/70 mt-1">{subValue}</div>}
          </div>
          {icon && <div className="text-primary opacity-80">{icon}</div>}
        </div>
        
        {trend && (
          <div className={`text-xs font-medium mt-2 ${trendUp ? 'text-success' : 'text-error'}`}>
            {trend}
          </div>
        )}
      </div>
    </div>
  );
}
