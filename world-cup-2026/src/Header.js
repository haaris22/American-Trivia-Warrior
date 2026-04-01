import React from 'react';
import { Link } from 'react-router-dom';
import './header.css';

function Header() {
  return (
    <header className="header">
      <h1>Haaris's Hobbies</h1>
      <nav>
        <Link to="/portfolio">Professional Portfolio</Link>
        <Link to="/fun">Creative Works</Link>
      </nav>
    </header>
  );
}

export default Header;