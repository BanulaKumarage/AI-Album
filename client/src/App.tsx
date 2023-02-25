import React from 'react';
import { enableMapSet } from "immer";
import './App.css';
import {
  createBrowserRouter,
  Navigate,
  RouterProvider,
} from "react-router-dom";
import AlbumMediaPage from './pages/albums-page/AlbumMediaPage';
import MediaPage from './pages/media-page/MediaPage';
import NavWrapperPage from './pages/nav-wrapper-page/NavWrapperPage';
import SideBarWrapperPage from './pages/nav-wrapper-page/SideBarWrapperPage';
import FacesPage from './pages/faces-page/FacesPage';


export type MainPageState = {
  anchorElNav?: any | null,
  anchorElUser?: any | null,
};

enableMapSet()

const router = createBrowserRouter([
  {
    path: "/",
    element: <Navigate to="explore/albums/all-media" replace />
  },
  {
    path: "/explore",
    element: <NavWrapperPage />,
    children: [
      {
        path: "",
        element: <SideBarWrapperPage />,
        children: [
          {
            path: "",
            element: <Navigate to="albums/all-media" replace />
          },
          {
            path: "albums",
            element: <Navigate to={'albums/all-media'} />
          },
          {
            path: "albums/:album",
            element: <AlbumMediaPage />,
          },
          {
            path: "faces",
            element: <FacesPage />,
          }
        ]
      },
      {
        path: "albums/:album/media/:media",
        element: <MediaPage />
      }
    ]
  },
]);

function App() {
  return (
    <RouterProvider router={router} />
  );
}

export default App;
