# Name:    nansat_tools.py
# Purpose: collection of libraries used in NANSAT modules
# Authors:      Asuka Yamakawa, Anton Korosov, Knut-Frode Dagestad,
#               Morten W. Hansen, Alexander Myasoyedov,
#               Dmitry Petrenko, Evgeny Morozov
# Created:      29.06.2011
# Copyright:    (c) NERSC 2011 - 2013
# Licence:
# This file is part of NANSAT.
# NANSAT is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 3 of the License.
# http://www.gnu.org/licenses/gpl-3.0.html
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.

# import standard modules

## used in domain and nansat_tools
import os.path
import re

## used in nansat, vrt, figure
import os

## used in vrt and nansat_tools
import logging

## used in domain
from math import atan2, sin, pi, cos, acos, radians, degrees, copysign
import string
from xml.etree.ElementTree import ElementTree

## used in nansat
import dateutil.parser
import glob
import inspect
import pdb
import sys

## used in vrt
import datetime
from dateutil.parser import parse
from random import choice
from string import Template, ascii_uppercase, digits

## used in figure, nansat_map
from math import floor, log10, pow

## used in nansat_tools
import copy
import warnings
import xml.dom.minidom as xdm

# try to import additional modules
## used in domain, nansat, vrt and nansat_tools
try:
    from osgeo import gdal, osr, ogr
except ImportError:
    try:
        import gdal
        import osr
        import ogr
    except ImportError:
        warnings.warn('Cannot import GDAL!'
                      'Nansat, Vrt, Domain and nansat_tools will not work'
                      'Try installing GDAL.')

## used in nansat, domain, vrt and figure
try:
    import numpy as np
except ImportError:
    warnings.warn('Cannot import numpy!'
                  'Domain, Figure and Vrt will not work.'
                  'Try installing numpy.')

## used in domain and figure
try:
    import matplotlib.pyplot as plt
except:
    warnings.warn('Cannot import matplotlib.pyplot!'
                  'Domain.write_map() and Figure will not work'
                  'Try installing matplotlib.')

## used in nansat and figure
try:
    from matplotlib import cm
except:
    warnings.warn('Cannot import matplotlib.cm!'
                  'Nansat.write_geotiffimage and Figure will not work.'
                  'Try installing matplotlib.')

## used in domain
try:
    from matplotlib.patches import Polygon
except:
    warnings.warn('Cannot import matplotlib.patches.Polygon!'
                  'Domain.write_map() will not work'
                  'Try installing matplotlib.')

try:
    from mpl_toolkits.basemap import Basemap
except:
    warnings.warn('Cannot import mpl_toolkits.basemap.Basemap!'
                  'Domain.write_map() will not work'
                  'Try installing Basemap.')

## used in nansat
try:
    from numpy import arange
except ImportError:
    warnings.warn('Cannot import numpy.arange!'
                  'Nansat.write_geotiffimage will not work.'
                  'Try installing numpy.')

## used in figure
try:
    from numpy import outer
except ImportError:
    warnings.warn('Cannot import numpy.outer!'
                  'Figure.create_legend will not work.'
                  'Try installing numpy.')

try:
    import Image
    import ImageDraw
    import ImageFont
except ImportError:
    try:
        from PIL import Image, ImageDraw, ImageFont
    except ImportError:
        warnings.warn('Cannot import PIL!'
                      'Figure will not work'
                      'Try installing PIL.')

## used in nansat_tools and nansatmap
try:
    from scipy import mod, ndimage
except ImportError:
    warnings.warn('Cannot import scipy.mod!'
                  'nansat_toolds will not work'
                  'Try installing scipy.')

