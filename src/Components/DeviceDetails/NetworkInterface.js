import React, { useState, useEffect } from 'react';

const NetWorkInterface = () => {
    const [devices, setDevices] = useState([]);

    useEffect(() => {
        const apiUrl = 'http://localhost:5000/api/network-interfaces'; // Ensure this URL is correct and CORS is configured

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
        <div>
            <h2>Network Interfaces</h2>
            {devices.length > 0 ? (
                <ul>
                    {devices.map((device, index) => (
                        <li key={index}>
                            <h3>Interface {index + 1}</h3>
                            <p><strong>ID:</strong> {device._id}</p>
                            <p><strong>Interface:</strong> {device.iface}</p>
                            <p><strong>Interface Name:</strong> {device.ifaceName}</p>
                            <p><strong>MAC Address:</strong> {device.mac}</p>
                            <p><strong>IPv4 Address:</strong> {device.ip4}</p>
                            <p><strong>IPv4 Subnet:</strong> {device.ip4subnet}</p>
                            <p><strong>IPv6 Address:</strong> {device.ip6}</p>
                            <p><strong>IPv6 Subnet:</strong> {device.ip6subnet}</p>
                            <p><strong>DNS Suffix:</strong> {device.dnsSuffix || "N/A"}</p>
                            <p><strong>Operational State:</strong> {device.operstate}</p>
                            <p><strong>Connection Type:</strong> {device.type}</p>
                            <p><strong>Speed:</strong> {device.speed} Mbps</p>
                            <p><strong>DHCP:</strong> {device.dhcp ? "Enabled" : "Disabled"}</p>
                            <p><strong>Default Interface:</strong> {device.default ? "Yes" : "No"}</p>
                            <p><strong>Virtual Interface:</strong> {device.virtual ? "Yes" : "No"}</p>
                        </li>
                    ))}
                </ul>
            ) : (
                <p>No network interfaces found.</p>
            )}
        </div>
    );
};

export default NetWorkInterface;
