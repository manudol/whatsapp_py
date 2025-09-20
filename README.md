# WhatsApp AI Chatbot

A powerful Python-based WhatsApp Business API integration that provides AI-powered conversational capabilities through OpenAI's GPT models. This project enables businesses to create intelligent chatbots that can handle multiple message types, maintain conversation context, and integrate with external systems.

## 🚀 Features

### Multi-Modal Message Support
- **Text Messages**: Standard text responses with URL previews
- **Audio Messages**: Voice message transcription using OpenAI Whisper
- **Image Processing**: Image analysis and description using GPT-4 Vision
- **Location Sharing**: Send and receive location data
- **Interactive Messages**: Button replies and call-to-action buttons
- **Product Recommendations**: Send product information with images and details

### AI-Powered Responses
- **OpenAI Integration**: Uses GPT models for intelligent responses
- **Context Awareness**: Maintains conversation history and context
- **Custom System Prompts**: Configurable AI behavior per business
- **Multiple Output Types**: Dynamic response formatting based on content

### Advanced Features
- **Conversation Threading**: Persistent conversation management
- **Django Backend Integration**: Seamless data persistence and user management
- **Token Management**: Automatic authentication and token refresh
- **Error Handling**: Robust error management and fallback responses
- **Webhook Verification**: Secure WhatsApp webhook integration

## 📋 Prerequisites

- Python 3.8+
- WhatsApp Business API access
- OpenAI API key
- Django backend (for full functionality)
- ngrok or similar tunneling service (for local development)

## 🛠️ Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/whatsapp_py.git
   cd whatsapp_py
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Environment Configuration**
   Create a `.env` file in the project root with the following variables:
   ```env
   # WhatsApp Business API
   WHATSAPP_TOKEN=your_whatsapp_business_token
   WHATSAPP_VERSION=v18.0
   WHATSAPP_VERIFY_TOKEN=your_webhook_verify_token
   
   # OpenAI API
   OPENAI_API_KEY=your_openai_api_key
   
   # Django Backend (Optional)
   BACKEND_URL=https://your-django-backend.com/
   SERVICE_EMAIL=your_service_email
   SERVICE_PASSWORD=your_service_password
   
   # Server Configuration
   HOST=localhost
   PORT=7000
   ```

## 🚀 Quick Start

1. **Start the server**
   ```bash
   python main.py
   ```

2. **Set up webhook** (for local development)
   ```bash
   # Install ngrok
   ngrok http 7000
   
   # Use the ngrok URL as your webhook URL in WhatsApp Business API
   ```

3. **Configure WhatsApp Business API**
   - Set webhook URL to: `https://your-domain.com/webhook`
   - Set verify token to match `WHATSAPP_VERIFY_TOKEN` in your `.env`
   - Subscribe to `messages` events

## 📱 Supported Message Types

### 1. Text Messages
Standard text responses with automatic URL detection and previews.

**Example Usage:**
```
User: "Hello, I need help with my order"
Bot: "Hello! I'd be happy to help you with your order. Can you please provide your order number?"
```

### 2. Audio Messages
Voice message transcription and AI response.

**Features:**
- Automatic voice message detection
- OpenAI Whisper transcription
- Context-aware responses

### 3. Image Processing
Image analysis and description using GPT-4 Vision.

**Features:**
- Automatic image download and processing
- AI-powered image description
- Context integration with conversation

### 4. Location Sharing
Send and request location information.

**Features:**
- Send business locations to customers
- Request customer location for services
- Location-based service recommendations

### 5. Interactive Messages
Button replies and call-to-action buttons.

**Features:**
- Custom button responses
- URL redirection
- Interactive user engagement

### 6. Product Recommendations
Send product information with details and images.

**Features:**
- Product catalog integration
- Rich product cards
- Pricing and description display

## 🏗️ Architecture

### Core Components

- **`main.py`**: FastAPI application with webhook endpoints
- **`interactObjects/`**: Core interaction logic
  - `interact.py`: AI conversation management
  - `whatsappInteract.py`: WhatsApp message handling
  - `djangoInteract.py`: Backend integration
- **`responseComponents/`**: Message type handlers
- **`openai_client/`**: OpenAI API integration

### Message Flow

1. **Webhook Reception**: WhatsApp sends message to `/webhook` endpoint
2. **Message Processing**: Determine message type and extract content
3. **AI Processing**: Send to OpenAI for intelligent response generation
4. **Response Formatting**: Format response based on AI output type
5. **WhatsApp Delivery**: Send formatted response back to user
6. **Data Persistence**: Save conversation to backend (if configured)

## 🔧 Configuration

### AI Response Types

The system supports multiple output types that the AI can choose from:

1. **`OUTPUT TYPE: text`** - Standard text response
2. **`OUTPUT TYPE: audio`** - Convert text to audio
3. **`OUTPUT TYPE: cta_button`** - Call-to-action button
4. **`OUTPUT TYPE: location`** - Send location information
5. **`OUTPUT TYPE: request_location`** - Request user location
6. **`OUTPUT TYPE: product`** - Send product information

### Custom System Prompts

Configure AI behavior by setting custom system prompts in your Django backend or by modifying the prompt in `interactObjects/interact.py`.

## 🚀 Deployment

### Production Deployment

1. **Environment Setup**
   ```bash
   # Set production environment variables
   export HOST=0.0.0.0
   export PORT=8000
   ```

2. **Run with Gunicorn**
   ```bash
   pip install gunicorn
   gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker
   ```

3. **Docker Deployment**
   ```dockerfile
   FROM python:3.9-slim
   WORKDIR /app
   COPY requirements.txt .
   RUN pip install -r requirements.txt
   COPY . .
   CMD ["python", "main.py"]
   ```

### Webhook Configuration

1. **Production Webhook URL**: `https://your-domain.com/webhook`
2. **Verify Token**: Must match `WHATSAPP_VERIFY_TOKEN`
3. **Subscribed Events**: `messages`

## 📊 Monitoring and Logging

The application includes comprehensive logging for:
- Message processing
- AI response generation
- Error handling
- Performance monitoring

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

For support and questions:
- Create an issue in the GitHub repository
- Check the documentation for common setup issues
- Review the logs for error details

## 🔄 Changelog

### Version 1.0.0
- Initial release
- Multi-modal message support
- OpenAI integration
- Django backend integration
- Webhook verification
- Conversation threading

## 📚 Additional Resources

- [WhatsApp Business API Documentation](https://developers.facebook.com/docs/whatsapp)
- [OpenAI API Documentation](https://platform.openai.com/docs)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)

---

**Note**: This project requires proper WhatsApp Business API setup and OpenAI API access. Ensure you have the necessary permissions and API keys before deployment.