import React, { useEffect, useState } from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import apiClient from '../api/client';
import { DashboardSummary } from '../types';
import DashboardCard from '../components/DashboardCard';

const Dashboard: React.FC = () => {
  const [summary, setSummary] = useState<DashboardSummary | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchSummary = async () => {
      try {
        const response = await apiClient.get<DashboardSummary>('/dashboard/summary');
        setSummary(response.data);
      } catch (error) {
        console.error('Failed to fetch dashboard summary:', error);
      } finally {
        setLoading(false);
      }
    };
    fetchSummary();
  }, []);

  if (loading) {
    return <div className="text-gray-600">Loading dashboard...</div>;
  }

  if (!summary) {
    return <div className="text-red-600">Failed to load dashboard data</div>;
  }

  const riskData = [
    { name: 'Low', value: summary.risk_distribution.low, fill: '#10b981' },
    { name: 'Medium', value: summary.risk_distribution.medium, fill: '#eab308' },
    { name: 'High', value: summary.risk_distribution.high, fill: '#f97316' },
    { name: 'Critical', value: summary.risk_distribution.critical, fill: '#ef4444' },
  ];

  const getRiskColor = (level: string) => {
    const colors: Record<string, string> = {
      low: 'text-green-600',
      medium: 'text-yellow-600',
      high: 'text-orange-600',
      critical: 'text-red-600',
    };
    return colors[level.toLowerCase()] || 'text-gray-600';
  };

  return (
    <div>
      <h1 className="text-3xl font-bold text-gray-900 mb-8">Dashboard</h1>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <DashboardCard
          title="Total Models"
          value={summary.total_models}
          colorClass="text-blue-600"
        />
        <DashboardCard
          title="Open Incidents"
          value={summary.open_incidents}
          colorClass="text-orange-600"
        />
        <DashboardCard
          title="Compliance Score"
          value={`${summary.compliance_score}%`}
          colorClass="text-green-600"
        />
        <DashboardCard
          title="Open Alerts"
          value={summary.open_alerts}
          colorClass="text-red-600"
        />
      </div>

      {/* Risk Distribution Chart */}
      <div className="bg-white rounded-lg shadow-sm p-6 mb-8">
        <h2 className="text-xl font-semibold text-gray-900 mb-4">Risk Distribution</h2>
        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={riskData}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="name" />
            <YAxis />
            <Tooltip />
            <Bar dataKey="value" />
          </BarChart>
        </ResponsiveContainer>
      </div>

      {/* Recent Incidents */}
      <div className="bg-white rounded-lg shadow-sm p-6">
        <h2 className="text-xl font-semibold text-gray-900 mb-4">Recent Incidents</h2>
        <div className="overflow-x-auto">
          <table className="min-w-full">
            <thead>
              <tr className="border-b">
                <th className="text-left py-3 px-4 text-sm font-medium text-gray-700">Title</th>
                <th className="text-left py-3 px-4 text-sm font-medium text-gray-700">Type</th>
                <th className="text-left py-3 px-4 text-sm font-medium text-gray-700">Severity</th>
                <th className="text-left py-3 px-4 text-sm font-medium text-gray-700">Status</th>
                <th className="text-left py-3 px-4 text-sm font-medium text-gray-700">Date</th>
              </tr>
            </thead>
            <tbody>
              {summary.recent_incidents.slice(0, 5).map((incident) => (
                <tr key={incident.id} className="border-b hover:bg-gray-50">
                  <td className="py-3 px-4">{incident.title}</td>
                  <td className="py-3 px-4 text-sm text-gray-600">{incident.type}</td>
                  <td className="py-3 px-4">
                    <span className={`inline-block px-2 py-1 text-xs font-semibold rounded ${getRiskColor(incident.severity)}`}>
                      {incident.severity}
                    </span>
                  </td>
                  <td className="py-3 px-4 text-sm text-gray-600">{incident.status}</td>
                  <td className="py-3 px-4 text-sm text-gray-600">
                    {new Date(incident.created_at).toLocaleDateString()}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
