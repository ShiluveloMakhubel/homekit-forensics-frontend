// src/components/DeviceDetails/DeviceDetails.js
import React, { useState } from 'react';
import DeviceInfo from './DeviceInfo';
import DeviceLogs from './DeviceLogs';
import DeviceConfig from './DeviceConfig';
import './DeviceDetails.css'; // For styling

const DeviceDetails = () => {
    const [activeTab, setActiveTab] = useState('info');

    return (
        <div className="device-details-container">
            <div className="tabs">
                <button
                    className={activeTab === 'info' ? 'active' : ''}
                    onClick={() => setActiveTab('info')}
                >
                    Device Info
                </button>
                <button
                    className={activeTab === 'logs' ? 'active' : ''}
                    onClick={() => setActiveTab('logs')}
                >
                    Device Logs
                </button>
                <button
                    className={activeTab === 'config' ? 'active' : ''}
                    onClick={() => setActiveTab('config')}
                >
                    Device Config
                </button>
            </div>
            <div className="tab-content">
                {activeTab === 'info' && <DeviceInfo />}
                {activeTab === 'logs' && <DeviceLogs />}
                {activeTab === 'config' && <DeviceConfig />}
            </div>
        </div>
    );
};

export default DeviceDetails;
