import { useEffect } from 'react'
import Paper from '@mui/material/Paper';
import ImageList from '@mui/material/ImageList';
import ImageListItem from '@mui/material/ImageListItem';
import { useImmer } from 'use-immer';
import { Waypoint } from 'react-waypoint';
import * as _ from 'lodash'
import { fetchFaces } from '../api-calls/faces';
import { Link } from 'react-router-dom';
import { Typography } from '@mui/material';


export type FacesViewState = {
  sort: string;
  skip: number;
  limit: number;
  prominantFaces: Array<any>;
  nonProminantFaces: Array<any>;
  isLoaded: boolean;
  error: any;
};

export default function FacesView() {
  const [state, updateState] = useImmer<FacesViewState>({
    sort: 'name',
    skip: 0,
    limit: 100,
    prominantFaces: [],
    nonProminantFaces: [],
    isLoaded: false,
    error: null
  });

  useEffect(() => {
    fetchFaces(state.skip, state.limit, state.sort)
      .then(
        (result) => {
          updateState((draft: FacesViewState) => {
            draft.isLoaded = true;
            draft.prominantFaces = _.filter(result, item => item.isProminant);
            draft.nonProminantFaces = _.filter(result, item => !item.isProminant);
          });
        },
        (error) => {
          updateState((draft: FacesViewState) => {
            draft.isLoaded = false;
            draft.error = error;
          });
        }
      )
  }, [])

  const atEnd = () => {
    const skip = state.skip + state.limit;

    fetchFaces(skip, state.limit, state.sort).then(
      (result: Array<any>) => {
        if (_.isEmpty(result)) return;
        updateState((draft: FacesViewState) => {
          draft.prominantFaces = [...state.prominantFaces, ..._.filter(result, item => item.isProminant)];
          draft.nonProminantFaces = [...state.nonProminantFaces, ..._.filter(result, item => !item.isProminant)];
          draft.skip = skip;
        });
      },
      (error) => {
        updateState((draft: FacesViewState) => {
          draft.isLoaded = false;
          draft.error = error;
        });
      }
    )
  }

  const renderContent = (cols: number, type: string) => {
    return (
      <>
        <ImageList sx={{ width: '100%', height: '100%', margin: '0' }} cols={cols} rowHeight={'auto'}>
          {
            _.map(_.get(state, type), (item: any, index: number) =>
              <ImageListItem component={Link} to={`./${item._id}`} relative={'route'} state={state} key={`faces-list-${item._id}`} style={{ overflow: 'hidden' }}>
                <img
                  src={`${process.env.REACT_APP_API}/thumbnail/${item.imageId}?top=${item.face.top}&right=${item.face.right}&bottom=${item.face.bottom}&left=${item.face.left}`}
                  srcSet={`${process.env.REACT_APP_API}/thumbnail/${item.imageId}?top=${item.face.top}&right=${item.face.right}&bottom=${item.face.bottom}&left=${item.face.left} 2x`}
                  alt={item.name}
                  loading="lazy"
                />
              </ImageListItem>
            )
          }
        </ImageList>
      </>
    )
  }

  return (
    <>
      {/* big screen */}
      <Paper sx={{ display: { xs: 'none', md: 'flex' } }}>
        {renderContent(5, 'prominantFaces')}
      </Paper>
      {!_.isEmpty(state.nonProminantFaces) && <Typography sx={{ display: { xs: 'none', md: 'flex' } }} variant="h5" gutterBottom>
        More people you might know...
      </Typography>}
      <Paper sx={{ display: { xs: 'none', md: 'flex' } }}>
        {renderContent(10, 'nonProminantFaces')}
      </Paper>
      {/* small screen */}
      <Paper sx={{ display: { xs: 'flex', md: 'none' } }}>
        {renderContent(3, 'prominantFaces')}
      </Paper>
      {!_.isEmpty(state.nonProminantFaces) && <Typography sx={{ display: { xs: 'flex', md: 'none' } }} variant="h5" gutterBottom>
        More people you might know...
      </Typography>}
      <Paper sx={{ display: { xs: 'flex', md: 'none' } }}>
        {renderContent(6, 'nonProminantFaces')}
      </Paper>
      {
        (!_.isEmpty(state.prominantFaces) || !_.isEmpty(state.nonProminantFaces)) && <Waypoint
          onEnter={() => atEnd()}
          topOffset={'10%'}
        />
      }
    </>
  )
};
