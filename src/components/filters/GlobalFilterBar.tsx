import React, { useState, useEffect } from 'react';
import { useFilterStore } from '../../stores/filterStore';
// react-day-picker is not installed yet, so using basic date inputs.
// import { DayPicker } from 'react-day-picker';
// import 'react-day-picker/dist/style.css';


// Placeholder data - in a real app, this might come from an API or config
const ALL_REGIONS = ['NCR', 'Region 3', 'Region 4A', 'Visayas', 'Mindanao', 'North Luzon', 'South Luzon'];
const ALL_BRANDS = ['Alaska', 'Oishi', 'Del Monte', 'Peerless', 'JTI', 'Nestle', 'Mondelez', 'Coca-Cola'];
const ALL_CATEGORIES = ['Beverages', 'Snacks', 'Personal Care', 'Household', 'Dairy', 'Canned Goods', 'Frozen Foods'];
const ALL_STORES = ['SM Supermarket', 'Robinsons Supermarket', 'Puregold', 'Waltermart', 'Alfamart', '7-Eleven']; // Example store names

const GlobalFilterBar: React.FC = () => {
  const {
    dateRange,
    selectedRegions,
    selectedBrands,
    selectedCategories,
    selectedStores,
    setDateRange,
    toggleRegion,
    toggleBrand,
    toggleCategory,
    toggleStore,
    clearFilters,
    _hasHydrated // Use this to prevent rendering with default state before hydration
  } = useFilterStore();

  // Local state for date inputs to allow user typing before committing to store
  const [localStartDate, setLocalStartDate] = useState(dateRange.start || '');
  const [localEndDate, setLocalEndDate] = useState(dateRange.end || '');

  useEffect(() => {
    // Update local state if global state changes (e.g. on hydration or external update)
    setLocalStartDate(dateRange.start || '');
    setLocalEndDate(dateRange.end || '');
  }, [dateRange.start, dateRange.end]);

  // If not hydrated, don't render or render a placeholder to avoid flicker/mismatch
  if (!_hasHydrated) {
    return <div className="p-4 bg-slate-100 text-center text-sm text-slate-500">Loading filters...</div>;
  }

  const handleDateChange = () => {
    // Basic validation: ensure end date is not before start date if both are set
    if (localStartDate && localEndDate && new Date(localEndDate) < new Date(localStartDate)) {
      alert("End date cannot be before start date.");
      return;
    }
    setDateRange(localStartDate || null, localEndDate || null);
  };

  const handleClearFilters = () => {
    clearFilters();
    // Also clear local date input state
    setLocalStartDate('');
    setLocalEndDate('');
  };

  return (
    <div className="p-3 bg-white shadow-md border-b border-slate-200 sticky top-16 z-20"> {/* Assuming header is h-16 */}
      <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-3 items-end">
        {/* Date Range Filter */}
        <div className="space-y-1 lg:col-span-2"> {/* Date range can take more space */}
          <label htmlFor="startDate" className="block text-xs font-medium text-slate-600">Date Range:</label>
          <div className="flex space-x-2">
            <input
              type="date"
              id="startDate"
              value={localStartDate}
              onChange={(e) => setLocalStartDate(e.target.value)}
              onBlur={handleDateChange} // Update store on blur
              className="form-input block w-full text-xs rounded-md border-slate-300 shadow-sm"
            />
            <input
              type="date"
              id="endDate"
              value={localEndDate}
              onChange={(e) => setLocalEndDate(e.target.value)}
              onBlur={handleDateChange} // Update store on blur
              className="form-input block w-full text-xs rounded-md border-slate-300 shadow-sm"
            />
          </div>
        </div>

        {/* Region Filter */}
        <div className="space-y-1">
          <label htmlFor="regions" className="block text-xs font-medium text-slate-600">Regions:</label>
          <select
            id="regions"
            multiple
            value={selectedRegions}
            onChange={(e) => Array.from(e.target.selectedOptions).forEach(option => toggleRegion(option.value))}
            className="form-multiselect block w-full text-xs rounded-md border-slate-300 shadow-sm h-20" // Basic height
          >
            {ALL_REGIONS.map(region => (
              <option key={region} value={region}>{region}</option>
            ))}
          </select>
          <p className="text-xxs text-slate-500">Ctrl+click to select multiple.</p>
        </div>

        {/* Brand Filter */}
        <div className="space-y-1">
          <label htmlFor="brands" className="block text-xs font-medium text-slate-600">Brands:</label>
          <select
            id="brands"
            multiple
            value={selectedBrands}
            onChange={(e) => Array.from(e.target.selectedOptions).forEach(option => toggleBrand(option.value))}
            className="form-multiselect block w-full text-xs rounded-md border-slate-300 shadow-sm h-20"
          >
            {ALL_BRANDS.map(brand => (
              <option key={brand} value={brand}>{brand}</option>
            ))}
          </select>
          <p className="text-xxs text-slate-500">Ctrl+click to select multiple.</p>
        </div>

        {/* Category Filter */}
        <div className="space-y-1">
          <label htmlFor="categories" className="block text-xs font-medium text-slate-600">Categories:</label>
          <select
            id="categories"
            multiple
            value={selectedCategories}
            onChange={(e) => Array.from(e.target.selectedOptions).forEach(option => toggleCategory(option.value))}
            className="form-multiselect block w-full text-xs rounded-md border-slate-300 shadow-sm h-20"
          >
            {ALL_CATEGORIES.map(category => (
              <option key={category} value={category}>{category}</option>
            ))}
          </select>
          <p className="text-xxs text-slate-500">Ctrl+click to select multiple.</p>
        </div>

        {/* Store Filter */}
        <div className="space-y-1">
          <label htmlFor="stores" className="block text-xs font-medium text-slate-600">Stores:</label>
          <select
            id="stores"
            multiple
            value={selectedStores}
            onChange={(e) => Array.from(e.target.selectedOptions).forEach(option => toggleStore(option.value))}
            className="form-multiselect block w-full text-xs rounded-md border-slate-300 shadow-sm h-20"
          >
            {ALL_STORES.map(store => (
              <option key={store} value={store}>{store}</option>
            ))}
          </select>
          <p className="text-xxs text-slate-500">Ctrl+click to select multiple.</p>
        </div>

        {/* Action Buttons */}
        <div className="flex items-end">
          <button
            onClick={handleClearFilters}
            className="px-3 py-1.5 text-xs font-medium text-white bg-slate-600 hover:bg-slate-700 rounded-md shadow-sm w-full"
          >
            Clear All Filters
          </button>
          {/* Add Apply button if prefer explicit application over onBlur/onChange */}
        </div>
      </div>
    </div>
  );
};

export default GlobalFilterBar;
