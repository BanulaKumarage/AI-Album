import React from 'react'
import ImageViewer from 'react-simple-image-viewer';
import { useImmer } from 'use-immer';
import { useParams } from 'react-router-dom';
import * as _ from 'lodash'

export type MediaPageProps = { 
  showImage: boolean;
};

export default function MediaPage() {
  const { media } = useParams();
  const [state, updateState] = useImmer<MediaPageProps>({
    showImage: false
  });

  const mediaUrl = `${process.env.REACT_APP_API}/fullsize/${media}`

  return (
    <ImageViewer
      src={[mediaUrl]}
      currentIndex={0}
      disableScroll={false}
      closeOnClickOutside={true}
      onClose={() => { updateState((draft) => { draft.showImage = false; }) }}
    />
  )
}
