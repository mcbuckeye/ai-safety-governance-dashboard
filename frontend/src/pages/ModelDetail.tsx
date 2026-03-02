import React, { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import apiClient from '../api/client';
import { AIModel, Incident, PolicyModelMapping } from '../types';

const ModelDetail: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const [model, setModel] = useState<AIModel | null>(null);
  const [incidents, setIncidents] = useState<Incident[]>([]);
  const [compliance, setCompliance] = useState<PolicyModelMapping[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [modelRes, incidentsRes, complianceRes] = await Promise.all([
          apiClient.get<AIModel>(`/models/${id}`),
          apiClient.get<Incident[]>(`/incidents/?model_id=${id}`),
          apiClient.get<PolicyModelMapping[]>(`/compliance/?model_id=${id}`),
        ]);
        setModel(modelRes.data);
        setIncidents(incidentsRes.data);
        setCompliance(complianceRes.data);
      } catch (error) {
        console.error('Failed to fetch model details:', error);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, [id]);

  const handleApprove = async () => {
    try {
      await apiClient.post(`/models/${id}/approve`);
      if (model) {
        setModel({ ...model, status: 'approved' });
      }
    } catch (error) {
      console.error('Failed to approve model:', error);
    }
  };

  const getRiskColor = (score: number) => {
    if (score >= 7) return 'bg-red-500';
    if (score >= 5) return 'bg-orange-500';
    if (score >= 3) return 'bg-yellow-500';
    return 'bg-green-500';
  };

  const getComplianceColor = (status: string) => {
    const colors: Record<string, string> = {
      compliant: 'bg-green-100 text-green-800',
      'non-compliant': 'bg-red-100 text-red-800',
      'under-review': 'bg-yellow-100 text-yellow-800',
    };
    return colors[status.toLowerCase()] || 'bg-gray-100 text-gray-800';
  };

  if (loading) {
    return <div className="text-gray-600">Loading model details...</div>;
  }

  if (!model) {
    return <div className="text-red-600">Model not found</div>;
  }

  return (
    <div>
      {/* Model Header */}
      <div className="bg-white rounded-lg shadow-sm p-6 mb-6">
        <div className="flex justify-between items-start mb-4">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">{model.name}</h1>
            <p className="text-gray-600 mt-1">Version {model.version}</p>
          </div>
          {model.status === 'testing' && (
            <button
              onClick={handleApprove}
              className="px-4 py-2 bg-green-600 hover:bg-green-700 text-white rounded transition-colors"
            >
              Approve
            </button>
          )}
        </div>
        <p className="text-gray-700 mb-4">{model.description}</p>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div>
            <div className="text-sm text-gray-600">Team</div>
            <div className="font-medium">{model.team}</div>
          </div>
          <div>
            <div className="text-sm text-gray-600">Risk Score</div>
            <div className="font-medium">{model.risk_score.toFixed(1)}/10</div>
          </div>
          <div>
            <div className="text-sm text-gray-600">Risk Level</div>
            <div className="font-medium capitalize">{model.risk_level}</div>
          </div>
          <div>
            <div className="text-sm text-gray-600">Status</div>
            <div className="font-medium capitalize">{model.status}</div>
          </div>
        </div>
      </div>

      {/* Risk Categories */}
      {model.risk_categories && model.risk_categories.length > 0 && (
        <div className="bg-white rounded-lg shadow-sm p-6 mb-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">Risk Categories</h2>
          <div className="space-y-3">
            {model.risk_categories.map((category) => (
              <div key={category.id}>
                <div className="flex justify-between text-sm mb-1">
                  <span className="font-medium capitalize">{category.category}</span>
                  <span className="text-gray-600">{category.score.toFixed(1)}/10</span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div
                    className={`h-2 rounded-full ${getRiskColor(category.score)}`}
                    style={{ width: `${(category.score / 10) * 100}%` }}
                  />
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Linked Incidents */}
      <div className="bg-white rounded-lg shadow-sm p-6 mb-6">
        <h2 className="text-xl font-semibold text-gray-900 mb-4">Linked Incidents</h2>
        {incidents.length === 0 ? (
          <p className="text-gray-600">No incidents reported for this model.</p>
        ) : (
          <div className="space-y-2">
            {incidents.map((incident) => (
              <div key={incident.id} className="flex justify-between items-center p-3 bg-gray-50 rounded">
                <div>
                  <div className="font-medium">{incident.title}</div>
                  <div className="text-sm text-gray-600">{incident.type}</div>
                </div>
                <div className="text-sm">
                  <span className={`px-2 py-1 rounded ${incident.severity === 'critical' ? 'bg-red-100 text-red-800' : 'bg-yellow-100 text-yellow-800'}`}>
                    {incident.severity}
                  </span>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Compliance Status */}
      <div className="bg-white rounded-lg shadow-sm p-6">
        <h2 className="text-xl font-semibold text-gray-900 mb-4">Compliance Status</h2>
        {compliance.length === 0 ? (
          <p className="text-gray-600">No compliance mappings found.</p>
        ) : (
          <div className="space-y-2">
            {compliance.map((mapping) => (
              <div key={mapping.id} className="flex justify-between items-center p-3 bg-gray-50 rounded">
                <div>
                  <div className="font-medium">Policy #{mapping.policy_id}</div>
                  {mapping.notes && <div className="text-sm text-gray-600">{mapping.notes}</div>}
                </div>
                <span className={`px-3 py-1 text-sm font-semibold rounded ${getComplianceColor(mapping.compliance_status)}`}>
                  {mapping.compliance_status}
                </span>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default ModelDetail;
