# WhatsApp MCP Dashboard

A comprehensive dashboard application that integrates with WhatsApp MCP Server to provide AI-powered message management, automated classification, and intelligent responses for WhatsApp Business communications.

## 🚀 Features

### Core Functionality
- **Real-time Message Management**: Monitor and manage incoming/outgoing WhatsApp messages
- **AI-Powered Classification**: Automatically categorize messages using OpenAI/Anthropic AI models
- **Automated Responses**: Create and manage intelligent auto-response rules
- **Broadcast Messaging**: Send messages to multiple contacts simultaneously
- **Contact Management**: Organize and track your WhatsApp contacts
- **Analytics & Insights**: Detailed analytics on message patterns and response rates

### AI & Automation
- **Smart Message Classification**: Support, Sales, Complaints, Inquiries, etc.
- **Sentiment Analysis**: Understand customer emotions and respond appropriately
- **Template-based Responses**: Customizable response templates with variable substitution
- **AI-Generated Responses**: Dynamic responses using Claude/GPT models
- **Rule-based Auto-responses**: Set up automated responses based on message categories

### Dashboard Features
- **Real-time Statistics**: Live dashboard with key metrics
- **Message History**: Complete conversation history with search and filtering
- **Visual Analytics**: Charts and graphs for message patterns
- **WhatsApp Status Monitoring**: Real-time connection status
- **Responsive Design**: Works on desktop, tablet, and mobile devices

## 🛠️ Technology Stack

### Backend
- **FastAPI**: Modern Python web framework
- **SQLAlchemy**: SQL toolkit and ORM
- **SQLite/PostgreSQL**: Database options
- **OpenAI/Anthropic**: AI model integration
- **WebSockets**: Real-time communication
- **Pydantic**: Data validation

### Frontend
- **React 18**: Modern React with hooks
- **Material-UI (MUI)**: Beautiful, responsive UI components
- **React Query**: Data fetching and state management
- **Recharts**: Interactive charts and analytics
- **React Router**: Client-side routing
- **Axios**: HTTP client

### Integration
- **WhatsApp MCP Server**: Interface with WhatsApp Web
- **Model Context Protocol (MCP)**: AI model integration standard

## 📋 Prerequisites

Before setting up the WhatsApp MCP Dashboard, ensure you have:

1. **Node.js** (v16 or higher)
2. **Python** (3.8 or higher)
3. **Git** for version control
4. **WhatsApp MCP Server** (setup instructions below)
5. **AI API Keys** (optional, for enhanced features):
   - OpenAI API key
   - Anthropic API key

## 🚀 Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/whatsapp-mcp-dashboard.git
cd whatsapp-mcp-dashboard
```

### 2. Setup WhatsApp MCP Server

First, you need to set up the WhatsApp MCP Server that this dashboard connects to:

```bash
# Clone the WhatsApp MCP Server
git clone https://github.com/lharries/whatsapp-mcp.git
cd whatsapp-mcp

# Install Go (if not already installed)
# Download from: https://go.dev/dl/

# Run the WhatsApp bridge
cd whatsapp-bridge
go run main.go
```

When you run the WhatsApp bridge, you'll see a QR code. Scan it with your WhatsApp mobile app:
1. Open WhatsApp on your phone
2. Go to Settings → Linked Devices
3. Tap "Link a Device"
4. Scan the QR code displayed in your terminal

### 3. Setup Backend

```bash
# Navigate back to the dashboard project
cd whatsapp-mcp-dashboard

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install backend dependencies
cd backend
pip install -r requirements.txt

# Copy environment template
cp .env.template .env

# Edit .env file with your configuration
nano .env  # or use your preferred editor
```

### 4. Configure Environment Variables

Edit the `backend/.env` file with your settings:

```env
# Database Configuration
DATABASE_URL=sqlite:///./whatsapp_mcp.db

# WhatsApp MCP Server Configuration
WHATSAPP_MCP_SERVER_URL=ws://localhost:8001
WHATSAPP_HTTP_URL=http://localhost:8001

# AI Service API Keys (Optional)
OPENAI_API_KEY=your_openai_api_key_here
ANTHROPIC_API_KEY=your_anthropic_api_key_here

# Business Configuration
BUSINESS_NAME=Your Business Name
BUSINESS_PHONE=+1234567890
BUSINESS_EMAIL=contact@yourbusiness.com
```

### 5. Setup Frontend

```bash
# Install frontend dependencies
cd ../frontend
npm install
```

### 6. Start the Application

In one terminal, start the backend:

```bash
cd backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

In another terminal, start the frontend:

```bash
cd frontend
npm start
```

The application will be available at:
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

## 📱 Usage

### Initial Setup

1. **Connect WhatsApp**: Ensure the WhatsApp MCP Server is running and connected
2. **Check Status**: Visit the dashboard to verify WhatsApp connection status
3. **Configure Auto-Responses**: Set up automated response rules in the Auto-Responses section
4. **Test the System**: Send a message to your WhatsApp number to test classification and auto-responses

### Managing Messages

