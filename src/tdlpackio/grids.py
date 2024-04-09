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

_mos_nps_23km = { 'proj4_alias': 'stere',
                  'proj': 5,
                  'nx': 593,
                  'ny': 337,
                  'latll': 2.8320,
                  'lonll': 150.0003,
                  'stdlat': 60.0000,
                  'orientlon': 105.0000,
                  'meshlength': 23812.500000
                     }

_mos_nps_47km = { 'proj4_alias': 'stere',
                  'proj': 5,
                  'nx': 297,
                  'ny': 169,
                  'latll': 2.8320,
                  'lonll': 150.0003,
                  'stdlat': 60.0000,
                  'orientlon': 105.0000,
                  'meshlength': 47625.000000
                     }

_mos_nps_95km = { 'proj4_alias': 'stere',
                  'proj': 5,
                  'nx': 149,
                  'ny': 85,
                  'latll': 2.8320,
                  'lonll': 150.0003,
                  'stdlat': 60.0000,
                  'orientlon': 105.0000,
                  'meshlength': 95250.000000
                     }

_nammos_ncep151 = { 'proj4_alias': 'stere',
                    'proj': 5,
                    'nx': 425,
                    'ny': 281,
                    'latll': 0.7279,
                    'lonll': 150.3583,
                    'stdlat': 60.0000,
                    'orientlon': 110.0000,
                    'meshlength': 33812.000000
                  }

_nammos_ncep221_exp = { 'proj4_alias': 'lcc',
                        'proj': 3,
                        'nx': 349,
                        'ny': 198,
                        'latll': 9.5803,
                        'lonll': 150.7806,
                        'stdlat': 50.0000,
                        'orientlon': 107.0000,
                        'meshlength': 32463.410156
                      }

grids = { 'nbmak': _blend_alaska,
          'nbmco': _blend_conus,
          'nbmhi': _blend_hawaii,
          'nbmoc': _blend_oceanic,
          'nbmpr': _blend_puertorico,
          'gfs23': _mos_nps_23km,
          'gfs47': _mos_nps_47km,
          'gfs95': _mos_nps_95km,
          'nam151': _nammos_ncep151,
          'nam221': _nammos_ncep221_exp
        }
