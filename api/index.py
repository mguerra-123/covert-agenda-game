from app_supabase import app

# This is the entry point for Vercel serverless functions
# Vercel expects this to be a callable that takes (environ, start_response)
def handler(environ, start_response):
    return app(environ, start_response)

# For local development
if __name__ == '__main__':
    app.run() 