obpg = {
'red': [  (0.00, 0.56, 0.56),
          (0.19, 0.00, 0.00),
          (0.38, 0.00, 0.00),
          (0.50, 0.00, 0.00),
          (0.63, 1.00, 1.00),
          (0.88, 1.00, 1.00),
          (1.00, 0.40, 0.40)],
'green': [(0.00, 0.00, 0.00),
          (0.19, 0.00, 0.00),
          (0.38, 1.00, 1.00),
          (0.50, 1.00, 1.00),
          (0.63, 1.00, 1.00),
          (0.88, 0.00, 0.00),
          (1.00, 0.00, 0.00)],
'blue': [ (0.00, 0.43, 0.43),
          (0.19, 1.00, 1.00),
          (0.38, 1.00, 1.00),
          (0.50, 0.00, 0.00),
          (0.63, 0.00, 0.00),
          (0.88, 0.00, 0.00),
          (1.00, 0.00, 0.00)],
}

ak01 = {

'red': [  (0,0.1,0.1,),
(0.1,0.56,0.56,),
(0.22,0,0,),
(0.27,0,0,),
(0.37,0.3,0.3,),
(0.47,0,0,),
(0.52,0,0,),
(0.64,1,1,),
(0.76,1,1,),
(0.88,0.4,0.4,),
(1,1,1,)],


'green': [(0,0,0,),
(0.1,0,0,),
(0.22,0,0,),
(0.27,0,0,),
(0.37,0.6,0.6,),
(0.47,0.6,0.6,),
(0.52,1,1,),
(0.64,1,1,),
(0.76,0,0,),
(0.88,0,0,),
(1,0.5,0.5,)],


'blue': [ (0,0.1,0.1,),
(0.1,0.5,0.5,),
(0.22,0.5,0.5,),
(0.27,1,1,),
(0.37,1,1,),
(0.47,0,0,),
(0.52,0,0,),
(0.64,0,0,),
(0.76,0,0,),
(0.88,0,0,),
(1,0.5,0.5,)],



}
try:
    cm.register_cmap(name='obpg', data=obpg, lut=256)
    cm.register_cmap(name='ak01', data=ak01, lut=256)
except:
    warnings.warn('Cannot generate and register the OBPG colormap!')

class Error(Exception):
    '''Base class for exceptions in this module.'''
    pass


class OptionError(Error):
    '''Error for improper options (arguments) '''
    pass


class ProjectionError(Error):
    '''Cannot get the projection'''
    pass


class GDALError(Error):
    '''Error from GDAL '''
    pass


class PointBrowser():
    '''
    Click on points and get the X-Y coordinates.

    '''
    def __init__(self, data, **kwargs):
        self.fig = plt.figure()
        self.data = data
        self.ax = self.fig.add_subplot(111)
        img = self.ax.imshow(self.data, extent=(0, self.data.shape[1],
                                                0, self.data.shape[0]),
                             origin='lower', **kwargs)
        self.fig.colorbar(img)
        self.points, = self.ax.plot([], [], '+', ms=12, color='b')
        self.line, = self.ax.plot([], [])
        self.coordinates = []

    def onclick(self, event):
        if event.xdata is not None and event.ydata is not None:
            self.coordinates.append((event.xdata, event.ydata))
            tCoordinates = map(tuple, zip(*self.coordinates))
            self.points.set_data(tCoordinates)
            self.points.figure.canvas.draw()
            self.line.set_data(tCoordinates)
            self.line.figure.canvas.draw()

    def get_points(self):
        self.fig.canvas.mpl_connect('button_press_event', self.onclick)
        self.fig.axes[0].set_xlim([0, self.data.shape[1]])
        self.fig.axes[0].set_ylim([0, self.data.shape[0]])
        text = "1. Please click on the figure and mark a point or draw a line.\n2. Then close the figure."
        plt.text(0, int(self.data.shape[0]*1.05), text, fontsize=13,
                 verticalalignment='top', horizontalalignment='left')
        plt.gca().invert_yaxis()
        plt.show()


