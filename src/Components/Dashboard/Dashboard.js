import React from 'react';
import DeviceOverview from './DeviceOverview';
import RecentActivities from './RecentActivities';
import SystemStatus from './SystemStatus';
import './Dashboard.css'; // Import the CSS file

const Dashboard = () => {
    return (
        <div className="dashboard-container">
            <DeviceOverview />
            <RecentActivities />
            <SystemStatus />
        </div>
    );
};

export default Dashboard;
