import React, { useEffect, useState } from 'react';
import { useFilterStore } from '../../stores/filterStore'; // Import global filter store
import { getDashboardSummary } from '../lib/apiClient';
import KPICard, { PlaceholderKPISVGIcon } from '../components/ui/KPICard';

interface SummaryData {
  total_revenue?: number;
  revenue_growth?: number;
  total_transactions?: number;
  transaction_growth?: number;
  unique_customers?: number;
  customer_growth?: number; // Assuming this might exist
  avg_order_value?: number;
  aov_growth?: number; // Assuming this might exist
  // Add other expected fields based on actual API response
}

const OverviewPage: React.FC = () => {
  const {
    dateRange: globalDateRange,
    selectedRegions,
    selectedBrands,
    selectedCategories,
    selectedStores
  } = useFilterStore();

  const [summaryData, setSummaryData] = useState<SummaryData | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        setError(null);

        const filters: any = {
          startDate: globalDateRange.start,
          endDate: globalDateRange.end,
          regions: selectedRegions.length > 0 ? selectedRegions.join(',') : undefined,
          brands: selectedBrands.length > 0 ? selectedBrands.join(',') : undefined,
          categories: selectedCategories.length > 0 ? selectedCategories.join(',') : undefined,
          stores: selectedStores.length > 0 ? selectedStores.join(',') : undefined,
        };
        // Remove undefined filters
        Object.keys(filters).forEach(key => filters[key] === undefined && delete filters[key]);

        // ACTUAL API CALL
        const data = await getDashboardSummary(filters);
        setSummaryData(data as SummaryData);
      } catch (err: any) {
        setError(err.message || 'Failed to fetch dashboard summary.');
        // Fallback to mock data for UI development
        const mockData: SummaryData = {
            total_revenue: 1250650.75,
            revenue_growth: 5.2,
            total_transactions: 42500,
            transaction_growth: -1.5,
            unique_customers: 15230,
            customer_growth: 2.1,
            avg_order_value: 29.43,
            aov_growth: 0.5,
          };
        setSummaryData(mockData);
        console.error("API Error, using mock data for OverviewPage:", err);

      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [globalDateRange, selectedRegions, selectedBrands, selectedCategories, selectedStores]);

  if (loading) {
    return <div className="p-4 text-center">Loading dashboard summary...</div>;
  }

  if (error && !summaryData) { // Show error only if no data (even mock) is available
    return <div className="p-4 text-center text-red-500">Error: {error}</div>;
  }

  if (!summaryData) {
    return <div className="p-4 text-center">No summary data available.</div>;
  }

  // Helper to determine growth type
  const getGrowthType = (growth: number | undefined) => {
    if (growth === undefined) return 'neutral';
    if (growth > 0) return 'positive';
    if (growth < 0) return 'negative';
    return 'neutral';
  };

  // Helper to format currency
  const formatCurrency = (value: number | undefined) => {
    if (value === undefined) return 'N/A';
    return new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' }).format(value);
  };

  // Helper to format numbers
  const formatNumber = (value: number | undefined) => {
    if (value === undefined) return 'N/A';
    return new Intl.NumberFormat('en-US').format(value);
  };


  return (
    <div className="p-4 space-y-4">
      <h1 className="text-2xl font-semibold text-slate-800">Overview Dashboard</h1>

      {error && <div className="p-3 text-sm text-orange-700 bg-orange-100 border border-orange-400 rounded-md">Warning: Could not connect to live data. Displaying cached or mock information. ({error})</div>}

      {/* Grid for KPI Cards */}
      <div className="grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-4">
        <KPICard
          title="Total Revenue"
          value={formatCurrency(summaryData.total_revenue)}
          growth={summaryData.revenue_growth}
          growthType={getGrowthType(summaryData.revenue_growth)}
          icon={<PlaceholderKPISVGIcon />}
          description="Total revenue from all transactions."
        />
        <KPICard
          title="Total Transactions"
          value={formatNumber(summaryData.total_transactions)}
          growth={summaryData.transaction_growth}
          growthType={getGrowthType(summaryData.transaction_growth)}
          icon={<PlaceholderKPISVGIcon />}
          description="Total number of transactions processed."
        />
        <KPICard
          title="Unique Customers"
          value={formatNumber(summaryData.unique_customers)}
          growth={summaryData.customer_growth}
          growthType={getGrowthType(summaryData.customer_growth)}
          icon={<PlaceholderKPISVGIcon />}
          description="Number of distinct customers."
        />
        <KPICard
          title="Average Order Value"
          value={formatCurrency(summaryData.avg_order_value)}
          growth={summaryData.aov_growth}
          growthType={getGrowthType(summaryData.aov_growth)}
          icon={<PlaceholderKPISVGIcon />}
          description="Average revenue per transaction."
        />
      </div>

      {/* Placeholder for more charts/tables */}
      <div className="mt-8 p-6 bg-white shadow-lg rounded-lg border border-slate-200">
        <h3 className="text-xl font-semibold text-slate-800">Further Analysis (Coming Soon)</h3>
        <p className="text-slate-600">Detailed charts and data tables will be displayed here.</p>
      </div>
    </div>
  );
};

export default OverviewPage;
