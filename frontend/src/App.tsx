import { Routes, Route } from 'react-router-dom';
import { Navbar } from './components/Navbar/Navbar';
import { InputPage } from './pages/input/InputPage';
import { HistoryPage } from './pages/history/HistoryPage';
import { ReportPage } from './pages/report/ReportPage';

export default function App() {
  return (
    <div className="app">
      <Navbar />
      <main>
        <Routes>
          <Route path="/" element={<InputPage />} />
          <Route path="/history" element={<HistoryPage />} />
          <Route path="/report" element={<ReportPage />} />
        </Routes>
      </main>
    </div>
  );
}