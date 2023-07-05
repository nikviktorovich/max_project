class TokenAuth:
    token: str


    def __init__(self, token: str) -> None:
        self.token = token
    

    def __call__(self, r):
        r.headers['Authorization'] = f'Bearer {self.token}'
        return r
