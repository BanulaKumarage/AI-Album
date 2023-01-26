import React from 'react';
import logo from './logo.svg';
import './App.css';
import {
  createBrowserRouter,
  RouterProvider,
} from "react-router-dom";
import HomePage from './home-page/HomePage';


const router = createBrowserRouter([
  {
    path: "/",
    element: <div>Hello world!</div>,
  },
  {
    path: "/home",
    element: <HomePage/>
  },
]);

function App() {
  return (
    <RouterProvider router={router} />
  );
}

export default App;
