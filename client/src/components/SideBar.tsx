import { Avatar, Badge, List, ListItemAvatar, ListItemButton, ListItemText, Paper } from '@mui/material';
import ImageIcon from '@mui/icons-material/Image';
import EditIcon from '@mui/icons-material/Edit';
import React, { useEffect } from 'react'
import { Link, useNavigate, useParams } from 'react-router-dom';
import * as _ from 'lodash'
import { useImmer } from 'use-immer';
import fetchAlbums from '../api-calls/albums';


export type AlbumsPageProps = { text?: string };
export type AlbumsPageState = {
    error: any,
    isLoaded: boolean,
    albums: Array<any>,
};

export default function SideBar() {
    const { album } = useParams();
    const [state, updateState] = useImmer<AlbumsPageState>({
        error: null,
        isLoaded: false,
        albums: [],
    });
    const navigate = useNavigate();

    const changeAlbum = (album: string) => {
        navigate(`/explore/albums/${album}`)
    }

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

    return (
        <Paper>
            <List sx={{ width: '100%', maxWidth: '100%', bgcolor: 'background.paper' }}>
                <ListItemButton component={Link} to={`/explore/faces`} selected={_.isEqual(album, 'faces')}>
                    <ListItemAvatar>
                        <Avatar>
                            <ImageIcon />
                        </Avatar>
                    </ListItemAvatar>
                    <ListItemText primary="People" secondary="Identified faces" />
                </ListItemButton>
                <ListItemButton component={Link} to={`/explore/albums/all-media`} selected={_.isEqual(album, 'all-media')}>
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
                                component={Link} to={`/explore/albums/${item._id}`}
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
    )
}
