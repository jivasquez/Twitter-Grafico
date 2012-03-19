# -*- coding: utf-8 -*-
import os
import hashlib

from bottle import request, redirect
from bottle import mako_template as template
from bottle import MakoTemplate

from twittergrafico.account import Account
TEMPLATES_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "templates")

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
    templ =  MakoTemplate(name=template_, lookup=[TEMPLATES_PATH], imports=['from webhelpers.html import escape'],
        default_filters=['escape'])
    return templ.render(**kwargs)
    
def get_json_from_clusters(clusters):
    new_clusters = []
    for cluster in clusters:
        new_cluster = []
        for tweet in cluster:
            new_cluster.append({"message":tweet.message, "id":tweet.id, "url":tweet.url, "image":tweet.image, "massive":tweet.massive})
        new_clusters.append(new_cluster)
    return new_clusters
    
def get_json_from_list(list_):
    new_list = []
    for key, tweet in list_.iteritems():
        new_list.append({"message":tweet.message, "id":tweet.id, "url":tweet.url, "image":tweet.image, "massive":tweet.massive})
    return new_list