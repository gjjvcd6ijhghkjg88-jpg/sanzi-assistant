// 作用：展示应用标题、终端模式切换和当前系统能力状态。

import { Monitor, Smartphone, Sparkles } from 'lucide-react';
import type { Platform } from '../types';

type HeaderProps = {
  platform: Platform;
  onPlatformChange: (platform: Platform) => void;
};

export function Header({ platform, onPlatformChange }: HeaderProps) {
  return (
    <header className="app-header">
      <div className="brand">
        <div className="brand-icon" aria-hidden="true">
          <Sparkles size={22} />
        </div>
        <div>
          <h1>三资管理助手</h1>
          <p>简明问答 · 场景指引 · 双端适配</p>
        </div>
      </div>

      <div className="platform-switch" aria-label="终端模式">
        <button
          className={platform === 'pc' ? 'active' : ''}
          type="button"
          onClick={() => onPlatformChange('pc')}
          title="PC 端模式"
        >
          <Monitor size={18} />
          <span>PC</span>
        </button>
        <button
          className={platform === 'mobile' ? 'active' : ''}
          type="button"
          onClick={() => onPlatformChange('mobile')}
          title="移动端模式"
        >
          <Smartphone size={18} />
          <span>移动</span>
        </button>
      </div>
    </header>
  );
}
