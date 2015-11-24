# -*- coding: utf-8 -*-
"""Main Controller"""

from tg import expose, flash, require, url, lurl
from tg import request, redirect, tmpl_context
from tg.i18n import ugettext as _, lazy_ugettext as l_
from tg.exceptions import HTTPFound
from tg import predicates
from tg import session
from trivia import model
from trivia.controllers.secure import SecureController
from trivia.model import DBSession
from tgext.admin.tgadminconfig import BootstrapTGAdminConfig as TGAdminConfig
from tgext.admin.controller import AdminController

from trivia.lib.base import BaseController
from trivia.controllers.error import ErrorController

from question_generator import QuestionGenerator
from repoze.what.predicates import is_anonymous
from cache import Cache

import transaction

__all__ = ['RootController']


class RootController(BaseController):
    """
    The root controller for the trivia application.

    All the other controllers and WSGI applications should be mounted on this
    controller. For example::

        panel = ControlPanelController()
        another_app = AnotherWSGIApplication()

    Keep in mind that WSGI applications shouldn't be mounted directly: They
    must be wrapped around with :class:`tg.controllers.WSGIAppController`.

    """
    secc = SecureController()
    admin = AdminController(model, DBSession, config_type=TGAdminConfig)

    error = ErrorController()
    
    question_generator = QuestionGenerator()
    cache = Cache()

    def _before(self, *args, **kw):
        tmpl_context.project_name = "trivia"

    @expose('trivia.templates.register')
    @require(is_anonymous(msg='Only one account per user is allowed'))
    def register(self):
        """Display the user registration form"""
        return {'page': 'user registration'}

    @expose()
    def submit_answer(self, options, question_id):

        correct_option = self.cache.get(int(question_id))

        if int(options) == correct_option: 
            # Assume it's always correct for now
            DBSession.query(model.User).filter_by(email_address=request.\
                                        identity['user'].email_address).\
                                        update({'score': model.User.score + 1})
            transaction.commit()
            session['answered_correctly'] = True
            session.save()
        else:
            session['answered_correctly'] = False

        session.save()
        redirect(url('/'))

    @expose()
    @require(is_anonymous(msg='Only one account per user is ' \
                              'allowed'))
    def add_user(self, username, email, passwd):
        # Defining the row
        user = model.User()
        user.user_name = username
        user.email_address = email
        user.password = passwd

        # Saving the row:
        DBSession.add(user)
        # Redirecting to the login form with a notification
        # message:
        flash('Account created! Please log in')
        redirect(url('/login'))

    @expose('trivia.templates.trivia')
    def index(self):
        """Handle the front-page."""


        if request.identity:
            generated_trivia = self.question_generator.get_question()
            self.cache.put(generated_trivia)
            score =  DBSession.query(model.User).get(request.identity['user']\
                                                .email_address).score

            answered_correctly = session.pop('answered_correctly', None)
            session.save()

            return { 'trivia': generated_trivia,
                     'score': score,
                     'answered_correctly': answered_correctly}
        else:
            redirect(url('/login'))

    @expose('trivia.templates.about')
    def about(self):
        """Handle the 'about' page."""
        return dict(page='about')

    @expose('trivia.templates.environ')
    def environ(self):
        """This method showcases TG's access to the wsgi environment."""
        return dict(page='environ', environment=request.environ)

    @expose('trivia.templates.data')
    @expose('json')
    def data(self, **kw):
        """
        This method showcases how you can use the same controller
        for a data page and a display page.
        """
        return dict(page='data', params=kw)

    @expose('trivia.templates.index')
    @require(predicates.has_permission('manage', msg=l_('Only for managers')))
    def manage_permission_only(self, **kw):
        """Illustrate how a page for managers only works."""
        return dict(page='managers stuff')

    @expose('trivia.templates.index')
    @require(predicates.is_user('editor', msg=l_('Only for the editor')))
    def editor_user_only(self, **kw):
        """Illustrate how a page exclusive for the editor works."""
        return dict(page='editor stuff')

    @expose('trivia.templates.login')
    def login(self, came_from=lurl('/'), failure=None, login=''):
        """Start the user login."""
        if failure is not None:
            if failure == 'user-not-found':
                flash(_('User not found'), 'error')
            elif failure == 'invalid-password':
                flash(_('Invalid Password'), 'error')

        login_counter = request.environ.get('repoze.who.logins', 0)
        if failure is None and login_counter > 0:
            flash(_('Wrong credentials'), 'warning')

        return dict(page='login', login_counter=str(login_counter),
                    came_from=came_from, login=login)

    @expose()
    def post_login(self, came_from=lurl('/')):
        """
        Redirect the user to the initially requested page on successful
        authentication or redirect her back to the login page if login failed.

        """
        if not request.identity:
            login_counter = request.environ.get('repoze.who.logins', 0) + 1
            redirect('/login',
                     params=dict(came_from=came_from, __logins=login_counter))
#         userid = request.identity['repoze.who.userid']
#         flash(_('Welcome back, %s!') % userid)

        # Do not use tg.redirect with tg.url as it will add the mountpoint
        # of the application twice.
        return HTTPFound(location=came_from)

    @expose()
    def post_logout(self, came_from=lurl('/')):
        """
        Redirect the user to the initially requested page on logout and say
        goodbye as well.

        """
        flash(_('We hope to see you soon!'))
        return HTTPFound(location=came_from)


    @expose()
    def logout(self):
        identity.current.logout()

        raise redirect('/')