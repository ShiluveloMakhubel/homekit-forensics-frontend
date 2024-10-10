import React, { useEffect, useState } from 'react';

const RecentActivities = () => {
  const [activities, setActivities] = useState([]);

  useEffect(() => {
    // Simulate fetching data from the backend
    const fetchData = async () => {
      const response = await fetch('http://localhost:5000/api/recent-activities');
      const data = await response.json();
      setActivities(data);
    };
    
    fetchData();
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
    </div>
  );
};

export default RecentActivities;
