import { Component, type ErrorInfo, type ReactNode } from "react";

interface Props {
  children: ReactNode;
  // Reset the error state whenever this key changes (e.g. on selection change).
  resetKey?: string | null;
}

interface State {
  error: Error | null;
}

export class ErrorBoundary extends Component<Props, State> {
  state: State = { error: null };

  static getDerivedStateFromError(error: Error): State {
    return { error };
  }

  componentDidUpdate(prev: Props) {
    if (prev.resetKey !== this.props.resetKey && this.state.error) {
      this.setState({ error: null });
    }
  }

  componentDidCatch(error: Error, info: ErrorInfo) {
    console.error("Render error:", error, info.componentStack);
  }

  render() {
    if (this.state.error) {
      return (
        <div className="detail-error">
          <h3>Could not render this schema</h3>
          <pre>{this.state.error.message}</pre>
          <p>Try selecting a different schema, or view the raw JSON in the source file.</p>
        </div>
      );
    }
    return this.props.children;
  }
}
