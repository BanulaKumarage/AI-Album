import React from 'react';
import logo from './logo.svg';
import './App.css';
import {
  createBrowserRouter,
  Navigate,
  RouterProvider,
} from "react-router-dom";
import AlbumsPage from './pages/albums-page/AlbumsPage';
import MediaPage from './pages/media-page/MediaPage';
import * as _ from 'lodash'
import NavWrapperPage from './pages/nav-wrapper-page/NavWrapperPage';


export type MainPageState = {
  anchorElNav?: any | null,
  anchorElUser?: any | null,
};

const router = createBrowserRouter([
  {
    path: "/",
    element: <Navigate to="/albums/all-media" replace />
  },
  {
    path: "/",
    element: <NavWrapperPage/>,
    children: [
      {
        path: "/albums",
        element: <Navigate to={'/albums/all-media'} />
      },
      {
        path: "/albums/:album",
        element: <AlbumsPage />
      },
      {
        path: "/albums/:album/media/:media",
        element: <MediaPage />
      }
    ]
  },
]);

function App() {
  return (
      <RouterProvider router={router}/>
  );
}

export default App;
