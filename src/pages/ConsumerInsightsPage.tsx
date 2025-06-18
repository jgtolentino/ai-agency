import React, { useEffect, useState } from 'react';
import { useFilterStore } from '../../stores/filterStore'; // Import global filter store
import { getAgeDistribution, getGenderDistribution } from '../lib/apiClient';
import { Bar, Pie } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  ArcElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js';

// Register Chart.js components
ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  ArcElement,
  Title,
  Tooltip,
  Legend
);

// Predefined list of colors for chart segments (re-usable)
const PREDEFINED_COLORS_RGBA = [
    'rgba(255, 99, 132, 0.7)', 'rgba(54, 162, 235, 0.7)', 'rgba(255, 206, 86, 0.7)',
    'rgba(75, 192, 192, 0.7)', 'rgba(153, 102, 255, 0.7)', 'rgba(255, 159, 64, 0.7)',
    'rgba(199, 199, 199, 0.7)', 'rgba(83, 102, 255, 0.7)'
];
const PREDEFINED_COLORS_SOLID = PREDEFINED_COLORS_RGBA.map(color => color.replace(/[^,]+(?=\))/, '1'));


interface ApiAgeDataPoint { age_group: string; customer_count: number; }
interface ApiGenderDataPoint { gender: string; customer_count: number; }

interface ChartDataState {
  labels: string[];
  datasets: {
    label?: string;
    data: number[];
    backgroundColor: string[];
    borderColor?: string[];
    borderWidth?: number;
  }[];
}

