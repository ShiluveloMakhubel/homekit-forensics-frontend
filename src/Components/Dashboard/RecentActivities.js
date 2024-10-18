import React, { useEffect, useState } from 'react';

const RecentActivities = () => {
  const [activities, setActivities] = useState([]);
  const [switchStatus, setSwitchStatus] = useState('Unknown'); // Initialize switch status
  const [motionStatus, setMotionStatus] = useState('Unknown'); // Initialize motion status
  const [timestamp, setTimestamp] = useState(null); // Initialize timestamp

  useEffect(() => {
    const fetchData = async () => {
      try {
        // Fetch recent activities
        const activitiesResponse = await fetch('http://localhost:5000/api/recent-activities');
        const activitiesData = await activitiesResponse.json();
        setActivities(activitiesData);

        // Fetch switch and motion status
        const switchResponse = await fetch('http://localhost:5000/api/switch/status');
        const switchData = await switchResponse.json();
        
        if (Array.isArray(switchData) && switchData.length > 0) {
          const latestSwitchStatus = switchData[switchData.length - 1]; // Get the latest status
          setSwitchStatus(latestSwitchStatus.status); // Set switch status
          setMotionStatus(latestSwitchStatus.motion_status); // Set motion sensor status
          setTimestamp(latestSwitchStatus.timestamp); // Set timestamp
        } else {
          setSwitchStatus('Unknown'); // Fallback in case no data is available
          setMotionStatus('Unknown');
          setTimestamp(null);
        }
      } catch (error) {
        console.error('Error fetching data:', error);
        setSwitchStatus('Unknown'); // Handle error
        setMotionStatus('Unknown');
        setTimestamp(null);
      }
    };

    fetchData(); // Fetch data on mount
    const interval = setInterval(fetchData, 10000); // Fetch data every 10 seconds

    return () => clearInterval(interval); // Cleanup interval on unmount
  }, []);

  return (
    <div className="card recent-activities">
      <h2>Recent Activities</h2>
      {activities.length === 0 ? (
        <p>No recent activities found.</p>
      ) : (
        <div className="activities-list">
          {activities.map((activity, index) => (
            <div key={index} className="activity-item">
              <h3>{activity.displayName}</h3>
              <p><strong>Plugin:</strong> {activity.plugin}</p>
              <p><strong>Platform:</strong> {activity.platform}</p>
              <p><strong>UUID:</strong> {activity.UUID}</p>
              
              <div className="services">
                <h4>Services:</h4>
                {activity.services.map((service, sIndex) => (
                  <div key={sIndex} className="service-item">
                    <p><strong>Service Name:</strong> {service.displayName || 'Unnamed Service'}</p>
                    <p><strong>UUID:</strong> {service.UUID}</p>
                    
                    <div className="characteristics">
                      <h5>Characteristics:</h5>
                      {service.characteristics.map((char, cIndex) => (
                        <div key={cIndex} className="characteristic-item">
                          <p><strong>Characteristic Name:</strong> {char.displayName}</p>
                          <p><strong>Value:</strong> {char.value.toString()}</p>
                        </div>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          ))}
        </div>
      )}
      <div className="sensor-status">
        <h2>Switch and Sensor Status</h2>
        <p><strong>Switch Status:</strong> {switchStatus}</p>
        <p><strong>Motion Sensor Status:</strong> {motionStatus}</p>
        <p><strong>Last Updated:</strong> {timestamp || 'N/A'}</p>
      </div>
    </div>
  );
};

export default RecentActivities;
