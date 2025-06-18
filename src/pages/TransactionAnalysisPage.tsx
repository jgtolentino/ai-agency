import React, { useEffect, useState } from 'react';
import { useFilterStore } from '../../stores/filterStore'; // Import global filter store
import { getTransactionTrends } from '../lib/apiClient';
import { Line } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler, // For area fill if desired
} from 'chart.js';

// Register Chart.js components
ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler
);

// Define expected data structure from API (adjust as per actual API)
interface ApiTrendDataPoint {
  date: string; // e.g., "2023-01-01"
  total_revenue: number;
  transaction_count: number;
}

// Define structure for chart data state
interface ChartDataState {
  labels: string[];
  datasets: any[]; // Define more specific dataset type if needed
}

const TransactionAnalysisPage: React.FC = () => {
  const {
    dateRange: globalDateRange,
    selectedRegions,
    selectedBrands
  } = useFilterStore();

  const [trendsData, setTrendsData] = useState<ChartDataState | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  // Local dateRange state is removed, will use globalDateRange

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        setError(null);

        // Construct filter parameters for the API call
        const filters: any = {};
        if (globalDateRange.start && globalDateRange.end) {
          filters.startDate = globalDateRange.start;
          filters.endDate = globalDateRange.end;
        }
        if (selectedRegions.length > 0) {
          filters.regions = selectedRegions.join(',');
        }
        if (selectedBrands.length > 0) {
          filters.brands = selectedBrands.join(',');
        }
        // If a period string is still needed by API when no specific dates:
        // if (!filters.startDate && !filters.endDate) {
        //   filters.period = '30d'; // Default or derive from global state if available
        // }


        // ACTUAL API CALL using global filters
        const apiData: ApiTrendDataPoint[] = await getTransactionTrends(filters);

        // Transform API data for Chart.js
        const labels = apiData.map(item => new Date(item.date).toLocaleDateString());
        const revenueDataset = {
          label: 'Total Revenue',
          data: apiData.map(item => item.total_revenue),
          borderColor: 'rgb(75, 192, 192)',
          backgroundColor: 'rgba(75, 192, 192, 0.2)',
          tension: 0.1,
          yAxisID: 'yRevenue',
        };
        const transactionsDataset = {
          label: 'Transaction Count',
          data: apiData.map(item => item.transaction_count),
          borderColor: 'rgb(255, 99, 132)',
          backgroundColor: 'rgba(255, 99, 132, 0.2)',
          tension: 0.1,
          yAxisID: 'yTransactions',
        };
        setTrendsData({ labels, datasets: [revenueDataset, transactionsDataset] });

      } catch (err: any) {
        console.error("API Error, using mock data for TransactionAnalysisPage:", err);
        setError(err.message || 'Failed to fetch transaction trends.');

        // Fallback to mock data for UI development
        // Ensure mock data generation is independent of removed local dateRange
        const mockLength = (globalDateRange.start && globalDateRange.end) ?
                           Math.max(1, (new Date(globalDateRange.end).getTime() - new Date(globalDateRange.start).getTime()) / (1000*60*60*24))
                           : 30;

        const mockApiData: ApiTrendDataPoint[] = Array.from({ length: mockLength }, (_, i) => {
          const date = globalDateRange.start ? new Date(globalDateRange.start) : new Date();
          if (!globalDateRange.start) date.setDate(date.getDate() - (mockLength - 1 - i));
          else date.setDate(date.getDate() + i);

          return {
            date: date.toISOString().split('T')[0],
            total_revenue: Math.random() * 1000 + 5000 + i * 50, // Example data trend
            transaction_count: Math.random() * 50 + 100 + i * 2, // Example data trend
          };
        });
        const labels = mockApiData.map(item => new Date(item.date).toLocaleDateString());
        const revenueDataset = {
          label: 'Total Revenue (Mock)',
          data: mockApiData.map(item => item.total_revenue),
          borderColor: 'rgb(75, 192, 192)',
          backgroundColor: 'rgba(75, 192, 192, 0.2)',
          tension: 0.1,
          yAxisID: 'yRevenue',
        };
        const transactionsDataset = {
          label: 'Transaction Count (Mock)',
          data: mockApiData.map(item => item.transaction_count),
          borderColor: 'rgb(255, 99, 132)',
          backgroundColor: 'rgba(255, 99, 132, 0.2)',
          tension: 0.1,
          yAxisID: 'yTransactions',
        };
        setTrendsData({ labels, datasets: [revenueDataset, transactionsDataset] });

      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [globalDateRange, selectedRegions, selectedBrands]); // Refetch when global filters change

  const chartTitle = () => {
    let title = 'Transaction Trends';
    if (globalDateRange.start && globalDateRange.end) {
      const start = new Date(globalDateRange.start).toLocaleDateString();
      const end = new Date(globalDateRange.end).toLocaleDateString();
      title += ` (${start} - ${end})`;
    } else {
      title += ' (All Time or Default Period)'; // Adjust as per API default
    }
    if(selectedRegions.length > 0) title += ` | Regions: ${selectedRegions.join(', ')}`;
    if(selectedBrands.length > 0) title += ` | Brands: ${selectedBrands.join(', ')}`;
    return title;
  }

  const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'top' as const,
      },
      title: {
        display: true,
        text: chartTitle(),
        font: { size: 16 }, // Adjusted size for potentially longer titles
      },
      tooltip: {
        mode: 'index' as const,
        intersect: false,
      },
    },
    scales: {
      x: {
        title: { display: true, text: 'Date' },
      },
      yRevenue: {
        type: 'linear' as const,
        display: true,
        position: 'left' as const,
        title: { display: true, text: 'Total Revenue ($)' },
        grid: { drawOnChartArea: false }, // Only draw grid for one axis to avoid clutter
      },
      yTransactions: {
        type: 'linear' as const,
        display: true,
        position: 'right' as const,
        title: { display: true, text: 'Transaction Count' },
      },
    },
    interaction: {
      mode: 'nearest' as const,
      axis: 'x' as const,
      intersect: false,
    },
  };

  return (
    <div className="p-4 space-y-4">
      <div className="flex justify-between items-center"> {/* Title remains, local filter UI removed */}
        <h1 className="text-2xl font-semibold text-slate-800">Transaction Analysis</h1>
      </div>

      {error && !trendsData && <div className="p-4 text-center text-red-500">Error fetching data: {error}</div>}
      {error && trendsData && <div className="p-3 text-sm text-orange-700 bg-orange-100 border border-orange-400 rounded-md">Warning: Could not connect to live data. Displaying cached or mock information. ({error})</div>}


      <div className="p-4 bg-white rounded-lg shadow-lg border border-slate-200" style={{ minHeight: '400px', maxHeight: '600px' }}>
        {loading && <div className="text-center py-10">Loading chart data...</div>}
        {!loading && trendsData && (
          <div style={{ height: '100%', minHeight: '380px' }}> {/* Ensure chart wrapper has height */}
            <Line options={chartOptions} data={trendsData} />
          </div>
        )}
        {!loading && !trendsData && !error && <div className="text-center py-10">No transaction data available for the selected period.</div>}
      </div>

      {/* Placeholder for more detailed tables or other charts */}
      <div className="mt-8 p-6 bg-white shadow-lg rounded-lg border border-slate-200">
        <h3 className="text-xl font-semibold text-slate-800">Detailed Transactions (Coming Soon)</h3>
        <p className="text-slate-600">A table with individual transaction details will be displayed here.</p>
      </div>
    </div>
  );
};

export default TransactionAnalysisPage;
