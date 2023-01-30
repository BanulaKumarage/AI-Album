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
import withRouter, { RouterProps } from '../inject-router';
import * as _ from 'lodash'
import MediaView from '../components/MediaView';


export type HomePageProps = { text?: string, router: RouterProps };
export type HomePageState = {
  error: any,
  isLoaded: boolean,
  albums: Array<any>,
  albumMedia: Array<any>,
  anchorElNav?: any,
  anchorElUser?: any,
  selectedAlbum?: any
};

class HomePage extends Component<HomePageProps, any> {
  constructor(props: HomePageProps) {
    super(props);
    const album = this.props.router.params.album;
    this.state = {
      error: null,
      isLoaded: false,
      albums: [],
      anchorElNav: null,
      anchorElUser: null,
      selectedAlbum: album,
      mediaUrl: _.isEqual(album, 'all-media') ? `${process.env.REACT_APP_API}/media` : `${process.env.REACT_APP_API}/albums/${album}/media`
    };

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

  componentDidUpdate(prevProps: any, prevState: any) {
    console.log('yeah', prevProps)
  }

  changeAlbum(album: string) {
    this.setState({
      ...this.state,
      mediaUrl: _.isEqual(album, 'all-media') ? `${process.env.REACT_APP_API}/media` : `${process.env.REACT_APP_API}/albums/${album}/media`,
      selectedAlbum: album
    })
    this.props.router.navigate(`/albums/${album}`)
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
                  <ListItemButton selected={_.isEqual(this.state.selectedAlbum, 'all-media')} onClick={() => this.changeAlbum('all-media')}>
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
                        <ListItemButton
                          key={`album-${item._id.$oid}`}
                          selected={_.isEqual(item._id.$oid, this.state.selectedAlbum)}
                          onClick={() => this.changeAlbum(item._id.$oid)}
                        >
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
              <MediaView url={this.state.mediaUrl}></MediaView>
            </Grid>
          </Grid>
        </div>
      </div>
    )
  }
}

export default withRouter(HomePage);
