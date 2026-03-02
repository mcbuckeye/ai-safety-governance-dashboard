import React from 'react';

interface DashboardCardProps {
  title: string;
  value: string | number;
  subtitle?: string;
  trend?: 'up' | 'down';
  colorClass?: string;
}

const DashboardCard: React.FC<DashboardCardProps> = ({
  title,
  value,
  subtitle,
  trend,
  colorClass = 'text-blue-600',
}) => {
  return (
    <div className="bg-white rounded-lg shadow-sm p-6">
      <h3 className="text-gray-600 text-sm font-medium mb-2">{title}</h3>
      <div className={`text-3xl font-bold ${colorClass}`}>{value}</div>
      {subtitle && (
        <div className="mt-2 flex items-center text-sm text-gray-500">
          {trend && (
            <span className={trend === 'up' ? 'text-green-600' : 'text-red-600'}>
              {trend === 'up' ? '↑' : '↓'}
            </span>
          )}
          <span className="ml-1">{subtitle}</span>
        </div>
      )}
    </div>
  );
};

export default DashboardCard;
