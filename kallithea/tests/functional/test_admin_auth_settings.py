from kallithea.tests import *
from kallithea.model.db import Setting


class TestAuthSettingsController(TestController):
    def _enable_plugins(self, plugins_list):
        test_url = url(controller='admin/auth_settings',
                       action='auth_settings')
        params={'auth_plugins': plugins_list, '_authentication_token': self.authentication_token()}

        for plugin in plugins_list.split(','):
            enable = plugin.partition('kallithea.lib.auth_modules.')[-1]
            params.update({'%s_enabled' % enable: True})
        response = self.app.post(url=test_url, params=params)
        return params
        #self.checkSessionFlash(response, 'Auth settings updated successfully')

    def test_index(self):
        self.log_user()
        response = self.app.get(url(controller='admin/auth_settings',
                                    action='index'))
        response.mustcontain('Authentication Plugins')

    def test_ldap_save_settings(self):
        self.log_user()
        if not ldap_lib_installed:
            raise SkipTest('skipping due to missing ldap lib')

        params = self._enable_plugins('kallithea.lib.auth_modules.auth_internal,kallithea.lib.auth_modules.auth_ldap')
        params.update({'auth_ldap_host': u'dc.example.com',
                       'auth_ldap_port': '999',
                       'auth_ldap_tls_kind': 'PLAIN',
                       'auth_ldap_tls_reqcert': 'NEVER',
                       'auth_ldap_dn_user': 'test_user',
                       'auth_ldap_dn_pass': 'test_pass',
                       'auth_ldap_base_dn': 'test_base_dn',
                       'auth_ldap_filter': 'test_filter',
                       'auth_ldap_search_scope': 'BASE',
                       'auth_ldap_attr_login': 'test_attr_login',
                       'auth_ldap_attr_firstname': 'ima',
                       'auth_ldap_attr_lastname': 'tester',
                       'auth_ldap_attr_email': 'test@example.com'})

        test_url = url(controller='admin/auth_settings',
                       action='auth_settings')

        response = self.app.post(url=test_url, params=params)
        self.checkSessionFlash(response, 'Auth settings updated successfully')

        new_settings = Setting.get_auth_settings()
        self.assertEqual(new_settings['auth_ldap_host'], u'dc.example.com',
                         'fail db write compare')

    def test_ldap_error_form_wrong_port_number(self):
        self.log_user()
        if not ldap_lib_installed:
            raise SkipTest('skipping due to missing ldap lib')

        params = self._enable_plugins('kallithea.lib.auth_modules.auth_internal,kallithea.lib.auth_modules.auth_ldap')
        params.update({'auth_ldap_host': '',
                       'auth_ldap_port': 'i-should-be-number',  # bad port num
                       'auth_ldap_tls_kind': 'PLAIN',
                       'auth_ldap_tls_reqcert': 'NEVER',
                       'auth_ldap_dn_user': '',
                       'auth_ldap_dn_pass': '',
                       'auth_ldap_base_dn': '',
                       'auth_ldap_filter': '',
                       'auth_ldap_search_scope': 'BASE',
                       'auth_ldap_attr_login': '',
                       'auth_ldap_attr_firstname': '',
                       'auth_ldap_attr_lastname': '',
                       'auth_ldap_attr_email': ''})
        test_url = url(controller='admin/auth_settings',
                       action='auth_settings')

        response = self.app.post(url=test_url, params=params)

        response.mustcontain("""<span class="error-message">"""
                             """Please enter a number</span>""")

    def test_ldap_error_form(self):
        self.log_user()
        if not ldap_lib_installed:
            raise SkipTest('skipping due to missing ldap lib')

        params = self._enable_plugins('kallithea.lib.auth_modules.auth_internal,kallithea.lib.auth_modules.auth_ldap')
        params.update({'auth_ldap_host': 'Host',
                       'auth_ldap_port': '123',
                       'auth_ldap_tls_kind': 'PLAIN',
                       'auth_ldap_tls_reqcert': 'NEVER',
                       'auth_ldap_dn_user': '',
                       'auth_ldap_dn_pass': '',
                       'auth_ldap_base_dn': '',
                       'auth_ldap_filter': '',
                       'auth_ldap_search_scope': 'BASE',
                       'auth_ldap_attr_login': '',  # <----- missing required input
                       'auth_ldap_attr_firstname': '',
                       'auth_ldap_attr_lastname': '',
                       'auth_ldap_attr_email': ''})

        test_url = url(controller='admin/auth_settings',
                       action='auth_settings')

        response = self.app.post(url=test_url, params=params)

        response.mustcontain("""<span class="error-message">The LDAP Login"""
                             """ attribute of the CN must be specified""")

    def test_ldap_login(self):
        pass

    def test_ldap_login_incorrect(self):
        pass

    def _container_auth_setup(self, **settings):
        self.log_user()

        params = self._enable_plugins('kallithea.lib.auth_modules.auth_internal,kallithea.lib.auth_modules.auth_container')
        params.update(settings)

        test_url = url(controller='admin/auth_settings',
                       action='auth_settings')

        response = self.app.post(url=test_url, params=params)
        response = response.follow()
        response.click('Log Out') # end admin login session

    def _container_auth_verify_login(self, resulting_username, **get_kwargs):
        response = self.app.get(
            url=url(controller='admin/my_account', action='my_account'),
            **get_kwargs
        )
        response.mustcontain('My Account %s' % resulting_username)

    def test_container_auth_login_header(self):
        self._container_auth_setup(
            auth_container_header='THE_USER_NAME',
            auth_container_fallback_header='',
            auth_container_clean_username='False',
        )
        self._container_auth_verify_login(
            extra_environ={'THE_USER_NAME': 'john@example.org'},
            resulting_username='john@example.org',
        )

    def test_container_auth_login_fallback_header(self):
        self._container_auth_setup(
            auth_container_header='THE_USER_NAME',
            auth_container_fallback_header='HTTP_X_YZZY',
            auth_container_clean_username='False',
        )
        self._container_auth_verify_login(
            headers={'X-Yzzy': r'foo\bar'},
            resulting_username=r'foo\bar',
        )

    def test_container_auth_clean_username_at(self):
        self._container_auth_setup(
            auth_container_header='REMOTE_USER',
            auth_container_fallback_header='',
            auth_container_clean_username='True',
        )
        self._container_auth_verify_login(
            extra_environ={'REMOTE_USER': 'john@example.org'},
            resulting_username='john',
        )

    def test_container_auth_clean_username_backslash(self):
        self._container_auth_setup(
            auth_container_header='REMOTE_USER',
            auth_container_fallback_header='',
            auth_container_clean_username='True',
        )
        self._container_auth_verify_login(
            extra_environ={'REMOTE_USER': r'example\jane'},
            resulting_username=r'jane',
        )

    def test_container_auth_no_logout(self):
        self._container_auth_setup(
            auth_container_header='REMOTE_USER',
            auth_container_fallback_header='',
            auth_container_clean_username='True',
        )
        response = self.app.get(
            url=url(controller='admin/my_account', action='my_account'),
            extra_environ={'REMOTE_USER': 'john'},
        )
        self.assertNotIn('Log Out', response.normal_body)

    def test_crowd_save_settings(self):
        self.log_user()

        params = self._enable_plugins('kallithea.lib.auth_modules.auth_internal,kallithea.lib.auth_modules.auth_crowd')
        params.update({'auth_crowd_host': ' hostname ',
                       'auth_crowd_app_password': 'secret',
                       'auth_crowd_admin_groups': 'mygroup',
                       'auth_crowd_port': '123',
                       'auth_crowd_app_name': 'xyzzy'})

        test_url = url(controller='admin/auth_settings',
                       action='auth_settings')

        response = self.app.post(url=test_url, params=params)
        self.checkSessionFlash(response, 'Auth settings updated successfully')

        new_settings = Setting.get_auth_settings()
        self.assertEqual(new_settings['auth_crowd_host'], u'hostname',
                         'fail db write compare')

    def test_pam_save_settings(self):
        self.log_user()

        if not pam_lib_installed:
            raise SkipTest('skipping due to missing pam lib')

        params = self._enable_plugins('kallithea.lib.auth_modules.auth_internal,kallithea.lib.auth_modules.auth_pam')
        params.update({'auth_pam_service': 'kallithea',
                       'auth_pam_gecos': '^foo-.*'})

        test_url = url(controller='admin/auth_settings',
                       action='auth_settings')

        response = self.app.post(url=test_url, params=params)
        self.checkSessionFlash(response, 'Auth settings updated successfully')

        new_settings = Setting.get_auth_settings()
        self.assertEqual(new_settings['auth_pam_service'], u'kallithea',
                         'fail db write compare')
