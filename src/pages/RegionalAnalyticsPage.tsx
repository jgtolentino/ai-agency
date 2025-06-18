import React, { useEffect, useState } from 'react';
import { useFilterStore } from '../../stores/filterStore'; // Import global filter store
import { getRegionalPerformance } from '../lib/apiClient';

interface RegionalData {
  region_id: string | number;
  region_name: string;
  total_revenue: number;
  transaction_count: number;
  avg_order_value: number;
  growth_rate?: number;
  // Add other metrics as needed from API
}

const RegionalAnalyticsPage: React.FC = () => {
  const {
    dateRange: globalDateRange,
    // selectedRegions, // Not used as a filter *for* regional performance, but as data points
    selectedBrands,
    selectedCategories,
    selectedStores,
  } = useFilterStore();

  const [regionalData, setRegionalData] = useState<RegionalData[] | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  // Local filterPeriod state removed

  useEffect(() => {
    const fetchData = async () => {
      setLoading(true);
      setError(null);
      try {
        const filters: any = {
          startDate: globalDateRange.start,
          endDate: globalDateRange.end,
          brands: selectedBrands.length > 0 ? selectedBrands.join(',') : undefined,
          categories: selectedCategories.length > 0 ? selectedCategories.join(',') : undefined,
          stores: selectedStores.length > 0 ? selectedStores.join(',') : undefined,
        };
        if (!filters.startDate && !filters.endDate) {
            filters.period = 'all_time'; // Default if API needs it
        }
        Object.keys(filters).forEach(key => filters[key] === undefined && delete filters[key]);

        const data = await getRegionalPerformance(filters);
        setRegionalData(data);
      } catch (err: any) {
        console.error("API Error, using mock data for RegionalAnalyticsPage:", err);
        setError(err.message || 'Failed to fetch regional performance data.');
        // Fallback to mock data
        const mockData: RegionalData[] = [
          { region_id: 'NA1', region_name: 'North America - West', total_revenue: 1250000, transaction_count: 15200, avg_order_value: 82.24, growth_rate: 5.2 },
          { region_id: 'NA2', region_name: 'North America - East', total_revenue: 980000, transaction_count: 12100, avg_order_value: 80.99, growth_rate: -1.5 },
          { region_id: 'EU1', region_name: 'Europe - Central', total_revenue: 1150000, transaction_count: 14300, avg_order_value: 80.42, growth_rate: 3.1 },
          { region_id: 'EU2', region_name: 'Europe - UK & Ireland', total_revenue: 750000, transaction_count: 9500, avg_order_value: 78.95, growth_rate: 0.5 },
          { region_id: 'APAC1', region_name: 'Asia Pacific - ANZ', total_revenue: 600000, transaction_count: 7200, avg_order_value: 83.33, growth_rate: 7.8 },
        ];
        setRegionalData(mockData);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [globalDateRange, selectedBrands, selectedCategories, selectedStores]);

  const formatCurrency = (value: number) => new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' }).format(value);
  const formatNumber = (value: number) => new Intl.NumberFormat('en-US').format(value);

  return (
    <div className="p-4 space-y-6">
      <div className="flex justify-between items-center"> {/* Title remains, local filter UI removed */}
        <h1 className="text-2xl font-semibold text-slate-800">Regional Analytics</h1>
      </div>

      {error && !regionalData && <div className="p-4 text-center text-red-500">Error fetching data: {error}</div>}
      {error && regionalData && <div className="p-3 text-sm text-orange-700 bg-orange-100 border border-orange-400 rounded-md">Warning: Could not connect to live data. Displaying cached or mock information. ({error})</div>}

      {/* Placeholder for Map Visualization */}
      <div className="p-6 text-center bg-slate-50 rounded-lg shadow border border-slate-200">
        <h3 className="text-xl font-semibold text-slate-700 mb-2">Geospatial Map for Regional Analysis</h3>
        <p className="text-slate-500">Map visualization will be integrated here in a future step.</p>
      </div>

      {/* Table for Regional Data */}
      <div className="bg-white shadow-lg rounded-lg border border-slate-200 overflow-x-auto">
        {loading && <div className="p-4 text-center">Loading regional data table...</div>}
        {!loading && regionalData && (
          <table className="min-w-full divide-y divide-slate-200">
            <thead className="bg-slate-50">
              <tr>
                <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-slate-500 uppercase tracking-wider">Region Name</th>
                <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-slate-500 uppercase tracking-wider">Total Revenue</th>
                <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-slate-500 uppercase tracking-wider">Transactions</th>
                <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-slate-500 uppercase tracking-wider">Avg. Order Value</th>
                <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-slate-500 uppercase tracking-wider">Growth Rate (%)</th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-slate-200">
              {regionalData.map((region) => (
                <tr key={region.region_id} className="hover:bg-slate-50">
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-slate-900">{region.region_name}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-slate-700">{formatCurrency(region.total_revenue)}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-slate-700">{formatNumber(region.transaction_count)}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-slate-700">{formatCurrency(region.avg_order_value)}</td>
                  <td className={`px-6 py-4 whitespace-nowrap text-sm font-semibold ${ (region.growth_rate ?? 0) >= 0 ? 'text-emerald-600' : 'text-red-600'}`}>
                    {region.growth_rate !== undefined ? `${region.growth_rate.toFixed(1)}%` : 'N/A'}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
        {!loading && !regionalData && !error && <div className="p-4 text-center">No regional data available.</div>}
      </div>
    </div>
  );
};

export default RegionalAnalyticsPage;
