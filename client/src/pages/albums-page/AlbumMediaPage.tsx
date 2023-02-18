import React, { useEffect } from 'react'
import Avatar from '@mui/material/Avatar';
import EditIcon from '@mui/icons-material/Edit';
import Paper from '@mui/material/Paper';
import Grid from '@mui/material/Grid';
import ListItemText from '@mui/material/ListItemText';
import ListItemAvatar from '@mui/material/ListItemAvatar';
import ImageIcon from '@mui/icons-material/Image';
import List from '@mui/material/List';
import { Badge, ListItemButton } from '@mui/material';
import { useParams, useNavigate } from 'react-router-dom';
import * as _ from 'lodash'
import { useImmer } from 'use-immer';
import MediaView from '../../components/MediaView';
import fetchAlbums from '../../api-calls/albums';


export type AlbumsPageProps = { text?: string };
export type AlbumsPageState = {
  error: any,
  isLoaded: boolean,
  albums: Array<any>,
};

export default function AlbumMediaPage(props: AlbumsPageProps) {
  const { album } = useParams();
  const mediaUrl = _.isEqual(album, 'all-media') ? `${process.env.REACT_APP_API}/media` : `${process.env.REACT_APP_API}/albums/${album}/media`


  return (
    <>
      <MediaView key={mediaUrl} url={mediaUrl}></MediaView>
    </>
  )
};
