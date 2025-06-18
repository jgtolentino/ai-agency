import React from 'react';

interface KPICardProps {
  title: string;
  value: string | number;
  growth?: string | number; // e.g., "+5.2%" or -10
  growthType?: 'positive' | 'negative' | 'neutral'; // To color the growth indicator
  icon?: React.ReactNode; // Placeholder for an icon
  description?: string;
}

const KPICard: React.FC<KPICardProps> = ({
  title,
  value,
  growth,
  growthType = 'neutral',
  icon,
  description,
}) => {
  let growthColorClass = 'text-slate-500'; // Neutral by default
  if (growthType === 'positive') {
    growthColorClass = 'text-emerald-500';
  } else if (growthType === 'negative') {
    growthColorClass = 'text-red-500';
  }

  return (
    <div className="flex flex-col col-span-full sm:col-span-6 xl:col-span-3 bg-white shadow-lg rounded-lg border border-slate-200">
      <div className="px-5 pt-5">
        {icon && <div className="flex justify-start mb-2">{icon}</div>}
        <h2 className="text-lg font-semibold text-slate-800 mb-1">{title}</h2>
        <div className="text-xs text-slate-500 mb-1">{description || ''}</div>
        <div className="flex items-start">
          <div className="text-3xl font-bold text-slate-800 mr-2">{value}</div>
          {growth !== undefined && (
            <div className={`text-sm font-semibold ${growthColorClass}`}>
              {growthType === 'positive' && growth > 0 ? `+${growth}` : growth}
              {typeof growth === 'number' || (typeof growth === 'string' && growth.slice(-1) !== '%') ? '%' : ''}
            </div>
          )}
        </div>
      </div>
      {/* Additional content or footer for the card can be added here if needed */}
      <div className="grow p-2"></div> {/* Spacer to push content up or for a chart later */}
    </div>
  );
};

// Example of a simple SVG icon to be passed if needed
export const PlaceholderKPISVGIcon: React.FC<{ className?: string }> = ({ className = "w-6 h-6 text-slate-500" }) => (
  <svg className={className} fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
  </svg>
);


export default KPICard;
