import { Link, useLocation } from 'react-router-dom';
import { Home, Users, FileText, LogOut, Shield, Key, Target, Building2, FileStack, ShieldCheck, BarChart3 } from 'lucide-react';
import { useAuth } from '@/contexts/AuthContext';
import { Button } from '@/components/ui/button';

export function Layout({ children }: { children: React.ReactNode }) {
  const location = useLocation();
  const { user, isAdmin, logout } = useAuth();

  const navItems = [
    { path: '/dashboard', label: 'Dashboard', icon: Home },
    { path: '/pipeline', label: 'Pipeline', icon: BarChart3 },
    { path: '/opportunities', label: 'Opportunities', icon: Target },
    { path: '/accounts', label: 'Accounts', icon: Building2 },
    { path: '/contacts', label: 'Contacts', icon: Users },
    { path: '/contracts', label: 'Contracts', icon: FileText },
    { path: '/vehicles', label: 'Vehicles', icon: FileStack },
    { path: '/compliance', label: 'Compliance', icon: ShieldCheck },
    { path: '/api-settings', label: 'API', icon: Key },
  ];

  // Add admin-only nav items
  if (isAdmin) {
    navItems.push({ path: '/users', label: 'Users', icon: Shield });
  }

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="border-b border-border bg-card">
        <div className="container mx-auto flex h-16 items-center justify-between px-4">
          <div className="flex items-center gap-4">
            <a href="https://pretorin.com" target="_blank" rel="noopener noreferrer" className="flex items-center gap-2">
              <img
                src="/logo-gray-orange.png"
                alt="Pretorin"
                className="h-8"
              />
            </a>
            <div className="border-l border-border h-8"></div>
            <h1 className="text-lg font-semibold">Simple CRM</h1>
          </div>
          <div className="flex items-center gap-4">
            {user && (
              <>
                <span className="text-sm text-muted-foreground">{user.name}</span>
                <Button variant="outline" size="sm" onClick={logout}>
                  <LogOut className="mr-2 h-4 w-4" />
                  Logout
                </Button>
              </>
            )}
          </div>
        </div>
      </header>

      {/* Navigation */}
      <nav className="border-b border-border bg-muted/30">
        <div className="container mx-auto px-4">
          <ul className="flex gap-1 overflow-x-auto">
            {navItems.map((item) => {
              const Icon = item.icon;
              const isActive = location.pathname === item.path ||
                (item.path !== '/dashboard' && item.path !== '/pipeline' && location.pathname.startsWith(item.path));
              return (
                <li key={item.path}>
                  <Link
                    to={item.path}
                    className={`flex items-center gap-2 px-4 py-3 text-sm font-medium transition-colors whitespace-nowrap ${
                      isActive
                        ? 'border-b-2 border-primary text-foreground'
                        : 'text-muted-foreground hover:text-foreground'
                    }`}
                  >
                    <Icon className="h-4 w-4" />
                    {item.label}
                  </Link>
                </li>
              );
            })}
          </ul>
        </div>
      </nav>

      {/* Main Content */}
      <main className="container mx-auto px-4 py-8">{children}</main>
    </div>
  );
}
