from fastapi import status, HTTPException, Depends, APIRouter
from sqlalchemy.orm import Session
from sqlalchemy.sql import func
from .. import models, schemas, oauth2
from ..database import get_db


router = APIRouter(prefix='/posts', tags=['Posts'])


# @router.get("/")
@router.get("/", response_model=list[schemas.PostWithVotesResponse])
def get_posts(db: Session = Depends(get_db), current_user: models.User = Depends(oauth2.get_current_user), 
              search: str = '', limit: int = 10, skip: int = 0):

    posts_query = db.query(models.Post, func.count(models.Vote.post_id).label("votes")).\
        join(models.Vote, models.Vote.post_id == models.Post.id, isouter=True).\
        group_by(models.Post.id)
    
    if search:
        posts_query = posts_query.filter(models.Post.content.contains(search))
    
    if skip:
        posts_query = posts_query.offset(skip)
    
    posts = posts_query.limit(limit=limit).all()
    return posts


@router.post('/', status_code=status.HTTP_201_CREATED, response_model=schemas.PostResponse)
def create_post(post: schemas.PostCreate, db: Session = Depends(get_db), 
                current_user: models.User = Depends(oauth2.get_current_user)):
    post_new = models.Post(user_id=current_user.id, **post.model_dump())
    db.add(post_new)
    db.commit()
    db.refresh(post_new)
    return post_new


@router.get('/{id}', response_model=schemas.PostWithVotesResponse)
def get_post(id: int, db: Session = Depends(get_db), current_user: models.User = Depends(oauth2.get_current_user)):
    posts_query = db.query(models.Post, func.count(models.Vote.post_id).label("votes")).\
        join(models.Vote, models.Vote.post_id == models.Post.id, isouter=True).\
        group_by(models.Post.id)
    post = posts_query.filter(models.Post.id == id).first()

    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'post with id: {id} was not found')

    return post


@router.delete('/{id}', status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id: int, db: Session = Depends(get_db), current_user: models.User = Depends(oauth2.get_current_user)):
    post_query = db.query(models.Post).filter(models.Post.id == id)

    post = post_query.first()

    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'post with id: {id} was not found')

    print(post.user_id, current_user.id)

    if post.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Not authorized to perform requested action')

    post_query.delete()
    db.commit()

    # return {'message': 'the post was deleted successfully'}


@router.put('/{id}', response_model=schemas.PostResponse)
def update_post(id: int, post: schemas.PostCreate, db: Session = Depends(get_db), 
                current_user: models.User = Depends(oauth2.get_current_user)):
    post_updated = db.query(models.Post).filter(models.Post.id == id)

    if not post_updated.first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'post with id: {id} was not found')

    post_updated.update(post.model_dump())
    db.commit()

    return post_updated.first()


