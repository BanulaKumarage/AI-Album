import React from 'react'
import { Link, Outlet } from 'react-router-dom'
import MenuItem from '@mui/material/MenuItem';
import HomeIcon from '@mui/icons-material/Home';
import AppBar from '@mui/material/AppBar';
import Box from '@mui/material/Box';
import Toolbar from '@mui/material/Toolbar';
import Typography from '@mui/material/Typography';
import Menu from '@mui/material/Menu';
import Container from '@mui/material/Container';
import { useImmer } from 'use-immer';
import * as _ from 'lodash'


export type MainPageState = {
    anchorElNav?: any | null,
    anchorElUser?: any | null,
};

export default function NavWrapperPage() {
    const [state, updateState] = useImmer<MainPageState>({
        anchorElNav: null,
        anchorElUser: null,
    });
    const pages: any = [];

    const handleOpenNavMenu = (event: React.MouseEvent<HTMLElement>) => {
        updateState((draft) => {
            draft.anchorElNav = event.currentTarget;
        })
    };

    const handleCloseNavMenu = () => {
        updateState((draft) => {
            draft.anchorElNav = null;
        })
    };

    return (
        <>
            <AppBar position="static">
                <Container maxWidth="xl">
                    <Toolbar disableGutters>
                        <HomeIcon sx={{ display: { xs: 'none', md: 'flex' }, mr: 1 }} />
                        <Typography
                            variant="h6"
                            noWrap
                            component={Link}
                            to={'/'}
                            sx={{
                                mr: 2,
                                display: { xs: 'none', md: 'flex' },
                                fontFamily: 'monospace',
                                fontWeight: 700,
                                letterSpacing: '.3rem',
                                color: 'inherit',
                                textDecoration: 'none',
                            }}
                        >
                            AI-ALBUM
                        </Typography>
                        <Box sx={{ flexGrow: 1, display: { xs: 'flex', md: 'none' } }}>
                            <Menu
                                id="menu-appbar"
                                anchorEl={state.anchorElNav}
                                anchorOrigin={{
                                    vertical: 'bottom',
                                    horizontal: 'left',
                                }}
                                keepMounted
                                transformOrigin={{
                                    vertical: 'top',
                                    horizontal: 'left',
                                }}
                                open={Boolean(state.anchorElNav)}
                                onClose={handleCloseNavMenu}
                                sx={{
                                    display: { xs: 'block', md: 'none' },
                                }}
                            >
                                {_.map(pages, (page) => (
                                    <MenuItem key={page} onClick={handleCloseNavMenu}>
                                        <Typography textAlign="center">{page}</Typography>
                                    </MenuItem>
                                ))}
                            </Menu>
                        </Box>
                        <HomeIcon sx={{ display: { xs: 'flex', md: 'none' }, mr: 1 }} />
                        <Typography
                            variant="h5"
                            noWrap
                            component={Link}
                            to={'/'}
                            sx={{
                                mr: 2,
                                display: { xs: 'flex', md: 'none' },
                                flexGrow: 1,
                                fontFamily: 'monospace',
                                fontWeight: 700,
                                letterSpacing: '.3rem',
                                color: 'inherit',
                                textDecoration: 'none',
                            }}
                        >
                            AI-ALBUM
                        </Typography>
                    </Toolbar>
                </Container>
            </AppBar>
            <Outlet></Outlet>
        </>
    )
}
