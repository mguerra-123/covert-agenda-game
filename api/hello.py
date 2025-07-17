def handler(request, context):
    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'application/json'
        },
        'body': '{"message": "Hello from Covert Agenda! API is working!"}'
    } 