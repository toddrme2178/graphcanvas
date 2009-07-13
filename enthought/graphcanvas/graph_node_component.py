import numpy
from math import sqrt

from enthought.enable.api import Component
from enthought.kiva import Font, MODERN
from enthought.traits.api import List, Int, Any, Str, cached_property, Property
from enthought.traits.ui.api import View, Item


def get_scale(gc):
    """  Get the scaling from the ctm.
    """
    ctm = gc.get_ctm()
    if hasattr(ctm, "__len__") and len(ctm) == 6:
        return sqrt( (ctm[0]+ctm[1]) * (ctm[0]+ctm[1]) / 2.0 + \
                     (ctm[2]+ctm[3]) * (ctm[2]+ctm[3]) / 2.0 )
        
    if hasattr(ctm, "scale"):
        return gc.get_ctm().scale()
        
    if hasattr(gc, "get_ctm_scale"):
        return gc.get_ctm_scale()
        
    raise RuntimeError("Unable to get scale from GC.")


class GraphNodeComponent(Component):
    """ An Enable Component which represents a graph node.
    """
    
    # Children of this node
    children = List()
    
    # The level from the root. This is used for layout and may not be
    # meaningful in graphs with no root level.
    level = Int(0)
    
    # The object contained in the graph node
    value = Any
    
    # The label which will be shown on the graph node
    label = Property(Str, depends_on='value')
    
    # The key on the graph for this node. This should not be
    # changed
    _key = Any
    
    traits_view = View(Item('value'))
    
    def draw(self, gc, view_bounds=None, mode="default"):
        """ Draws the graph node
        """
        
        font = Font(family=MODERN)
        gc.set_font(font)
        
        # update the size to match the text extent.
        x, y, width, height = gc.get_text_extent(self.label)
        
        self.padding = [5,5,5,5]
        
        self.width = width + self.padding_left + self.padding_right
        self.height = height + self.padding_bottom + self.padding_top

        self._draw_border(gc, view_bounds, mode)
        self._draw_text(gc, view_bounds, mode)
                
    def _draw_text(self, gc, view_bounds, mode):
        scale = get_scale(gc)
        pos = (scale * (self.x + self.padding_left),
               scale * (self.y2 - 2*self.padding_bottom))
        
        gc.show_text(self.label, pos)
        
        
    def _draw_border(self, gc, view_bounds, mode):
        """ Draws a nicely shaded border around the graph node
        """
        end_radius = 4
        starting_color = numpy.array([0.0, 1.0, 1.0, 1.0, 1.0])
        ending_color = numpy.array([1.0, 0.0, 0.0, 0.0, 1.0])        
        
        x = self.x
        y = self.y
        
        gc.begin_path()
        gc.move_to(x + end_radius, y)
        gc.arc_to(x + self.width, y,
                x + self.width,
                y + end_radius, end_radius)
        gc.arc_to(x + self.width,
                y + self.height,
                x + self.width - end_radius,
                y + self.height, end_radius)
        gc.arc_to(x, y + self.height,
                x, y,
                end_radius)
        gc.arc_to(x, y,
                x + self.width + end_radius,
                y, end_radius)
        
        gc.linear_gradient(x, y, x, y+100,
                numpy.array([starting_color, ending_color]),
                "pad")

        gc.draw_path()
        
    def __key_default(self):
        return self.value
    
    @cached_property
    def _get_label(self):
        if hasattr(self.value, 'label'):
            text = self.value.label
        else:
            text = str(self.value)
        if len(text) > 20:
            text = text[0:17] + "..."
        return text 
        
    def _value_changed(self):
        self.request_redraw()