import React from 'react'
import { useParams } from 'react-router-dom';
import MediaView from '../../components/MediaView';


export type FaceImagesPageProps = { text?: string };
export type FaceImagesPageState = {
  error: any,
  isLoaded: boolean,
  FaceImages: Array<any>,
};

export default function FaceImagesPage(props: FaceImagesPageProps) {
  const { faceGroup } = useParams();
  const mediaUrl = `${process.env.REACT_APP_API}/faces/${faceGroup}`


  return (
    <>
      <MediaView key={`Face-images-${faceGroup}`} url={mediaUrl}></MediaView>
    </>
  )
};
