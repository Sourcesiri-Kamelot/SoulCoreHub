import React, { useState, useContext, useEffect } from 'react';
import { AnimaContext } from './contexts/AnimaContext';
import { ThemeContext } from './contexts/ThemeContext';
import { useHuggingFace } from './contexts/HuggingFaceContext';
import styled from '@emotion/styled';
import { motion } from 'framer-motion';

// Components
import LoadingScreen from './components/LoadingScreen';
import EmotiveAura from './components/EmotiveAura';
import MemoryLogsPanel from './components/MemoryLogsPanel';
import AgentDashboard from './components/AgentDashboard';
import GPTControlPanel from './components/GPTControlPanel';
import MCPStatusModule from './components/MCPStatusModule';
import FileInteractionSection from './components/FileInteractionSection';
import Notifications from './components/Notifications';
import CommandInput from './components/CommandInput';

// Icons
import MenuIcon from '@mui/icons-material/Menu';
import CloseIcon from '@mui/icons-material/Close';
import DashboardIcon from '@mui/icons-material/Dashboard';
import MemoryIcon from '@mui/icons-material/Memory';
import SettingsIcon from '@mui/icons-material/Settings';
import PersonIcon from '@mui/icons-material/Person';
import LogoutIcon from '@mui/icons-material/Logout';
import BrightnessMediumIcon from '@mui/icons-material/BrightnessMedium';
import PaletteIcon from '@mui/icons-material/Palette';

const AppContainer = styled.div`
  display: flex;
  height: 100vh;
  overflow: hidden;
  position: relative;
`;

const Sidebar = styled(motion.div)`
  width: ${props => props.expanded ? '240px' : '70px'};
  background: rgba(10, 10, 26, 0.8);
  backdrop-filter: blur(10px);
  border-right: 1px solid rgba(106, 17, 203, 0.3);
  padding: 1.5rem 0;
  display: flex;
  flex-direction: column;
  transition: width var(--transition-speed);
  z-index: 10;
`;

const SidebarHeader = styled.div`
  display: flex;
  align-items: center;
  justify-content: ${props => props.expanded ? 'space-between' : 'center'};
  padding: 0 1.5rem;
  margin-bottom: 2rem;
`;

const Logo = styled.div`
  font-family: var(--font-display);
  font-size: ${props => props.expanded ? '1.5rem' : '1.2rem'};
  font-weight: 700;
  background: linear-gradient(135deg, var(--accent-1), var(--accent-2));
  -webkit-background-clip: text;
  background-clip: text;
  color: transparent;
  text-shadow: var(--glow-soft);
`;

const MenuButton = styled.button`
  background: none;
  border: none;
  color: var(--primary-light);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  
  &:hover {
    color: var(--accent-1);
  }
  
  svg {
    font-size: 1.5rem;
  }
`;

const NavItems = styled.div`
  display: flex;
  flex-direction: column;
  flex: 1;
`;

const NavItem = styled.div`
  display: flex;
  align-items: center;
  padding: 0.75rem 1.5rem;
  cursor: pointer;
  transition: all var(--transition-speed);
  position: relative;
  
  &:hover {
    background: rgba(106, 17, 203, 0.1);
  }
  
  ${props => props.active && `
    background: rgba(106, 17, 203, 0.2);
    
    &::before {
      content: '';
      position: absolute;
      left: 0;
      top: 0;
      height: 100%;
      width: 4px;
      background: linear-gradient(to bottom, var(--accent-1), var(--accent-2));
    }
  `}
`;

const NavIcon = styled.div`
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: ${props => props.expanded ? '1rem' : '0'};
  
  svg {
    font-size: 1.5rem;
    color: ${props => props.active ? 'var(--accent-1)' : 'var(--primary-light)'};
  }
`;

const NavText = styled.div`
  font-size: 1rem;
  color: var(--primary-light);
  display: ${props => props.expanded ? 'block' : 'none'};
  white-space: nowrap;
`;

