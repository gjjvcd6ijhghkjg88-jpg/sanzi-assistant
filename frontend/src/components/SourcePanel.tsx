// 作用：展示当前回答引用的资料来源，帮助经办人员追溯依据。

import { BookOpen, Search } from 'lucide-react';
import type { ChatMessage } from '../types';

type SourcePanelProps = {
  message?: ChatMessage;
};

export function SourcePanel({ message }: SourcePanelProps) {
  const sources = message?.sources ?? [];

  return (
    <aside className="source-panel" aria-label="资料来源">
      <div className="panel-title">
        <BookOpen size={18} />
        <h2>资料依据</h2>
      </div>

      {sources.length === 0 ? (
        <div className="empty-source">
          <Search size={22} />
          <p>完成一次问答后，这里会展示命中的政策、手册或平台说明。</p>
        </div>
      ) : (
        <div className="source-list">
          {sources.map((source) => (
            <article className="source-card" key={source.id}>
              <div className="source-meta">
                <span>{source.id}</span>
                <strong>{source.category}</strong>
              </div>
              <h3>{source.title}</h3>
              <p>{source.excerpt}</p>
            </article>
          ))}
        </div>
      )}
    </aside>
  );
}
