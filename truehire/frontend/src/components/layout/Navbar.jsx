import React from 'react';

/**
 * Top navigation bar with app branding and step indicator.
 */
export default function Navbar({ currentView, stepLabels }) {
  const steps = stepLabels || [
    { key: 'upload', label: 'Upload', num: 1 },
    { key: 'hr_gate', label: 'Prioritize', num: 2 },
    { key: 'pipeline', label: 'Analyze', num: 3 },
    { key: 'results', label: 'Results', num: 4 },
  ];

  return (
    <nav className="app-navbar flex items-center justify-between px-6 border-b"
         style={{ background: 'var(--color-bg-secondary)', borderColor: 'var(--color-border)' }}>
      {/* Logo & Brand */}
      <div className="flex items-center gap-3">
        <div className="w-9 h-9 rounded-xl flex items-center justify-center text-lg font-black"
             style={{ background: 'var(--gradient-primary)' }}>
          T
        </div>
        <div>
          <h1 className="text-lg font-bold tracking-tight gradient-text">TrueHire</h1>
          <p className="text-[10px] tracking-widest uppercase"
             style={{ color: 'var(--color-text-muted)' }}>
            AI Candidate Intelligence
          </p>
        </div>
      </div>

      {/* Step Indicator */}
      <div className="flex items-center gap-1">
        {steps.map((step, i) => {
          const isActive = step.key === currentView;
          const isPast = steps.findIndex(s => s.key === currentView) > i;
          return (
            <React.Fragment key={step.key}>
              <div className="flex items-center gap-2">
                <div className={`
                  w-7 h-7 rounded-full flex items-center justify-center text-xs font-bold
                  transition-all duration-300
                  ${isActive
                    ? 'text-white shadow-lg'
                    : isPast
                      ? 'text-emerald-400'
                      : 'text-gray-500'
                  }
                `}
                style={{
                  background: isActive
                    ? 'var(--gradient-primary)'
                    : isPast
                      ? 'rgba(16, 185, 129, 0.15)'
                      : 'var(--color-bg-glass)',
                  border: `1.5px solid ${
                    isActive
                      ? 'transparent'
                      : isPast
                        ? 'rgba(16, 185, 129, 0.3)'
                        : 'var(--color-border)'
                  }`,
                }}>
                  {isPast ? '✓' : step.num}
                </div>
                <span className={`text-xs font-medium hidden sm:inline ${
                  isActive ? 'text-white' : isPast ? 'text-emerald-400' : 'text-gray-500'
                }`}>
                  {step.label}
                </span>
              </div>
              {i < steps.length - 1 && (
                <div className="w-8 h-px mx-1"
                     style={{
                       background: isPast ? 'var(--color-accent-emerald)' : 'var(--color-border)',
                     }} />
              )}
            </React.Fragment>
          );
        })}
      </div>

      {/* Version badge */}
      <div className="text-[10px] font-mono px-2 py-1 rounded-md"
           style={{ background: 'var(--color-bg-glass)', color: 'var(--color-text-muted)' }}>
        v1.0
      </div>
    </nav>
  );
}
