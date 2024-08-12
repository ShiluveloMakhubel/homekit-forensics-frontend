// src/components/Settings/UserSettings.js
import React from 'react';

const UserSettings = () => {
    return (
        <div>
            <h2>User Settings</h2>
            <form>
                <div className="form-group">
                    <label htmlFor="username">Username</label>
                    <input type="text" id="username" name="username" />
                </div>
                <div className="form-group">
                    <label htmlFor="email">Email</label>
                    <input type="email" id="email" name="email" />
                </div>
                <div className="form-group">
                    <label htmlFor="password">Password</label>
                    <input type="password" id="password" name="password" />
                </div>
                <button type="submit">Update</button>
            </form>
        </div>
    );
};

export default UserSettings;
