// src/components/Settings/Settings.js
import React from 'react';
import UserSettings from './UserSettings';
import SecuritySettings from './SecuritySettings';
import AppPreferences from './AppPreferences';
import './Settings.css'; // For styling

const Settings = () => {
    return (
        <div className="settings-container">
            <h1>Settings</h1>
            <div className="settings-panel">
                <UserSettings />
            </div>
            <div className="settings-panel">
                <SecuritySettings />
            </div>
            <div className="settings-panel">
                <AppPreferences />
            </div>
        </div>
    );
};

export default Settings;
