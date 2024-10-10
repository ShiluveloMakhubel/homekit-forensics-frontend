import React from 'react';
import { Link } from 'react-router-dom';
import DeviceOverview from './DeviceOverview';
import RecentActivities from './RecentActivities';
import SystemStatus from './SystemStatus';
import './Dashboard.css'; // Import the CSS file

const Dashboard = () => {
    return (
        <div className="dashboard-container">
            
            <SystemStatus />
            <RecentActivities />
            <ul className="dashboard-links">
            <DeviceOverview className="device-overview" />
                <li>
                    <Link to="/device-details" className="dashboard-link">
                        <span className="material-icons">settings_input_component</span>
                        Device Details
                    </Link>
                </li>
                <li>
                    <Link to="/settings" className="dashboard-link">
                        <span className="material-icons">settings</span>
                        Settings
                    </Link>
                </li>
                <li>
                    <Link to="/logs" className="dashboard-link">
                        <span className="material-icons">analytics</span>
                        Logs
                    </Link>
                </li>
               
            </ul>
           

        </div>
    );
};

export default Dashboard;
