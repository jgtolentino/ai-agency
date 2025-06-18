import axios, { AxiosInstance, AxiosError } from 'axios';

// Define the base URL: Use Vite's env variable or fallback for local dev
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:3001/api';

// Create an Axios instance
const apiClient: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Function to set the JWT token for authorization
export const setAuthToken = (token: string | null): void => {
  if (token) {
    apiClient.defaults.headers.common['Authorization'] = `Bearer ${token}`;
    localStorage.setItem('authToken', token);
  } else {
    delete apiClient.defaults.headers.common['Authorization'];
    localStorage.removeItem('authToken');
  }
};

// Get AI Insights
interface AIInsight {
  id: string;
  title: string;
  summary: string;
  suggested_action: string;
  severity: 'low' | 'medium' | 'high' | 'critical';
  date: string; // ISO date string
  category?: string; // e.g., "Inventory", "Sales Trend", "Customer Behavior"
}

// Base Filters applicable to many endpoints
interface BaseFilters {
  startDate?: string | null;
  endDate?: string | null;
  regions?: string; // Comma-separated list of region IDs/names
  brands?: string;  // Comma-separated list of brand IDs/names
  categories?: string; // Comma-separated list of category IDs/names
  stores?: string; // Comma-separated list of store IDs/names
  period?: string; // Fallback like '7d', '30d', 'all_time' if no dateRange
}

interface AIInsightsFilters extends BaseFilters { // AI Insights might also be filterable by general criteria
  priority?: 'high' | 'critical'; // Example specific filter
  // category?: string; // Already in BaseFilters if 'categories' is used, or could be specific here
}
export const getAIInsights = async (filters: AIInsightsFilters = {}): Promise<AIInsight[]> => {
  try {
    const response = await apiClient.get<AIInsight[]>('/ai/insights', { params: filters });
    return response.data;
  } catch (error) {
    console.error('Failed to fetch AI insights:', error);
    throw error;
  }
};

// Get Regional Performance
interface RegionalPerformanceDataPoint {
  region_id: string | number;
  region_name: string;
  total_revenue: number;
  transaction_count: number;
  avg_order_value: number;
  growth_rate?: number; // Optional
}
interface RegionalPerformanceFilters extends BaseFilters {
  country?: string; // Example specific filter
}
export const getRegionalPerformance = async (filters: RegionalPerformanceFilters = {}): Promise<RegionalPerformanceDataPoint[]> => {
  try {
    const response = await apiClient.get<RegionalPerformanceDataPoint[]>('/analytics/regions/performance', { params: filters });
    return response.data;
  } catch (error) {
    console.error('Failed to fetch regional performance:', error);
    throw error;
  }
};

// Get Age Distribution
interface AgeDistributionDataPoint {
  age_group: string; // e.g., "18-24", "25-34"
  customer_count: number;
  total_spent?: number; // Optional
}
interface AgeDistributionFilters extends BaseFilters {}

export const getAgeDistribution = async (filters: AgeDistributionFilters = {}): Promise<AgeDistributionDataPoint[]> => {
  try {
    const response = await apiClient.get<AgeDistributionDataPoint[]>('/kpi/age-distribution', { params: filters });
    return response.data;
  } catch (error) {
    console.error('Failed to fetch age distribution:', error);
    throw error;
  }
};

// Get Gender Distribution
interface GenderDistributionDataPoint {
  gender: string; // e.g., "Male", "Female", "Other"
  customer_count: number;
  total_spent?: number; // Optional
}
interface GenderDistributionFilters extends BaseFilters {}

export const getGenderDistribution = async (filters: GenderDistributionFilters = {}): Promise<GenderDistributionDataPoint[]> => {
  try {
    const response = await apiClient.get<GenderDistributionDataPoint[]>('/kpi/gender-distribution', { params: filters });
    return response.data;
  } catch (error)
 {
    console.error('Failed to fetch gender distribution:', error);
    throw error;
  }
};

