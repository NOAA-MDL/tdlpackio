"""
Grid defintions of "common" grids in the MOS-2000/TDLPACK system.
"""

_blend_alaska = { 'proj4_alias': 'stere',
                  'proj': 5,
                  'nx': 1649,
                  'ny': 1105,
                  'latll': 40.5301,
                  'lonll': 178.5713,
                  'stdlat': 60.0000,
                  'orientlon': 150.0000,
                  'meshlength': 2976.560059
                 }

_blend_conus = { 'proj4_alias': 'lcc',
                 'proj': 3,
                 'nx': 2345,
                 'ny': 1597,
                 'latll': 19.2289,
                 'lonll': 126.2766,
                 'stdlat': 25.0000,
                 'orientlon': 95.0000,
                 'meshlength': 2539.702881
                }

_blend_hawaii = { 'proj4_alias': 'merc',
                  'proj': 7,
                  'nx': 625,
                  'ny': 561,
                  'latll': 14.3515,
                  'lonll': 164.9695,
                  'stdlat': 20.0000,
                  'orientlon': 160.0000,
                  'meshlength': 2500.000000
                 }

_blend_oceanic = { 'proj4_alias': 'merc',
                   'proj': 7,
                   'nx': 2517,
                   'ny': 1817,
                   'latll': -30.4192,
                   'lonll': 230.0942,
                   'stdlat': 20.0000,
                   'orientlon': 360.0000,
                   'meshlength': 10000.000000
                  }

_blend_puertorico = { 'proj4_alias': 'merc',
                      'proj': 7,
                      'nx': 353,
                      'ny': 257,
                      'latll': 16.8280,
                      'lonll': 68.1954,
                      'stdlat': 20.0000,
                      'orientlon': 65.0000,
                      'meshlength': 1250.000000
                     }

grids = { 'blend_alaska': _blend_alaska,
          'blend_conus': _blend_conus,
          'blend_hawaii': _blend_hawaii,
          'blend_oceanic': _blend_oceanic,
          'blend_puertorico': _blend_puertorico
        }
