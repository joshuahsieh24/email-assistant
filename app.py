"""Simple Flask app for Railway deployment."""

from flask import Flask, jsonify

# Create Flask app
app = Flask(__name__)

@app.route('/healthz')
def health_check():
    """Health check endpoint."""
    return jsonify({
        "status": "healthy",
        "version": "0.1.0",
        "redis_status": "unavailable"
    })

@app.route('/')
def root():
    """Root endpoint."""
    return jsonify({"message": "OpenAI Gateway is running!"})

if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 8000))
    app.run(host='0.0.0.0', port=port) 