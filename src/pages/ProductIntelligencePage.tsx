import React, { useEffect, useState } from 'react';
import { useFilterStore } from '../../stores/filterStore'; // Import global filter store
import { getProductCategoriesSummary } from '../lib/apiClient';
import { Doughnut } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  ArcElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js';
// import { randomColor } from 'randomcolor'; // Replaced with predefined colors

// Register Chart.js components
ChartJS.register(ArcElement, Title, Tooltip, Legend);

// Predefined list of colors for chart segments
const PREDEFINED_COLORS_RGBA = [
  'rgba(255, 99, 132, 0.7)',
  'rgba(54, 162, 235, 0.7)',
  'rgba(255, 206, 86, 0.7)',
  'rgba(75, 192, 192, 0.7)',
  'rgba(153, 102, 255, 0.7)',
  'rgba(255, 159, 64, 0.7)',
  'rgba(199, 199, 199, 0.7)',
  'rgba(83, 102, 255, 0.7)',
  'rgba(100, 255, 100, 0.7)',
  'rgba(255, 100, 100, 0.7)',
];

const PREDEFINED_COLORS_SOLID = PREDEFINED_COLORS_RGBA.map(color => color.replace(/[^,]+(?=\))/, '1'));

// Define expected data structure from API
interface ApiCategoryDataPoint {
  name: string;
  value: number; // e.g., total sales or quantity
  change?: number;
}

// Define structure for chart data state
interface ChartDataState {
  labels: string[];
  datasets: {
    label: string;
    data: number[];
    backgroundColor: string[];
    borderColor?: string[];
    borderWidth?: number;
  }[];
}

