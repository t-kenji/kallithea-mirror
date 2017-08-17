# -*- coding: utf-8 -*-

avail_exts = []

class IExtensions(object):
    pass

class IRoute(IExtensions):

    def make_map(config, rmap):
        pass

class ITemplatePullrequests(IExtensions):

    def add_property(c):
        pass
