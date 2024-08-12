// src/components/Settings/AppPreferences.js
import React from 'react';

const AppPreferences = () => {
    return (
        <div>
            <h2>App Preferences</h2>
            <form>
                <div className="form-group">
                    <label htmlFor="theme">Theme</label>
                    <select id="theme" name="theme">
                        <option value="light">Light</option>
                        <option value="dark">Dark</option>
                    </select>
                </div>
                <div className="form-group">
                    <label htmlFor="notifications">Notifications</label>
                    <input type="checkbox" id="notifications" name="notifications" />
                </div>
                <button type="submit">Update Preferences</button>
            </form>
        </div>
    );
};

export default AppPreferences;
