import React, { useEffect, useRef } from 'react';
import NodeStatus from './NodeStatus';

/**
 * Pipeline progress view — vertical stepper with live polling.
 */
export default function PipelineView({ status, onComplete }) {
  const polledComplete = useRef(false);

  useEffect(() => {
    if (status?.status === 'complete' && !polledComplete.current) {
      polledComplete.current = true;
      // Small delay before navigating to results
      setTimeout(() => onComplete?.(), 1500);
    }
  }, [status?.status, onComplete]);

  if (!status) {
    return (
      <div className="flex items-center justify-center h-64">
        <p style={{ color: 'var(--color-text-muted)' }}>Waiting for pipeline to start...</p>
      </div>
    );
  }

  const progressPct = status.progress_pct || 0;
  const isComplete = status.status === 'complete';
  const isError = status.status === 'error';

  return (
    <div className="animate-fade-in max-w-2xl mx-auto">
      {/* Header */}
      <div className="text-center mb-8">
        <h2 className="text-2xl font-bold mb-2">
          {isComplete ? '✅ Analysis Complete!' :
           isError ? '❌ Pipeline Error' :
           '⚡ Analyzing Candidates...'}
        </h2>
        <p className="text-sm" style={{ color: 'var(--color-text-secondary)' }}>
          {isComplete
            ? 'All candidates have been analyzed and ranked. Navigating to results...'
            : isError
              ? status.error_message || 'An error occurred during analysis'
              : 'Sit back while our AI analyzes each candidate holistically'}
        </p>
      </div>

      {/* Progress bar */}
      <div className="mb-8">
        <div className="flex items-center justify-between mb-2">
          <span className="text-xs font-semibold" style={{ color: 'var(--color-text-secondary)' }}>
            Progress
          </span>
          <span className="text-xs font-bold text-purple-400">
            {Math.round(progressPct)}%
          </span>
        </div>
        <div className="progress-bar">
          <div className="progress-bar-fill" style={{ width: `${progressPct}%` }} />
        </div>
      </div>

      {/* Pipeline stepper */}
      <div className="glass-card p-6">
        <div className="pipeline-stepper">
          {(status.nodes || []).map((node, i) => (
            <NodeStatus
              key={node.name}
              node={node}
              isLast={i === (status.nodes?.length || 0) - 1}
            />
          ))}
        </div>
      </div>

      {/* Current status text */}
      {!isComplete && !isError && status.current_node && (
        <div className="text-center mt-6">
          <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full"
               style={{
                 background: 'rgba(124, 58, 237, 0.1)',
                 border: '1px solid rgba(124, 58, 237, 0.2)',
               }}>
            <span className="animate-pulse-glow w-2 h-2 rounded-full bg-purple-400" />
            <span className="text-sm text-purple-300">
              Currently running: <strong>{status.current_node}</strong>
            </span>
          </div>
        </div>
      )}
    </div>
  );
}
