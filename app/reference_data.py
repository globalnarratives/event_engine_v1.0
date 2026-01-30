REGIONS = {
        
    'WEU': ['ala', 'and', 'aut', 'bel', 'che', 'cze', 'deu', 'dnk', 'esp', 'fin', 'fra', 'fro', 'gbr', 'ggy', 'gib', 'grc', 'grl', 'hrv', 'imn', 'irl', 'isl', 'ita', 'jey', 'lie', 
            'lux', 'mco', 'mlt', 'nld', 'nor', 'pol', 'prt', 'sjm', 'smr', 'swe', ],
    'EEU': ['alb', 'arm', 'bgr', 'bih', 'blr', 'cyp', 'est', 'geo', 'hun', 'ltu', 'lva', 'mda', 'mkd', 'mne', 'rou', 'rus', 'srb', 'svk', 'svn', 'ukr',   ],
    'NAM': ['bmu', 'can', 'mex', 'spm',  'usa', ],
    'SAM': ['arg', 'bol', 'bra', 'chl', 'col', 'ecu', 'flk', 'guf', 'per', 'phl', 'pry', 'ury', 'ven', ],
    'NEA': ['chn', 'hkg', 'jpn', 'kor', 'mac', 'mng', 'prk', 'twn', ],
    'SEA': ['brn', 'idn', 'khm', 'lao', 'mmr', 'mys', 'sgp', 'tha', 'tls', 'vnm',  ],
    'OCE': ['asm', 'atf','aus', 'cck', 'cok', 'cxr', 'fij', 'fsm', 'gum', 'iot', 'kir', 'mhl', 'mnp', 'ncl', 'nfk', 'niu', 'nru', 'nzl', 'pcn', 'plw', 'png', 'pyf', 'sgs', 'slb', 
            'tkl', 'ton', 'tuv', 'umi', 'vut', 'wlf', 'wsm',    ],
    'SAS': ['bgd', 'btn', 'ind', 'lka', 'npl', 'pak',   ],
    'CAS': ['afg', 'kaz', 'kgz', 'tjk', 'tkm', 'uzb',  ],
    'MEA': ['are', 'aze', 'bhr', 'dza', 'egy', 'irn','irq', 'isr', 'jor', 'kwt', 'lbn', 'lby', 'mar', 'omn', 'pse', 'qat', 'sau', 'sdn', 'syr', 'tun', 'tur', 'yem',   ],
    'WAF': ['ben', 'bfa', 'civ', 'cmr', 'cpv', 'esh', 'gab', 'gha', 'gin', 'gmb', 'gnb', 'lbr', 'mli', 'mrt', 'ner', 'nga', 'sen', 'sle', 'stp', 'tca', 'tgo',   ],
    'EAF': ['dji', 'eri', 'eth', 'ken',  'myt', 'som', 'ssd', 'tza', 'uga',  ],
    'CAF': ['ago', 'bdi', 'caf', 'cod', 'cog', 'gnq', 'rwa', 'shn', 'zmb',   ],
    'SAF': ['bwa', 'com', 'lso', 'mdg', 'mdv', 'moz', 'mus', 'mwi', 'nam', 'reu', 'swz', 'syc', 'zaf', 'zwe',   ],
    'CMB': ['abw','aia', 'atg', 'bes', 'bhs', 'blm', 'blz', 'brb', 'cri', 'cub', 'cuw', 'cym', 'dma', 'dom', 'glp', 'grd', 'gtm', 'guy', 'hnd', 'hti', 'jam', 'kna', 'lca', 'maf', 'mst', 
            'mtq', 'nic', 'pan', 'pri', 'slv', 'sur', 'sxm', 'tca', 'tto', 'vct', 'vgb', 'vir',   ],
    'IGO': ['igo', 'vat', ],

}

REGION_NAMES = {
    'WEU': 'Western Europe',
    'EEU': 'Eastern Europe',
    'NAM': 'North America',
    'SAM': 'South America',
    'NEA': 'Northeast Asia',
    'SEA': 'Southeast Asia',
    'OCE': 'Oceania',
    'SAS': 'South Asia',
    'CAS': 'Central Asia',
    'MEA': 'Middle East',
    'WAF': 'West Africa',
    'EAF': 'East Africa',
    'CAF': 'Central Africa',
    'SAF': 'Southern Africa',
    'CMB': 'Caribbean and Central America',
    'IGO': 'IGOs'
}


# Auto-generate country → region lookup
COUNTRY_REGIONS = {}
for region, countries in REGIONS.items():
    for country in countries:
        COUNTRY_REGIONS[country] = region