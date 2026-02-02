
import React from 'react';
import { UserRole } from '../types';
import { LayoutDashboard, UserCircle, PlayCircle, History, LogOut } from 'lucide-react';

interface SidebarProps {
  role: UserRole;
  activePage: string;
  onNavigate: (page: string) => void;
  onLogout: () => void;
}

const Sidebar: React.FC<SidebarProps> = ({ role, activePage, onNavigate, onLogout }) => {
  const menuItems = [
    { id: 'dashboard', label: 'Dashboard', icon: LayoutDashboard },
    { id: 'profile', label: 'Resume Profile', icon: UserCircle, show: role === UserRole.CANDIDATE },
    { id: 'interview', label: 'Start Interview', icon: PlayCircle, show: role === UserRole.CANDIDATE },
    { id: 'history', label: 'Interview History', icon: History, show: role === UserRole.CANDIDATE },
  ].filter(item => item.show !== false);

  return (
    <aside className="w-20 md:w-64 bg-slate-900 border-r border-slate-800 flex flex-col">
      <div 
        className="p-6 flex items-center gap-3 cursor-pointer hover:opacity-80 transition-opacity" 
        onClick={() => onNavigate('landing')}
        title="Go to Home Page"
      >
        <div className="w-10 h-10 bg-blue-600 rounded-xl flex items-center justify-center shadow-lg shadow-blue-500/20">
          <span className="font-bold text-xl text-white">Z</span>
        </div>
        <span className="hidden md:block font-bold text-xl tracking-tight text-white">Zynergy AI</span>
      </div>

      <nav className="flex-1 px-4 py-4 space-y-2">
        {menuItems.map((item) => (
          <button
            key={item.id}
            onClick={() => onNavigate(item.id)}
            className={`w-full flex items-center gap-4 px-4 py-3 rounded-lg transition-all ${
              activePage === item.id 
                ? 'bg-blue-600 text-white' 
                : 'text-slate-400 hover:bg-slate-800 hover:text-slate-200'
            }`}
          >
            <item.icon size={20} />
            <span className="hidden md:block font-medium">{item.label}</span>
          </button>
        ))}
      </nav>

      <div className="p-4 border-t border-slate-800">
        <button 
          onClick={onLogout}
          className="w-full flex items-center gap-4 px-4 py-3 text-red-400 hover:bg-red-950/20 rounded-lg transition-all"
        >
          <LogOut size={20} />
          <span className="hidden md:block font-medium">Logout</span>
        </button>
      </div>
    </aside>
  );
};

export default Sidebar;
