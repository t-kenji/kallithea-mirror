# -*- coding: utf-8 -*-


avail_exts = []

class IExtension(object):
    pass

class IRoute(IExtension):
    def make_map(self, config, rmap):
        pass

class ITemplatePullrequests(IExtension):
    def add_property(self, ctx):
        pass

    def add_action(self, name):
        pass

