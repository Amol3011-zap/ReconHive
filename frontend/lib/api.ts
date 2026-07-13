// API client for ReconHive backend
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

export const api = {
  async get<T>(path: string): Promise<T> {
    const response = await fetch(`${API_BASE_URL}${path}`, {
      headers: {
        'Authorization': `Bearer ${getToken()}`,
      },
    });
    if (!response.ok) throw new Error(`API error: ${response.status}`);
    return response.json();
  },

  async post<T>(path: string, data: any): Promise<T> {
    const response = await fetch(`${API_BASE_URL}${path}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${getToken()}`,
      },
      body: JSON.stringify(data),
    });
    if (!response.ok) throw new Error(`API error: ${response.status}`);
    return response.json();
  },

  async put<T>(path: string, data: any): Promise<T> {
    const response = await fetch(`${API_BASE_URL}${path}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${getToken()}`,
      },
      body: JSON.stringify(data),
    });
    if (!response.ok) throw new Error(`API error: ${response.status}`);
    return response.json();
  },

  async delete(path: string): Promise<void> {
    const response = await fetch(`${API_BASE_URL}${path}`, {
      method: 'DELETE',
      headers: {
        'Authorization': `Bearer ${getToken()}`,
      },
    });
    if (!response.ok) throw new Error(`API error: ${response.status}`);
  },
};

function getToken(): string {
  if (typeof window === 'undefined') return '';
  return localStorage.getItem('token') || 'demo-token';
}

// Mock data for demo (when API is unavailable)
export const mockData = {
  engagements: [
    { id: '1', name: 'Acme Corp Internal Test', target: 'acme.com', status: 'ACTIVE', type: 'PENETRATION_TEST', created_at: new Date(Date.now() - 7 * 24 * 60 * 60 * 1000) },
    { id: '2', name: 'Beta Finance Security Audit', target: 'betafinance.io', status: 'ACTIVE', type: 'VULNERABILITY_ASSESSMENT', created_at: new Date(Date.now() - 5 * 24 * 60 * 60 * 1000) },
    { id: '3', name: 'DataCorp Web App Assessment', target: 'data.example.com', status: 'COMPLETED', type: 'PENETRATION_TEST', created_at: new Date(Date.now() - 30 * 24 * 60 * 60 * 1000) },
  ],
  assets: 4231,
  scans: 7,
  findings: 156,
  criticalFindings: 9,
  evidence: 156,
  aiInsights: 4,
};
