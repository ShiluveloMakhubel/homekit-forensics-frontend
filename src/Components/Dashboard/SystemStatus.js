import React, { useEffect, useState } from 'react';
import { Line } from 'react-chartjs-2';
import {
    Chart as ChartJS,
    CategoryScale,
    LinearScale,
    PointElement,
    LineElement,
    Title,
    Tooltip,
    Legend,
    TimeScale
} from 'chart.js';
import 'chartjs-adapter-date-fns'; // To adapt the time scale for Chart.js
import './SystemStatus.css';

// Register the required Chart.js components
ChartJS.register(
    CategoryScale,
    LinearScale,
    PointElement,
    LineElement,
    Title,
    Tooltip,
    Legend,
    TimeScale // Register TimeScale for timestamps
);

const SystemStatus = () => {
    const [status, setStatus] = useState(null);
    const [cpuData, setCpuData] = useState([]);
    const [ramData, setRamData] = useState([]);
    const [networkData, setNetworkData] = useState([]);
    const [timestamps, setTimestamps] = useState([]);
    
    const getStatusColor = (value, thresholds) => {
        if (value >= thresholds.high) return 'red'; // High usage
        if (value >= thresholds.medium) return 'orange'; // Medium usage
        return 'green'; // Low usage, good health
    };

    const maxDataPoints = 20; // Number of points to display in the graph

    useEffect(() => {
        const fetchData = () => {
            fetch('http://localhost:5000/api/system-status')
                .then(response => response.json())
                .then(data => {
                    setStatus(data);

                    const currentTime = new Date().toISOString();

                    // Update the timestamps
                    setTimestamps(prevTimes => {
                        const newTimes = [...prevTimes, currentTime];
                        return newTimes.length > maxDataPoints ? newTimes.slice(1) : newTimes;
                    });

                    // Update the CPU, RAM, and Network data arrays
                    setCpuData(prevData => {
                        const newData = [...prevData, data.cpu_status?.currentLoad || 0];
                        return newData.length > maxDataPoints ? newData.slice(1) : newData;
                    });

                    const usedRamPercent = (data.ram_status?.mem.used / data.ram_status?.mem.total) * 100;
                    setRamData(prevData => {
                        const newData = [...prevData, usedRamPercent || 0];
                        return newData.length > maxDataPoints ? newData.slice(1) : newData;
                    });

                    const totalNetworkUsage = (data.network_status?.net.rx_bytes + data.network_status?.net.tx_bytes) / (1024 * 1024); // in MB
                    setNetworkData(prevData => {
                        const newData = [...prevData, totalNetworkUsage || 0];
                        return newData.length > maxDataPoints ? newData.slice(1) : newData;
                    });
                })
                .catch(error => console.error('Error fetching system status:', error));
        };

        // Fetch data initially
        fetchData();

        // Set up an interval to fetch data every 5 seconds
        const intervalId = setInterval(fetchData, 5000);

        // Clean up the interval on component unmount
        return () => clearInterval(intervalId);
    }, []);

    const createChartData = (data) => ({
        labels: timestamps, // Use timestamps as the labels
        datasets: [{
            label: 'Usage',
            data,
            fill: false,
            backgroundColor: 'rgba(75,192,192,0.4)',
            borderColor: 'rgba(75,192,192,1)',
            borderWidth: 1,
        }]
    });

    const chartOptions = {
        scales: {
            x: {
                type: 'time', // Use time scale for x-axis
                time: {
                    unit: 'second', // Adjust this to 'minute', 'hour', etc., if needed
                    tooltipFormat: 'PPpp', // Format for tooltips
                    displayFormats: {
                        second: 'h:mm:ss a' // Display format for the x-axis labels
                    }
                },
                title: {
                    display: true,
                    text: 'Timestamp'
                }
            },
            y: {
                beginAtZero: true
            }
        }
    };

    const cpuLoad = status?.cpu_status?.currentLoad || 0;

    return (
        <div className="card system-status">
            <h2>System Status</h2>
            {status ? (
                <div>
                    <h3>CPU Usage</h3>
                    <p style={{ color: getStatusColor(cpuLoad, { high: 80, medium: 50 }) }}>
                        Current Load: {cpuLoad ? `${cpuLoad.toFixed(2)}%` : 'N/A'}
                    </p>

                    {/* Warning when CPU exceeds 85% */}
                    {cpuLoad > 85 && (
                        <div className="warning">
                            <p style={{ color: 'red', fontWeight: 'bold' }}>
                                Warning: Potential attack detected! CPU usage is critically high.
                            </p>
                        </div>
                    )}

                    <Line data={createChartData(cpuData)} options={chartOptions} />

                    <h3>RAM Usage</h3>
                    <p style={{ color: getStatusColor(status.ram_status?.mem.used / status.ram_status?.mem.total * 100, { high: 80, medium: 50 }) }}>
                        Used RAM: {status.ram_status?.mem.used ? `${(status.ram_status.mem.used / (1024 * 1024)).toFixed(2)} MB` : 'N/A'}</p>
                    <p style={{ color: getStatusColor(status.ram_status?.mem.free / status.ram_status?.mem.total * 100, { high: 80, medium: 50 }) }}>
                        Free RAM: {status.ram_status?.mem.free ? `${(status.ram_status.mem.free / (1024 * 1024)).toFixed(2)} MB` : 'N/A'}</p>

                    <Line data={createChartData(ramData)} options={chartOptions} />

                    <h3>Network Usage</h3>
                    <p>Transmitted Bytes: {status.network_status?.net?.rx_bytes ? `${(status.network_status.net.rx_bytes / (1024 * 1024)).toFixed(2)} MB` : 'N/A'}</p>
                    <p>Received Bytes: {status.network_status?.net?.tx_bytes ? `${(status.network_status.net.tx_bytes / (1024 * 1024)).toFixed(2)} MB` : 'N/A'}</p>

                    <Line data={createChartData(networkData)} options={chartOptions} />
                </div>
            ) : (
                <p>Loading...</p>
            )}
        </div>
    );
};

export default SystemStatus;
