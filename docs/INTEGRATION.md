# Website Integration Guide

This guide explains how to integrate the AI RAG Waterproofing Chatbot widget into your existing website.

## Quick Integration

### Step 1: Host the Widget Script

Copy `widget/chat-widget.js` to your website. You can:
- Place it in your website's `/js/` or `/assets/` directory
- Host it on a CDN for better performance
- Keep it on the same server as your backend (not recommended for production)

### Step 2: Add the Script to Your Website

Add the following code to your HTML, preferably before the closing `</body>` tag:

```html
<script src="/path/to/chat-widget.js"></script>
<script>
    WaterproofingChatbot.init({
        apiUrl: 'https://your-api-domain.com/api/v1',
        position: 'bottom-right',
        primaryColor: '#007bff',
        title: 'Waterproofing Assistant',
        placeholder: 'Ask about waterproofing...'
    });
</script>
```

### Step 3: Configure CORS

Ensure your backend API allows requests from your website domain. Update `config/config.yaml`:

```yaml
server:
  cors:
    origins:
      - "https://your-website.com"
      - "https://www.your-website.com"
```

## Configuration Options

The widget accepts the following configuration options:

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `apiUrl` | string | `'http://localhost:8000/api/v1'` | Backend API URL |
| `position` | string | `'bottom-right'` | Widget position: `'bottom-right'` or `'bottom-left'` |
| `primaryColor` | string | `'#007bff'` | Primary color for the widget (hex code) |
| `title` | string | `'Waterproofing Assistant'` | Widget header title |
| `placeholder` | string | `'Ask about waterproofing...'` | Input placeholder text |

## Integration Examples

### Static HTML Website

```html
<!DOCTYPE html>
<html>
<head>
    <title>My Website</title>
</head>
<body>
    <h1>Welcome to My Website</h1>
    <p>Your content here...</p>

    <!-- Chatbot Widget -->
    <script src="/js/chat-widget.js"></script>
    <script>
        WaterproofingChatbot.init({
            apiUrl: 'https://api.example.com/api/v1',
            position: 'bottom-right',
            primaryColor: '#ff6600'
        });
    </script>
</body>
</html>
```

### React Application

```jsx
import { useEffect } from 'react';

function App() {
    useEffect(() => {
        // Load widget script
        const script = document.createElement('script');
        script.src = '/js/chat-widget.js';
        script.async = true;
        document.body.appendChild(script);

        // Initialize widget after script loads
        script.onload = () => {
            window.WaterproofingChatbot.init({
                apiUrl: process.env.REACT_APP_API_URL,
                position: 'bottom-right',
                primaryColor: '#007bff'
            });
        };

        return () => {
            document.body.removeChild(script);
        };
    }, []);

    return (
        <div>
            <h1>My React App</h1>
            {/* Your app content */}
        </div>
    );
}
```

### WordPress

Add to your theme's `footer.php` or use a plugin like "Insert Headers and Footers":

```html
<script src="/wp-content/themes/your-theme/js/chat-widget.js"></script>
<script>
    WaterproofingChatbot.init({
        apiUrl: 'https://api.example.com/api/v1',
        position: 'bottom-right'
    });
</script>
```

### Wix / Squarespace / Website Builders

Most website builders allow custom code injection. Look for:
- "Custom Code" or "Embed Code" sections
- Footer injection options
- Third-party script integration

Add the script and initialization code there.

## Customization

### Changing Colors

Match the widget to your brand:

```javascript
WaterproofingChatbot.init({
    apiUrl: 'https://api.example.com/api/v1',
    primaryColor: '#your-brand-color'
});
```

### Position

Choose the widget position:

```javascript
WaterproofingChatbot.init({
    apiUrl: 'https://api.example.com/api/v1',
    position: 'bottom-left'  // or 'bottom-right'
});
```

### Custom Styling

The widget uses inline styles injected via JavaScript. To override styles, add custom CSS to your website with higher specificity:

```css
.wp-chat-widget-container {
    z-index: 10000 !important;
}

.wp-chat-toggle-btn {
    width: 70px !important;
    height: 70px !important;
}
```

## Troubleshooting

### Widget Not Appearing

1. Check browser console for errors
2. Verify the script path is correct
3. Ensure the script loads before initialization
4. Check that `WaterproofingChatbot` is available in the global scope

### API Errors

1. Verify the `apiUrl` is correct and accessible
2. Check CORS configuration on the backend
3. Ensure the backend is running
4. Check network tab in browser dev tools for failed requests

### Styling Issues

1. Check for CSS conflicts with your existing styles
2. Use browser dev tools to inspect widget elements
3. Add custom CSS overrides if needed

## Best Practices

1. **Host on CDN**: Use a CDN for the widget script for faster loading
2. **Minify**: Minify the widget script for production use
3. **Version Control**: Use versioned script filenames (e.g., `chat-widget-v1.0.0.js`)
4. **CORS**: Configure CORS properly to allow only your domains
5. **HTTPS**: Use HTTPS for both your website and API
6. **Testing**: Test on mobile devices and different browsers

## Support

For integration issues:
1. Check the browser console for errors
2. Review API documentation in `docs/API.md`
3. Verify backend is running and accessible
4. Test API endpoints directly (e.g., using curl or Postman)