const SidebarFooter = styled.div`
  padding: 1.5rem;
  border-top: 1px solid rgba(106, 17, 203, 0.3);
  display: flex;
  flex-direction: column;
  gap: 1rem;
`;

const FooterButton = styled.button`
  background: ${props => props.active ? 'rgba(106, 17, 203, 0.2)' : 'none'};
  border: none;
  border-radius: var(--border-radius);
  color: var(--primary-light);
  cursor: pointer;
  display: flex;
  align-items: center;
  padding: 0.5rem;
  transition: all var(--transition-speed);
  
  &:hover {
    background: rgba(106, 17, 203, 0.1);
  }
  
  svg {
    font-size: 1.5rem;
    margin-right: ${props => props.expanded ? '0.5rem' : '0'};
  }
`;

const FooterText = styled.span`
  display: ${props => props.expanded ? 'block' : 'none'};
`;

const MainContent = styled.div`
  flex: 1;
  padding: 1.5rem;
  overflow-y: auto;
  position: relative;
  
  &::-webkit-scrollbar {
    width: 8px;
  }
  
  &::-webkit-scrollbar-track {
    background: rgba(10, 10, 26, 0.3);
  }
  
  &::-webkit-scrollbar-thumb {
    background: rgba(106, 17, 203, 0.5);
    border-radius: 4px;
  }
`;

const Header = styled.header`
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
`;

const PageTitle = styled.h1`
  font-family: var(--font-display);
  font-size: 2rem;
  font-weight: 600;
  margin: 0;
  color: var(--primary-light);
`;

const EmotionDisplay = styled.div`
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  background: rgba(10, 10, 26, 0.5);
  border-radius: var(--border-radius);
  border: 1px solid rgba(106, 17, 203, 0.2);
`;

const EmotionIndicator = styled.div`
  width: 12px;
  height: 12px;
  border-radius: 50%;
  background: ${props => props.color || 'var(--accent-1)'};
  box-shadow: 0 0 10px ${props => props.color || 'var(--accent-1)'};
`;

const EmotionText = styled.div`
  font-size: 0.9rem;
  color: var(--primary-light);
`;

const Grid = styled.div`
  display: grid;
  grid-template-columns: repeat(12, 1fr);
  grid-template-rows: repeat(2, 1fr);
  gap: 1.5rem;
  height: calc(100vh - 6rem);
`;

const GridItem = styled(motion.div)`
  grid-column: ${props => props.col};
  grid-row: ${props => props.row};
  min-height: 0;
`;

