import { Link, useLocation } from 'react-router-dom';
import './navbar.css';

export function Navbar() {
  const location = useLocation();

  const links = [
    { to: '/', label: 'Ввод' },
    { to: '/tasks', label: 'Очередь' },
    { to: '/history', label: 'История' },
    { to: '/report', label: 'Отчёт' },
  ];

  return (
    <nav className="navbar">
      <Link to="/" className="navbar-brand">Railway Agent</Link>
      <div className="navbar-links">
        {links.map((link) => (
          <Link
            key={link.to}
            to={link.to}
            className={`navbar-link${location.pathname === link.to ? ' active' : ''}`}
          >
            {link.label}
          </Link>
        ))}
      </div>
    </nav>
  );
}