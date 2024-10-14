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
import 'chartjs-adapter-date-fns';
import './SystemStatus.css';

ChartJS.register(
    CategoryScale,
    LinearScale,
    PointElement,
    LineElement,
    Title,
    Tooltip,
    Legend,
    TimeScale
);

const SystemStatus = () => {
    const [status, setStatus] = useState(null);
    const [cpuData, setCpuData] = useState([]);
    const [ramData, setRamData] = useState([]);
    const [networkData, setNetworkData] = useState([]);
    const [timestamps, setTimestamps] = useState([]);

    const maxDataPoints = 20;

    const getStatusColor = (value, thresholds) => {
        if (value >= thresholds.high) return 'red';
        if (value >= thresholds.medium) return 'orange';
        return 'green';
    };

    const sendWarning = (message, metric, value) => {
        fetch('http://localhost:5000/api/warnings', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                message,
                metric,
                value
            })
        })
        .then(response => response.json())
        .then(result => {
            console.log('Warning sent successfully:', result);
        })
        .catch(error => {
            console.error('Error sending warning:', error);
        });
    };

    useEffect(() => {
        const fetchData = () => {
            fetch('http://localhost:5000/api/system-status')
                .then(response => response.json())
                .then(data => {
                    setStatus(data);

                    const currentTime = new Date().toISOString();
                    setTimestamps(prevTimes => {
                        const newTimes = [...prevTimes, currentTime];
                        return newTimes.length > maxDataPoints ? newTimes.slice(1) : newTimes;
                    });

                    // Update CPU data
                    const cpuLoad = data.cpu_status?.currentLoad || 0;
                    setCpuData(prevData => {
                        const newData = [...prevData, cpuLoad];
                        return newData.length > maxDataPoints ? newData.slice(1) : newData;
                    });

                    // Send warning if CPU exceeds threshold
                    if (cpuLoad > 80) {
                        sendWarning('CPU usage is critically high.', 'CPU', cpuLoad);
                    }

                    // Update RAM data
                    const usedRamPercent = (data.ram_status?.mem.used / data.ram_status?.mem.total) * 100;
                    setRamData(prevData => {
                        const newData = [...prevData, usedRamPercent];
                        return newData.length > maxDataPoints ? newData.slice(1) : newData;
                    });

                    // Send warning if RAM exceeds threshold
                    if (usedRamPercent > 80) {
                        sendWarning('RAM usage is critically high.', 'RAM', usedRamPercent);
                    }

                    // Update Network data
                    const totalNetworkUsage = (data.network_status?.net.rx_bytes + data.network_status?.net.tx_bytes) / (1024 * 1024); // in MB
                    setNetworkData(prevData => {
                        const newData = [...prevData, totalNetworkUsage];
                        return newData.length > maxDataPoints ? newData.slice(1) : newData;
                    });

                    // Send warning if network usage exceeds threshold (example threshold: 100 MB)
                    if (totalNetworkUsage > 150) {
                        sendWarning('Network usage is critically high.', 'Network', totalNetworkUsage);
                    }
                })
                .catch(error => console.error('Error fetching system status:', error));
        };

        fetchData();
        const intervalId = setInterval(fetchData, 5000);
        return () => clearInterval(intervalId);
    }, []);

    const createChartData = (data) => ({
        labels: timestamps,
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
                type: 'time',
                time: {
                    unit: 'second',
                    tooltipFormat: 'PPpp',
                    displayFormats: {
                        second: 'h:mm:ss a'
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

    return (
        <div className="card system-status">
            <h2>System Status</h2>
            {status ? (
                <div>
                    <h3>CPU Usage</h3>
                    <p style={{ color: getStatusColor(cpuData[cpuData.length - 1], { high: 80, medium: 50 }) }}>
                        Current Load: {cpuData[cpuData.length - 1] ? `${cpuData[cpuData.length - 1].toFixed(2)}%` : 'N/A'}
                    </p>
                    <Line data={createChartData(cpuData)} options={chartOptions} />

                    <h3>RAM Usage</h3>
                    <p style={{ color: getStatusColor(ramData[ramData.length - 1], { high: 80, medium: 50 }) }}>
                        Used RAM: {ramData[ramData.length - 1] ? `${ramData[ramData.length - 1].toFixed(2)}%` : 'N/A'}
                    </p>
                    <Line data={createChartData(ramData)} options={chartOptions} />

                    <h3>Network Usage</h3>
                    <p>
                        Total Network Usage: {networkData[networkData.length - 1] ? `${networkData[networkData.length - 1].toFixed(2)} MB` : 'N/A'}
                    </p>
                    <Line data={createChartData(networkData)} options={chartOptions} />
                </div>
            ) : (
                <p>Loading...</p>
            )}
        </div>
    );
};

export default SystemStatus;
