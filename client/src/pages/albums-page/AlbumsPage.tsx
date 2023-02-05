import React, { useEffect } from 'react'
import AppBar from '@mui/material/AppBar';
import Box from '@mui/material/Box';
import Toolbar from '@mui/material/Toolbar';
import Typography from '@mui/material/Typography';
import Menu from '@mui/material/Menu';
import Container from '@mui/material/Container';
import Avatar from '@mui/material/Avatar';
import MenuItem from '@mui/material/MenuItem';
import HomeIcon from '@mui/icons-material/Home';
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

export default function AlbumsPage(props: AlbumsPageProps) {
  const navigate = useNavigate();
  const { album } = useParams();
  const mediaUrl = _.isEqual(album, 'all-media') ? `${process.env.REACT_APP_API}/media` : `${process.env.REACT_APP_API}/albums/${album}/media`
  const [state, updateState] = useImmer<AlbumsPageState>({
    error: null,
    isLoaded: false,
    albums: [],
  });

  useEffect(() => {
    fetchAlbums(0, 100, 'name').then(
      (result) => {
        updateState((draft) => {
          draft.isLoaded = true;
          draft.albums = result;
        });
      },
      (error) => {
        updateState((draft) => {
          draft.isLoaded = true;
          draft.error = error;
        });
      }
    )
  }, [])

  const changeAlbum = (album: string) => {
    navigate(`/albums/${album}`)
  }

  return (
    <>
      <Grid container spacing={1} padding={1} textAlign={'center'}>
        <Grid item xs={4}>
          <Paper>
            <List sx={{ width: '100%', maxWidth: '100%', bgcolor: 'background.paper' }}>
              <ListItemButton selected={_.isEqual(album, 'all-media')} onClick={() => changeAlbum('all-media')}>
                <ListItemAvatar>
                  <Avatar>
                    <ImageIcon />
                  </Avatar>
                </ListItemAvatar>
                <ListItemText primary="All media" secondary="All the media you have" />
              </ListItemButton>
              {
                _.map(_.get(state, 'albums'), (item: any) => {
                  return (
                    <ListItemButton
                      key={`album-${item._id}`}
                      selected={_.isEqual(item._id, album)}
                      onClick={() => changeAlbum(item._id)}
                    >
                      <ListItemAvatar>
                        <Avatar>
                          <ImageIcon />
                        </Avatar>
                      </ListItemAvatar>
                      <ListItemText primary={item.name} secondary="TBD" />
                      <Badge color="primary" onClick={(e) => e.stopPropagation()}>
                        <EditIcon color="action" />
                      </Badge>
                    </ListItemButton>
                  )
                })
              }
            </List>
          </Paper>
        </Grid>
        <Grid item xs={8}>
          <MediaView key={mediaUrl} url={mediaUrl}></MediaView>
        </Grid>
      </Grid>
    </>
  )
};
