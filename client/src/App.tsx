import React from 'react';
import logo from './logo.svg';
import './App.css';
import {
  createBrowserRouter,
  Navigate,
  RouterProvider,
} from "react-router-dom";
import HomePage from './home-page/HomePage';


const router = createBrowserRouter([
  {
    path: "/",
    element: <Navigate to="/albums/all-media" replace />
  },
  {
    path: "/albums",
    element: <Navigate to="/albums/all-media" replace />
  },
  {
    path: "/albums/:album",
    element: <HomePage/>
  }
]);

function App() {
  return (
    <RouterProvider router={router} />
  );
}

export default App;
