from fastapi import security


oauth2_scheme = security.OAuth2PasswordBearer(tokenUrl='token')
