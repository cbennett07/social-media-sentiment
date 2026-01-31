#!/bin/sh
set -e

# Replace API_URL placeholder in the built JavaScript
if [ -n "$API_URL" ]; then
    echo "Configuring API_URL: $API_URL"
    # Replace the /api placeholder with the actual API URL
    find /usr/share/nginx/html -name "*.js" -exec sed -i "s|/api|${API_URL}|g" {} \;
fi

# Replace COLLECTOR_URL placeholder
if [ -n "$COLLECTOR_URL" ]; then
    echo "Configuring COLLECTOR_URL: $COLLECTOR_URL"
    find /usr/share/nginx/html -name "*.js" -exec sed -i "s|/collect|${COLLECTOR_URL}/collect|g" {} \;
fi

# Replace PROCESSOR_URL placeholder
if [ -n "$PROCESSOR_URL" ]; then
    echo "Configuring PROCESSOR_URL: $PROCESSOR_URL"
    find /usr/share/nginx/html -name "*.js" -exec sed -i "s|/process|${PROCESSOR_URL}/process|g" {} \;
fi

# Start nginx
exec nginx -g 'daemon off;'
