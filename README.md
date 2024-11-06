# SecureCollect Research Project

This project investigates SecureCollect, a digital forensic readiness prototype, with a focus on enhancing digital forensic capabilities in IoT environments, particularly within Apple's HomeKit ecosystem. Our goal is to create a reliable, scalable solution for forensic data collection and analysis that aligns with ISO/IEC 27043 standards for digital readiness.

## Project Overview
SecureCollect serves as an intermediary between IoT devices, Homebridge, and the Home App, allowing for structured and secure data collection. The project explores IoT forensic readiness through:
- Identification and extraction of critical data from IoT devices.
- Ensuring data security during transfer and storage.
- Development of forensic logging and reporting capabilities.

## Project Goals
1. **Digital Forensic Readiness**: Enhance digital forensic capabilities for IoT, ensuring data availability and integrity.
2. **IoT Forensics**: Address unique forensic challenges posed by IoT devices.
3. **Security Compliance**: Align with ISO/IEC 27043 standards.

## Technologies and Tools
- **Programming Languages**: Python, JavaScript (React for frontend)
- **Databases**: MongoDB for secure data storage
- **Infrastructure**: Homebridge integration with Apple HomeKit
- **SSL/TLS**: Secure data transfer using SSL keys, generated with OpenSSL
- **ISO Standards**: ISO/IEC 27043 guidelines for forensic readiness

## Key Features
- **Data Collection and Storage**: Aggregates data from various IoT devices, securely stored in MongoDB.
- **Forensic Analysis**: Enables structured analysis and monitoring through logging and reporting mechanisms.
- **User Interaction**: Provides insights via frontend visualizations and flow diagrams.
- **Security**: SSL encryption and user authentication ensure compliance with security standards.

## Files and Directory Structure
- **Diagrams**: Includes flow diagrams for SecureCollect interactions.
- **Figures**: Readiness processes and system layouts, bordered for better visualization.
- **SSL Keys**: Generated using OpenSSL for secure data transfer.

## Future Work
1. **Enhanced Forensic Analysis**: Improving analysis capabilities to streamline the identification of anomalies.
2. **User Interface**: Developing a user-friendly interface for better interaction with the collected data.
3. **Broader Integration**: Testing compatibility with other IoT ecosystems.

## Getting Started
1. **SSL Key Generation**:
    ```bash
    openssl genpkey -algorithm RSA -out private.key
    openssl req -new -key private.key -out request.csr
    openssl x509 -req -days 365 -in request.csr -signkey private.key -out certificate.crt
    ```
2. **Run MongoDB**: Start the database server for secure data storage.
3. **Start Homebridge**: Ensure the Homebridge server is running to connect IoT devices.
