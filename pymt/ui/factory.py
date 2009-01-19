
class MTWidgetFactory(object):
    """Widget factory"""

    _widgets = {}

    @staticmethod
    def register(widgetname, widgetclass):
        if not MTWidgetFactory._widgets.has_key(widgetname):
            MTWidgetFactory._widgets[widgetname] = widgetclass

    @staticmethod
    def get(widgetname):
        if MTWidgetFactory._widgets.has_key(widgetname):
            return MTWidgetFactory._widgets[widgetname]
        raise Exception('Widget %s are not known in MTWidgetFactory' % widgetname)

