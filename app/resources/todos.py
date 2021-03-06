from flask_restx import Namespace, Resource, fields
from werkzeug.exceptions import BadRequest
from flask_jwt_extended import  jwt_required, create_access_token, get_jwt_identity, jwt_refresh_token_required, create_refresh_token, fresh_jwt_required


from datetime import datetime

from models.todo_model import Todo, TodoSchema, User


api = Namespace('todos', description='Todos Operations')

todo_schema = TodoSchema()
todos_schema = TodoSchema(many=True)

todo_model = api.model('Todo', {
    'title': fields.String(required=True, description='The title'),
    'description': fields.String(required=True, description='The description')
})


@api.route('/')
class TodoList(Resource):
    @api.doc('list_todos', security='apikey', responses={ 200: 'OK', 400: 'Invalid Argument', 404: 'Not Found', 500: 'Mapping Key Error' })    
    @jwt_required
    def get(self):
        '''List all todos'''
        try:
            my_todos = Todo.fetch_all() 
            todos = todos_schema.dump(my_todos)
            return {'status':'Matches retrieved', 'todos':todos}, 200
        except KeyError as e:
            api.abort(500, e.__doc__, status = "Could not perform this action", statusCode = "500")
        except Exception as e:
            api.abort(400, e.__doc__, status = "Could perform this action", statusCode = "400")
    
    @api.doc('post_todo', responses={ 200: 'OK', 201:'Created', 400: 'Invalid Argument', 404: 'Not Found', 500: 'Mapping Key Error' })    
    @api.expect(todo_model)
    @jwt_required
    def post(self):
        '''Post todo item to database'''
        try:
            data = api.payload
            #user = get_jwt_claims()
            #user_id = User.fetch_by_user(user).id
            new_todo = Todo(title=data['title'], description=data['description'])#, user_id=user_id)
            new_todo.insert_record()
            todo = todo_schema.dump(data)
            return {'status':'Todo item added', 'todo':todo}, 201
        except KeyError as e:
            api.abort(500, e.__doc__, status = "Could not perform this action", statusCode = "500")
        except Exception as e:
            api.abort(400, e.__doc__, status = "Could not perform this action", statusCode = "400")

@api.route('/<int:id>')
@api.param('id', 'The todo item identifier')
class TodoItem(Resource):
    @api.doc('get_todo', responses={ 200: 'OK', 400: 'Invalid Argument', 404: 'Not Found', 500: 'Mapping Key Error' })
    @jwt_required
    def get(self, id):
        '''Get todo item from database'''
        try:
            my_todo = Todo.fetch_by_id(id)
            todo = todo_schema.dump(my_todo)
            if len(todo) == 0:
                e = BadRequest('Todo item does not exist')
                e.data = {'status':'404'}
                raise e
            return {'status':'Match retrieved', 'todo':todo}, 200
        except KeyError as e:
            api.abort(500, e.__doc__, status = "Could not retrieve information", statusCode = "500")
        except Exception as e:
            api.abort(404, e.__doc__, status = "Todo item does not exist", statusCode = "404")

    @api.doc('edit_todo', responses={ 200: 'OK', 201:'Created', 400: 'Invalid Argument', 404: 'Not Found', 500: 'Mapping Key Error' })
    @api.expect(todo_model)
    @jwt_required
    def put(self, id):
        '''Edit todo item in database'''
        try:
            data = api.payload
            
            id=id
            title = data['title']
            description = data['description']
            updated = datetime.utcnow()
            Todo.update_todo(id=id, title=title,  description=description, updated=updated)
            todo = todo_schema.dump(data)
            return {'status':'Todo item has been updated', 'todo':todo}, 201
        except KeyError as e:
            api.abort(500, e.__doc__, status = "Could not perform this action", statusCode = "500")
        except Exception as e:
            api.abort(400, e.__doc__, status = "Could not perform this action", statusCode = "400")

    @api.doc('delete_todo', responses={ 200: 'OK', 201:'Created', 400: 'Invalid Argument', 404: 'Not Found', 500: 'Mapping Key Error' })
    @jwt_required
    def delete(self, id):
        '''Delete todo item from database'''
        try:
            my_todo = Todo.fetch_by_id(id)
            todo = todo_schema.dump(my_todo)
            if len(todo) == 0:
                e = BadRequest('Todo item does not exist')
                e.data = {'status':'404'}
                raise e
            Todo.delete_by_id(id)
            return {'status':'Todo item has been deleted'}
        except KeyError as e:
            api.abort(500, e.__doc__, status = "Could not perform this action", statusCode = "500")
        except Exception as e:
            api.abort(400, e.__doc__, status = "Could perform this action", statusCode = "400")