const App = () => {
  const { isLoading, emotionalState, emotionProfiles } = useContext(AnimaContext);
  const { darkMode, toggleDarkMode } = useContext(ThemeContext);
  const [sidebarExpanded, setSidebarExpanded] = useState(true);
  const [activeNavItem, setActiveNavItem] = useState('dashboard');
  const [loadingComplete, setLoadingComplete] = useState(false);
  
  // Handle loading complete
  const handleLoadingComplete = () => {
    setLoadingComplete(true);
  };
  
  // Get current emotion profile
  const emotion = emotionProfiles[emotionalState] || emotionProfiles.neutral;
  
  // Animation variants
  const itemVariants = {
    hidden: { opacity: 0, y: 20 },
    visible: { 
      opacity: 1, 
      y: 0,
      transition: { duration: 0.5 }
    }
  };
  
  // Show loading screen if loading
  if (isLoading && !loadingComplete) {
    return <LoadingScreen onLoadingComplete={handleLoadingComplete} />;
  }
  
  return (
    <AppContainer>
      <EmotiveAura />
      
      <Sidebar expanded={sidebarExpanded}>
        <SidebarHeader expanded={sidebarExpanded}>
          <Logo expanded={sidebarExpanded}>
            {sidebarExpanded ? 'ANIMA' : 'A'}
          </Logo>
          <MenuButton onClick={() => setSidebarExpanded(!sidebarExpanded)}>
            {sidebarExpanded ? <CloseIcon /> : <MenuIcon />}
          </MenuButton>
        </SidebarHeader>
        
        <NavItems>
          <NavItem 
            active={activeNavItem === 'dashboard'} 
            onClick={() => setActiveNavItem('dashboard')}
          >
            <NavIcon active={activeNavItem === 'dashboard'} expanded={sidebarExpanded}>
              <DashboardIcon />
            </NavIcon>
            <NavText expanded={sidebarExpanded}>Dashboard</NavText>
          </NavItem>
          
          <NavItem 
            active={activeNavItem === 'memory'} 
            onClick={() => setActiveNavItem('memory')}
          >
            <NavIcon active={activeNavItem === 'memory'} expanded={sidebarExpanded}>
              <MemoryIcon />
            </NavIcon>
            <NavText expanded={sidebarExpanded}>Memory</NavText>
          </NavItem>
          
          <NavItem 
            active={activeNavItem === 'settings'} 
            onClick={() => setActiveNavItem('settings')}
          >
            <NavIcon active={activeNavItem === 'settings'} expanded={sidebarExpanded}>
              <SettingsIcon />
            </NavIcon>
            <NavText expanded={sidebarExpanded}>Settings</NavText>
          </NavItem>
          
          <NavItem 
            active={activeNavItem === 'profile'} 
            onClick={() => setActiveNavItem('profile')}
          >
            <NavIcon active={activeNavItem === 'profile'} expanded={sidebarExpanded}>
              <PersonIcon />
            </NavIcon>
            <NavText expanded={sidebarExpanded}>Profile</NavText>
          </NavItem>
        </NavItems>
        
        <SidebarFooter>
          <FooterButton onClick={toggleDarkMode} expanded={sidebarExpanded}>
            <BrightnessMediumIcon />
            <FooterText expanded={sidebarExpanded}>
              {darkMode ? 'Light Mode' : 'Dark Mode'}
            </FooterText>
          </FooterButton>
          
          <FooterButton expanded={sidebarExpanded}>
            <PaletteIcon />
            <FooterText expanded={sidebarExpanded}>Theme</FooterText>
          </FooterButton>
          
          <FooterButton expanded={sidebarExpanded}>
            <LogoutIcon />
            <FooterText expanded={sidebarExpanded}>Logout</FooterText>
          </FooterButton>
        </SidebarFooter>
      </Sidebar>
      
      <MainContent>
        <Header>
          <PageTitle>Command Center</PageTitle>
          <EmotionDisplay>
            <EmotionIndicator color={emotion.color} />
            <EmotionText>{emotionalState}</EmotionText>
          </EmotionDisplay>
        </Header>
        
        <Grid>
          <GridItem 
            col="span 8" 
            row="1"
            variants={itemVariants}
            initial="hidden"
            animate="visible"
          >
            <AgentDashboard />
          </GridItem>
          
          <GridItem 
            col="span 4" 
            row="1"
            variants={itemVariants}
            initial="hidden"
            animate="visible"
            transition={{ delay: 0.1 }}
          >
            <GPTControlPanel />
          </GridItem>
          
          <GridItem 
            col="span 4" 
            row="2"
            variants={itemVariants}
            initial="hidden"
            animate="visible"
            transition={{ delay: 0.2 }}
          >
            <MemoryLogsPanel />
          </GridItem>
          
          <GridItem 
            col="span 4" 
            row="2"
            variants={itemVariants}
            initial="hidden"
            animate="visible"
            transition={{ delay: 0.3 }}
          >
            <FileInteractionSection />
          </GridItem>
          
          <GridItem 
            col="span 4" 
            row="2"
            variants={itemVariants}
            initial="hidden"
            animate="visible"
            transition={{ delay: 0.4 }}
          >
            <MCPStatusModule />
          </GridItem>
        </Grid>
      </MainContent>
      
      <Notifications />
      <CommandInput />
    </AppContainer>
  );
};

export default App;
