
import axios from 'axios';

export const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const original = error.config;
    const refreshToken = localStorage.getItem('refreshToken');
    if (error.response?.status === 401 && refreshToken && !original._retry) {
      original._retry = true;
      try {
        const response = await axios.post(`${API_BASE_URL}/api/v1/auth/refresh`, {
          refresh_token: refreshToken,
        });
        localStorage.setItem('token', response.data.access_token);
        localStorage.setItem('refreshToken', response.data.refresh_token);
        original.headers.Authorization = `Bearer ${response.data.access_token}`;
        return api(original);
      } catch (refreshError) {
        localStorage.removeItem('token');
        localStorage.removeItem('refreshToken');
      }
    }
    return Promise.reject(error);
  }
);

export const authAPI = {
  register: (data) => api.post('/api/v1/auth/register', data),
  login: (data) => api.post('/api/v1/auth/login', data),
  getMe: () => api.get('/api/v1/auth/me'),
  updateMe: (data) => api.put('/api/v1/auth/me', data),
  forgotPassword: (email) => api.post('/api/v1/auth/forgot-password', { email }),
  logout: (refreshToken) => api.post('/api/v1/auth/logout', { refresh_token: refreshToken }),
};

export const urlAPI = {
  list: (params = {}) => api.get('/api/v1/urls/', { params }),
  get: (id) => api.get(`/api/v1/urls/${id}`),
  create: (data) => api.post('/api/v1/urls/', data),
  update: (id, data) => api.put(`/api/v1/urls/${id}`, data),
  delete: (id) => api.delete(`/api/v1/urls/${id}`),
  bulk: (urls) => api.post('/api/v1/urls/bulk', { urls }),
  qr: (id) => api.get(`/api/v1/urls/${id}/qr`),
  exportCsv: () => api.get('/api/v1/urls/export/csv', { responseType: 'blob' }),
};

export const analyticsAPI = {
  getStats: () => api.get('/api/v1/analytics/stats'),
  searchURLs: (query, isActive, page = 1, size = 20) => api.get('/api/v1/analytics/urls', {
    params: { query, is_active: isActive, page, size }
  }),
  reportCsv: () => api.get('/api/v1/analytics/report.csv', { responseType: 'blob' }),
};

export const adminAPI = {
  summary: () => api.get('/api/v1/admin/summary'),
  users: (params = {}) => api.get('/api/v1/admin/users', { params }),
  setUserStatus: (id, isActive) => api.patch(`/api/v1/admin/users/${id}/status`, null, {
    params: { is_active: isActive },
  }),
};

export default api;
