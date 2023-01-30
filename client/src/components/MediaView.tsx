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
import { Waypoint } from 'react-waypoint';
import * as _ from 'lodash'

export type MediaViewProps = { url: string };
export type MediaViewState = { 
  sort: string;
  skip: number;
  limit: number; 
  media: Array<any>; 
  isLoaded: boolean;
  error: any;
  mediaUrl: string;
};

// TODO listen to route changes

class MediaView extends Component<MediaViewProps, MediaViewState> {
  scrollskip: number;

  constructor(props: MediaViewProps) {
    super(props);

    this.state = {
      sort: 'name',
      skip: 0,
      limit: 100,
      mediaUrl: this.props.url,
      media: [],
      isLoaded: false,
      error: null
    }
    this.scrollskip = 0;
  }
  
  componentDidMount() {
    this.load();
  }

  componentDidUpdate(prevProps: any, prevState: any) {
    if (!_.isEqual(prevProps.url, this.props.url)) {
      this.load();
      this.setState({
        ...this.state,
        mediaUrl: prevProps.url,
        skip: 0
      })
    }
  }

  atEnd() {
    const newSkip = this.scrollskip + this.state.limit;

    fetch(this.props.url + '?' + new URLSearchParams({
      limit: this.state.limit.toString(), 
      skip: newSkip.toString(), 
      sort: this.state.sort
    }))
      .then(res => res.json())
      .then(
        (result) => {
          this.setState({
            ...this.state,
            isLoaded: true,
            media: [...this.state.media, ...result],
            mediaUrl: this.props.url
          });
          this.scrollskip = newSkip
        },
        (error) => {
          this.setState({
            isLoaded: false,
            error
          });
        }
      )
  }

  load() {
    fetch(this.props.url + '?' + new URLSearchParams({
      limit: this.state.limit.toString(), 
      skip: this.state.skip.toString(), 
      sort: this.state.sort
    }))
      .then(res => res.json())
      .then(
        (result) => {
          this.setState({
            ...this.state,
            isLoaded: true,
            media: result,
            mediaUrl: this.props.url
          });
        },
        (error) => {
          this.setState({
            isLoaded: false,
            error
          });
        }
      )
  }

  render() {
    return (
      <Paper>
        <ImageList sx={{ width: '100%', height: '100%' }} cols={5} rowHeight={150}>
          {_.map(_.get(this.state, 'media'), (item: any) => (
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
        <Waypoint
          onEnter={() => this.atEnd()}
          topOffset={'10%'}
        />
      </Paper>
    )
  }
}

export default withRouter(MediaView);