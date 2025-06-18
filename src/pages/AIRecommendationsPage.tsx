import React, { useEffect, useState } from 'react';
import { useFilterStore } from '../../stores/filterStore'; // Import global filter store
import { getAIInsights } from '../lib/apiClient';
// Attempt to import InsightCard from its original location, assuming it's usable.
// Adjust path if InsightCard.tsx was moved or if a new/different one is needed.
// Path from src/pages/* to components/* is typically ../../components/*
import InsightCard from '../../components/InsightCard';

interface AIInsight {
  id: string;
  title: string;
  summary: string;
  insight: string; // Assuming InsightCard expects 'insight' prop for summary
  description: string; // Assuming InsightCard expects 'description' for suggested_action
  severity: 'low' | 'medium' | 'high' | 'critical';
  date: string; // ISO date string
  category?: string;
  actionable: boolean; // Assuming InsightCard might use this
  // Add other fields as expected by the actual InsightCard or needed by the page
}

// Helper to map severity for InsightCard if needed (example)
const mapSeverityToInsightCardVariant = (severity: AIInsight['severity']) => {
  switch (severity) {
    case 'critical': return 'error';
    case 'high': return 'warning';
    case 'medium': return 'info';
    case 'low': return 'success'; // Or a more neutral variant
    default: return 'default';
  }
};

const AIRecommendationsPage: React.FC = () => {
  const {
    dateRange: globalDateRange,
    selectedRegions,
    selectedBrands,
    selectedCategories, // This can be used if AI insights are filterable by product categories
    selectedStores,
  } = useFilterStore();

  const [insightsData, setInsightsData] = useState<AIInsight[] | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  // Local filterCategory state can be kept if it's for a specific AI insight category filter
  // that is different from the global product category filter.
  // For now, let's assume the select dropdown for "Category" on this page
  // refers to AI Insight categories, not product categories from global filter.
  // If global product categories should filter AI Insights, then this local state should be removed/reconciled.
  const [localAICategoryFilter, setLocalAICategoryFilter] = useState<string>('all');


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
          // Pass global product categories if the AI insights are related to them
          categories: selectedCategories.length > 0 ? selectedCategories.join(',') : undefined,
          stores: selectedStores.length > 0 ? selectedStores.join(',') : undefined,
        };
        if (localAICategoryFilter !== 'all') {
          filters.aiCategory = localAICategoryFilter; // API might expect 'category' or 'aiCategory'
        }
        Object.keys(filters).forEach(key => filters[key] === undefined && delete filters[key]);

        const data = await getAIInsights(filters);
        const formattedData: AIInsight[] = data.map(item => ({
          ...item,
          insight: item.summary, // Map summary to InsightCard's 'insight' prop
          description: item.suggested_action, // Map suggested_action to 'description'
          actionable: !!item.suggested_action, // Example logic for 'actionable'
        }));
        setInsightsData(formattedData);
      } catch (err: any) {
        console.error("API Error, using mock data for AIRecommendationsPage:", err);
        setError(err.message || 'Failed to fetch AI insights.');

        // Fallback to mock data
        const mockData: AIInsight[] = [
          { id: '1', title: 'High Inventory for Product X', summary: 'Product X has unusually high inventory levels compared to sales velocity.', suggested_action: 'Consider running a promotion for Product X or reducing reorder quantity.', severity: 'high', date: new Date().toISOString(), category: 'Inventory', actionable: true, insight: 'Product X has unusually high inventory levels.', description: 'Consider running a promotion.' },
          { id: '2', title: 'Sales Dip in Region Y', summary: 'Region Y experienced a 15% sales dip last week for key products.', suggested_action: 'Investigate local market conditions or competitor activity in Region Y.', severity: 'medium', date: new Date().toISOString(), category: 'Sales Trend', actionable: true, insight: 'Region Y experienced a 15% sales dip.', description: 'Investigate local market.' },
          { id: '3', title: 'Positive Customer Sentiment for Service Z', summary: 'Recent customer feedback shows high satisfaction with Service Z.', suggested_action: 'Highlight Service Z in marketing campaigns and gather testimonials.', severity: 'low', date: new Date().toISOString(), category: 'Customer Behavior', actionable: true, insight: 'High satisfaction with Service Z.', description: 'Highlight in marketing.' },
          { id: '4', title: 'Critical Stockout Risk for Product A', summary: 'Product A is projected to go out of stock in 3 days based on current demand.', suggested_action: 'Expedite next shipment of Product A or find alternative sourcing immediately.', severity: 'critical', date: new Date().toISOString(), category: 'Inventory', actionable: true, insight: 'Product A stockout risk.', description: 'Expedite shipment.' },
        ];
        setInsightsData(mockData);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [globalDateRange, selectedRegions, selectedBrands, selectedCategories, selectedStores, localAICategoryFilter]);

  return (
    <div className="p-4 space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-semibold text-slate-800">AI Recommendations & Insights</h1>
        {/* This local filter for AI Insight Category can remain if it's distinct from global product categories */}
        <div className="flex items-center space-x-2">
          <label htmlFor="filterCategoryAI" className="text-sm font-medium text-slate-700">Insight Category:</label>
          <select id="filterCategoryAI" value={localAICategoryFilter} onChange={(e) => setLocalAICategoryFilter(e.target.value)}
            className="block w-full max-w-xs px-3 py-2 text-sm bg-white border rounded-md shadow-sm border-slate-300 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
          >
            <option value="all">All AI Insights</option>
            <option value="Inventory">Inventory</option>
            <option value="Sales Trend">Sales Trend</option>
            <option value="Customer Behavior">Customer Behavior</option>
            <option value="Pricing">Pricing</option>
            {/* Add more AI-specific categories if needed */}
          </select>
        </div>
      </div>

      {error && !insightsData && <div className="p-4 text-center text-red-500">Error fetching insights: {error}</div>}
      {error && insightsData && <div className="p-3 text-sm text-orange-700 bg-orange-100 border border-orange-400 rounded-md">Warning: Could not connect to live AI insights. Displaying cached or mock information. ({error})</div>}

      {loading && <div className="p-4 text-center">Loading AI insights...</div>}

      {!loading && insightsData && insightsData.length > 0 && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {insightsData.map((insight) => (
            <InsightCard
              key={insight.id}
              variant={mapSeverityToInsightCardVariant(insight.severity)} // Map severity to variant
              title={insight.title}
              insight={insight.insight} // Mapped from summary
              description={insight.description} // Mapped from suggested_action
              actionable={insight.actionable} // If your card supports this
              // Pass other props as required by InsightCard
              // e.g. learnMoreLink, onActionClick, etc.
              // For now, keeping it simple.
            />
          ))}
        </div>
      )}
      {!loading && insightsData && insightsData.length === 0 && (
        <div className="p-6 text-center bg-white rounded-lg shadow border border-slate-200">
          <h3 className="text-xl font-semibold text-slate-700">No Insights Available</h3>
          <p className="text-slate-500">There are currently no AI insights for the selected category or period.</p>
        </div>
      )}
    </div>
  );
};

export default AIRecommendationsPage;
