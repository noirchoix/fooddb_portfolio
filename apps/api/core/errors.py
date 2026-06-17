from fastapi import HTTPException, status


class FoodDBError(Exception):
    def __init__(self, message: str, code: str = 'fooddb_error') -> None:
        self.message = message
        self.code = code
        super().__init__(message)


def not_found(message: str) -> HTTPException:
    return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={'code': 'not_found', 'message': message})


def bad_request(message: str) -> HTTPException:
    return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail={'code': 'bad_request', 'message': message})
