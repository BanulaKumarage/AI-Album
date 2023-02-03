import React from 'react';
import logo from './logo.svg';
import './App.css';
import {
  createBrowserRouter,
  Navigate,
  RouterProvider,
} from "react-router-dom";
import AlbumsPage from './pages/albums-page/AlbumsPage';
import MediaPage from './pages/MediaPage';


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
    element: <AlbumsPage/>
  },
  {
    path: "/albums/:album/media/:media",
    element: <MediaPage/>
  }
]);

function App() {
  return (
    <RouterProvider router={router} />
  );
}

export default App;
