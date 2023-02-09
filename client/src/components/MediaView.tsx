import { useEffect } from 'react'
import Paper from '@mui/material/Paper';
import ImageList from '@mui/material/ImageList';
import ImageListItem from '@mui/material/ImageListItem';
import { useImmer } from 'use-immer';
import { Waypoint } from 'react-waypoint';
import * as _ from 'lodash'
import { fetchMediaByAlbum } from '../api-calls/media';
import { Link, useNavigate } from 'react-router-dom';
import { Button } from '@mui/material';


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

export default function MediaView(props: MediaViewProps) {
  const [state, updateState] = useImmer<MediaViewState>({
    sort: 'name',
    skip: 0,
    limit: 100,
    mediaUrl: props.url,
    media: [],
    isLoaded: false,
    error: null
  });

  useEffect(() => {
    fetchMediaByAlbum(props.url, state.skip, state.limit, state.sort)
      .then(
        (result) => {
          updateState((draft: MediaViewState) => {
            draft.isLoaded = true;
            draft.media = result;
            draft.mediaUrl = props.url;
          });
        },
        (error) => {
          updateState((draft: MediaViewState) => {
            draft.isLoaded = false;
            draft.error = error;
          });
        }
      )
  }, [])

  const atEnd = () => {
    const skip = state.skip + state.limit;
    console.log('At end', skip)

    fetchMediaByAlbum(state.mediaUrl, skip, state.limit, state.sort).then(
      (result: Array<any>) => {
        updateState((draft: MediaViewState) => {
          draft.media = [...state.media, ...result];
          draft.skip = skip;
        });
      },
      (error) => {
        updateState((draft: MediaViewState) => {
          draft.isLoaded = false;
          draft.error = error;
        });
      }
    )
  }

  return (
    <>
      <Paper>
        <ImageList sx={{ width: '100%', height: '100%', margin: '0' }} cols={5} rowHeight={150}>
          {_.map(_.get(state, 'media'), (item: any, index: number) => (
            <ImageListItem component={Link} to={`./media/${item._id}`} state={state} key={item._id}>
              <img
                src={`${process.env.REACT_APP_API}/thumbnail/${item._id}`}
                srcSet={`${process.env.REACT_APP_API}/thumbnail/${item._id} 2x`}
                alt={item.name}
                loading="lazy"
                />
            </ImageListItem>
          ))}
        </ImageList>
        {
          !_.isEmpty(state.media) && <Waypoint
          onEnter={() => atEnd()}
          topOffset={'10%'}
        />}
      </Paper>
    </>
  )
};
