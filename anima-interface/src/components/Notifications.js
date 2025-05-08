import React, { useContext } from 'react';
import { AnimaContext } from '../contexts/AnimaContext';
import { motion, AnimatePresence } from 'framer-motion';
import styled from '@emotion/styled';

// Icons
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import ErrorIcon from '@mui/icons-material/Error';
import InfoIcon from '@mui/icons-material/Info';
import WarningIcon from '@mui/icons-material/Warning';
import CloseIcon from '@mui/icons-material/Close';

const NotificationsContainer = styled.div`
  position: fixed;
  top: 20px;
  right: 20px;
  display: flex;
  flex-direction: column;
  gap: 10px;
  z-index: 1000;
  pointer-events: none;
`;

const NotificationItem = styled(motion.div)`
  background: rgba(10, 10, 26, 0.9);
  backdrop-filter: blur(10px);
  border-radius: var(--border-radius);
  border-left: 4px solid ${props => getNotificationColor(props.type)};
  padding: 1rem;
  min-width: 300px;
  max-width: 400px;
  box-shadow: var(--shadow-medium);
  display: flex;
  pointer-events: auto;
  overflow: hidden;
  position: relative;
  
  &::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: linear-gradient(90deg, ${props => getNotificationColor(props.type) + '20'}, transparent);
    opacity: 0.1;
    pointer-events: none;
  }
`;

const NotificationIcon = styled.div`
  margin-right: 1rem;
  display: flex;
  align-items: flex-start;
  
  svg {
    font-size: 1.5rem;
    color: ${props => getNotificationColor(props.type)};
  }
`;

const NotificationContent = styled.div`
  flex: 1;
`;

const NotificationTitle = styled.div`
  font-weight: 600;
  margin-bottom: 0.25rem;
  color: var(--primary-light);
`;

const NotificationMessage = styled.div`
  font-size: 0.9rem;
  color: rgba(248, 249, 250, 0.8);
`;

const NotificationClose = styled.button`
  background: none;
  border: none;
  color: rgba(248, 249, 250, 0.5);
  cursor: pointer;
  padding: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-left: 0.5rem;
  
  &:hover {
    color: var(--primary-light);
  }
  
  svg {
    font-size: 1.2rem;
  }
`;

const NotificationProgress = styled(motion.div)`
  position: absolute;
  bottom: 0;
  left: 0;
  height: 3px;
  background: ${props => getNotificationColor(props.type)};
`;

// Helper function to get notification color based on type
function getNotificationColor(type) {
  switch (type) {
    case 'success':
      return '#2ecc71';
    case 'error':
      return '#e74c3c';
    case 'warning':
      return '#f39c12';
    case 'info':
    default:
      return '#3498db';
  }
}

// Helper function to get notification icon based on type
function getNotificationIcon(type) {
  switch (type) {
    case 'success':
      return <CheckCircleIcon />;
    case 'error':
      return <ErrorIcon />;
    case 'warning':
      return <WarningIcon />;
    case 'info':
    default:
      return <InfoIcon />;
  }
}

const Notifications = () => {
  const { notifications, addNotification } = useContext(AnimaContext);
  
  // Remove notification
  const removeNotification = (id) => {
    // In a real implementation, this would remove the notification from the context
    console.log(`Removing notification ${id}`);
  };
  
  // Animation variants
  const containerVariants = {
    hidden: { opacity: 0, x: 100 },
    visible: { 
      opacity: 1, 
      x: 0,
      transition: { 
        type: "spring", 
        damping: 25, 
        stiffness: 500 
      }
    },
    exit: { 
      opacity: 0,
      x: 100,
      transition: { duration: 0.3 }
    }
  };
  
  return (
    <NotificationsContainer>
      <AnimatePresence>
        {notifications.map((notification) => (
          <NotificationItem
            key={notification.id}
            type={notification.type}
            initial="hidden"
            animate="visible"
            exit="exit"
            variants={containerVariants}
            layout
          >
            <NotificationIcon type={notification.type}>
              {getNotificationIcon(notification.type)}
            </NotificationIcon>
            
            <NotificationContent>
              <NotificationTitle>{notification.title}</NotificationTitle>
              <NotificationMessage>{notification.message}</NotificationMessage>
            </NotificationContent>
            
            <NotificationClose onClick={() => removeNotification(notification.id)}>
              <CloseIcon />
            </NotificationClose>
            
            <NotificationProgress
              type={notification.type}
              initial={{ width: '100%' }}
              animate={{ width: '0%' }}
              transition={{ duration: 5, ease: 'linear' }}
            />
          </NotificationItem>
        ))}
      </AnimatePresence>
    </NotificationsContainer>
  );
};

export default Notifications;
