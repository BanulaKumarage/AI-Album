import { Grid } from '@mui/material'
import React from 'react'
import { Outlet } from 'react-router-dom'
import SideBar from '../../components/SideBar'

export default function SideBarWrapperPage() {
    return (
        <Grid container spacing={1} padding={1} textAlign={'center'}>
            <Grid item xs={12} md={4}>
                <SideBar></SideBar>
            </Grid>
            <Grid item xs={12} md={8}>
                <Outlet></Outlet>
            </Grid>
        </Grid>
    )
}
