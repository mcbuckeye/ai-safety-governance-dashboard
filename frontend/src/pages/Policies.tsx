import React, { useEffect, useState } from 'react';
import apiClient from '../api/client';
import { Policy, ComplianceMatrix } from '../types';

const Policies: React.FC = () => {
  const [policies, setPolicies] = useState<Policy[]>([]);
  const [matrix, setMatrix] = useState<ComplianceMatrix | null>(null);
  const [loading, setLoading] = useState(true);
  const [view, setView] = useState<'list' | 'matrix'>('list');

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      const [policiesRes, matrixRes] = await Promise.all([
        apiClient.get<Policy[]>('/policies/'),
        apiClient.get<ComplianceMatrix>('/compliance/matrix'),
      ]);
      setPolicies(policiesRes.data);
      setMatrix(matrixRes.data);
    } catch (error) {
      console.error('Failed to fetch policies:', error);
    } finally {
      setLoading(false);
    }
  };

  const getComplianceStatus = (modelId: number, policyId: number): string => {
    if (!matrix) return 'unknown';
    const mapping = matrix.mappings.find(
      (m) => m.model_id === modelId && m.policy_id === policyId
    );
    return mapping?.compliance_status || 'unknown';
  };

  const getStatusColor = (status: string) => {
    const colors: Record<string, string> = {
      compliant: 'bg-green-500',
      'non-compliant': 'bg-red-500',
      'under-review': 'bg-yellow-500',
      unknown: 'bg-gray-300',
    };
    return colors[status] || 'bg-gray-300';
  };

  if (loading) {
    return <div className="text-gray-600">Loading policies...</div>;
  }

  return (
    <div>
      <div className="flex justify-between items-center mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Policies</h1>
        <div className="flex gap-2">
          <button
            onClick={() => setView('list')}
            className={`px-4 py-2 rounded transition-colors ${
              view === 'list'
                ? 'bg-blue-600 text-white'
                : 'bg-gray-200 text-gray-800 hover:bg-gray-300'
            }`}
          >
            List
          </button>
          <button
            onClick={() => setView('matrix')}
            className={`px-4 py-2 rounded transition-colors ${
              view === 'matrix'
                ? 'bg-blue-600 text-white'
                : 'bg-gray-200 text-gray-800 hover:bg-gray-300'
            }`}
          >
            Matrix
          </button>
        </div>
      </div>

      {view === 'list' ? (
        <div className="space-y-4">
          {policies.map((policy) => (
            <div key={policy.id} className="bg-white rounded-lg shadow-sm p-6">
              <h2 className="text-xl font-semibold text-gray-900 mb-2">{policy.name}</h2>
              <p className="text-gray-700 mb-4">{policy.description}</p>
              <div className="mb-4">
                <h3 className="text-sm font-medium text-gray-700 mb-2">Requirements:</h3>
                <p className="text-sm text-gray-600 whitespace-pre-wrap">{policy.requirements}</p>
              </div>
              <div>
                <h3 className="text-sm font-medium text-gray-700 mb-2">Applicable Model Types:</h3>
                <div className="flex flex-wrap gap-2">
                  {policy.applicable_model_types.map((type, idx) => (
                    <span
                      key={idx}
                      className="px-3 py-1 bg-blue-100 text-blue-800 text-sm rounded"
                    >
                      {type}
                    </span>
                  ))}
                </div>
              </div>
              <div className="mt-4 text-xs text-gray-500">
                Created: {new Date(policy.created_at).toLocaleDateString()}
              </div>
            </div>
          ))}
        </div>
      ) : (
        <div className="bg-white rounded-lg shadow-sm overflow-x-auto">
          {matrix && (
            <table className="min-w-full">
              <thead className="bg-gray-50">
                <tr>
                  <th className="text-left py-3 px-4 text-sm font-medium text-gray-700 sticky left-0 bg-gray-50">
                    Model
                  </th>
                  {matrix.policies.map((policy) => (
                    <th
                      key={policy.id}
                      className="text-center py-3 px-4 text-sm font-medium text-gray-700 min-w-[120px]"
                    >
                      {policy.name}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {matrix.models.map((model) => (
                  <tr key={model.id} className="border-b hover:bg-gray-50">
                    <td className="py-3 px-4 font-medium sticky left-0 bg-white">
                      {model.name}
                      <div className="text-xs text-gray-500">{model.version}</div>
                    </td>
                    {matrix.policies.map((policy) => {
                      const status = getComplianceStatus(model.id, policy.id);
                      return (
                        <td key={policy.id} className="py-3 px-4 text-center">
                          <div
                            className={`w-6 h-6 rounded-full mx-auto ${getStatusColor(status)}`}
                            title={status}
                          />
                        </td>
                      );
                    })}
                  </tr>
                ))}
              </tbody>
            </table>
          )}
          <div className="p-4 bg-gray-50 border-t flex gap-4 text-sm">
            <div className="flex items-center gap-2">
              <div className="w-4 h-4 rounded-full bg-green-500" />
              <span>Compliant</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-4 h-4 rounded-full bg-yellow-500" />
              <span>Under Review</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-4 h-4 rounded-full bg-red-500" />
              <span>Non-Compliant</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-4 h-4 rounded-full bg-gray-300" />
              <span>Unknown</span>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Policies;
