import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Dashboard from './Components/Dashboard/Dashboard';
import DeviceDetails from './Components/DeviceDetails/DeviceDetails';
import Settings from './Components/Settings/Settings';
import Logs from './Components/Logs/Logs';

function App() {
    return (
        <Router>
            <Routes>
                <Route path="/" element={<Dashboard />} />
                <Route path="/device-details" element={<DeviceDetails />} />
                <Route path="/settings" element={<Settings />} />
                <Route path="/logs" element={<Logs />} />
            </Routes>
        </Router>
    );
}

export default App;
