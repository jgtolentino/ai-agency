import React from 'react';

const Header: React.FC = () => {
  return (
    <header className="sticky top-0 bg-white border-b border-slate-200 z-30">
      <div className="px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16 -mb-px">
          {/* Header: Left side */}
          <div className="flex">
            <h1 className="text-2xl font-bold text-slate-800">Scout Analytics</h1>
          </div>

          {/* Header: Right side */}
          <div className="flex items-center space-x-3">
            {/* Placeholder for Search Bar */}
            <div className="relative">
              <input
                type="search"
                placeholder="Search..."
                className="form-input pl-9 text-sm focus:border-slate-300 w-full"
              />
              <svg
                className="w-4 h-4 fill-current text-slate-400 absolute top-1/2 left-3 transform -translate-y-1/2"
                viewBox="0 0 16 16"
              >
                <path d="M15.707 14.293l-3.142-3.142A5.934 5.934 0 0014 8c0-3.309-2.691-6-6-6S2 4.691 2 8s2.691 6 6 6c1.425 0 2.73-.498 3.777-1.335l3.142 3.142a.999.999 0 101.414-1.414zM4 8c0-2.206 1.794-4 4-4s4 1.794 4 4-1.794 4-4 4-4-1.794-4-4z" />
              </svg>
            </div>
            {/* Placeholder for User Controls */}
            <div className="flex items-center">
              <button className="p-2 rounded-full hover:bg-slate-100">
                <svg className="w-6 h-6 text-slate-500" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9"></path></svg>
              </button>
              <button className="p-2 rounded-full hover:bg-slate-100">
                <svg className="w-6 h-6 text-slate-500" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 6V4m0 16v-2m8-6h-2M4 12H2m15.364 6.364l-1.414-1.414M6.05 6.05l-1.414-1.414m12.728 0l-1.414 1.414M6.05 17.95l-1.414 1.414m12.728 0l-1.414-1.414"></path></svg>
              </button>
              <div className="ml-2">
                <img className="w-8 h-8 rounded-full" src="https://via.placeholder.com/32" alt="User" />
              </div>
            </div>
          </div>
        </div>
      </div>
    </header>
  );
};

export default Header;
