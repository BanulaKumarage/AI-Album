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
  anchorElNav?: any | null,
  anchorElUser?: any | null,
};

export default function AlbumsPage(props: AlbumsPageProps) {
  const navigate = useNavigate();
  const { album } = useParams();
  const mediaUrl = _.isEqual(album, 'all-media') ? `${process.env.REACT_APP_API}/media` : `${process.env.REACT_APP_API}/albums/${album}/media`
  const [state, updateState] = useImmer<AlbumsPageState>({
    error: null,
    isLoaded: false,
    albums: [],
    anchorElNav: null,
    anchorElUser: null,
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

  const pages: any = [];

  const handleOpenNavMenu = (event: React.MouseEvent<HTMLElement>) => {
    updateState((draft) => {
      draft.anchorElNav = event.currentTarget;
    })
  };

  const handleCloseNavMenu = () => {
    updateState((draft) => {
      draft.anchorElNav = null;
    })
  };

  const changeAlbum = (album: string) => {
    navigate(`/albums/${album}`)
  }

  return (
    <>
      <AppBar position="static">
        <Container maxWidth="xl">
          <Toolbar disableGutters>
            <HomeIcon sx={{ display: { xs: 'none', md: 'flex' }, mr: 1 }} />
            <Typography
              variant="h6"
              noWrap
              component="a"
              href="/"
              sx={{
                mr: 2,
                display: { xs: 'none', md: 'flex' },
                fontFamily: 'monospace',
                fontWeight: 700,
                letterSpacing: '.3rem',
                color: 'inherit',
                textDecoration: 'none',
              }}
            >
              AI-ALBUM
            </Typography>

            <Box sx={{ flexGrow: 1, display: { xs: 'flex', md: 'none' } }}>
              <Menu
                id="menu-appbar"
                anchorEl={state.anchorElNav}
                anchorOrigin={{
                  vertical: 'bottom',
                  horizontal: 'left',
                }}
                keepMounted
                transformOrigin={{
                  vertical: 'top',
                  horizontal: 'left',
                }}
                open={Boolean(state.anchorElNav)}
                onClose={handleCloseNavMenu}
                sx={{
                  display: { xs: 'block', md: 'none' },
                }}
              >
                {_.map(pages, (page) => (
                  <MenuItem key={page} onClick={handleCloseNavMenu}>
                    <Typography textAlign="center">{page}</Typography>
                  </MenuItem>
                ))}
              </Menu>
            </Box>
            <HomeIcon sx={{ display: { xs: 'flex', md: 'none' }, mr: 1 }} />
            <Typography
              variant="h5"
              noWrap
              component="a"
              href=""
              sx={{
                mr: 2,
                display: { xs: 'flex', md: 'none' },
                flexGrow: 1,
                fontFamily: 'monospace',
                fontWeight: 700,
                letterSpacing: '.3rem',
                color: 'inherit',
                textDecoration: 'none',
              }}
            >
              AI-ALBUM
            </Typography>
          </Toolbar>
        </Container>
      </AppBar>
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
                      key={`album-${item._id.$oid}`}
                      selected={_.isEqual(item._id.$oid, album)}
                      onClick={() => changeAlbum(item._id.$oid)}
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
