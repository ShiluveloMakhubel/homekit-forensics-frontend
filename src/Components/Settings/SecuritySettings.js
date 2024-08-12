// src/components/Settings/SecuritySettings.js
import React from 'react';

const SecuritySettings = () => {
    return (
        <div>
            <h2>Security Settings</h2>
            <form>
                <div className="form-group">
                    <label htmlFor="encryption">Encryption</label>
                    <select id="encryption" name="encryption">
                        <option value="aes">AES</option>
                        <option value="rsa">RSA</option>
                    </select>
                </div>
                <div className="form-group">
                    <label htmlFor="mfa">Multi-Factor Authentication</label>
                    <input type="checkbox" id="mfa" name="mfa" />
                </div>
                <button type="submit">Update Security Settings</button>
            </form>
        </div>
    );
};

export default SecuritySettings;
