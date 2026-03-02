import React, { useEffect, useState } from 'react';
import apiClient from '../api/client';
import { AuditEntry } from '../types';

const AuditLog: React.FC = () => {
  const [entries, setEntries] = useState<AuditEntry[]>([]);
  const [loading, setLoading] = useState(true);
  const [filterAction, setFilterAction] = useState('');
  const [filterResourceType, setFilterResourceType] = useState('');

  useEffect(() => {
    fetchAuditLog();
  }, []);

  const fetchAuditLog = async () => {
    try {
      const response = await apiClient.get<AuditEntry[]>('/audit/');
      setEntries(response.data);
    } catch (error) {
      console.error('Failed to fetch audit log:', error);
    } finally {
      setLoading(false);
    }
  };

  const filteredEntries = entries.filter((entry) => {
    if (filterAction && entry.action.toLowerCase() !== filterAction.toLowerCase()) return false;
    if (filterResourceType && entry.resource_type.toLowerCase() !== filterResourceType.toLowerCase()) return false;
    return true;
  });

  if (loading) {
    return <div className="text-gray-600">Loading audit log...</div>;
  }

  return (
    <div>
      <h1 className="text-3xl font-bold text-gray-900 mb-8">Audit Log</h1>

      {/* Filters */}
      <div className="bg-white rounded-lg shadow-sm p-4 mb-6 flex gap-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Action</label>
          <select
            value={filterAction}
            onChange={(e) => setFilterAction(e.target.value)}
            className="px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-600"
          >
            <option value="">All</option>
            <option value="create">Create</option>
            <option value="update">Update</option>
            <option value="delete">Delete</option>
            <option value="approve">Approve</option>
            <option value="login">Login</option>
          </select>
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Resource Type</label>
          <select
            value={filterResourceType}
            onChange={(e) => setFilterResourceType(e.target.value)}
            className="px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-600"
          >
            <option value="">All</option>
            <option value="model">Model</option>
            <option value="incident">Incident</option>
            <option value="policy">Policy</option>
            <option value="alert">Alert</option>
            <option value="user">User</option>
          </select>
        </div>
      </div>

      {/* Audit Table */}
      <div className="bg-white rounded-lg shadow-sm overflow-x-auto">
        <table className="min-w-full">
          <thead className="bg-gray-50">
            <tr>
              <th className="text-left py-3 px-4 text-sm font-medium text-gray-700">Timestamp</th>
              <th className="text-left py-3 px-4 text-sm font-medium text-gray-700">User</th>
              <th className="text-left py-3 px-4 text-sm font-medium text-gray-700">Action</th>
              <th className="text-left py-3 px-4 text-sm font-medium text-gray-700">Resource Type</th>
              <th className="text-left py-3 px-4 text-sm font-medium text-gray-700">Resource ID</th>
              <th className="text-left py-3 px-4 text-sm font-medium text-gray-700">Details</th>
            </tr>
          </thead>
          <tbody>
            {filteredEntries.map((entry) => (
              <tr key={entry.id} className="border-b hover:bg-gray-50">
                <td className="py-3 px-4 text-sm text-gray-600">
                  {new Date(entry.created_at).toLocaleString()}
                </td>
                <td className="py-3 px-4 text-sm text-gray-600">User #{entry.user_id}</td>
                <td className="py-3 px-4">
                  <span className="px-2 py-1 bg-blue-100 text-blue-800 text-xs font-semibold rounded capitalize">
                    {entry.action}
                  </span>
                </td>
                <td className="py-3 px-4 text-sm text-gray-600 capitalize">{entry.resource_type}</td>
                <td className="py-3 px-4 text-sm text-gray-600">
                  {entry.resource_id || 'N/A'}
                </td>
                <td className="py-3 px-4 text-sm text-gray-600">
                  <pre className="text-xs overflow-x-auto max-w-md">
                    {JSON.stringify(entry.details, null, 2)}
                  </pre>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default AuditLog;
