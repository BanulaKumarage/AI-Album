import React from 'react'
import { useParams } from 'react-router-dom';
import * as _ from 'lodash'
import MediaView from '../../components/MediaView';


export type AlbumsPageProps = { text?: string };
export type AlbumsPageState = {
  error: any,
  isLoaded: boolean,
  albums: Array<any>,
};

export default function AlbumMediaPage(props: AlbumsPageProps) {
  const { album } = useParams();
  const mediaUrl = _.isEqual(album, 'all-media') ? `${process.env.REACT_APP_API}/media` : `${process.env.REACT_APP_API}/albums/${album}/media`


  return (
    <>
      <MediaView key={`album-media-${album}`} url={mediaUrl}></MediaView>
    </>
  )
};
