class ResponseTemplate:
    @staticmethod
    def getSuccessResponse(message, data=None):
        return {
            "status": "success",
            "message": message,
            "data": data
        }

    @staticmethod
    def getErrorResponse(message, errors=None):
        return {
            "status": "error",
            "message": message,
            "errors": errors
        }
