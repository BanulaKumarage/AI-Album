import React from 'react'
import FacesView from '../../components/FacesView';


export type FacesPageState = {
  error: any,
  isLoaded: boolean,
  faces: Array<any>,
};

export default function FacesPage() {
  return (
    <>
      <FacesView key={'faces-view'}></FacesView>
    </>
  )
};
