import { Avatar, Badge, Collapse, Grid, List, ListItemAvatar, ListItemButton, ListItemText, Paper } from '@mui/material';
import ImageIcon from '@mui/icons-material/Image';
import React, { Fragment, useEffect } from 'react'
import { Link, useParams } from 'react-router-dom';
import * as _ from 'lodash'
import { useImmer } from 'use-immer';
import fetchAlbums from '../api-calls/albums';
import { ExpandLess, ExpandMore } from '@mui/icons-material';


export type AlbumsPageProps = { text?: string };
export type AlbumsPageState = {
    error: any,
    isLoaded: boolean,
    albums: Array<any>,
    expanded: Map<string, boolean>,
    children: Map<string, Array<any>>,
};

export default function SideBar() {
    const { album } = useParams();
    const [state, updateState] = useImmer<AlbumsPageState>({
        error: null,
        isLoaded: false,
        albums: [],
        expanded: new Map<string, boolean>(),
        children: new Map<string, Array<any>>(),
    });

    useEffect(() => {
        fetchAlbums('null', 0, 100, 'name').then(
            (result) => {
                updateState((draft) => {
                    draft.isLoaded = true;
                    draft.albums = result;
                    _.each(result, (item) => {
                        draft.expanded.set(item._id, false);
                    });
                });
            },
            (error) => {
                updateState((draft) => {
                    draft.isLoaded = false;
                    draft.error = error;
                });
            }
        )
    }, [])

    const render_album_block = (padding: number, id: string, name: string, hasChildren: boolean) => {
        return (
            <Fragment key={`frag-album-button-${id}`}>
                <ListItemButton style={{ marginLeft: padding }} key={`album-button-${id}`} component={Link} to={`/explore/albums/${id}`} selected={_.isEqual(album, id)}>
                    <ListItemAvatar>
                        <Avatar>
                            <ImageIcon />
                        </Avatar>
                    </ListItemAvatar>
                    <ListItemText primary={name} secondary="All the media you have" />
                    {
                        hasChildren && (
                            state.expanded.get(id) ? (
                                <Badge color="primary" onClick={(e) => {
                                    updateState((draft) => {
                                        draft.expanded.set(id, !draft.expanded.get(id));
                                    })
                                    e.preventDefault();
                                }}>
                                    <ExpandLess />
                                </Badge>


                            ) : (
                                <Badge color="primary" onClick={(e) => {
                                    if (_.isEmpty(state.children.get(id))) {
                                        fetchAlbums(id, 0, 100, 'name').then(
                                            (result) => {
                                                updateState((draft) => {
                                                    draft.expanded.set(id, !draft.expanded.get(id));
                                                    draft.children.set(id, result);
                                                });
                                            },
                                            (error) => {
                                                console.log(error);
                                            }

                                        );
                                    } else {
                                        updateState((draft) => {
                                            draft.expanded.set(id, !draft.expanded.get(id));
                                        });
                                    }
                                    e.preventDefault();
                                }}>
                                    <ExpandMore />
                                </Badge>
                            )
                        )
                    }
                </ListItemButton>
                {hasChildren &&
                    <>
                        <Collapse
                            key={`collapse-album-${id}`}
                            in={state.expanded.get(id)}
                            timeout="auto"
                            unmountOnExit
                        >
                            {
                                _.map(state.children.get(id), (item: any) => render_album_block(padding + 20, item._id, item.name, item.hasChildren))
                            }
                        </Collapse>
                    </>
                }
            </Fragment>
        )
    }

    return (
        <Paper>
            <List sx={{ width: '100%', maxWidth: '100%', bgcolor: 'background.paper' }}>
                <ListItemButton key={`album-button-faces`} component={Link} to={`/explore/faces`} selected={_.isEqual(album, 'faces')}>
                    <ListItemAvatar>
                        <Avatar>
                            <ImageIcon />
                        </Avatar>
                    </ListItemAvatar>
                    <ListItemText primary="People" secondary="Identified faces" />
                </ListItemButton>
                <ListItemButton key={`album-button-all`} component={Link} to={`/explore/albums/all-media`} selected={_.isEqual(album, 'all-media')}>
                    <ListItemAvatar>
                        <Avatar>
                            <ImageIcon />
                        </Avatar>
                    </ListItemAvatar>
                    <ListItemText primary="All media" secondary="All the media you have" />
                </ListItemButton>
                {
                    _.map(_.get(state, 'albums'), (item: any) => render_album_block(0, item._id, item.name, item.hasChildren))
                }
            </List>
        </Paper>
    )
}
