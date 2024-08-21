import React, { useState, useEffect } from 'react';
import './DeviceOverview.css'; // Import the CSS file

const DeviceOverview = () => {
    const [devices, setDevices] = useState([]);

    useEffect(() => {
        const apiUrl = 'http://localhost:5000/api/devices'; // Ensure this URL is correct and CORS is configured

        fetch(apiUrl)
            .then(response => {
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                return response.json();
            })
            .then(data => setDevices(data))
            .catch(error => console.error('Error fetching data:', error));
    }, []); // This effect runs once on mount

    return (
        <div className="card device-overview">
            <h2>Device Overview</h2>
            {devices.length > 0 ? (
                <ul>
                    {devices.map(device => (
                        <li key={device.aid}>
                            <strong>{device.accessoryInformation.Name}</strong> - 
                            Manufacturer: {device.accessoryInformation.Manufacturer}, 
                            Model: {device.accessoryInformation.Model}, 
                            Firmware: {device.accessoryInformation['Firmware Revision']},
                            IP: {device.instance.ipAddress}, 
                            Port: {device.instance.port}
                        </li>
                    ))}
                </ul>
            ) : (
                <p>No devices found</p>
            )}
        </div>
    );
};

export default DeviceOverview;