const ConsumerInsightsPage: React.FC = () => {
  const {
    dateRange: globalDateRange,
    selectedRegions,
    selectedBrands,
    selectedCategories,
    selectedStores,
  } = useFilterStore();

  const [ageChartData, setAgeChartData] = useState<ChartDataState | null>(null);
  const [genderChartData, setGenderChartData] = useState<ChartDataState | null>(null);
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
          regions: selectedRegions.length > 0 ? selectedRegions.join(',') : undefined,
          brands: selectedBrands.length > 0 ? selectedBrands.join(',') : undefined,
          categories: selectedCategories.length > 0 ? selectedCategories.join(',') : undefined,
          stores: selectedStores.length > 0 ? selectedStores.join(',') : undefined,
        };
        if (!filters.startDate && !filters.endDate) {
            filters.period = 'all_time'; // Default if API needs it
        }
        Object.keys(filters).forEach(key => filters[key] === undefined && delete filters[key]);

        const [ageData, genderData] = await Promise.all([
          getAgeDistribution(filters),
          getGenderDistribution(filters)
        ]);

        // Process Age Data for Bar Chart
        setAgeChartData({
          labels: ageData.map(item => item.age_group),
          datasets: [{
            label: 'Customer Count by Age Group',
            data: ageData.map(item => item.customer_count),
            backgroundColor: PREDEFINED_COLORS_RGBA.slice(0, ageData.length),
            borderColor: PREDEFINED_COLORS_SOLID.slice(0, ageData.length),
            borderWidth: 1,
          }],
        });

        // Process Gender Data for Pie Chart
        setGenderChartData({
          labels: genderData.map(item => item.gender),
          datasets: [{
            data: genderData.map(item => item.customer_count),
            backgroundColor: PREDEFINED_COLORS_RGBA.slice(0, genderData.length),
            borderColor: PREDEFINED_COLORS_SOLID.slice(0, genderData.length),
            borderWidth: 1,
          }],
        });

      } catch (err: any) {
        console.error("API Error, using mock data for ConsumerInsightsPage:", err);
        setError(err.message || 'Failed to fetch consumer demographic data.');

        // Fallback to mock data
        const mockAgeData: ApiAgeDataPoint[] = [
          { age_group: '18-24', customer_count: Math.random() * 100 + 50 },
          { age_group: '25-34', customer_count: Math.random() * 200 + 100 },
          { age_group: '35-44', customer_count: Math.random() * 150 + 80 },
          { age_group: '45-54', customer_count: Math.random() * 100 + 60 },
          { age_group: '55+', customer_count: Math.random() * 80 + 40 },
        ];
        setAgeChartData({
          labels: mockAgeData.map(item => item.age_group),
          datasets: [{ label: 'Customer Count by Age Group (Mock)', data: mockAgeData.map(item => item.customer_count), backgroundColor: PREDEFINED_COLORS_RGBA, borderColor: PREDEFINED_COLORS_SOLID, borderWidth: 1 }],
        });

        const mockGenderData: ApiGenderDataPoint[] = [
          { gender: 'Female', customer_count: Math.random() * 300 + 200 },
          { gender: 'Male', customer_count: Math.random() * 250 + 150 },
          { gender: 'Other', customer_count: Math.random() * 50 + 10 },
        ];
        setGenderChartData({
          labels: mockGenderData.map(item => item.gender),
          datasets: [{ data: mockGenderData.map(item => item.customer_count), backgroundColor: PREDEFINED_COLORS_RGBA.slice(0,3), borderColor: PREDEFINED_COLORS_SOLID.slice(0,3), borderWidth: 1 }],
        });
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [globalDateRange, selectedRegions, selectedBrands, selectedCategories, selectedStores]);

  const barChartOptions = { responsive: true, plugins: { legend: { display: false }, title: { display: true, text: 'Age Distribution of Customers', font: {size: 16} } } };
  const pieChartOptions = { responsive: true, plugins: { legend: { position: 'right' as const }, title: { display: true, text: 'Gender Distribution of Customers', font: {size: 16} } } };
  // Chart titles could also be made dynamic based on filters if desired

  return (
    <div className="p-4 space-y-6">
      <div className="flex justify-between items-center"> {/* Title remains, local filter UI removed */}
        <h1 className="text-2xl font-semibold text-slate-800">Consumer Insights</h1>
      </div>

      {error && !(ageChartData && genderChartData) && <div className="p-4 text-center text-red-500">Error fetching data: {error}</div>}
      {error && (ageChartData || genderChartData) && <div className="p-3 text-sm text-orange-700 bg-orange-100 border border-orange-400 rounded-md">Warning: Could not connect to live data. Displaying cached or mock information. ({error})</div>}

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="p-4 bg-white rounded-lg shadow-lg border border-slate-200" style={{ minHeight: '350px', maxHeight: '450px' }}>
          {loading && <div className="text-center py-10">Loading age distribution chart...</div>}
          {!loading && ageChartData && <div style={{height: '100%', minHeight: '330px'}}><Bar options={barChartOptions} data={ageChartData} /></div>}
          {!loading && !ageChartData && !error && <div className="text-center py-10">No age data available.</div>}
        </div>
        <div className="p-4 bg-white rounded-lg shadow-lg border border-slate-200" style={{ minHeight: '350px', maxHeight: '450px' }}>
          {loading && <div className="text-center py-10">Loading gender distribution chart...</div>}
          {!loading && genderChartData && <div style={{height: '100%', minHeight: '330px'}}><Pie options={pieChartOptions} data={genderChartData} /></div>}
          {!loading && !genderChartData && !error && <div className="text-center py-10">No gender data available.</div>}
        </div>
      </div>

      <div className="mt-8 space-y-6">
        <div className="p-6 bg-white shadow-lg rounded-lg border border-slate-200">
          <h3 className="text-xl font-semibold text-slate-800 mb-2">Location Mapping</h3>
          <p className="text-slate-600">Geospatial visualization of customer locations will be displayed here.</p>
        </div>
        <div className="p-6 bg-white shadow-lg rounded-lg border border-slate-200">
          <h3 className="text-xl font-semibold text-slate-800 mb-2">Purchase Behavior Patterns</h3>
          <p className="text-slate-600">Analysis of customer purchase frequencies, times, and preferred channels.</p>
        </div>
        <div className="p-6 bg-white shadow-lg rounded-lg border border-slate-200">
          <h3 className="text-xl font-semibold text-slate-800 mb-2">Preference Signals</h3>
          <p className="text-slate-600">Insights derived from product affinities, brand preferences, and promotion responses.</p>
        </div>
      </div>
    </div>
  );
};

export default ConsumerInsightsPage;
