import React from 'react';

const Guide: React.FC = () => {
  return (
    <div>
      <h1 className="text-3xl font-bold text-gray-900 mb-8">User Guide</h1>

      <div className="bg-white rounded-lg shadow-sm p-6 space-y-6">
        <section>
          <h2 className="text-2xl font-semibold text-gray-900 mb-3">Welcome to AI Safety Dashboard</h2>
          <p className="text-gray-700">
            This dashboard helps you manage and monitor AI models, track incidents, ensure policy compliance,
            and maintain comprehensive audit trails for your organization's AI systems.
          </p>
        </section>

        <section>
          <h2 className="text-xl font-semibold text-gray-900 mb-3">Dashboard</h2>
          <p className="text-gray-700 mb-2">
            The dashboard provides an executive overview of your AI safety posture:
          </p>
          <ul className="list-disc list-inside text-gray-700 space-y-1 ml-4">
            <li>Total number of registered AI models</li>
            <li>Open incidents requiring attention</li>
            <li>Overall compliance score</li>
            <li>Active alerts</li>
            <li>Risk distribution across all models</li>
            <li>Recent incidents and audit activity</li>
          </ul>
        </section>

        <section>
          <h2 className="text-xl font-semibold text-gray-900 mb-3">Models</h2>
          <p className="text-gray-700 mb-2">
            The Models page allows you to:
          </p>
          <ul className="list-disc list-inside text-gray-700 space-y-1 ml-4">
            <li>View all registered AI models in your organization</li>
            <li>Filter models by risk level and status</li>
            <li>Register new models for tracking and compliance</li>
            <li>Click on any model to view detailed information including risk categories, linked incidents, and compliance status</li>
          </ul>
        </section>

        <section>
          <h2 className="text-xl font-semibold text-gray-900 mb-3">Incidents</h2>
          <p className="text-gray-700 mb-2">
            Track and manage AI safety incidents:
          </p>
          <ul className="list-disc list-inside text-gray-700 space-y-1 ml-4">
            <li>Report new incidents (safety, bias, privacy, performance)</li>
            <li>Filter incidents by type, severity, and status</li>
            <li>Link incidents to specific models</li>
            <li>Track incident resolution lifecycle</li>
          </ul>
        </section>

        <section>
          <h2 className="text-xl font-semibold text-gray-900 mb-3">Policies</h2>
          <p className="text-gray-700 mb-2">
            Manage compliance policies and review compliance status:
          </p>
          <ul className="list-disc list-inside text-gray-700 space-y-1 ml-4">
            <li>View all organizational AI policies</li>
            <li>See policy requirements and applicable model types</li>
            <li>Use the compliance matrix to get a visual overview of which models comply with which policies</li>
          </ul>
        </section>

        <section>
          <h2 className="text-xl font-semibold text-gray-900 mb-3">Alerts</h2>
          <p className="text-gray-700 mb-2">
            Monitor and respond to active alerts:
          </p>
          <ul className="list-disc list-inside text-gray-700 space-y-1 ml-4">
            <li>View alerts filtered by status</li>
            <li>Acknowledge alerts to signal awareness</li>
            <li>Resolve alerts once addressed</li>
          </ul>
        </section>

        <section>
          <h2 className="text-xl font-semibold text-gray-900 mb-3">Audit Log</h2>
          <p className="text-gray-700 mb-2">
            The audit log provides a comprehensive trail of all actions:
          </p>
          <ul className="list-disc list-inside text-gray-700 space-y-1 ml-4">
            <li>Filter by action type and resource type</li>
            <li>View detailed information about each action</li>
            <li>Track who did what and when</li>
          </ul>
        </section>

        <section>
          <h2 className="text-xl font-semibold text-gray-900 mb-3">Risk Levels</h2>
          <p className="text-gray-700 mb-2">Risk levels are color-coded for easy identification:</p>
          <ul className="list-disc list-inside text-gray-700 space-y-1 ml-4">
            <li><span className="text-green-600 font-semibold">Low</span> - Minimal risk</li>
            <li><span className="text-yellow-600 font-semibold">Medium</span> - Moderate risk, monitor closely</li>
            <li><span className="text-orange-600 font-semibold">High</span> - Significant risk, requires attention</li>
            <li><span className="text-red-600 font-semibold">Critical</span> - Severe risk, immediate action required</li>
          </ul>
        </section>

        <section>
          <h2 className="text-xl font-semibold text-gray-900 mb-3">Need Help?</h2>
          <p className="text-gray-700">
            If you have questions or need assistance, please contact your system administrator or
            AI safety officer.
          </p>
        </section>
      </div>
    </div>
  );
};

export default Guide;
