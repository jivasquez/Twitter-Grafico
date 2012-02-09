import hashlib

from bottle import request, redirect
from bottle import mako_template as template

from twittergrafico.account import Account


def auth():
    def decorator(view):
        def wrapper(*args, **kwargs):
            session = request.get_cookie('t')
            user = Account.get_user_from_session_id(session)
            if user:
                return view(user, *args, **kwargs)
            return redirect('/#login_div')
        return wrapper
    return decorator

def passhash(password):
    return hashlib.sha256('this is a salt' + password).hexdigest()
    
def render(template_, **kwargs):
    session = request.get_cookie('t')
    user = Account.get_user_from_session_id(session)
    kwargs['user'] = user
    return template(template_, **kwargs)
    