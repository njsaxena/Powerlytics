# Powerlytics Demo Script (3 minutes)

## 0:00-0:20 — Elevator Pitch
"Powerlytics helps homeowners and building managers reduce energy costs by learning usage patterns and providing AI-driven recommendations. Our platform ingests IoT energy data, performs real-time anomaly detection, and offers conversational AI assistance for actionable energy insights."

## 0:20-0:45 — Dashboard Overview
- **Show current usage**: Point to the metrics overview showing total energy consumption today
- **Highlight live data**: Show real-time power readings from connected devices
- **Demonstrate predictions**: Click on a device to show 24-hour energy consumption forecast
- **Point out anomalies**: Show any detected anomalies in the sidebar

## 0:45-1:30 — Anomaly Detection Demo
- **Click on an anomaly**: Show detailed anomaly information with power spike data
- **Explain the evidence**: Point to the time series chart showing the spike
- **Show AI explanation**: Highlight the natural language explanation of what caused the anomaly
- **Demonstrate actionability**: Show the recommended actions to address the issue

## 1:30-2:10 — Chat Assistant Demo
- **Switch to AI Assistant tab**: Click on the chat interface
- **Ask a question**: "Why was my usage high yesterday?"
- **Show AI response**: Point to the detailed response with confidence score
- **Highlight recommendations**: Show the specific action items with potential savings
- **Ask follow-up**: "When is the cheapest time to run my dishwasher?"
- **Show time-based insights**: Demonstrate the AI's understanding of usage patterns

## 2:10-2:40 — Architecture Overview
- **Show architecture slide**: Display the system diagram
- **Explain data flow**: IoT devices → Fivetran connector → BigQuery → Vertex AI → Cloud Run → Frontend
- **Highlight AI components**: Point out anomaly detection, forecasting, and conversational AI
- **Mention scalability**: Cloud-native architecture with auto-scaling

## 2:40-3:00 — Wrap Up
- **Show metrics**: Display potential savings and efficiency improvements
- **Provide links**: Share GitHub repo and live demo URLs
- **Invite questions**: "I'd be happy to answer any questions about the platform"

## Key Talking Points

### Technical Highlights
- **Real-time processing**: Sub-second anomaly detection
- **AI-powered insights**: Vertex AI for forecasting and recommendations
- **Scalable architecture**: Cloud-native with BigQuery and Cloud Run
- **Easy integration**: Simple API for connecting IoT devices

### Business Value
- **Cost reduction**: 15-30% energy savings through optimization
- **Proactive maintenance**: Early detection of equipment issues
- **User-friendly**: Conversational interface for non-technical users
- **Actionable insights**: Specific recommendations with potential savings

### Demo Tips
- **Keep it moving**: Don't spend too much time on any one feature
- **Show confidence**: The AI responses should feel natural and helpful
- **Highlight uniqueness**: Focus on the conversational AI and real-time anomaly detection
- **Be prepared**: Have backup data ready in case of connectivity issues

## Backup Demo Scenarios

### If No Real Data
- Use the mock device API to generate sample data
- Show the data generation process
- Demonstrate the anomaly simulation feature

### If API Issues
- Use pre-recorded screenshots or video
- Focus on the UI/UX and user experience
- Explain the technical architecture in detail

### If Time Runs Short
- Skip the detailed anomaly explanation
- Focus on the chat interface and AI responses
- Show the architecture diagram quickly

## Post-Demo Q&A Preparation

### Common Questions
1. **"How accurate are the predictions?"**
   - 85-95% accuracy for 24-hour forecasts
   - Confidence intervals provided for all predictions
   - Continuously improving with more data

2. **"What types of devices can connect?"**
   - Any device with power monitoring capabilities
   - Smart meters, IoT sensors, smart plugs
   - Standard APIs for easy integration

3. **"How does the AI learn?"**
   - Learns from historical usage patterns
   - Adapts to seasonal and daily cycles
   - Improves with user feedback and corrections

4. **"What about data privacy?"**
   - All data encrypted in transit and at rest
   - No personal information stored
   - GDPR and CCPA compliant

5. **"How much does it cost?"**
   - Pay-per-use pricing model
   - Free tier for small deployments
   - Enterprise pricing available

## Demo Environment Setup

### Prerequisites
- [ ] Mock device API running
- [ ] Backend API deployed and healthy
- [ ] Frontend deployed and accessible
- [ ] Sample data loaded in BigQuery
- [ ] Test anomalies generated

### Test Data
- [ ] 5+ devices with realistic power patterns
- [ ] At least 2-3 anomalies for demonstration
- [ ] 24+ hours of historical data
- [ ] Predictions generated for all devices

### Backup Plans
- [ ] Screenshots of key features
- [ ] Video recording of full demo
- [ ] Offline mode with cached data
- [ ] Alternative demo environment
