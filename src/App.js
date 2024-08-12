import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Dashboard from './Components/Dashboard/Dashboard';
import DeviceDetails from './Components/DeviceDetails/DeviceDetails';
import Settings from './Components/Settings/Settings';
import Logs from './Components/Logs/Logs';
import Login from './Components/Login/Login'


function App() {
    return (
        <Router>
            <Routes>
                <Route path="/" element={<Login />} />
                <Route path="/dashboard" element={<Dashboard />} />
                <Route path="/device-details" element={<DeviceDetails />} />
                <Route path="/settings" element={<Settings />} />
                <Route path="/logs" element={<Logs />} />
            </Routes>
        </Router>
    );
}

export default App;
