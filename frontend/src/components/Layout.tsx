import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { Code2, LogOut, User } from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';

interface LayoutProps {
  children: React.ReactNode;
}

export const Layout: React.FC<LayoutProps> = ({ children }) => {
  const location = useLocation();
  const { user, isAuthenticated, logout, isStudent, isRecruiter } = useAuth();

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
              {isAuthenticated ? (
                <>
                  {/* Student Navigation */}
                  {isStudent() && (
                    <Link
                      to="/student/dashboard"
                      className={`text-lg font-medium transition-colors hover:text-secondary ${
                        isActive('/student/dashboard') ? 'text-secondary' : 'text-white'
                      }`}
                    >
                      My Applications
                    </Link>
                  )}

                  {/* Recruiter Navigation */}
                  {isRecruiter() && (
                    <>
                      <Link
                        to="/company/dashboard"
                        className={`text-lg font-medium transition-colors hover:text-secondary ${
                          isActive('/company/dashboard') ? 'text-secondary' : 'text-white'
                        }`}
                      >
                        Dashboard
                      </Link>
                      <Link
                        to="/company/applications"
                        className={`text-lg font-medium transition-colors hover:text-secondary ${
                          isActive('/company/applications') ? 'text-secondary' : 'text-white'
                        }`}
                      >
                        Applications
                      </Link>
                      <Link
                        to="/company/rankings"
                        className={`text-lg font-medium transition-colors hover:text-secondary ${
                          isActive('/company/rankings') ? 'text-secondary' : 'text-white'
                        }`}
                      >
                        Rankings
                      </Link>
                    </>
                  )}

                  {/* User Menu */}
                  <div className="flex items-center gap-4 ml-4 pl-4 border-l border-white/20">
                    <div className="flex items-center gap-2">
                      <User className="w-5 h-5" />
                      <span className="text-sm">{user?.name}</span>
                    </div>
                    <button
                      onClick={logout}
                      className="flex items-center gap-1 text-sm text-white/70 hover:text-white transition-colors"
                    >
                      <LogOut className="w-4 h-4" />
                      Logout
                    </button>
                  </div>
                </>
              ) : (
                <>
                  {/* Public/Standalone Navigation */}
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
                </>
              )}
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
          <p className="text-white/70">
            {isAuthenticated 
              ? `Integrated with I-Intern Platform`
              : `AI-Powered Technical Skill Verification`
            }
          </p>
        </div>
      </footer>
    </div>
  );
};
