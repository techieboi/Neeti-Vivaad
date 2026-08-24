'use client';

import { useEffect, useState } from 'react';
import { Check, Sparkles } from 'lucide-react';

type AIProcessingStateProps = {
  title: string;
  description?: string;
  stages: string[];
};

export default function AIProcessingState({
  title,
  description,
  stages,
}: AIProcessingStateProps) {
  const [activeStage, setActiveStage] = useState(0);
  const stageKey = stages.join('|');

  useEffect(() => {
    if (stages.length < 2) return;

    const interval = window.setInterval(() => {
      setActiveStage((current) => Math.min(current + 1, stages.length - 1));
    }, 1700);

    return () => window.clearInterval(interval);
  }, [stageKey, stages.length]);

  return (
    <div
      role="status"
      aria-live="polite"
      aria-busy="true"
      className="relative overflow-hidden rounded-[10px] border border-emerald-200 bg-linear-to-br from-emerald-50 via-white to-emerald-50/40 p-5"
    >
      <div className="pointer-events-none absolute -right-10 -top-12 h-36 w-36 rounded-full bg-emerald-200/30 blur-3xl" />
      <div className="relative flex items-start gap-4">
        <div className="relative h-12 w-12 shrink-0" aria-hidden="true">
          <div className="absolute inset-0 rounded-full border border-emerald-200" />
          <div className="absolute inset-0 animate-spin rounded-full border-2 border-transparent border-r-[#24b47e] border-t-[#24b47e] motion-reduce:animate-none" />
          <div className="absolute inset-2 animate-pulse rounded-full bg-emerald-100 motion-reduce:animate-none" />
          <Sparkles className="absolute inset-0 m-auto h-4 w-4 text-emerald-700" />
        </div>

        <div className="min-w-0 flex-1">
          <div className="flex flex-wrap items-center justify-between gap-2">
            <h3 className="text-sm font-semibold text-[#171717]">{title}</h3>
            <span className="inline-flex items-center gap-1.5 rounded-full border border-emerald-200 bg-white px-2.5 py-1 text-[10px] font-mono font-semibold uppercase tracking-wider text-emerald-800">
              AI is working
              <span className="flex gap-0.5" aria-hidden="true">
                {[0, 1, 2].map((dot) => (
                  <span
                    key={dot}
                    className="h-1 w-1 animate-bounce rounded-full bg-emerald-600 motion-reduce:animate-none"
                    style={{ animationDelay: `${dot * 140}ms` }}
                  />
                ))}
              </span>
            </span>
          </div>

          {description && (
            <p className="mt-1 text-xs leading-relaxed text-[#707070]">{description}</p>
          )}

          <div className="mt-4 h-1 overflow-hidden rounded-full bg-emerald-100" aria-hidden="true">
            <div className="h-full w-2/5 animate-pulse rounded-full bg-[#24b47e] motion-reduce:animate-none" />
          </div>

          <div className="mt-3 grid gap-2 sm:grid-cols-3">
            {stages.map((stage, index) => {
              const isComplete = index < activeStage;
              const isActive = index === activeStage;

              return (
                <div
                  key={stage}
                  className={`flex min-w-0 items-center gap-2 rounded-[6px] border px-2.5 py-2 text-[10px] font-mono transition-colors ${
                    isActive
                      ? 'border-emerald-300 bg-emerald-100/80 text-emerald-950'
                      : isComplete
                        ? 'border-emerald-100 bg-white/70 text-emerald-700'
                        : 'border-[#ededed] bg-white/50 text-[#9a9a9a]'
                  }`}
                >
                  <span
                    className={`flex h-4 w-4 shrink-0 items-center justify-center rounded-full ${
                      isActive
                        ? 'bg-[#24b47e] text-white'
                        : isComplete
                          ? 'bg-emerald-100 text-emerald-700'
                          : 'bg-[#ededed] text-[#707070]'
                    }`}
                  >
                    {isComplete ? (
                      <Check className="h-2.5 w-2.5" />
                    ) : isActive ? (
                      <span className="h-1.5 w-1.5 animate-ping rounded-full bg-white motion-reduce:animate-none" />
                    ) : (
                      index + 1
                    )}
                  </span>
                  <span className="truncate">{stage}</span>
                </div>
              );
            })}
          </div>
        </div>
      </div>

      <span className="sr-only">{stages[activeStage]}</span>
    </div>
  );
}