class Node(object):
    '''
    Rapidly assemble XML using minimal coding.

    By Bruce Eckel, (c)2006 MindView Inc. www.MindView.net
    Permission is granted to use or modify without payment as
    long as this copyright notice is retained.

    Everything is a Node, and each Node can either have a value
    or subnodes. Subnodes can be appended to Nodes using '+=',
    and a group of Nodes can be strung together using '+'.

    Create a node containing a value by saying
    Node('tag', 'value')
    You can also give attributes to the node in the constructor:
    Node('tag', 'value', attr1 = 'attr1', attr2 = 'attr2')
    or without a value:
    Node('tag', attr1 = 'attr1', attr2 = 'attr2')

    To produce xml from a finished Node n, say n.xml() (for
    nicely formatted output) or n.rawxml().

    You can read and modify the attributes of an xml Node using
    getAttribute(), setAttribute(), or delAttribute().

    You can find the value of the first subnode with tag == 'tag'
    by saying n['tag']. If there are multiple instances of n['tag'],
    this will only find the first one, so you should use node() or
    nodeList() to narrow your search down to a Node that only has
    one instance of n['tag'] first.

    You can replace the value of the first subnode with tag == 'tag'
    by saying n['tag'] = newValue. The same issues exist as noted
    in the above paragraph.

    You can find the first node with tag == 'tag' by saying
    node('tag'). If there are multiple nodes with the same tag
    at the same level, use nodeList('tag').

    The Node class is also designed to create a kind of 'domain
    specific language' by subclassing Node to create Node types
    specific to your problem domain.

    This implementation uses xml.dom.minidom which is available
    in the standard Python 2.4 library. However, it can be
    retargeted to use other XML libraries without much effort.

    '''

    def __init__(self, tag, value=None, **attributes):
        '''Everything is a Node. The XML is maintained as (very efficient)
        Python objects until an XML representation is needed.

        '''
        self.tag = tag.strip()
        self.attributes = attributes
        self.children = []
        self.value = value
        if self.value:
            self.value = self.value.strip()

    def getAttribute(self, name):
        ''' Read XML attribute of this node. '''
        return self.attributes[name]

    def setAttribute(self, name, item):
        ''' Modify XML attribute of this node. '''
        self.attributes[name] = item

    def delAttribute(self, name):
        ''' Remove XML attribute with this name. '''
        del self.attributes[name]

    def replaceAttribute(self, name, value):
        ''' replace XML arrtibute of this node. '''
        del self.attributes[name]
        self.attributes[name] = value

    def node(self, tag, elemNum=0):
        ''' Recursively find the first subnode with this tag.

        elemNum : int
            if there are several same tag, specify which element to take.

        '''
        if self.tag == tag:
            return self
        ielm = 0
        for child in self.children:
            result = child.node(tag)
            if result and ielm == elemNum:
                return result
            elif result:
                ielm += 1
        return False


    def replaceNode(self, tag, elemNum=0, newNode=None):
        ''' Find the first subnode with this tag and replace with given node.

        tag : str
            node tag
        elemNum : int
            number of subnode among other subnodes with similar tag

        '''
        status = False
        elemi = 0
        for i in range(len(self.children)):
            if str(self.children[i].tag) == tag:
                if elemi == elemNum:
                    self.children[i] = newNode
                    status = True
                    break
                else:
                    elemi += 1
        return status

    def delNode(self, tag, options=None):
        '''
        Recursively find the all subnodes with this tag and remove
        from self.children.

        options : dictionary
            if there are several same tags, specify a node by their attributes.

        '''
        for i, child in enumerate(self.children):
            if child.node(tag) and options is None:
                self.children.pop(i)
            elif child.node(tag):
                for j, jKey in enumerate(options.keys()):
                    try:
                        if (child.getAttribute(jKey) == str(options[jKey]) and
                                len(options.keys()) == j+1):
                            self.children.pop(i)
                    except:
                        break
            else:
                child.delNode(tag)

    def find_dom_child(self, dom, tagName, n=0):
        '''Recoursively find child of the dom'''
        children = dom.childNodes
        theChild = None
        
        chn = 0
        for child in children:
            print child, child.nodeType, chn
            if child.nodeType == 1:
                print child.tagName
                if str(child.tagName) == tagName:
                    print child.tagName, tagName, 'OK'
                    if chn == n:
                        theChild = child
                    chn += 1
    
            if theChild is not None:
                break
    
            if child.hasChildNodes():
                print 'has childs'
                theChild = self.find_dom_child(child, tagName, n)
            
        
        return theChild

    def _replace_dom_Node(self, tag, nodeNumber, contents):
        '''Replace child node with new contents'''

        dom0 = self.dom()
        oldChild = self.find_dom_child(dom0, tag, nodeNumber)
        newChild = xdm.parseString(contents).childNodes[0]
        dom0.replaceChild(newChild, oldChild)
        
        return Node.create(dom0)

    def nodeList(self, tag):
        '''
        Produce a list of subnodes with the same tag.
        Note:
        It only makes sense to do this for the immediate
        children of a node. If you went another level down,
        the results would be ambiguous, so the user must
        choose the node to iterate over.

        '''
        return [n for n in self.children if n.tag == tag]

    def tagList(self):
        ''' Produce a list of all tags of the immediate children '''
        taglist = []
        for iTag in range(len(self.children)):
            taglist.append(str(self.children[iTag].tag))
        return taglist

    def replaceTag(self, oldTag, newTag):
        ''' Replace tag name '''
        tags = self.tagList()
        for itag, itagName in enumerate(tags):
            if itagName == oldTag:
                self.node(self.tag).children[itag].tag = newTag

    def getAttributeList(self):
        ''' get attributes and valuse from the node and return their lists '''
        nameList = []
        valList = []
        for key, val in self.attributes.items():
            nameList.append(key)
            valList.append(val)
        return nameList, valList

    def insert(self, contents):
        ''' return Node of the node with inserted <contents>'''
        dom2 = xdm.parseString(contents)
        dom1 = xdm.parseString(self.dom().toxml())
        dom1.childNodes[0].appendChild(dom1.importNode(dom2.childNodes[0],
                                                       True))
        return Node.create(dom1)

    def __getitem__(self, tag):
        '''
        Produce the value of a single subnode using operator[].
        Recursively find the first subnode with this tag.
        If you want duplicate subnodes with this tag, use
        nodeList().

        '''
        subnode = self.node(tag)
        if not subnode:
            raise KeyError
        return subnode.value

    def __setitem__(self, tag, newValue):
        '''
        Replace the value of the first subnode containing 'tag'
        with a new value, using operator[].

        '''
        assert isinstance(newValue, str), ('Value %s must be a string'
                                           % str(newValue))
        subnode = self.node(tag)
        if not subnode:
            raise KeyError
        subnode.value = newValue

    def __iadd__(self, other):
        ''' Add child nodes using operator += '''
        assert isinstance(other, Node), 'Tried to += ' + str(other)
        self.children.append(other)
        return self

    def __add__(self, other):
        ''' Allow operator + to combine children '''
        return self.__iadd__(other)

    def __str__(self):
        ''' Display this object (for debugging) '''
        result = self.tag + '\n'
        for k, v in self.attributes.items():
            result += '    attribute: %s = %s\n' % (k, v)
        if self.value:
            result += '    value: [%s]' % self.value
        return result

    # The following are the only methods that rely on the underlying
    # Implementation, and thus the only methods that need to change
    # in order to retarget to a different underlying implementation.

    # A static dom implementation object, used to create elements:
    doc = xdm.getDOMImplementation().createDocument(None, None, None)

    def dom(self):
        '''
        Lazily create a minidom from the information stored
        in this Node object.

        '''
        element = Node.doc.createElement(self.tag)
        for key, val in self.attributes.items():
            element.setAttribute(key, val)
        if self.value:
            assert not self.children, ('cannot have value and children: %s'
                                       % str(self))
            element.appendChild(Node.doc.createTextNode(self.value))
        else:
            for child in self.children:
                element.appendChild(child.dom())  # Generate children as well
        return element

    def xml(self, separator='  '):
        return self.dom().toprettyxml(separator)

    def rawxml(self):
        return str(self.dom().toxml())

    @staticmethod
    def create(dom):
        '''
        Create a Node representation, given either
        a string representation of an XML doc, or a dom.

        '''
        if isinstance(dom, str):
            if os.path.exists(dom):
                # parse input file
                dom = xdm.parse(dom)
            else:
                # Strip all extraneous whitespace so that
                # text input is handled consistently:
                dom = re.sub('\s+', ' ', dom)
                dom = dom.replace('> ', '>')
                dom = dom.replace(' <', '<')
                return Node.create(xdm.parseString(dom))
        if dom.nodeType == dom.DOCUMENT_NODE:
            return Node.create(dom.childNodes[0])
        if dom.nodeName == '#text':
            return
        node = Node(dom.nodeName)
        if dom.attributes:
            for name, val in dom.attributes.items():
                node.setAttribute(name, val)
        for n in dom.childNodes:
            if n.nodeType == n.TEXT_NODE and n.wholeText.strip():
                node.value = n.wholeText
            else:
                subnode = Node.create(n)
                if subnode:
                    node += subnode
        return node


