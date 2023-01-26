import React, { Component } from 'react'
import AppBar from '@mui/material/AppBar';
import Box from '@mui/material/Box';
import Toolbar from '@mui/material/Toolbar';
import IconButton from '@mui/material/IconButton';
import Typography from '@mui/material/Typography';
import Menu from '@mui/material/Menu';
import MenuIcon from '@mui/icons-material/Menu';
import Container from '@mui/material/Container';
import Avatar from '@mui/material/Avatar';
import Button from '@mui/material/Button';
import Tooltip from '@mui/material/Tooltip';
import MenuItem from '@mui/material/MenuItem';
import HomeIcon from '@mui/icons-material/Home';
import Paper from '@mui/material/Paper';
import Grid from '@mui/material/Grid';
import ListItem from '@mui/material/ListItem';
import ListItemText from '@mui/material/ListItemText';
import ListItemAvatar from '@mui/material/ListItemAvatar';
import ImageIcon from '@mui/icons-material/Image';
import List from '@mui/material/List';
import { ListItemButton } from '@mui/material';
import ImageList from '@mui/material/ImageList';
import ImageListItem from '@mui/material/ImageListItem';
import * as _ from 'lodash'

export type HomePageProps = { text?: string };

export default class HomePage extends Component<HomePageProps, any> {
  constructor(props: HomePageProps) {
    super(props);
    this.state = {
      error: null,
      isLoaded: false,
      albums: [],
      albumMedia: [],
      anchorElNav: null,
      anchorElUser: null,
      selectedAlbum: null
    };
  }

  componentDidMount() {
    this.getAlbums();
  }

  getAlbums() {
    fetch(`${process.env.REACT_APP_API}/albums`)
      .then(res => res.json())
      .then(
        (result) => {
          this.setState({
            isLoaded: true,
            albums: result
          });
          console.log(result);
        },
        (error) => {
          this.setState({
            isLoaded: true,
            error
          });
        }
      )
  }

  getMedia(album='') {
    fetch(`${process.env.REACT_APP_API}/media`)
      .then(res => res.json())
      .then(
        (result) => {
          this.setState({
            ...this.state,
            isLoaded: true,
            albumMedia: result,
            selectedAlbum: ''
          });
          console.log(result);
        },
        (error) => {
          this.setState({
            isLoaded: true,
            error
          });
        }
      )
  }

  scroll(event: any) {
    console.log(event)
  }

  render() {
    const pages: any = [];

    const handleOpenNavMenu = (event: React.MouseEvent<HTMLElement>) => {
      this.setState({
        ...this.state,
        anchorElNav: event.currentTarget
      })
    };
  
    const handleCloseNavMenu = () => {
      console.log('click')
      this.setState({
        ...this.state,
        anchorElNav: null
      })
    };

    return (
      <div>
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
                  anchorEl={this.state.anchorElNav}
                  anchorOrigin={{
                    vertical: 'bottom',
                    horizontal: 'left',
                  }}
                  keepMounted
                  transformOrigin={{
                    vertical: 'top',
                    horizontal: 'left',
                  }}
                  open={Boolean(this.state.anchorElNav)}
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
        <div className='m-0'>
        <Grid container spacing={1} padding={1} textAlign={'center'}> 
          <Grid item xs={4}>
            <Paper>
            <List sx={{ width: '100%', maxWidth: '100%', bgcolor: 'background.paper' }}>
              <ListItemButton selected={this.state.selectedAlbum==''} onClick={() => this.getMedia('')}>
                <ListItemAvatar>
                  <Avatar>
                    <ImageIcon />
                  </Avatar>
                </ListItemAvatar>
                <ListItemText primary="All media" secondary="All the media you have" />
              </ListItemButton>
              {
                _.map(_.get(this.state, 'albums'), (item: any) => {
                  return (
                    <ListItemButton selected={item._id == this.state.selectedAlbum} onClick={() => this.getMedia(item._id.$oid)}>
                      <ListItemAvatar>
                        <Avatar>
                          <ImageIcon />
                        </Avatar>
                      </ListItemAvatar>
                      <ListItemText primary={item.name} secondary="TBD" />
                    </ListItemButton>
                  )
                })
              }
            </List>
            </Paper>
          </Grid>
          <Grid item xs={8}>
            <Paper>
            <ImageList sx={{ width: '100%', height: '100%' }} cols={5} rowHeight={150} onScrollCapture={this.scroll}>
              {_.map(_.get(this.state, 'albumMedia'), (item) => (
                <ImageListItem key={item.path}>
                  <img
                    src={`${process.env.REACT_APP_API}/thumbnail/${item.path}`}
                    srcSet={`${process.env.REACT_APP_API}/thumbnail/${item.path} 2x`}
                    alt={item.name}
                    loading="lazy"
                  />
                </ImageListItem>
              ))}
            </ImageList>
            </Paper>
          </Grid>
        </Grid>
        </div>
      </div>
    )
  }
}
