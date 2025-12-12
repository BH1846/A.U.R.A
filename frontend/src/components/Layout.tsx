import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { Code2 } from 'lucide-react';

interface LayoutProps {
  children: React.ReactNode;
}

export const Layout: React.FC<LayoutProps> = ({ children }) => {
  const location = useLocation();

  const isActive = (path: string) => {
    return location.pathname === path;
  };

  return (
    <div className="min-h-screen bg-neutral-light flex flex-col">
      {/* Navigation Header */}
      <header className="bg-tertiary text-white shadow-lg sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            {/* Logo */}
            <Link to="/" className="flex items-center gap-2 hover:opacity-80 transition-opacity">
              <Code2 className="w-8 h-8 text-secondary" />
              <span className="text-2xl font-bold">AURA</span>
            </Link>

            {/* Navigation Links */}
            <nav className="flex items-center gap-6">
              <Link
                to="/submit"
                className={`text-lg font-medium transition-colors hover:text-secondary ${
                  isActive('/submit') ? 'text-secondary' : 'text-white'
                }`}
              >
                Submit
              </Link>
              <Link
                to="/dashboard"
                className={`text-lg font-medium transition-colors hover:text-secondary ${
                  isActive('/dashboard') ? 'text-secondary' : 'text-white'
                }`}
              >
                Dashboard
              </Link>
            </nav>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="flex-1 pb-20">{children}</main>

      {/* Footer */}
      <footer className="bg-neutral-dark text-white py-8 px-6">
        <div className="max-w-7xl mx-auto text-center">
          <p className="text-lg font-medium mb-2">
            © 2024 AURA - Automated Understanding & Role Assessment
          </p>
          <p className="text-white/70">AI-Powered Technical Skill Verification</p>
        </div>
      </footer>
    </div>
  );
};
