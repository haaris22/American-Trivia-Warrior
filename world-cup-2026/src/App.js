import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Header from './Header';

function Portfolio() {
  return (
    <div>
      <h2>Portfolio</h2>
      <ul>
        <li>Resume (link or content)</li>
        <li>Project 1</li>
        <li>Project 2</li>
        {/* Add more projects */}
      </ul>
    </div>
  );
}

function Media() {
  return <div><h3>Media Projects</h3><p>Creative media content here.</p></div>;
}

function Sports() {
  return <div><h3>Sports Projects</h3><p>Sports-related content here.</p></div>;
}

function Finance() {
  return <div><h3>Finance Projects</h3><p>Finance-related content here.</p></div>;
}

import { Link, Outlet } from 'react-router-dom';

function Fun() {
  return (
    <div>
      <h2>Fun Stuff & Blogs</h2>
      <nav>
        <Link to="media">Media</Link> |{" "}
        <Link to="sports">Sports</Link> |{" "}
        <Link to="finance">Finance</Link>
      </nav>
      <Outlet />
    </div>
  );
}

function App() {
  return (
    <Router>
      <Header />
      <Routes>
        <Route path="/portfolio" element={<Portfolio />} />
        <Route path="/fun" element={<Fun />}>
          <Route path="media" element={<Media />} />
          <Route path="sports" element={<Sports />} />
          <Route path="finance" element={<Finance />} />
        </Route>
        <Route path="/" element={<div><h2>Welcome!</h2></div>} />
      </Routes>
    </Router>
  );
}

export default App;