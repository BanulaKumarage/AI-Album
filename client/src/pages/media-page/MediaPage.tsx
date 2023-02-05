import React, { useEffect } from 'react'
import ImageViewer from 'react-simple-image-viewer';
import ArrowBackIcon from '@mui/icons-material/ArrowBack';
import { useImmer } from 'use-immer';
import { useNavigate, useParams } from 'react-router-dom';
import * as _ from 'lodash'
import { Button, Container, Grid, Paper, Table, TableBody, TableCell, TableContainer, TableHead, TableRow } from '@mui/material';
import { fetchMediaById } from '../../api-calls/media';
import { result } from 'lodash';

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
  const rows = [
    createData('Frozen yoghurt', 159, 6.0, 24, 4.0),
    createData('Ice cream sandwich', 237, 9.0, 37, 4.3),
    createData('Eclair', 262, 16.0, 24, 6.0),
    createData('Cupcake', 305, 3.7, 67, 4.3),
    createData('Gingerbread', 356, 16.0, 49, 3.9),
  ];

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
        <Grid container item xs={1} p={1} m={1}>
          <Button variant="outlined" color='inherit' onClick={() => navigate('../')}>
            <ArrowBackIcon />
          </Button>
        </Grid>
        <Grid container item xs={12} p={1} m={1}>
          <Paper>
            <img onClick={() => updateState((draft) => { draft.showImage = true; })} src={mediaUrl} alt="Media" style={{ maxHeight: '100%', maxWidth: '100%', display: 'block', margin: '10px auto' }} />
          </Paper>
        </Grid>
      </Container>
      {
        state.isLoaded &&
        <Container>
          <Grid container item xs={12} m={1} p={1}>
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
                  <TableRow
                    key={`${media}-caption`}
                    sx={{ '&:last-child td, &:last-child th': { border: 0 } }}
                  >
                    <TableCell component="th" scope="row">
                      Generated Caption
                    </TableCell>
                    <TableCell align="left">
                      {_.map(state.metadata.caption.split('.'), (sentence, index) => {
                        return (
                          <div key={`sentence-${index}`}>
                            {_.capitalize(sentence)}
                          </div>
                        )
                      })}
                    </TableCell>
                  </TableRow>
                </TableBody>
              </Table>
            </TableContainer>
          </Grid>
        </Container>
      }
      {state.showImage && <ImageViewer
        src={[mediaUrl]}
        currentIndex={0}
        disableScroll={false}
        closeOnClickOutside={true}
        onClose={() => { updateState((draft) => { draft.showImage = false; }) }}
      />}
    </>
  )
}