def initial_bearing(lon1, lat1, lon2, lat2):
        '''Initial bearing when traversing from point1 (lon1, lat1)
        to point2 (lon2, lat2)

        See http://www.movable-type.co.uk/scripts/latlong.html

        Parameters
        ----------
        lon1, lat1 : float
            longitude and latitude of start point
        lon2, lat2 : float
            longitude and latitude of end point

        Returns
        -------
        initial_bearing : float
            The initial bearing (azimuth direction) when heading out
            from the start point towards the end point along a great circle.

        '''
        rlon1 = np.radians(lon1)
        rlat1 = np.radians(lat1)
        rlon2 = np.radians(lon2)
        rlat2 = np.radians(lat2)
        deltalon = rlon2 - rlon1
        bearing = np.arctan2(np.sin(rlon2 - rlon1) * np.cos(rlat2),
                             np.cos(rlat1) * np.sin(rlat2) -
                             np.sin(rlat1) * np.cos(rlat2) *
                             np.cos(rlon2 - rlon1))
        return mod(np.degrees(bearing) + 360, 360)

def haversine(lon1, lat1, lon2, lat2):
    """ 
    Calculate the great circle distance between two points 
    on the spherical earth (specified in decimal degrees)
    """                      
    # convert decimal degrees to radians  
    lon1, lat1, lon2, lat2 = map(np.radians, [lon1, lat1, lon2, lat2])
    # haversine formula 
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = np.sin(dlat/2)**2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon/2)**2
    c = 2 * np.arcsin(np.sqrt(a))
    distance_meters = 6367000 * c
    return distance_meters

