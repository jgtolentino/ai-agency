import React from 'react';
import { NavLink } from 'react-router-dom';

interface SidebarLinkProps {
  to: string;
  children: React.ReactNode;
  icon?: React.ReactNode; // Placeholder for icon
}

const SidebarLink: React.FC<SidebarLinkProps> = ({ to, children, icon }) => {
  return (
    <NavLink
      to={to}
      className={({ isActive }) =>
        `block text-slate-200 hover:text-white truncate transition duration-150 ${
          isActive ? 'text-indigo-400 bg-slate-900' : ''
        }`
      }
    >
      <div className="flex items-center p-2">
        {icon && <span className="mr-3">{icon}</span>}
        <span className="text-sm font-medium">{children}</span>
      </div>
    </NavLink>
  );
};

// Placeholder Icon component
const PlaceholderIcon: React.FC<{ className?: string }> = ({ className = "w-5 h-5" }) => (
  <svg className={className} viewBox="0 0 20 20" fill="currentColor">
    <path d="M10 3a1 1 0 011 1v4h4a1 1 0 110 2h-4v4a1 1 0 11-2 0v-4H5a1 1 0 110-2h4V4a1 1 0 011-1z" />
  </svg>
);


const Sidebar: React.FC = () => {
  const navigationItems = [
    { name: 'Overview', path: '/', icon: <PlaceholderIcon /> },
    { name: 'Transaction Analysis', path: '/transactions', icon: <PlaceholderIcon /> },
    { name: 'Product Intelligence', path: '/products', icon: <PlaceholderIcon /> },
    { name: 'Consumer Insights', path: '/consumers', icon: <PlaceholderIcon /> },
    { name: 'Regional Analytics', path: '/regional', icon: <PlaceholderIcon /> },
    { name: 'AI Recommendations', path: '/ai-recommendations', icon: <PlaceholderIcon /> },
  ];

  return (
    <div className="flex flex-col w-64 h-screen bg-slate-800 text-white">
      {/* Sidebar header (optional, e.g., logo) */}
      <div className="p-4 border-b border-slate-700">
        <h2 className="text-xl font-semibold text-white">Scout Menu</h2>
      </div>

      {/* Navigation Links */}
      <nav className="mt-5 flex-grow">
        <ul>
          {navigationItems.map((item) => (
            <li key={item.name} className="px-3 py-1 rounded-sm mb-0.5 last:mb-0">
              <SidebarLink to={item.path} icon={item.icon}>
                {item.name}
              </SidebarLink>
            </li>
          ))}
        </ul>
      </nav>

      {/* Sidebar footer (optional) */}
      <div className="p-4 border-t border-slate-700">
        {/* Placeholder for user profile or settings link */}
        <div className="text-sm text-slate-400">Version 1.0.0</div>
      </div>
    </div>
  );
};

export default Sidebar;