- **View Messages**: Go to the Messages page to see all conversations
- **Filter by Contact**: Use the contact filter to view specific conversations
- **Send Messages**: Use the compose feature to send messages to contacts
- **View Classifications**: See how AI has categorized each message

### Setting Up Auto-Responses

1. Go to **Auto-Responses** page
2. Click **"Add New Response"**
3. Configure:
   - **Category**: Choose which message type triggers this response
   - **Template**: Write your response template (supports variables)
   - **Priority**: Set response priority if multiple rules match
   - **Conditions**: Add additional conditions (optional)

### Broadcasting Messages

1. Go to **Broadcast** page
2. Select contacts or upload a contact list
3. Compose your message
4. Schedule immediately or for later
5. Monitor delivery status

### Analytics

- **Dashboard**: Overview of key metrics
- **Analytics Page**: Detailed reports and trends
- **Message Categories**: Distribution of message types
- **Response Rates**: Auto-response effectiveness

## 🔧 Configuration

### Message Categories

The system automatically classifies messages into these categories:

- **Support**: Help requests, technical issues
- **Sales**: Purchase inquiries, pricing questions
- **Inquiry**: General questions and information requests
- **Complaint**: Negative feedback, issues, refund requests
- **Compliment**: Positive feedback, testimonials
- **Appointment**: Scheduling, booking requests
- **General**: Greetings, small talk, unclassified messages

### Response Templates

Templates support variables that are automatically replaced:

- `{current_time}`: Current time
- `{current_date}`: Current date
- `{business_name}`: Your business name
- `{category}`: Message category
- `{sentiment}`: Message sentiment
- `{contact_name}`: Contact's name

Example template:
```
Hello {contact_name}! Thank you for reaching out to {business_name}. 
I understand you have a {category} inquiry. We'll get back to you within 24 hours.
```

### AI Configuration

For enhanced AI features, configure your API keys:

**OpenAI Setup:**
1. Get API key from https://platform.openai.com/
2. Add to `.env`: `OPENAI_API_KEY=your_key_here`

**Anthropic Setup:**
1. Get API key from https://console.anthropic.com/
2. Add to `.env`: `ANTHROPIC_API_KEY=your_key_here`

## 🔒 Security

### Production Deployment

For production use:

1. **Use HTTPS**: Deploy with SSL/TLS certificates
2. **Secure Database**: Use PostgreSQL instead of SQLite
3. **Environment Variables**: Store sensitive data securely
4. **API Rate Limiting**: Implement rate limiting for API endpoints
5. **Authentication**: Add user authentication if needed

### Data Privacy

- All message data is stored locally in your database
- AI processing can be done locally or via API calls
- No message data is shared with third parties
- Regular database backups recommended

## 🐛 Troubleshooting

### Common Issues

**WhatsApp Connection Issues:**
```bash
# Check if WhatsApp MCP server is running
curl http://localhost:8001/status

# Restart WhatsApp bridge
cd whatsapp-mcp/whatsapp-bridge
go run main.go
```

**Database Issues:**
```bash
# Reset database (CAUTION: This will delete all data)
rm backend/whatsapp_mcp.db

# Restart the backend server to recreate tables
```

**AI Classification Not Working:**
- Check API keys in `.env` file
- Verify API key permissions and quotas
- Check logs for error messages: `tail -f backend/logs/app.log`

**Frontend Build Issues:**
```bash
# Clear npm cache
npm cache clean --force

# Delete node_modules and reinstall
rm -rf node_modules package-lock.json
npm install
```

### Logs

- **Backend logs**: Check the console output where you started the FastAPI server
- **Frontend logs**: Check browser console for JavaScript errors
- **WhatsApp MCP logs**: Check the terminal where you're running the Go server

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guidelines](CONTRIBUTING.md) for details.

### Development Setup

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes
4. Add tests if applicable
5. Commit your changes: `git commit -am 'Add some feature'`
6. Push to the branch: `git push origin feature-name`
7. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **WhatsApp MCP Server** by [lharries](https://github.com/lharries/whatsapp-mcp)
- **Model Context Protocol (MCP)** for standardized AI integration
- **Material-UI** for beautiful React components
- **FastAPI** for the excellent Python web framework

## 📞 Support

For support and questions:

- **Issues**: [GitHub Issues](https://github.com/yourusername/whatsapp-mcp-dashboard/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/whatsapp-mcp-dashboard/discussions)
- **Email**: support@yourdomain.com

## 🗺️ Roadmap

### Upcoming Features

- [ ] Multi-language support
- [ ] Advanced analytics with ML insights
- [ ] WhatsApp Business API integration
- [ ] Team collaboration features
- [ ] Advanced scheduling options
- [ ] Integration with CRM systems
- [ ] Mobile app (React Native)
- [ ] Voice message support
- [ ] Chatbot builder interface
- [ ] A/B testing for auto-responses

### Recent Updates

- ✅ AI-powered message classification
- ✅ Real-time dashboard with WebSocket support
- ✅ Broadcast messaging functionality
- ✅ Responsive Material-UI design
- ✅ Auto-response system with templates

---

**Made with ❤️ for better WhatsApp Business communication**
