from fastapi import status, HTTPException, Depends, APIRouter
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from .. import models, schemas, utils, oauth2
from ..database import get_db


router = APIRouter(tags=['Auth'])


@router.post('/login',  response_model=schemas.Token)
def login(user: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user_db = db.query(models.User).filter(models.User.email == user.username).first()

    if not user_db:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Invalid Credentials')

    if not utils.verify_password(user.password, user_db.password):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Invalid Credentials')

    access_token = oauth2.create_access_token({'user_id': user_db.id})

    return schemas.Token(access_token=access_token, token_type='bearer')

