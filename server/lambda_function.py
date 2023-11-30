
def lambda_handler(event, context):
    return {
        "statusCode": 200,
        "body": "Hello from Lambda!"
    }


# To run locally, use `poetry run python server/lambda_function.py`
if __name__ == "__main__":
    lambda_handler(None, None)
