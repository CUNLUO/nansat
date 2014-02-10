# Name:    nansat_map.py
# Purpose: Container of NansatMap class
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

from nansat_tools import *


class Nansatmap(Basemap):
    '''Perform opeartions with graphical files: create,
    add legend and geolocation_grids, save.

    | NansatMap instance is created in the Nansat.write_map method.
    | The methods below are applied consequently in order to get projection,
      generate a basemap from array(s), add legend and geolocation grids,
      save to a file.

    '''
    # general attributes
    cmap = cm.jet
    colorbar = None
    mpl = []
    lon, lat, x, y = None, None, None, None
    # parameters for smoothing
    # convolve
    convolve_weightSize = 7
    convolve_weights = None
    convolve_mode = 'reflect'
    convolve_cval = 0.0
    convolve_origin = 0
    # fourier_gaussian
    fourier_sigma = 1.0
    fourier_n = -1
    fourier_axis = -1
    # spline
    spline_order = 3
    spline_axis = -1
    # gaussian filter
    gaussian_sigma = 2.5
    gaussian_order = 0
    gaussian_mode = 'reflect'
    gaussian_cval = 0.0
    # saving parameters
    DEFAULT_EXTENSION = '.png'

    def __init__(self, domain, **kwargs):
        ''' Set attributes

        Get proj4 from the given domain and convert the proj4 projection to
        the basemap projection.

        Parameters
        -----------
        domain : domain object
        kwargs : dictionary
            parameters that are used for all operations.

        Attributes
        ----------
        fig : figure
            matplotlib.pyplot.figure
        colorbar : boolean
            | if colorbar is True, it is possible to put colorbar.
            | e.g. contour_plots(contour_style='fill'), put_color()
        mpl : list
            elements are matplotlib.contour.QuadContourSet instance,
                         matplotlib.quiver.Quiver instance or
                         matplotlib.collections.QuadMesh object
        cmap : default cm.jet
        colorbar : default None
        mpl : default []
        lon : default None
        lat : default None
        x : default None
        y : default None
        convolve_weightSize : default 7
        convolve_weights : default None
        convolve_mode : default 'reflect'
        convolve_cval : default 0.0
        convolve_origin : default 0
        fourier_sigma : default 1.0
        fourier_n : default -1
        fourier_axis : default -1
        spline_order : default 3
        spline_axis : default -1
        gaussian_sigma : default 2.5
        gaussian_order : default 0
        gaussian_mode : default 'reflect'
        gaussian_cval : default 0.0
        DEFAULT_EXTENSION : default '.png'

        References
        ----------
        basemap() : http://matplotlib.org/basemap/api/basemap_api.html

        '''
        self.domain = domain

        # get proj4
        spatialRef = osr.SpatialReference()
        projection = domain.vrt.get_projection()
        spatialRef.ImportFromWkt(projection)
        proj4 = spatialRef.ExportToProj4()

        # convert proj4 to basemap projection
        projStr = proj4.split(' ')[0][6:]
        projection = {'aea': 'aea', 'ocea': 'aea',
                      'aeqd': 'aeqd', 'xxx1': 'spaeqd', 'xxx2': 'npaeqd',
                      'cass': 'cass',
                      'cea': 'cea',
                      'eqc': 'cyl', 'longlat': 'cyl',
                      'eck4': 'eck4',
                      'eqdc': 'eqdc',
                      'gall': 'gall',
                      'geos': 'geos',
                      'gnom': 'gnom',
                      'hammer': 'hammer', 'nell_h': 'hammer',
                      'kav7': 'kav7',
                      'laea': 'laea', 'xxx3': 'splaea', 'xxx4': 'nplaea',
                      'lcc': 'lcc', 'lcca': 'lcc',
                      'mbtfpq': 'mbtfpq',
                      'somerc': 'merc', 'merc': 'merc', 'omerc': 'merc',
                      'mill': 'mill',
                      'moll': 'moll',
                      'nsper': 'nsper',
                      'omerc': 'omerc',
                      'ortho': 'ortho',
                      'poly': 'poly', 'rpoly': 'poly', 'imw_p': 'poly',
                      'robin': 'robin',
                      'sinu': 'sinu', 'fouc_s': 'sinu', 'gn_sinu': 'sinu',
                      'mbtfps': 'sinu', 'urmfps': 'sinu',
                      'stere': 'stere', 'sterea': 'stere', 'lee_os': 'stere',
                      'mil_os': 'stere', 'rouss': 'stere',
                      'ups': 'npstere', 'ups': 'spstere',  # CHECK!!
                      'tmerc': 'tmerc', 'gstmerc': 'tmerc', 'utm': 'tmerc',
                      'vandg': 'vandg', 'vandg2': 'vandg',
                      'vandg3': 'vandg', 'vandg4': 'vandg',
                      }.get(projStr, 'cyl')

        if projection in ['stere']:
            lon_0 = float(re.findall('lon_0=+[-+]?\d*[.\d*]*',
                                     proj4)[0].split('=')[1])
            lat_0 = float(re.findall('lat_0=+[-+]?\d*[.\d*]*',
                                     proj4)[0].split('=')[1])
            kwargs['lon_0'] = lon_0
            kwargs['lat_0'] = lat_0

        self.extensionList = ['png', 'emf', 'eps', 'pdf', 'rgba',
                              'ps', 'raw', 'svg', 'svgz']

        # set llcrnrlat, urcrnrlat, llcrnrlon and urcrnrlon to kwargs.
        # if required, modify them from -90. to 90.
        # get min/max lon/lat
        lonCrn, latCrn = domain.get_corners()
        self.lonMin = min(lonCrn)
        self.lonMax = max(lonCrn)
        self.latMin = max(min(latCrn), -90.)
        self.latMax = min(max(latCrn), 90.)

        if not('llcrnrlat' in kwargs.keys()):
            kwargs['llcrnrlat'] = self.latMin
        if not('urcrnrlat' in kwargs.keys()):
            kwargs['urcrnrlat'] = self.latMax
        if not('llcrnrlon' in kwargs.keys()):
            kwargs['llcrnrlon'] = self.lonMin
        if not('urcrnrlon' in kwargs.keys()):
            kwargs['urcrnrlon'] = self.lonMax

        # separate kwarge of plt.figure() from kwargs
        figArgs = ['num', 'figsize', 'dpi', 'facecolor', 'edgecolor',
                   'frameon']
        figKwargs = {}
        for iArg in figArgs:
            if iArg in kwargs.keys():
                figKwargs[iArg] = kwargs.pop(iArg)

        Basemap.__init__(self, projection=projection, **kwargs)

        # create figure and set it as an attribute
        plt.close()
        self.fig = plt.figure(**figKwargs)

    def smooth(self, idata, mode, **kwargs):
        '''Smooth data for contour() and contourf()

        idata is smoothed by convolve, fourier_gaussian, spline or
        gaussian (default). If contour_mode is 'convolve' and weight is None,
        the weight matrix is created automatically.

        Parameters
        -----------
        idata : numpy 2D array
            Input data
        mode : string
            'convolve','fourier','spline' or 'gaussian'

        Returns
        ---------
        odata : numpy 2D array

        References
        ----------
        scipy.ndimage() :
            http://docs.scipy.org/doc/scipy/reference/ndimage.html

        '''
        # modify default parameter
        self._set_defaults(kwargs)

        if mode == 'convolve':
            # if weight is None, create a weight matrix
            if self.convolve_weights is None:
                weights = np.ones((self.convolve_weightSize,
                                   self.convolve_weightSize))
                center = (self.convolve_weightSize - 1) / 2
                for i in range(- (center), center + 1, 1):
                    for j in range(- (center), center + 1, 1):
                        weights[i][j] /= pow(2.0, max(abs(i), abs(j)))
                self.convolve_weights = weights
            odata = ndimage.convolve(idata,
                                     weights=self.convolve_weights,
                                     mode=self.convolve_mode,
                                     cval=self.convolve_cval,
                                     origin=self.convolve_origin)
        elif mode == 'fourier':
            odata = ndimage.fourier_gaussian(idata,
                                             sigma=self.fourier_sigma,
                                             n=self.fourier_n,
                                             axis=self.fourier_axis)
        elif mode == 'spline':
            odata = ndimage.spline_filter1d(idata,
                                            order=self.spline_order,
                                            axis=self.spline_axis)
        else:
            if mode != 'gaussian':
                print 'apply Gaussian filter in image_process()'
            odata = ndimage.gaussian_filter(idata,
                                            sigma=self.gaussian_sigma,
                                            order=self.gaussian_order,
                                            mode=self.gaussian_mode,
                                            cval=self.gaussian_cval)
        return odata

    def _do_contour(self, bmfunc, data, v, smooth, mode, **kwargs):
        ''' Prepare data and make contour or contourf plots

        | Smooth data
        | Add colormap
        | Append contour or contourf plot to self.mpl

        Parameters
        -----------
        bmfunc : Basemap function
            Basemap.contour, Basemap.contourf
        data : numpy 2D array
            Input data
        v : list with values
            draw contour lines at the values specified in sequence v
        smooth : Boolean
            Apply smoothing?
        mode : string
            'gaussian', 'spline', 'fourier', 'convolve'
            mname of smoothing algorithm to apply

        '''
        self._create_xy_grids()

        # if cmap is given, set to self.cmap
        if 'cmap' in kwargs.keys():
            self.cmap = kwargs.pop('cmap')

        # smooth data
        if smooth:
            data = self.smooth(data, mode, **kwargs)

        # draw contour lines
        if v is None:
            self.mpl.append(bmfunc(self, self.x, self.y, data, **kwargs))
        else:
            self.mpl.append(bmfunc(self, self.x, self.y, data, v, **kwargs))

    def contour(self, data, v=None, smooth=False, mode='gaussian',
                label=True, **kwargs):
        '''Draw lined contour plots

        If smooth is True, data is smoothed. Then draw lined contour.

        Parameters
        ----------
        data : numpy 2D array
            Input data
        v : list with values
            draw contour lines at the values specified in sequence v
        smooth : Boolean
            Apply smoothing?
        mode : string
            'gaussian', 'spline', 'fourier', 'convolve'
            mname of smoothing algorithm to apply
        label : boolean
            Add lables?
        **kwargs:
            | Optional parameters for Nansatmap.smooth()
            | Optional parameters for pyplot.contour().
            | Optional parameters for pyplot.clabel()

        Modifies
        ---------
        self.mpl : list
            append QuadContourSet instance
        '''

        self._do_contour(Basemap.contour, data, v, smooth, mode, **kwargs)

        # add lables to the contour lines
        if label:
            plt.clabel(self.mpl[-1], **kwargs)

    def contourf(self, data, v=None,
                 smooth=False, mode='gaussian', **kwargs):
        '''Draw filled contour plots

        If smooth is True, data is smoothed. Then draw filled contour.

        Parameters
        ----------
        data : numpy 2D array
            Input data
        v : list with values
            draw contour lines at the values specified in sequence v
        smooth : Boolean
            Apply smoothing?
        mode : string
            'gaussian', 'spline', 'fourier', 'convolve'
            mname of smoothing algorithm to apply
        **kwargs:
            | cmap : colormap (e.g. cm.jet)
            | Optional parameters for Nansatmap.smooth()
            | Optional parameters for pyplot.contourf().

        Modifies
        ---------
        self.mpl : list
            append QuadContourSet instance

        '''
        self._do_contour(Basemap.contourf, data, v, smooth, mode, **kwargs)
        self.colorbar = len(self.mpl) - 1

    def pcolormesh(self, data, validValues=None, **kwargs):
        '''Make a pseudo-color plot over the map

        Parameters
        ----------
        data : numpy 2D array
            Input data
        validValues : list with two scalars (e.g. [min, max])
            minimum and maximum valid values
        Parameters of Basemap.pcolormesh

        Modifies
        ---------
        self.mpl : list
            append matplotlib.collections.QuadMesh object

        '''
        # mask nan data
        data = np.ma.array(data, mask=np.isnan(data))
        # Plot a quadrilateral mesh.
        self._create_xy_grids()
        self.mpl.append(Basemap.pcolormesh(self, self.x, self.y, data,
                                           **kwargs))
        self.colorbar = len(self.mpl) - 1

    def quiver(self, dataX, dataY, quivectors=30, **kwargs):
        '''Draw quiver plots

        Parameters
        ----------
        dataX :  numpy array
            Input data with X-component
        dataY :  numpy array
            Input data with Y-component
        quivectors : int
            Number of vectors along both dimentions
        Parameters of Basemap.quiver()

        Modifies
        ---------
        self.mpl : list
            append matplotlib.quiver.Quiver instance

        '''
        # if Nan is included, apply mask
        dataX = np.ma.array(dataX, mask=np.isnan(dataX))
        dataY = np.ma.array(dataY, mask=np.isnan(dataY))
        # subset grids for quiver plot
        if type(quivectors) in [list, tuple]:
            quivectors0 = quivectors[0]
            quivectors1 = quivectors[1]
        else:
            quivectors0 = quivectors
            quivectors1 = quivectors
        step0 = dataX.shape[0] / quivectors0
        step1 = dataX.shape[1] / quivectors1
        dataX2 = dataX[::step0, ::step1]
        dataY2 = dataY[::step0, ::step1]
        self._create_lonlat_grids()
        lon2 = self.lon[::step0, ::step1]
        lat2 = self.lat[::step0, ::step1]
        x2, y2 = self(lon2, lat2)
        self.mpl.append(Basemap.quiver(self, x2, y2, dataX2, dataY2, **kwargs))

    def add_colorbar(self, fontsize=6, **kwargs):
        '''Add color bar

        Parameters
        ----------
        fontsize : int
        Parameters for matplotlib.pyplot.colorbar

        Modifies
        ---------
        Adds colorbar to self.fig

        '''
        if kwargs is None:
            kwargs = {}
        if not ('orientation' in kwargs.keys()):
            kwargs['orientation'] = 'horizontal'
        if not ('pad' in kwargs.keys()):
            kwargs['pad'] = 0.01

        # add colorbar and set font size
        if self.colorbar is not None:
            cbar = self.fig.colorbar(self.mpl[self.colorbar], **kwargs)
            imaxes = plt.gca()
            plt.axes(cbar.ax)
            plt.xticks(fontsize=fontsize)
            plt.axes(imaxes)

    def drawgrid(self, fontsize=10, lat_num=5, lon_num=5,
                 lat_labels=[True, False, False, False],
                 lon_labels=[False, False, True, False]):
        '''Draw and label parallels (lat and lon lines) for values (in degrees)

        Parameters
        -----------
        fontsize : int
        lat_num : int
            Number of latitude lables
        lon_num :
            Number of longitude lables
        lat_labels : list of Bool
            Location of latitude labels
        lon_labels : list of Bool
            Location of longitude labels

        References
        ----------
        Basemap.drawparallels() :
            http://matplotlib.org/basemap/api/basemap_api.html#mpl_toolkits.basemap.Basemap.drawparallels
        Basemap.drawmeridians() :
            http://matplotlib.org/basemap/api/basemap_api.html#mpl_toolkits.basemap.Basemap.drawmeridians

        '''
        self.drawparallels(np.arange(self.latMin, self.latMax,
                           (self.latMax - self.latMin) / lat_num),
                           labels=lat_labels,
                           fontsize=fontsize)
        self.drawmeridians(np.arange(self.lonMin, self.lonMax,
                           (self.lonMax - self.lonMin) / lon_num),
                           labels=lon_labels,
                           fontsize=fontsize)

    def draw_continents(self, **kwargs):
        ''' Draw continents

        Parameters
        ----------
        Parameters of basemap.fillcontinents

        '''
        if kwargs is None:
            kwargs = {}
        if not ('color' in kwargs.keys()):
            kwargs['color'] = '#999999'
        if not ('lake_color' in kwargs.keys()):
            kwargs['lake_color'] = '#99ffff'

        # draw continets
        self.fillcontinents(**kwargs)

    def save(self, fileName, landmask=True, **kwargs):
        '''Draw continents and save

        Parameters
        -----------
        fileName : string
            name of outputfile
        landmask : Boolean
            Draw landmask?
        Parameters of basemap.fillcontinents

        '''
        if landmask:
            self.draw_continents(**kwargs)

        # set default extension
        if not((fileName.split('.')[-1] in self.extensionList)):
            fileName = fileName + self.DEFAULT_EXTENSION
        self.fig.savefig(fileName)

    def _set_defaults(self, idict):
        '''Check input params and set defaut values

        Look throught default parameters (self.d) and given parameters (dict)
        and paste value from input if the key matches

        Parameters
        ----------
        idict : dictionary
            parameter names and values

        Modifies
        ---------
        default self attributes

        '''
        for key in idict:
            if hasattr(self, key):
                setattr(self, key, idict[key])

    def _create_lonlat_grids(self):
        '''Generate grids with lon/lat coordinates in each cell

        Modifies
        ---------
        self.lon : numpy array with lon coordinates
        self.lat : numpy array with lat coordinates

        '''
        if self.lon is None or self.lat is None:
            self.lon, self.lat = self.domain.get_geolocation_grids()

    def _create_xy_grids(self):
        '''Generate grids with x/y coordinates in each cell

        Modifies
        ---------
        self.x : numpy array with X coordinates
        self.y : numpy array with Y coordinates

        '''
        self._create_lonlat_grids()
        if self.x is None or self.y is None:
            self.x, self.y = self(self.lon, self.lat)
