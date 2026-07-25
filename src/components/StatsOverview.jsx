import React from 'react';
import { ListTodo, Clock, AlertTriangle, CheckCircle2, ShieldQuestion, AlertCircle, FileCheck } from 'lucide-react';

export default function StatsOverview({ items = [], decisions = [], risksBlockers = [] }) {
  const total = items.length;
  const pending = items.filter(i => i.status === 'pending').length;
  const dueSoon = items.filter(i => i.status === 'due_soon' || i.status === 'reminded').length;
  const overdue = items.filter(i => i.status === 'overdue').length;
  const completed = items.filter(i => i.status === 'completed').length;
  const needsReview = items.filter(i => i.needs_review || i.status === 'needs_review').length;
  const atRisk = items.filter(i => i.status === 'at_risk' || i.escalated).length + risksBlockers.length;
  const decisionsCount = decisions.length;

  const completionRate = total > 0 ? Math.round((completed / total) * 100) : 0;

  const stats = [
    {
      label: 'Action Items',
      value: total,
      subtext: `${pending} pending`,
      icon: ListTodo,
      textColor: 'text-indigo-600',
      bgColor: 'bg-indigo-50',
      borderColor: 'border-indigo-100'
    },
    {
      label: 'Due Soon',
      value: dueSoon,
      subtext: 'Next 24h / Reminded',
      icon: Clock,
      textColor: 'text-amber-600',
      bgColor: 'bg-amber-50',
      borderColor: 'border-amber-100'
    },
    {
      label: 'Overdue',
      value: overdue,
      subtext: 'Needs immediate action',
      icon: AlertCircle,
      textColor: 'text-rose-600',
      bgColor: 'bg-rose-50',
      borderColor: 'border-rose-100'
    },
    {
      label: 'Completed',
      value: completed,
      subtext: `${completionRate}% completion rate`,
      icon: CheckCircle2,
      textColor: 'text-emerald-600',
      bgColor: 'bg-emerald-50',
      borderColor: 'border-emerald-100'
    },
    {
      label: 'Decisions',
      value: decisionsCount,
      subtext: 'Agreed outcomes',
      icon: FileCheck,
      textColor: 'text-blue-600',
      bgColor: 'bg-blue-50',
      borderColor: 'border-blue-100'
    },
    {
      label: 'Needs Review',
      value: needsReview,
      subtext: 'Ambiguous extraction',
      icon: ShieldQuestion,
      textColor: 'text-violet-600',
      bgColor: 'bg-violet-50',
      borderColor: 'border-violet-100'
    },
    {
      label: 'At Risk / Blocked',
      value: atRisk,
      subtext: 'Dependencies at risk',
      icon: AlertTriangle,
      textColor: 'text-orange-600',
      bgColor: 'bg-orange-50',
      borderColor: 'border-orange-100'
    }
  ];

  return (
    <div className="grid grid-cols-2 sm:grid-cols-4 lg:grid-cols-7 gap-3">
      {stats.map((stat, idx) => {
        const Icon = stat.icon;
        return (
          <div 
            key={idx}
            className={`saas-card p-3.5 rounded-xl border ${stat.borderColor} transition-all hover:shadow-md`}
          >
            <div className="flex items-center justify-between">
              <span className="text-[11px] font-medium text-slate-500">{stat.label}</span>
              <div className={`p-1.5 rounded-lg ${stat.bgColor}`}>
                <Icon className={`w-3.5 h-3.5 ${stat.textColor}`} />
              </div>
            </div>
            <h3 className="text-xl font-bold text-slate-900 mt-1">{stat.value}</h3>
            <p className="text-[10px] text-slate-500 mt-0.5 truncate">{stat.subtext}</p>
          </div>
        );
      })}
    </div>
  );
}
