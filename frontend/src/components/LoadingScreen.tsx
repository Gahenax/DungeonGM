import "./LoadingScreen.css";

interface LoadingScreenProps {
  message: string;
  error?: string | null;
}

export function LoadingScreen({ message, error }: LoadingScreenProps) {
  return (
    <div className="loading-screen">
      <div className="loading-content">
        <div className="loading-spinner" />
        <h2>{message}</h2>
        {error && <p className="error-message">{error}</p>}
        <p className="loading-subtext">Preparing the dungeon...</p>
      </div>
    </div>
  );
}
