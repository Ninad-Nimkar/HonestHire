import React from 'react';

/**
 * Sidebar navigation between the 4 views.
 */
export default function Sidebar({ currentView, onNavigate, jdUploaded, candidatesUploaded, pipelineComplete }) {
  const navItems = [
    {
      key: 'upload',
      label: 'Upload',
      icon: '📄',
      description: 'JD & Candidates',
      enabled: true,
    },
    {
      key: 'hr_gate',
      label: 'Prioritize',
      icon: '🎯',
      description: 'Skill Tiering',
      enabled: jdUploaded,
    },
    {
      key: 'pipeline',
      label: 'Analyze',
      icon: '⚡',
      description: 'Pipeline Progress',
      enabled: jdUploaded && candidatesUploaded,
    },
    {
      key: 'results',
      label: 'Results',
      icon: '📊',
      description: 'Ranked Dashboard',
      enabled: pipelineComplete,
    },
  ];

  return (
    <aside className="app-sidebar flex flex-col border-r overflow-y-auto"
           style={{
             background: 'var(--gradient-sidebar)',
             borderColor: 'var(--color-border)',
           }}>
      {/* Navigation */}
      <nav className="flex-1 py-4 px-3 space-y-1">
        {navItems.map((item) => {
          const isActive = currentView === item.key;
          return (
            <button
              key={item.key}
              onClick={() => item.enabled && onNavigate(item.key)}
              disabled={!item.enabled}
              className={`
                w-full flex items-center gap-3 px-4 py-3 rounded-xl text-left
                transition-all duration-200 group
                ${isActive
                  ? 'text-white'
                  : item.enabled
                    ? 'text-gray-400 hover:text-white'
                    : 'text-gray-600 cursor-not-allowed opacity-50'
                }
              `}
              style={{
                background: isActive
                  ? 'rgba(124, 58, 237, 0.15)'
                  : 'transparent',
                border: `1px solid ${isActive ? 'rgba(124, 58, 237, 0.3)' : 'transparent'}`,
              }}
            >
              <span className="text-xl">{item.icon}</span>
              <div className="flex-1 min-w-0">
                <div className="text-sm font-semibold">{item.label}</div>
                <div className="text-[11px]" style={{ color: 'var(--color-text-muted)' }}>
                  {item.description}
                </div>
              </div>
              {isActive && (
                <div className="w-1.5 h-6 rounded-full"
                     style={{ background: 'var(--gradient-primary)' }} />
              )}
            </button>
          );
        })}
      </nav>

      {/* Bottom info */}
      <div className="p-4 mx-3 mb-3 rounded-xl"
           style={{
             background: 'var(--color-bg-glass)',
             border: '1px solid var(--color-border)',
           }}>
        <div className="flex items-center gap-2 mb-2">
          <div className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
          <span className="text-xs font-medium text-emerald-400">System Online</span>
        </div>
        <p className="text-[11px]" style={{ color: 'var(--color-text-muted)' }}>
          Powered by GPT-4o dual-LLM debate with verification pipeline
        </p>
      </div>
    </aside>
  );
}