const ProductIntelligencePage: React.FC = () => {
  const {
    dateRange: globalDateRange,
    selectedRegions,
    selectedBrands,
    // selectedCategories, // Not used as a filter *for* category breakdown, but could be for sub-categories
    selectedStores,
  } = useFilterStore();

  const [categoryChartData, setCategoryChartData] = useState<ChartDataState | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  // Local filterPeriod state is removed

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
          stores: selectedStores.length > 0 ? selectedStores.join(',') : undefined,
          // period: filterPeriod, // This was local, replace or remove if dateRange covers it
        };
        // If API still needs a 'period' when no specific date range, derive or set default:
        if (!filters.startDate && !filters.endDate) {
            filters.period = '30d'; // Example default if API requires it
        }
        Object.keys(filters).forEach(key => filters[key] === undefined && delete filters[key]);

        const apiData: ApiCategoryDataPoint[] = await getProductCategoriesSummary(filters);

        // Transform API data for Chart.js Doughnut chart
        const labels = apiData.map(item => item.name);
        const dataValues = apiData.map(item => item.value);

        // Use predefined colors, cycling if more categories than colors
        const backgroundColors = labels.map((_, index) => PREDEFINED_COLORS_RGBA[index % PREDEFINED_COLORS_RGBA.length]);
        const borderColors = labels.map((_, index) => PREDEFINED_COLORS_SOLID[index % PREDEFINED_COLORS_SOLID.length]);

        setCategoryChartData({
          labels,
          datasets: [
            {
              label: 'Category Breakdown',
              data: dataValues,
              backgroundColor: backgroundColors,
              borderColor: borderColors, // Use solid colors for borders
              borderWidth: 1,
            },
          ],
        });

      } catch (err: any) {
        console.error("API Error, using mock data for ProductIntelligencePage:", err);
        setError(err.message || 'Failed to fetch product category data.');

        // Fallback to mock data
        const mockApiData: ApiCategoryDataPoint[] = [
          { name: 'Electronics', value: Math.random() * 10000 + 50000 },
          { name: 'Apparel', value: Math.random() * 8000 + 40000 },
          { name: 'Groceries', value: Math.random() * 12000 + 60000 },
          { name: 'Home Goods', value: Math.random() * 7000 + 30000 },
          { name: 'Books', value: Math.random() * 5000 + 20000 },
        ];
        const labels = mockApiData.map(item => item.name);
        const dataValues = mockApiData.map(item => item.value);
        // Use predefined colors for mock data as well
        const mockBackgroundColors = labels.map((_, index) => PREDEFINED_COLORS_RGBA[index % PREDEFINED_COLORS_RGBA.length]);
        const mockBorderColors = labels.map((_, index) => PREDEFINED_COLORS_SOLID[index % PREDEFINED_COLORS_SOLID.length]);


        setCategoryChartData({
          labels,
          datasets: [
            {
              label: 'Category Breakdown (Mock)',
              data: dataValues,
              backgroundColor: mockBackgroundColors,
              borderColor: mockBorderColors,
              borderWidth: 1,
            },
          ],
        });
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [globalDateRange, selectedRegions, selectedBrands, selectedStores]); // Refetch when global filters change

  const chartTitle = () => {
    let title = 'Product Category Breakdown';
    if (globalDateRange.start && globalDateRange.end) {
      const start = new Date(globalDateRange.start).toLocaleDateString();
      const end = new Date(globalDateRange.end).toLocaleDateString();
      title += ` (${start} - ${end})`;
    }
    // Add other active filters to title if desired
    return title;
  }

  const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'right' as const,
      },
      title: {
        display: true,
        text: chartTitle(),
        font: { size: 18 },
      },
      tooltip: {
        callbacks: {
          label: function(context: any) {
            let label = context.label || '';
            if (label) {
              label += ': ';
            }
            if (context.parsed !== null) {
              // Assuming value is monetary, format accordingly
              label += new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' }).format(context.parsed);
            }
            return label;
          }
        }
      }
    },
  };

  return (
    <div className="p-4 space-y-6">
      <div className="flex justify-between items-center"> {/* Title remains, local filter UI removed */}
        <h1 className="text-2xl font-semibold text-slate-800">Product Intelligence</h1>
      </div>

      {error && !categoryChartData && <div className="p-4 text-center text-red-500">Error fetching data: {error}</div>}
      {error && categoryChartData && <div className="p-3 text-sm text-orange-700 bg-orange-100 border border-orange-400 rounded-md">Warning: Could not connect to live data. Displaying cached or mock information. ({error})</div>}


      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="p-4 bg-white rounded-lg shadow-lg border border-slate-200" style={{ minHeight: '400px', maxHeight: '500px' }}>
          {loading && <div className="text-center py-10">Loading category chart...</div>}
          {!loading && categoryChartData && (
            <div style={{ height: '100%', minHeight: '380px' }}>
              <Doughnut options={chartOptions} data={categoryChartData} />
            </div>
          )}
          {!loading && !categoryChartData && !error && <div className="text-center py-10">No category data available.</div>}
        </div>

        {/* Placeholder for another chart or table */}
        <div className="p-4 bg-white rounded-lg shadow-lg border border-slate-200">
          <h3 className="text-lg font-semibold text-slate-700 mb-3">Performance Trends</h3>
          <p className="text-slate-500 text-sm">Line chart for category performance over time will be here.</p>
          {/* Placeholder for a line chart related to categories */}
        </div>
      </div>

      {/* Placeholders for Advanced Product Analysis */}
      <div className="mt-8 space-y-6">
        <div className="p-6 bg-white shadow-lg rounded-lg border border-slate-200">
          <h3 className="text-xl font-semibold text-slate-800 mb-2">Top SKUs Table</h3>
          <p className="text-slate-600">A sortable, filterable table of top-performing SKUs will be displayed here.</p>
        </div>
        <div className="p-6 bg-white shadow-lg rounded-lg border border-slate-200">
          <h3 className="text-xl font-semibold text-slate-800 mb-2">Basket Analysis Insights</h3>
          <p className="text-slate-600">Insights from market basket analysis (e.g., frequently co-purchased items) will be presented here.</p>
        </div>
        <div className="p-6 bg-white shadow-lg rounded-lg border border-slate-200">
          <h3 className="text-xl font-semibold text-slate-800 mb-2">Substitution Patterns</h3>
          <p className="text-slate-600">Analysis of product substitution behaviors will be shown here.</p>
        </div>
      </div>
    </div>
  );
};

export default ProductIntelligencePage;
