// src/components/DeviceDetails/DeviceInfo.js
import React, { useState, useEffect } from 'react';

const DeviceInfo = () => {
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
    }, []);
    return (
        <div >
            <h2>Device Overview</h2>
            {devices.length > 0 ? (
                <ul>
                    {devices.map((device, index) => (
                        <><li key={index}>
                            <strong>{device.serviceName}</strong> -

                           
                            
                            

                        </li>
                         <div>manufacturer: {device.manufacturer}</div>
                         <div>ipAddress: {device.ipAddress}</div>
                            
                            
                            <div>Device Name: {device.model}</div>
                            
                            
                              <div>port: {device.port}</div>
                            
                            
                            <div>firmware: {device.firmware}</div>
                            </>
                    ))}
                </ul>
            ) : (
                <p>No devices found</p>
            )}
        </div>
    );
};

export default DeviceInfo;