def add_logger(logName='', logLevel=None):
    ''' Creates and returns logger with default formatting for Nansat

    Parameters
    -----------
    logName : string, optional
        Name of the logger

    Returns
    --------
    logging.logger

    See also
    --------
    http://docs.python.org/howto/logging.html

    '''
    if logLevel is not None:
        os.environ['LOG_LEVEL'] = str(logLevel)
    # create (or take already existing) logger
    # with default logging level WARNING
    logger = logging.getLogger(logName)
    logger.setLevel(int(os.environ['LOG_LEVEL']))

    # if logger already exits, default stream handler has been already added
    # otherwise create and add a new handler
    if len(logger.handlers) == 0:
        # create console handler and set level to debug
        ch = logging.StreamHandler()
        # create formatter
        formatter = logging.Formatter('%(asctime)s|%(levelno)s|%(module)s|'
                                      '%(funcName)s|%(message)s',
                                      datefmt='%I:%M:%S')
        # add formatter to ch
        ch.setFormatter(formatter)
        # add ch to logger
        logger.addHandler(ch)

    logger.handlers[0].setLevel(int(os.environ['LOG_LEVEL']))

    return logger


def set_defaults(dictionary, newParm):
        '''Check input params and set defaut values

        Look throught default parameters (self.d) and given parameters (dict)
        and paste value from input if the key matches

        Parameters
        ----------
        dict : dictionary
            parameter names and values

        Modifies
        ---------
        self.d

        '''
        for key in newParm:
            if key in dictionary:
                dictionary[key] = newParm[key]

        return dictionary
