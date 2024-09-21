import time
from typing import Optional
from fastapi import Body, FastAPI, Response, status, HTTPException
from pydantic import BaseModel
import psycopg2
from psycopg2.extras import RealDictCursor

# 10:30:00
app = FastAPI()

while True:
    try:
        conn = psycopg2.connect(host='localhost', dbname='fastapi', user='postgres', password='123456', cursor_factory=RealDictCursor)
        cursor = conn.cursor()
        print('connect database was successful')
        break
    except Exception as error:
        print('connect database was fail')
        print('error:', error)
        time.sleep(2)

class Post(BaseModel):
    title: str
    content: str
    published: bool = True
    # rating: Optional[int] = None


my_posts = [
        {'id': 1, 'title': 'title1', 'content': 'content1'},
        {'id': 2, 'title': 'title2', 'content': 'content2'}
    ]


def find_post(id: int):
    for p in my_posts:
        if p['id'] == id:
            return p


def find_index_post(id: int):
    for i, p in enumerate(my_posts):
        if p['id'] == id:
            return i


@app.get("/")
async def root():
    return {'message': 'hello world'}


@app.get("/posts")
def get_posts():
    cursor.execute('SELECT * FROM posts')
    posts = cursor.fetchall()    
    return {'data': posts}


@app.post('/posts', status_code=status.HTTP_201_CREATED)
# def create_post(post: dict = Body(...)):
def create_post(post: Post):
    cursor.execute('INSERT INTO posts (title, content, published) VALUES (%s, %s, %s) RETURNING *', (post.title, post.content, post.published))
    new_post = cursor.fetchone()
    conn.commit()
    return {'data': new_post}


@app.get('/posts/{id}')
def get_post(id: int):
    cursor.execute('SELECT * FROM posts WHERE id = %s', str(id))
    post = cursor.fetchone()

    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'post with id: {id} was not found')

    return {'data': post}


@app.delete('/posts/{id}', status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id: int):
    cursor.execute('DELETE FROM posts WHERE id = %s RETURNING *', str(id))
    post_deleted = cursor.fetchone()
    conn.commit()

    if not post_deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'post with id: {id} was not found')

    # return {'message': 'the post was deleted successfully'}


@app.put('/posts/{id}')
def update_post(id: int, post: Post):
    cursor.execute('UPDATE posts SET title = %s, content = %s, published = %s WHERE id = %s RETURNING *', 
                   (post.title, post.content, post.published, str(id)))
    post_updated = cursor.fetchone()
    conn.commit()

    if not post_updated:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'post with id: {id} was not found')

    return {'data': post_updated}