// Get Product Categories Summary
interface ProductCategoryData {
  name: string; // Category name
  value: number; // e.g., total sales or quantity
  change?: number; // Optional: period-over-period change
}

interface ProductCategoryFilters {
  period?: string;
  metric?: 'sales' | 'quantity'; // Example specific filter
}
interface ProductCategoryFiltersExtended extends BaseFilters, ProductCategoryFilters {}


export const getProductCategoriesSummary = async (filters: ProductCategoryFiltersExtended = {}): Promise<ProductCategoryData[]> => {
  try {
    const response = await apiClient.get<ProductCategoryData[]>('/analytics/products/categories-summary', {
      params: filters,
    });
    return response.data;
  } catch (error) {
    console.error('Failed to fetch product categories summary:', error);
    throw error;
  }
};

// Function to clear the JWT token
export const clearAuthToken = (): void => {
  setAuthToken(null);
};

// On load, check localStorage for an existing token and set it
const storedToken = localStorage.getItem('authToken');
if (storedToken) {
  setAuthToken(storedToken);
}

// Response interceptor to handle 401 errors
apiClient.interceptors.response.use(
  (response) => response,
  (error: AxiosError) => {
    if (error.response && error.response.status === 401) {
      // Unauthorized: clear token and redirect to login
      clearAuthToken();
      // Assuming a router is available globally or passed around,
      // or using window.location for simplicity here.
      // In a real app, this might involve a navigation service or history object.
      if (window.location.pathname !== '/login') {
        window.location.href = '/login';
      }
    }
    return Promise.reject(error);
  }
);

// --- Initial Data Fetching Functions ---

// Login
interface LoginResponse {
  token: string;
  user: any; // Define a proper user type later
}

export const login = async (email_address: string, password_hash: string): Promise<LoginResponse> => {
  try {
    // Corrected payload to match typical backend expectations
    const response = await apiClient.post<LoginResponse>('/auth/login', { email_address, password_hash });
    if (response.data.token) {
      setAuthToken(response.data.token);
    }
    return response.data;
  } catch (error) {
    console.error('Login failed:', error);
    throw error; // Re-throw to be handled by the caller
  }
};


// Logout
export const logout = async (): Promise<void> => {
  try {
    // Optional: Call a backend logout endpoint if it exists
    // await apiClient.post('/auth/logout');
  } catch (error) {
    console.error('Logout API call failed (if implemented):', error);
    // Don't let this block client-side logout
  } finally {
    clearAuthToken();
    // Optionally redirect to login page
    if (window.location.pathname !== '/login') {
       // window.location.href = '/login'; // Decided by caller usually
    }
  }
};

// Get Dashboard Summary
interface DashboardSummary {
  // Define expected structure based on API
  totalSales: number;
  totalOrders: number;
  newCustomers: number;
  // ... other KPIs
}
// Update DashboardSummary to accept filters
export const getDashboardSummary = async (filters: BaseFilters = {}): Promise<DashboardSummary> => {
  try {
    const response = await apiClient.get<DashboardSummary>('/kpi/summary', { params: filters });
    return response.data;
  } catch (error) {
    console.error('Failed to fetch dashboard summary:', error);
    throw error;
  }
};

// Get Transaction Trends
interface TransactionFilters extends BaseFilters {
  // period?: string; // Already in BaseFilters
  segment?: string; // e.g., 'product_category', 'customer_demographic', specific to trends
}

interface TransactionTrendData { // This is the response structure, not filters
  // Define expected structure
  date: string;
  value: number;
}

export const getTransactionTrends = async (filters: TransactionFilters = {}): Promise<TransactionTrendData[]> => {
  try {
    const response = await apiClient.get<TransactionTrendData[]>('/analytics/transactions/trends', {
      params: filters,
    });
    return response.data;
  } catch (error) {
    console.error('Failed to fetch transaction trends:', error);
    throw error;
  }
};

export default apiClient;
