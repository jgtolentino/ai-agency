import React from 'react';
import { BrowserRouter as Router, Routes, Route, Outlet } from 'react-router-dom';
import Sidebar from './partials/Sidebar';
import Header from './partials/Header';
import GlobalFilterBar from './components/filters/GlobalFilterBar'; // Import GlobalFilterBar
import LoginPage from './pages/LoginPage'; // Import the LoginPage
import OverviewPage from './pages/OverviewPage'; // Import the actual OverviewPage
import TransactionAnalysisPage from './pages/TransactionAnalysisPage'; // Import the actual TransactionAnalysisPage
import ProductIntelligencePage from './pages/ProductIntelligencePage'; // Import the actual ProductIntelligencePage
import ConsumerInsightsPage from './pages/ConsumerInsightsPage'; // Import the actual ConsumerInsightsPage
import RegionalAnalyticsPage from './pages/RegionalAnalyticsPage'; // Import the actual RegionalAnalyticsPage
import AIRecommendationsPage from './pages/AIRecommendationsPage'; // Import the actual AIRecommendationsPage

// Placeholder Page Components for other pages (all main pages are now imported)
const NotFoundPage: React.FC = () => <div className="p-4"><h1>404 - Page Not Found</h1></div>;

const AppLayout: React.FC = () => {
  return (
    <div className="flex h-screen bg-slate-100">
      {/* Sidebar */}
      <Sidebar />

      {/* Content area */}
      <div className="relative flex flex-col flex-1 overflow-y-auto overflow-x-hidden">
        {/*  Site header */}
        <Header />

        {/* Global Filter Bar */}
        <GlobalFilterBar />

        <main className="flex-1">
          <div className="px-4 sm:px-6 lg:px-8 py-8 w-full max-w-9xl mx-auto">
            <Outlet /> {/* This is where nested routes will render their components */}
          </div>
        </main>
      </div>
    </div>
  );
};

const App: React.FC = () => {
  return (
    // Router is handled in main.tsx as per instructions
    // If not, it should be <Router><Routes>...</Routes></Router> here
    <Routes>
      {/* Routes with Sidebar and Header */}
      <Route path="/" element={<AppLayout />}>
        <Route index element={<OverviewPage />} />
        <Route path="transactions" element={<TransactionAnalysisPage />} />
        <Route path="products" element={<ProductIntelligencePage />} />
        <Route path="consumers" element={<ConsumerInsightsPage />} />
        <Route path="regional" element={<RegionalAnalyticsPage />} />
        <Route path="ai-recommendations" element={<AIRecommendationsPage />} />
        {/* Add other authenticated routes here inside AppLayout */}
      </Route>

      {/* Standalone Login Page Route */}
      <Route path="/login" element={<LoginPage />} />

      {/* Catch-all for 404 - Placed outside AppLayout if it shouldn't have navbars */}
      {/* Or, if 404 should be within AppLayout, move it inside that Route element. */}
      {/* For now, making it a general catch-all, might need adjustment based on UX. */}
      <Route path="*" element={<NotFoundPage />} />
    </Routes>
  );
};

export default App;
