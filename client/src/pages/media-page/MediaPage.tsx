import React, { useEffect } from 'react'
import ImageViewer from 'react-simple-image-viewer';
import ArrowBackIcon from '@mui/icons-material/ArrowBack';
import { useImmer } from 'use-immer';
import { useNavigate, useParams } from 'react-router-dom';
import * as _ from 'lodash'
import { Avatar, Button, Container, Grid, Paper, Table, TableBody, TableCell, TableContainer, TableHead, TableRow } from '@mui/material';
import { fetchMediaById } from '../../api-calls/media';
import { Stack } from '@mui/system';

export type MediaPageState = {
  showImage: boolean;
  error: any;
  isLoaded: boolean;
  metadata: any;
};

function createData(
  name: string,
  calories: number,
  fat: number,
  carbs: number,
  protein: number,
) {
  return { name, calories, fat, carbs, protein };
}

export default function MediaPage() {
  const { media } = useParams();
  const navigate = useNavigate();
  const [state, updateState] = useImmer<MediaPageState>({
    showImage: false,
    error: null,
    isLoaded: false,
    metadata: null
  });
  const mediaUrl = `${process.env.REACT_APP_API}/fullsize/${media}`
  const faceUrl = `${process.env.REACT_APP_API}/thumbnail/${media}`

  useEffect(() => {
    fetchMediaById(`${media}`).then(
      (result) => {
        updateState((draft) => {
          draft.metadata = result;
          draft.isLoaded = true;
        });
      },
      (error) => {
        updateState((draft) => {
          draft.error = error;
        });
      }
    )
  }, [])


  return (
    <>
      <Container>
        <Grid container item xs={1} p={0} my={1}>
          <Button variant="outlined" color='inherit' onClick={() => navigate(-1)}>
            <ArrowBackIcon />
          </Button>
        </Grid>
        <Grid container item xs={12} p={0} mb={1} alignItems={'center'} justifyContent={'center'}>
          <Paper>
            <img onClick={() => updateState((draft) => { draft.showImage = true; })} src={mediaUrl} alt="Media" style={{ maxHeight: '100%', maxWidth: '100%', display: 'block', margin: '0 auto' }} />
          </Paper>
        </Grid>
      </Container>
      {
        state.isLoaded &&
        <Container>
          <Grid container item xs={12} m={0} p={0}>
            <TableContainer component={Paper}>
              <Table aria-label="simple table">
                <TableHead>
                  <TableRow>
                    <TableCell width={'30%'}>Attribute</TableCell>
                    <TableCell width={'70%'}>Value</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  <TableRow
                    key={`${media}-name`}
                    sx={{ '&:last-child td, &:last-child th': { border: 0 } }}
                  >
                    <TableCell component="th" scope="row">
                      Image name
                    </TableCell>
                    <TableCell>
                      {state.metadata.name}
                    </TableCell>
                  </TableRow>
                  {_.has(state.metadata, 'caption') && <TableRow
                    key={`${media}-caption`}
                    sx={{ '&:last-child td, &:last-child th': { border: 0 } }}
                  >
                    <TableCell component="th" scope="row">
                      Generated caption
                    </TableCell>
                    <TableCell align="left">
                      {_.map(state.metadata.caption.split('\n'), (sentence, index) => {
                        return (
                          <div key={`sentence-${index}`}>
                            {sentence}
                            <hr />
                          </div>
                        )
                      })}
                    </TableCell>
                  </TableRow>}
                  {_.has(state.metadata, 'faces') && <TableRow
                    key={`${media}-people`}
                    sx={{ '&:last-child td, &:last-child th': { border: 0 } }}
                  >
                    <TableCell component="th" scope="row">
                      Faces detected
                    </TableCell>
                    <TableCell align="left">
                      <Stack direction="row" spacing={2}>
                        {_.map(state.metadata.faces, (face, index) => {
                          return (
                            <Avatar sx={{ width: 100, height: 100 }} key={`face-${index}`} alt="" src={`${faceUrl}?top=${face.top}&right=${face.right}&bottom=${face.bottom}&left=${face.left}`} />
                          )
                        })}
                      </Stack>
                    </TableCell>
                  </TableRow>}
                </TableBody>
              </Table>
            </TableContainer>
          </Grid>
        </Container>
      }
      {
        state.showImage && <ImageViewer
          src={[mediaUrl]}
          currentIndex={0}
          disableScroll={false}
          closeOnClickOutside={true}
          onClose={() => { updateState((draft) => { draft.showImage = false; }) }}
        />
      }
    </>
  )
}
