import React from 'react'
import { useParams } from 'react-router-dom';
import * as _ from 'lodash'
import MediaView from '../../components/MediaView';


export type FacesPageState = {
  error: any,
  isLoaded: boolean,
  faces: Array<any>,
};

export default function FacesPage() {
  const mediaUrl = `${process.env.REACT_APP_API}/media`;

  return (
    <>
      <MediaView key={mediaUrl} url={mediaUrl}></MediaView>
    </>
  )
};
