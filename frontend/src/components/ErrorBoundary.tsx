// 作用：React 运行时错误兜底。捕获子树未处理异常，渲染降级 UI 并提供重置入口。

import { Component, type ErrorInfo, type ReactNode } from 'react';

type ErrorBoundaryProps = {
  children: ReactNode;
  fallback?: (error: Error, reset: () => void) => ReactNode;
};

type ErrorBoundaryState = {
  error: Error | null;
};

export class ErrorBoundary extends Component<ErrorBoundaryProps, ErrorBoundaryState> {
  state: ErrorBoundaryState = { error: null };

  static getDerivedStateFromError(error: Error): ErrorBoundaryState {
    return { error };
  }

  componentDidCatch(error: Error, info: ErrorInfo): void {
    // 非生产环境保留堆栈，便于联调定位。生产环境建议接入 Sentry 等。
    console.error('[ErrorBoundary]', error, info);
  }

  reset = (): void => {
    this.setState({ error: null });
  };

  render(): ReactNode {
    const { error } = this.state;
    if (!error) {
      return this.props.children;
    }

    if (this.props.fallback) {
      return this.props.fallback(error, this.reset);
    }

    return (
      <div role="alert" className="error-boundary">
        <h2>页面遇到意外错误</h2>
        <p>你可以点击下方按钮重试，或刷新页面。工程团队已记录该问题。</p>
        <pre className="error-boundary-detail">{error.message}</pre>
        <button type="button" onClick={this.reset}>
          重试
        </button>
      </div>
    );
  }
}
