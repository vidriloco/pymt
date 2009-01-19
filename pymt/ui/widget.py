import sys
import os

from math import *
from math import sqrt, sin
from pyglet.gl import *
from pyglet import *
from pyglet.text import HTMLLabel, Label
from pyglet.window import key
from pymt.graphx import *
from pymt.mtpyglet import *
from pymt.ui.animation import *
from pymt.ui.factory import *
from pymt.vector import Vector

_id_2_widget = {}

def getWidgetByID(id):
    global _id_2_widget
    if _id_2_widget.has_key(id):
        return _id_2_widget[id]

class MTWidget(pyglet.event.EventDispatcher):
    """Global base for any multitouch widget.
    Implement event for mouse, object, touch and animation.

    Event are dispatched through widget only if it's visible.
    """

    def __init__(self, parent=None, **kargs):
        global _id_2_widget
        if kargs.has_key('id'):
            self.id = kargs['id']
            _id_2_widget[kargs['id']] = self

        pyglet.event.EventDispatcher.__init__(self)
        self.parent = parent
        self.children = []
        self._visible = False

        self.animations = []
        self.visible = True
        self.init()

    def _set_visible(self, visible):
        if self._visible == visible:
            return
        self._visible = visible
        self.update_event_registration()
    def _get_visible(self):
        return self._visible
    visible = property(_get_visible, _set_visible)

    def dispatch_event(self, event_type, *args):
        '''Dispatch a single event to the attached handlers.
        
        The event is propogated to all handlers from from the top of the stack
        until one returns `EVENT_HANDLED`.  This method should be used only by
        `EventDispatcher` implementors; applications should call
        the ``dispatch_events`` method.

        :Parameters:
            `event_type` : str
                Name of the event.
            `args` : sequence
                Arguments to pass to the event handler.

        '''
        assert event_type in self.event_types

        # Search handler stack for matching event handlers
        for frame in list(self._event_stack):
            handler = frame.get(event_type, None)
            if handler:
                try:
                    if handler(*args):
                        return True
                except TypeError:
                    self._raise_dispatch_exception(event_type, args, handler)


        # Check instance for an event handler
        if hasattr(self, event_type):
            try:
                if getattr(self, event_type)(*args):
                    return True
            except TypeError:
                self._raise_dispatch_exception(
                    event_type, args, getattr(self, event_type))


    def update_event_registration(self):
        evs = [ 'on_draw',
                'on_mouse_press',
                'on_mouse_drag',
                'on_mouse_release',
                'on_touch_up',
                'on_touch_move',
                'on_touch_down',
                'on_object_up',
                'on_object_move',
                'on_object_down',
                'on_animation_complete',
                'on_animation_reset',
                'on_animation_start' ]

        if self.visible:
            for ev in evs:
                self.register_event_type(ev)
        else:
            for ev in evs:
                if not hasattr(self, 'event_types'):
                    continue
                if ev in self.event_types:
                    self.event_types.remove(ev)

    def init(self):
        pass

    def bring_to_front(self):
        """Remove it from wherever it is and add it back at the top"""
        if self.parent:
            self.parent.children.remove(self)
            self.parent.children.append(self)

    def hide(self):
        self.visible = False

    def show(self):
        self.visible = True

    def on_draw(self):
        if not self.visible:
            return
        self.draw()
        for w in self.children:
            w.dispatch_event('on_draw')

    def draw(self):
        pass

    def add_widget(self, w, front=True):
        if front:
            self.children.append(w)
        else:
            self.children.insert(0,w)
        try:
            w.parent = self
        except:
            pass

    def remove_widget(self, w):
        try:
            self.children.remove(w)
        except:
            pass

    def add_animation(self, label, prop, to , timestep, length,
                      func=AnimationAlpha.ramp):
        anim = Animation(self, label, prop, to, timestep, length, func=func)
        self.animations.append(anim)
        return anim

    def start_animations(self, label='all'):
        for anim in self.animations:
            if anim.label == label or label == 'all':
                anim.reset()
                anim.start()

    def remove_animation(self, label):
        for anim in self.animations:
            if anim.label == label:
                self.animations.remove(anim)

    #hack for now to allow consumtion of events..really we need to work out a different way of propagatiing the events, rather than dispatching for each child
    def consumes_event(self, x,y):
        return False

    def on_touch_down(self, touches, touchID, x, y):
        for w in reversed(self.children):
            if w.dispatch_event('on_touch_down', touches, touchID, x, y):
                return True

    def on_touch_move(self, touches, touchID, x, y):
        for w in reversed(self.children):
            if w.dispatch_event('on_touch_move', touches, touchID, x, y):
                return True

    def on_touch_up(self, touches, touchID, x, y):
        for w in reversed(self.children):
            if w.dispatch_event('on_touch_up', touches, touchID, x, y):
                return True

    def on_mouse_press(self, x, y, button, modifiers):
        for w in reversed(self.children):
            w.dispatch_event('on_mouse_press',x, y, button, modifiers)

    def on_mouse_drag(self, x, y, dx, dy, button, modifiers):
        for w in reversed(self.children):
            w.dispatch_event('on_mouse_drag',x, y, dx, dy, button, modifiers)

    def on_mouse_release(self, x, y, button, modifiers):
        for w in reversed(self.children):
            w.dispatch_event('on_mouse_release', x, y, button, modifiers)

    def on_object_down(self, touches, touchID,id, x, y,angle):
        for w in reversed(self.children):
            w.dispatch_event('on_object_down', touches, touchID,id, x, y,angle)

    def on_object_move(self, touches, touchID,id, x, y,angle):
        for w in reversed(self.children):
            w.dispatch_event('on_object_move', touches, touchID,id, x, y,angle)

    def on_object_up(self, touches, touchID,id, x, y,angle):
        for w in reversed(self.children):
            w.dispatch_event('on_object_up', touches, touchID,id, x, y,angle)


# Register all base widgets
MTWidgetFactory.register('MTWidget', MTWidget)
