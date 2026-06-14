import React from 'react';

/**
 * Single pipeline node status indicator.
 */
export default function NodeStatus({ node, isLast }) {
  const statusIcons = {
    waiting: '○',
    running: '●',
    done: '✓',
    error: '✕',
    skipped: '—',
  };

  const statusColors = {
    waiting: 'var(--color-text-muted)',
    running: 'var(--color-accent-purple-light)',
    done: 'var(--color-accent-emerald)',
    error: 'var(--color-accent-rose)',
    skipped: 'var(--color-text-muted)',
  };

  return (
    <div className="pipeline-node">
      <div className={`pipeline-node-icon ${node.status}`}>
        {node.status === 'running' ? (
          <span className="animate-spin-slow inline-block text-xs">⟳</span>
        ) : (
          <span>{statusIcons[node.status]}</span>
        )}
      </div>

      <div className="flex items-center justify-between">
        <div>
          <p className={`text-sm font-semibold ${
            node.status === 'running' ? 'text-purple-300' :
            node.status === 'done' ? 'text-emerald-400' :
            node.status === 'error' ? 'text-rose-400' : 'text-gray-500'
          }`}>
            {node.display_name || node.name}
          </p>
          {node.status === 'running' && (
            <p className="text-[11px] text-purple-400/70 mt-0.5">
              Processing... {node.elapsed_seconds > 0 ? `${node.elapsed_seconds.toFixed(1)}s` : ''}
            </p>
          )}
          {node.status === 'done' && node.elapsed_seconds > 0 && (
            <p className="text-[11px] mt-0.5" style={{ color: 'var(--color-text-muted)' }}>
              Completed in {node.elapsed_seconds.toFixed(1)}s
            </p>
          )}
          {node.status === 'error' && node.error_message && (
            <p className="text-[11px] text-rose-400/70 mt-0.5">
              {node.error_message}
            </p>
          )}
        </div>

        {/* Status tag */}
        <span className={`text-[10px] px-2 py-0.5 rounded-full font-semibold uppercase tracking-wider ${
          node.status === 'running' ? 'text-purple-400 bg-purple-400/10' :
          node.status === 'done' ? 'text-emerald-400 bg-emerald-400/10' :
          node.status === 'error' ? 'text-rose-400 bg-rose-400/10' :
          'text-gray-500 bg-gray-500/10'
        }`}>
          {node.status}
        </span>
      </div>
    </div>
  );
}
