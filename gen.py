#!/usr/bin/env python3
"""Joinwell Joinery static site generator. One data file, every page.
Copy comes from the client's own captions, TradeTap text and Facebook reviews (assets/)."""
import json, os, re, html, shutil
from pathlib import Path

ROOT = Path(__file__).parent
LIB = Path.home() / '.claude/skills/signature-web/library/base'
M = json.load(open(ROOT / 'img/manifest.json'))
DOMAIN = ''  # no confirmed domain yet; set it before launch (canonical + og:image become absolute)
SITE = DOMAIN or 'https://joinwelljoinery.co.uk'  # assumed for sitemap/robots: no DNS record on 2026-10-01, confirm with the client
PHONE_D, PHONE_T = '+44 7948 347730', '+447948347730'
EMAIL = 'joinwellj@gmail.com'
FB = 'https://www.facebook.com/profile.php?id=100042636765929'
FB_REVIEWS = FB + '&sk=reviews'
IG = 'https://www.instagram.com/joinwelljoinery/'
MYBUILDER = 'https://www.mybuilder.com/profile/joinwell_joinery'
LEGAL = ('Joinwell Joinery Ltd. Registered in England and Wales, Company No. 15997981. '
         'Registered office: Office 17 Boundary Road Business Centre, Boundary Road, Lytham St Annes, FY8 5LT.')
AREA = ['Kirkham', 'Lytham', 'Blackpool', 'Preston', 'Manchester', 'Cheshire']
LD = {'@context': 'https://schema.org', '@type': 'HomeAndConstructionBusiness', 'name': 'Joinwell Joinery', 'legalName': 'Joinwell Joinery Ltd', 'telephone': PHONE_T, 'email': EMAIL, 'areaServed': AREA + ['North West England'], 'sameAs': [FB, IG]}
e = html.escape

def stems(prefix, drop=()):
    out = [s for s in M if s.startswith(prefix + '-') and not s.startswith('_') and re.fullmatch(re.escape(prefix) + r'-\d+', s)]
    out.sort(key=lambda s: int(s.rsplit('-', 1)[1]))
    return [s for s in out if s not in drop]

def best(stem, target):
    ws = M[stem]['widths']
    ok = [w for w in ws if w >= target]
    return min(ok) if ok else max(ws)

def img(stem, sizes, alt, cls='', lazy=True, attrs=''):
    m = M[stem]; ws = m['widths']
    srcset = ', '.join(f'/img/g/{stem}-{w}.webp {w}w' for w in ws)
    src = f'/img/g/{stem}-{best(stem, 960)}.webp'
    la = ' loading="lazy" decoding="async"' if lazy else ' fetchpriority="high"'
    c = f' class="{cls}"' if cls else ''
    return f'<img{c} src="{src}" srcset="{srcset}" sizes="{sizes}" width="{m["w"]}" height="{m["h"]}" alt="{e(alt)}"{la}{attrs}>'

def big(stem):
    return f'/img/g/{stem}-{best(stem, 2000)}.webp'

# ------------------------------------------------------------------ data
SERV = {
  'kitchens': 'Kitchens', 'wardrobes': 'Wardrobes', 'media-walls': 'Media walls',
  'bathrooms': 'Bathrooms', 'staircases': 'Staircases', 'renovations': 'Renovations'}

P = [
 dict(slug='black-kitchen-and-island', title='Black kitchen and island', svc=['kitchens'], place=None,
      sub='Designed with purpose. Finished to perfection.',
      lead='A handleless kitchen in matt black: an island with seating and a worktop that runs down to the floor, and a run of tall units with lit open shelving.',
      rest=['Designed by us, manufactured in our workshop and installed by our team.'],
      details='Matt black, handleless · Island with seating · Lit open shelving',
      photos=stems('p03'), cover='p03-1', second='p03-3', band=['p03-1', 'p03-5', 'p03-3']),
 dict(slug='poolside', title='Poolside', svc=['staircases', 'wardrobes', 'bathrooms'], place=None,
      sub='A staircase, a walk-in wardrobe and a vanity unit for one house.',
      lead='An ash staircase designed and manufactured in our workshop, stained black then lacquered, with the glass templated to the strings. Upstairs, a walk-in wardrobe and a floating vanity unit.',
      rest=['The vanity unit is in Ares Beton, a Xylocleaf board, on the handleless Gola profile in matt black to match the rest of the bathroom furniture.',
            'The walk-in wardrobe pairs light boards with matt black rails and knobs, with hanging, shelving and drawers planned around the room.'],
      details='Ash, stained black · Xylocleaf Ares Beton · Matt black ironmongery',
      photos=stems('p43', drop=('p43-7', 'p43-8', 'p43-9')) + stems('p45') + stems('p46', drop=('p46-8', 'p46-9')),
      cover='p43-4', second='p45-2', band=['p43-4', 'p46-3', 'p45-2']),
 dict(slug='nookwood', title='Nookwood', svc=['kitchens'], place=None,
      sub='A kitchen chosen to flow with the rest of the house.',
      lead='A bespoke kitchen in Xylocleaf Santos Grey, chosen because it flows with the interior throughout the house. Handleless on the Gola profile, with a full wall of tall units and an island.',
      rest=['Designed and manufactured by us, then fitted on site by our team.'],
      details='Xylocleaf Santos Grey · Gola profile, handleless · Island',
      photos=stems('p39'), cover='p39-3', second='p39-6', band=['p39-3', 'p39-6', 'p39-8']),
 dict(slug='cloakroom-lytham-st-annes', title='Cloakroom in Lytham St Annes', svc=['bathrooms'], place='Lytham St Annes, Lancashire',
      sub='A small cloakroom, completed.',
      lead='A wood-veneer panel with a lit niche above a wall-hung toilet, the cistern hidden behind it, and stone-effect tiles below.',
      rest=['Designed, made and fitted by our team. The before photograph is at the end of the gallery.'],
      details='Veneer panel with lit niche · Wall-hung WC · Concealed cistern',
      photos=stems('p16'), cover='p16-4', second='p16-2', band=['p16-4', 'p16-2', 'p16-1'], before='p16-8'),
 dict(slug='media-wall-and-fireplace', title='Media wall and fireplace', svc=['media-walls'], place=None,
      sub='A recessed television, a fire that wraps the corner and lit shelving either side.',
      lead='A media wall built around one living room: the television set into the wall above a fire that wraps the corner, fluted panels, and lit shelving either side for the things you want on show.',
      rest=['Designed and built by our team.'],
      details='Corner fire · Fluted panels · Lit shelving',
      photos=stems('p02'), cover='p02-1', second='p02-4', band=['p02-1', 'p02-4', 'p02-2']),
 dict(slug='black-kitchen-white-island', title='Black kitchen with a white island', svc=['kitchens'], place=None,
      sub='Fully designed by us and manufactured in our workshop.',
      lead='Dark handleless units under a vaulted ceiling with roof lights, and an island with a white veined worktop that wraps down both ends.',
      rest=['Designed by us, manufactured in our workshop and installed by our team.'],
      details='Handleless doors · Waterfall island · Vaulted ceiling with roof lights',
      photos=['p15-1'] + stems('p19', drop=('p19-8', 'p19-9')), cover='p19-3', second='p19-4', band=['p15-1', 'p19-3', 'p19-4']),
 dict(slug='shower-room-hidden-door', title='Shower room with a hidden door', svc=['bathrooms', 'renovations'], place=None,
      sub='A bathroom turned into a shower room, in black throughout.',
      lead='We took the bath out for a black slate shower tray, kept the blackout look throughout and built a hidden door into the slat panelling.',
      rest=['The room was designed to make the most of the space. All work was carried out by our team, from start to finish.'],
      details='Black slate shower tray · Slat panelling · Hidden door',
      photos=stems('p21'), cover='p21-1', second='p21-6', band=['p21-1', 'p21-6', 'p21-3'], before='p21-9'),
 dict(slug='bedroom-hidden-doors', title='Bedroom with hidden doors', svc=['wardrobes', 'renovations'], place=None,
      sub='Full-height wardrobes on push-to-open doors.',
      lead='Floor-to-ceiling wardrobes on push-to-open doors, so the doors read as a wall, finished with a walnut slat panel and a lit headboard.',
      rest=['The whole room was designed and manufactured to the customer’s brief.'],
      details='Push-to-open doors · Walnut slat panel · Lit headboard',
      photos=['p33-1'] + stems('p32'), cover='p33-1', second='p32-4', band=['p33-1', 'p32-4', 'p32-3'], before='p32-7'),
 dict(slug='matt-black-and-brass-kitchen', title='Matt black and brass kitchen', svc=['kitchens'], place=None,
      sub='Matt black doors contrasting with a brushed brass Gola profile.',
      lead='Matt black doors with a brushed brass Gola profile, the recessed rail that takes the place of handles, set against a brick wall.',
      rest=['Manufactured and designed by us, and fitted by our team.'],
      details='Matt black doors · Brushed brass Gola profile',
      photos=stems('p37'), cover='p37-4', second='p37-6', band=['p37-4', 'p37-6', 'p37-3']),
 dict(slug='kitchen-wall-of-tall-units', title='Kitchen with a wall of tall units', svc=['kitchens'], place=None,
      sub='Fully designed through us and manufactured in our workshop.',
      lead='A wall of tall units with built-in ovens, an island with a white worktop and wine storage, and a lit recess in the ceiling above.',
      rest=['Designed by us, manufactured in our workshop and installed by our team.'],
      details='Tall oven housing · Island with wine storage · Lit ceiling recess',
      photos=stems('p29'), cover='p29-1', second='p29-3', band=['p29-1', 'p29-3', 'p29-6']),
 dict(slug='media-wall-xylocleaf', title='Media wall in Xylocleaf', svc=['media-walls'], place=None,
      sub='Designed and manufactured, keeping it contemporary.',
      lead='A concrete-effect Xylocleaf panel behind the television, a low run of black cabinets around the fire, and lit open shelving on both sides.',
      rest=['Designed and manufactured by us. The before photograph is at the end of the gallery.'],
      details='Xylocleaf panel · Inset fire · Lit open shelving',
      photos=stems('p41'), cover='p41-3', second='p41-1', band=['p41-3', 'p41-1', 'p41-5'], before='p41-8'),
 dict(slug='walk-in-wardrobe', title='Walk-in wardrobe with drawers for heels', svc=['wardrobes'], place=None,
      sub='Pull-out drawers for the heels.',
      lead='Open hanging, shelving and pull-out drawers for the heels, all made in our workshop to fit the room.',
      rest=['Designed, manufactured and fitted by our team.'],
      details='Pull-out shoe drawers · Open hanging · Shelving',
      photos=stems('p34'), cover='p34-1', second='p34-4', band=None),
 dict(slug='ash-staircase', title='Ash staircase with glass', svc=['staircases'], place=None,
      sub='Manufactured and designed in our workshop.',
      lead='A set of ash stairs with the glass templated and cut to the strings, finished by J-DEC.',
      rest=['The strings, treads and handrail were made in our workshop and fitted by our team.'],
      details='Ash · Glass templated to the strings · Finish by J-DEC',
      photos=stems('p40'), cover='p40-1', second='p40-3', band=['p40-1', 'p40-3', 'p40-5']),
]
PJ = {p['slug']: p for p in P}
for p in P:
    p['photos'] = [s for s in p['photos'] if s in M]
    assert p['cover'] in M and p['second'] in M, p['slug']

REVIEWS = {
 'carol': dict(name='Carol B.', text='fantastic job on fitted wardrobes, made and fitted just like the picture I showed them. Well done Zak and Paul', on='Fitted wardrobes'),
 'mel': dict(name='Mel B.', text='We would highly recommend Joinwell Joinery. Zak and his team recently refurbished our small downstairs bathroom and the work they’ve done is exceptional. They kept us updated along the way, nothing was ever too much trouble and they were a pleasure to work with.', on='Downstairs bathroom'),
 'corinne': dict(name='Corinne E.', text='We had an oak balustrade with glass panel done looks absolutely amazing, also had a gorgeous oak floating beam put in above our fireplace, again looks amazing, they also did our floor to ceiling sliding wardrobes fitted in the spare room …', on='Oak balustrade, beam and sliding wardrobes'),
 'darren': dict(name='Darren M.', text='Looks fantastic Zak. So pleased with them.', on='Fitted wardrobes', src='Facebook comment', url='https://www.facebook.com/reel/3367519103419647/'),
}

S = [
 dict(slug='kitchens', c=('p39-3', 'nookwood'), nav='Kitchens', title='Bespoke kitchens in the North West',
      h1='Bespoke kitchens, designed, made and fitted in the North West',
      desc='Bespoke kitchens designed, manufactured in our workshop and fitted by Joinwell Joinery across Lancashire, Manchester and Cheshire. Free home consultation.',
      lead='Bespoke kitchens designed around your lifestyle, combining craftsmanship, smart storage, premium materials, and timeless style.',
      a=('p15-1', 'black-kitchen-white-island'), b=('p37-4', 'matt-black-and-brass-kitchen'),
      spec_h='What goes into our kitchens',
      spec=[('Handleless, on the Gola profile', 'Doors with no handles, opened on a recessed rail: in matt black, or in brushed brass against matt black doors.'),
            ('Shaker and in-frame', 'Shaker kitchens with the doors painted to the colour you choose, for houses that suit something more traditional.'),
            ('Boards chosen for the house', 'Xylocleaf boards such as Santos Grey and Blue Lagoon, picked so the kitchen flows with the rest of the interior.'),
            ('Tall units and larders', 'Ovens, larders and open shelving built into one wall, with lighting where it helps.'),
            ('Islands', 'Islands with seating and wine storage, and worktops that wrap down the ends.'),
            ('Made in our workshop', 'Designed with you, manufactured in our workshop and installed by the same team.')],
      projects=['black-kitchen-and-island', 'black-kitchen-white-island', 'nookwood', 'matt-black-and-brass-kitchen', 'kitchen-wall-of-tall-units'],
      extra=[('p11-1', 'Handleless kitchen · Lytham'), ('p10-2', 'Kitchen with lit plinths and ceiling lines'), ('p12-1', 'Kitchen with island and seating'),
             ('p10-4', 'Kitchen with lit plinths and ceiling lines'), ('p04-1', 'Shaker kitchen with pendants'), ('p14-1', 'Grey textile utility room')],
      reviews=[]),
 dict(slug='wardrobes', c=('p34-1', 'walk-in-wardrobe'), nav='Wardrobes', title='Fitted wardrobes and bedrooms in the North West',
      h1='Fitted wardrobes and bedrooms, made to measure in the North West',
      desc='Bespoke fitted wardrobes, walk-in wardrobes and bedroom furniture, designed and manufactured by Joinwell Joinery to make the most of every inch.',
      lead='Bespoke fitted wardrobes, designed and manufactured to make the most of every inch.',
      a=('p01-1', None), b=('p33-1', 'bedroom-hidden-doors'), a_cap='Two-tone fitted wardrobes under a sloping ceiling',
      spec_h='How we fit a wardrobe to the room',
      spec=[('Floor to ceiling', 'Full-height wardrobes on push-to-open doors, so the doors read as part of the wall.'),
            ('Walk-in wardrobes', 'Double and long hanging, shelving and pull-out drawers, planned around what you own.'),
            ('Sliding doors', 'Sliders for rooms where there is not much space for doors to open.'),
            ('Under the eaves', 'Doors made to size to fit under the purlins of a loft conversion, and units shaped to a sloping ceiling.'),
            ('Lighting', 'LED lights sunk in under the shelves, on sensors as you walk into the room.'),
            ('Finishes', 'Shaker or flat doors, sprayed MDF or boards in colours such as Mussel and dust grey, with matt black handles or none at all.')],
      projects=['bedroom-hidden-doors', 'walk-in-wardrobe', 'poolside'],
      extra=[('p36-1', 'Shaker wardrobes'), ('p36-3', 'Shaker wardrobes'), ('p46-3', 'Walk-in wardrobe · Poolside'), ('p46-6', 'Matt black knobs · Poolside'),
             ('p32-5', 'Bedroom with hidden doors'), ('p34-4', 'Drawers for heels')],
      reviews=['carol', 'darren']),
 dict(slug='media-walls', c=('p41-3', 'media-wall-xylocleaf'), nav='Media walls', title='Bespoke media walls in the North West',
      h1='Media walls and fitted living rooms across the North West',
      desc='Bespoke media walls with fires, lit shelving and panelling, plus studies and fitted furniture, designed and built by Joinwell Joinery in the North West.',
      lead='Bespoke furniture for living, designed around you. Crafted with precision, built to last and designed bespoke to your space, style and everyday needs.',
      a=('p07-1', None), b=('p02-1', 'media-wall-and-fireplace'), a_cap='Media wall with lit timber shelving · Manchester',
      spec_h='What a media wall can hold',
      spec=[('Television and fire', 'A screen set into the wall and a fire built into the base, so the wall reads as one piece.'),
            ('Lit shelving', 'Open shelves and niches either side, lit with LED.'),
            ('Panelling', 'Slat panelling, fluted panels and Xylocleaf boards.'),
            ('Studies and fitted furniture', 'Desks, alcove units and storage for the rest of the room, made to the same finish.'),
            ('One team on site', 'Joinery by us, with the electrician, plasterer and painter we work with.'),
            ('Made in our workshop', 'Designed and manufactured by us, then fitted by our team.')],
      projects=['media-wall-and-fireplace', 'media-wall-xylocleaf'],
      extra=[('p18-1', 'Media wall · Lytham'), ('p24-1', 'Media wall with lit shelving'), ('p25-1', 'Media wall with fire'),
             ('p30-1', 'Media wall with lit niches'), ('p30-3', 'Media wall with lit niches'), ('p02-3', 'Media wall and fireplace')],
      reviews=[]),
 dict(slug='bathrooms', c=('p16-4', 'cloakroom-lytham-st-annes'), nav='Bathrooms', title='Bespoke bathrooms and vanity units in the North West',
      h1='Bathrooms, cloakrooms and vanity units in the North West',
      desc='Luxury bespoke bathrooms, cloakrooms and floating vanity units, designed, made and fitted by the Joinwell Joinery team from start to finish.',
      lead='Luxury bespoke bathrooms crafted with precision, premium finishes and tailored design.',
      a=('p26-1', None), b=('p21-1', 'shower-room-hidden-door'), a_cap='Bathroom with timber wall panelling and lit mirrors',
      spec_h='How we take on a bathroom',
      spec=[('Start to finish', 'All work is carried out by our team, from start to finish.'),
            ('Layouts that work', 'Toilet, sink and bath moved to where the room works better, with a wet room where it fits.'),
            ('Vanity units', 'Floating vanity units made in our workshop, handleless on the Gola profile, in boards such as Ares Beton.'),
            ('Panelling with storage', 'Wooden panels that give a smaller room more storage.'),
            ('Hidden doors and lit niches', 'Doors built into slat panelling, and lit niches set into a veneer wall.'),
            ('Traditional rooms', 'In-frame shaker cabinets, wall panelling, a Belfast sink and oak worktops.')],
      projects=['shower-room-hidden-door', 'cloakroom-lytham-st-annes', 'poolside'],
      extra=[('p23-1', 'Family bathroom with a wet room'), ('p42-1', 'Cloakroom with a Belfast sink and oak worktop'), ('p31-1', 'Bathroom renovation'),
             ('p35-3', 'Shower room with a lit niche'), ('p45-2', 'Vanity unit in Ares Beton · Poolside'), ('p42-3', 'In-frame shaker vanity')],
      reviews=['mel']),
 dict(slug='staircases', c=('p40-1', 'ash-staircase'), nav='Staircases', title='Bespoke ash and oak staircases in the North West',
      h1='Bespoke staircases in ash and oak, made in our workshop',
      desc='Bespoke handmade ash and oak staircases with cut strings and glass, designed and manufactured in the Joinwell Joinery workshop for homes in the North West.',
      lead='Bespoke handmade ash staircases, fully designed and manufactured in our workshop to exactly what our customer wanted.',
      a=('p28-1', None), b=('p43-4', 'poolside'), a_cap='Ash staircase, stained and lacquered black',
      spec_h='How our staircases are made',
      spec=[('Ash and oak', 'Ash staircases, oak balustrades, newel posts and handrails.'),
            ('Cut strings and glass', 'Cut strings with the glass templated round each step.'),
            ('Stained to match', 'Timber stained and lacquered in black to match the internal doors.'),
            ('Loft conversions', 'Stairs manufactured for loft conversions.'),
            ('Finished properly', 'Lacquer and paint by J-DEC, the finisher we work with.'),
            ('Made in our workshop', 'Strings, treads and handrails made on our bench, then fitted by our team.')],
      projects=['poolside', 'ash-staircase'],
      extra=[('p43-2', 'Ash staircase · Poolside'), ('p43-1', 'Ash staircase · Poolside'), ('p40-2', 'Ash staircase with glass'), ('p40-4', 'Ash staircase with glass'), ('p43-5', 'Ash staircase · Poolside'), ('p40-6', 'Ash staircase with glass')],
      reviews=['corinne']),
 dict(slug='renovations', c=('p33-1', 'bedroom-hidden-doors'), nav='Renovations', title='Room renovations in the North West',
      h1='Room renovations, one team from start to finish',
      desc='Bathroom, bedroom and living room renovations across the North West, with the joinery made in our workshop and all work carried out by the Joinwell Joinery team.',
      lead='All work is carried out by our team from start to finish: the strip-out, the joinery from our workshop, and the fitting.',
      a=('p21-1', 'shower-room-hidden-door'), b=('p16-4', 'cloakroom-lytham-st-annes'),
      spec_h='What we take on',
      spec=[('Bathrooms', 'Stripped back and rebuilt, with layouts changed where the room works better.'),
            ('Bedrooms', 'Wardrobes, panelling and lighting fitted as one job.'),
            ('Feature walls', 'Panelling with hidden doors to an en-suite, storage or a stop tap.'),
            ('Flooring', 'Oak engineered and click flooring laid to finish the room.')],
      projects=['shower-room-hidden-door', 'cloakroom-lytham-st-annes', 'bedroom-hidden-doors', 'media-wall-xylocleaf'],
      extra=[], reviews=['mel']),
]
SJ = {s['slug']: s for s in S}
BEFORE_CAP = '<span class="cap">Before</span>'
SING = {'kitchens': 'Kitchen', 'wardrobes': 'Wardrobe', 'media-walls': 'Media wall', 'bathrooms': 'Bathroom', 'staircases': 'Staircase', 'renovations': 'Renovation'}
ROOMS = [  # home index: rooms -> service pages
 ('kitchens', 'Kitchens', 'Handleless, shaker and Xylocleaf · islands and tall units', 'p15-1', 'Black kitchen with a white island'),
 ('wardrobes', 'Fitted wardrobes', 'Walk-in, sliding and floor to ceiling', 'p01-1', 'Two-tone wardrobes under a sloping ceiling'),
 ('media-walls', 'Media walls', 'Fires, lit shelving and panelling', 'p07-1', 'Media wall · Manchester'),
 ('bathrooms', 'Bathrooms & vanity units', 'Cloakrooms, shower rooms and full refits', 'p26-1', 'Bathroom with timber wall panelling'),
 ('staircases', 'Staircases', 'Ash and oak, cut strings and glass', 'p43-4', 'Ash staircase · Poolside'),
 ('renovations', 'Renovations', 'Whole rooms, one team', 'p21-1', 'Shower room with a hidden door'),
]
for st in [r[3] for r in ROOMS] + [s['a'][0] for s in S] + [s['b'][0] for s in S] + [x[0] for s in S for x in s['extra']]:
    assert st in M, st

# ------------------------------------------------------------------ chrome
FONTS = 'https://fonts.googleapis.com/css2?family=Sofia+Sans+Condensed:wght@300;400;500&family=Sofia+Sans:wght@400;500&display=swap'
NAV = [('kitchens', 'Kitchens'), ('wardrobes', 'Wardrobes'), ('media-walls', 'Media walls'), ('bathrooms', 'Bathrooms'), ('staircases', 'Staircases'), ('work', 'Our work')]
MENU = NAV[:5] + [('renovations', 'Renovations'), ('work', 'Our work'), ('contact', 'Contact')]

def head(title, desc, path, extra_head='', ld=None, noindex=False):
    can = f'<link rel="canonical" href="{DOMAIN}{path}">' if DOMAIN else ''
    og_img = f'{DOMAIN}/og.jpg'
    ld = ld or LD
    ldj = f'<script type="application/ld+json">{json.dumps(ld, ensure_ascii=False)}</script>'
    return f'''<!doctype html>
<html lang="en-GB">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(title)}</title>
<meta name="description" content="{e(desc)}">
{can}
<meta property="og:type" content="website">
<meta property="og:site_name" content="Joinwell Joinery">
<meta property="og:title" content="{e(title)}">
<meta property="og:description" content="{e(desc)}">
<meta property="og:image" content="{og_img}">
<meta property="og:locale" content="en_GB">
<meta name="twitter:card" content="summary_large_image">
{'<meta name="robots" content="noindex">' if noindex else ''}
<meta name="theme-color" content="#151515">
<link rel="icon" href="/favicon-32.png" sizes="32x32">
<link rel="apple-touch-icon" href="/apple-touch-icon.png">
<link rel="preload" href="/fonts/SofiaSansCondensed-latin.woff2" as="font" type="font/woff2" crossorigin>
<link rel="preload" href="/fonts/SofiaSans-latin.woff2" as="font" type="font/woff2" crossorigin>
{extra_head}
<link rel="stylesheet" href="/css/site.css">
<script>(function(d){{d.classList.add('js','no-intro')}})(document.documentElement)</script>
{ldj}
</head>
<body>
<a class="skip" href="#content">Skip to content</a>
'''

def nav(cur, over=False):
    AC = ' aria-current="page"'
    links = ''.join(f'<a href="/{k}/"{AC if k == cur else ""}>{n}</a>' for k, n in NAV)
    mlinks = ''.join(f'<a href="/{k}/" data-menu-close style="--i:{i}">{n}</a>' for i, (k, n) in enumerate(MENU))
    return f'''<header class="nav"{" data-over" if over else ""} data-nav>
  <div class="wrap nav__in">
    <a class="brand" href="/" aria-label="Joinwell Joinery, home"><i></i></a>
    <nav class="nav__links" aria-label="Main">{links}</nav>
    <a class="nav__tel" href="tel:{PHONE_T}">{PHONE_D}</a>
    <a class="btn" href="/contact/">Free consultation</a>
    <button class="nav__menu" type="button" aria-expanded="false" aria-controls="menu" data-menu-open><span>Menu</span><span class="nav__burger" aria-hidden="true"></span></button>
  </div>
</header>
<div class="menu" id="menu" hidden data-menu>
  <div class="menu__top"><a class="brand" href="/" aria-label="Joinwell Joinery, home"><i></i></a><button class="menu__close" type="button" data-menu-close>Close</button></div>
  <nav class="menu__links" aria-label="Menu">{mlinks}</nav>
  <div class="menu__foot"><a class="tel" href="tel:{PHONE_T}" style="--i:8">{PHONE_D}</a><a class="u" href="mailto:{EMAIL}" style="justify-self:start;--i:9">{EMAIL}</a><a class="btn btn--gold" href="/contact/" style="justify-self:start;--i:10">Book a free consultation</a></div>
</div>
'''

def close_band(h='Book a free home consultation'):
    area = ''.join(f'<span>{a}</span>' for a in AREA)
    return f'''<section class="close sec on-dark" aria-labelledby="close-h">
  <div class="wrap g12">
    <h2 id="close-h" class="t-display rv">{h}</h2>
    <div class="close__aside rv" style="--d:120ms">
      <p class="muted">We come to you, measure the room and talk it through. The consultation is complimentary and the quotation is free.</p>
      <a class="close__tel" href="tel:{PHONE_T}">{PHONE_D}</a>
      <a class="btn btn--gold" href="/contact/">Book a consultation</a>
    </div>
    <p class="close__area hl">{area}<span>and throughout the North West</span></p>
  </div>
</section>
'''

def footer(tab=True):
    rooms = ''.join(f'<a class="u" href="/{k}/">{v}</a>' for k, v in SERV.items())
    return f'''<footer class="foot on-dark">
  <div class="wrap">
    <div class="foot__grid">
      <div class="foot__brand">
        <img src="/img/brand/lockup-gold-720.png" width="720" height="309" alt="Joinwell Joinery" loading="lazy">
        <p>Specialists in bespoke luxury fitted furniture in the North West.</p>
      </div>
      <div class="foot__col rv"><h3>Rooms</h3>{rooms}</div>
      <div class="foot__col rv" style="--d:80ms"><h3>Joinwell</h3><a class="u" href="/work/">Our work</a><a class="u" href="/contact/">Contact</a><a class="u" href="/privacy/">Privacy notice</a></div>
      <div class="foot__col rv" style="--d:160ms"><h3>Follow</h3><a class="u" href="{IG}" rel="noopener">Instagram</a><a class="u" href="{FB}" rel="noopener">Facebook</a><a class="u" href="{MYBUILDER}" rel="noopener">MyBuilder</a></div>
      <div class="foot__col foot__contact rv" style="--d:240ms"><h3>Contact</h3><a class="u tel" href="tel:{PHONE_T}">{PHONE_D}</a><a class="u" href="mailto:{EMAIL}">{EMAIL}</a></div>
    </div>
    <div class="foot__legal hl"><p>{LEGAL}</p><p>© 2026 Joinwell Joinery Ltd</p></div>
  </div>
</footer>
{'<a class="tab" href="/contact/">Free home consultation</a>' if tab else ''}
<nav class="callbar" aria-label="Quick contact"><a href="tel:{PHONE_T}">Call {PHONE_D}</a><a href="/contact/">Free consultation</a></nav>
'''

def lightbox():
    return '''<dialog class="lb" data-lb aria-label="Photographs">
  <div class="lb__bar"><p><b data-lb-title></b> <span data-lb-count></span></p><button class="lb__close" type="button" data-lb-close>Close</button></div>
  <figure><img data-lb-img alt="Enlarged photograph" width="1200" height="1500"></figure>
  <button class="lb__btn lb__btn--prev" type="button" data-lb-prev aria-label="Previous photograph">‹</button>
  <button class="lb__btn lb__btn--next" type="button" data-lb-next aria-label="Next photograph">›</button>
</dialog>
'''

def tail(gallery=None):
    g = ''
    if gallery:
        G = {k: [{'src': big(s), 'w': M[s]['w'], 'h': M[s]['h']} for s in v[1]] for k, v in gallery.items()}
        T = {k: v[0] for k, v in gallery.items()}
        g = f'<script>window.GALLERY={json.dumps(G)};window.GALLERY_TITLES={json.dumps(T, ensure_ascii=False)};</script>\n'
    return g + '<script src="/js/lenis.min.js" defer></script>\n<script src="/js/site.js" defer></script>\n</body>\n</html>\n'

def svc_line(p):
    return ', '.join(SERV[k] for k in p['svc'])

def card(p, sizes='(max-width: 479px) 92vw, (max-width: 899px) 48vw, 47vw'):
    meta = svc_line(p) + (f' · {p["place"].split(",")[0]}' if p['place'] else '')
    return f'''<a class="card fw" href="/work/{p["slug"]}/">
  <span class="ph"><span class="par" data-par="4">{img(p["cover"], sizes, p["title"] + ", " + svc_line(p).lower() + " by Joinwell Joinery")}{img(p["second"], sizes, p["title"] + ", second view", attrs=' aria-hidden="true"')}</span></span>
  <span class="card__t hl"><h3>{e(p["title"])}</h3><p>{e(meta)}</p></span>
</a>'''

def write(path, content):
    out = ROOT / path.lstrip('/')
    if path.endswith('/'): out = out / 'index.html'
    out.parent.mkdir(parents=True, exist_ok=True)
    assert '—' not in content, 'em dash in ' + path
    out.write_text(content)

# ------------------------------------------------------------------ home
def home():
    ld = {'@context': 'https://schema.org', '@type': 'HomeAndConstructionBusiness', 'name': 'Joinwell Joinery', 'legalName': 'Joinwell Joinery Ltd',
          'description': 'Specialists in bespoke luxury fitted furniture in the North West.', 'telephone': PHONE_T, 'email': EMAIL,
          'areaServed': AREA + ['North West England'], 'sameAs': [FB, IG], 'logo': f'{DOMAIN}/img/brand/lockup-gold.png'}
    pre = ('<link rel="preload" as="image" href="/img/hero/home-d-1920.webp" imagesrcset="/img/hero/home-d-1280.webp 1280w, /img/hero/home-d-1920.webp 1920w, /img/hero/home-d-2560.webp 2560w" imagesizes="100vw" media="(min-width: 900px)" fetchpriority="high">')
    h = head('Joinwell Joinery | Bespoke fitted furniture in the North West',
             'Bespoke kitchens, fitted wardrobes, media walls, bathrooms and staircases, designed, made in our workshop and fitted by one team across Lancashire, Manchester and Cheshire.',
             '/', pre, ld)
    m = M['p03-1']
    hero = f'''<section class="hero" data-hero aria-labelledby="h1">
  <picture>
    <source media="(min-width: 900px)" srcset="/img/hero/home-d-1280.webp 1280w, /img/hero/home-d-1920.webp 1920w, /img/hero/home-d-2560.webp 2560w" sizes="100vw" width="2560" height="1440">
    <img src="/img/g/p03-1-960.webp" srcset="{', '.join(f'/img/g/p03-1-{w}.webp {w}w' for w in m['widths'])}" sizes="100vw" width="{m['w']}" height="{m['h']}" alt="Black handleless kitchen with an island, bar stools and a brass pendant light, designed and made by Joinwell Joinery" fetchpriority="high">
  </picture>
  <div class="hero__in"><div class="wrap g12">
    <h1 id="h1" class="rv">Bespoke fitted furniture for homes across the North West</h1>
    <div class="hero__aside rv" style="--d:160ms">
      <p>Kitchens, wardrobes, media walls, bathrooms and staircases. Designed with you, made in our workshop and fitted by our own team.</p>
      <a class="go" href="/contact/">Book a free home consultation</a>
    </div>
  </div></div>
</section>
'''
    proof = f'''<section class="proof" aria-label="Why people book us">
  <ul class="wrap">
    <li class="rv" style="--d:300ms"><a href="{FB_REVIEWS}" rel="noopener"><b>100%</b> recommended on Facebook</a></li>
    <li class="rv" style="--d:380ms"><a href="{MYBUILDER}" rel="noopener">Verified on MyBuilder</a></li>
    <li class="rv" style="--d:460ms">Made in our own workshop</li>
    <li class="rv" style="--d:540ms">Free home consultation and quotation</li>
  </ul>
</section>
'''
    intro = f'''<section class="intro sec" aria-labelledby="intro-h">
  <div class="wrap g12">
    <h2 id="intro-h" class="t-statement intro__st rv">Specialists in bespoke luxury fitted furniture in the North West.</h2>
    <a class="intro__ph ph ph--link fw" href="/work/black-kitchen-and-island/"><span class="par" data-par="4">{img("p03-5", "(max-width: 899px) 80vw, 40vw", "Tall black kitchen unit with lit open shelving and drawers")}</span></a>
    <div class="intro__tx rv">
      <p class="t-lead">Our joiners design, make and fit kitchens, wardrobes, media walls, bathrooms and staircases. Each piece is drawn for the room it goes in, manufactured in our workshop and installed by the same team.</p>
      <p class="muted">We work across Kirkham, Lytham, Blackpool, Preston, Manchester and Cheshire, and throughout the North West.</p>
      <a class="go" href="/work/">See our work</a>
    </div>
  </div>
</section>
'''
    rows = ''.join(f'<a class="ix__row rv" style="--d:{i * 70}ms" href="/{k}/" data-k="{k}"><span class="ix__name">{e(n)}</span><span class="ix__meta">{e(c)}</span></a>' for i, (k, n, c, s, a) in enumerate(ROOMS))
    plates = ''.join(img(s, '(max-width: 899px) 1px, 40vw', a, cls='is-on' if i == 0 else '', attrs=f' data-k="{k}" data-cap="{e(a)}"') for i, (k, n, c, s, a) in enumerate(ROOMS))
    rail = ''.join(f'<a href="/{k}/"><span class="ph">{img(s, "78vw", a)}</span><h3>{e(n)}</h3><p class="cap">{e(c)}</p></a>' for k, n, c, s, a in ROOMS)
    rooms = f'''<section class="rooms sec bg-2" aria-labelledby="rooms-h" data-signature>
  <div class="wrap">
    <div class="head"><h2 id="rooms-h" class="t-h2 rv">Rooms we design, make and fit</h2><p class="rv" style="--d:120ms">Every photograph here is our own work, in a home in the North West.</p></div>
    <div class="ix" data-ix>
      <nav class="ix__rows hl" aria-label="Rooms">{rows}</nav>
      <div class="ix__plate" aria-hidden="true">{plates}<p class="ix__cap">{e(ROOMS[0][4])}</p></div>
      <div class="ix__rail rail">{rail}</div>
    </div>
  </div>
</section>
'''
    feat = ['black-kitchen-and-island', 'poolside', 'cloakroom-lytham-st-annes', 'media-wall-and-fireplace']
    work = f'''<section class="work sec" aria-labelledby="work-h">
  <div class="wrap">
    <div class="head"><h2 id="work-h" class="t-h2 rv">Recent work</h2><p class="rv" style="--d:120ms">Four recent jobs, each designed with the client, made in our workshop and fitted by our team.</p></div>
    <div class="works">{''.join(card(PJ[s]) for s in feat)}</div>
    <div class="more hl"><p class="muted">{len(P)} projects in the North West, with photographs of every room.</p><a class="go" href="/work/">All projects</a></div>
  </div>
</section>
'''
    D = [('d1', 'p03-5', 'Lit larder shelving and deep drawers', 'black-kitchen-and-island', '(max-width: 899px) 92vw, 40vw'),
         ('d2', 'p37-4', 'Brushed brass Gola profile on matt black doors', 'matt-black-and-brass-kitchen', '(max-width: 899px) 48vw, 25vw'),
         ('d3', 'p32-4', 'Push-to-open doors, no handles', 'bedroom-hidden-doors', '(max-width: 899px) 48vw, 25vw'),
         ('d4', 'p21-6', 'A door hidden in the slat panelling', 'shower-room-hidden-door', '(max-width: 899px) 48vw, 25vw'),
         ('d5', 'p43-4', 'Ash treads stained black, glass cut to the strings', 'poolside', '(max-width: 899px) 48vw, 25vw'),
         ('d6', 'p16-4', 'A lit niche in a veneer panel', 'cloakroom-lytham-st-annes', '(max-width: 899px) 48vw, 33vw')]
    figs = ''.join(f'''<figure class="{c}"><a class="ph ph--link" href="/work/{pj}/" tabindex="-1" aria-hidden="true"><span class="par" data-par="3">{img(s, sz, t)}</span></a><figcaption><b>{e(t)}</b><a class="u" href="/work/{pj}/">{e(PJ[pj]["title"])}</a></figcaption></figure>''' for c, s, t, pj, sz in D)
    inch = f'''<section class="inch sec on-dark" aria-labelledby="inch-h" data-client-only>
  <div class="wrap">
    <div class="inch__grid"><div class="inch__head"><h2 id="inch-h" class="t-h2 rv">Designed and manufactured to make the most of every inch.</h2><p class="rv" style="--d:120ms">Details from recent jobs, photographed as they were fitted: the drawer, the rail, the door you cannot see.</p></div>{figs}</div>
  </div>
</section>
'''
    film = [('h-poolside-28', 'Strings cut on the bench', 'The ash strings for the Poolside staircase, in our workshop.'),
            ('h-poolside-30', 'Assembled in our workshop', 'Built and checked before it leaves for site.'),
            ('h-poolside-57', 'Fitted by our team', 'On site, with the glass templated and fitted.'),
            ('p43-2', 'Finished', 'Stained black and lacquered by J-DEC.')]
    ff = ''.join(f'<figure><span class="ph"><span class="par" data-par="3">{img(s, "(max-width: 899px) 74vw, 28vw", t + ", ash staircase for the Poolside house")}</span></span><figcaption><b>{e(t)}</b>{e(c)}</figcaption></figure>' for s, t, c in film)
    make = f'''<section class="make sec" aria-labelledby="make-h">
  <div class="wrap">
    <div class="make__top">
      <div class="make__intro rv"><h2 id="make-h" class="t-h2">Designed, made and fitted by one team</h2><p>One job from start to finish: the ash staircase for the Poolside house, from our bench to the hallway.</p><a class="go" href="/contact/">Book a free home consultation</a></div>
      <ol class="make__steps hl">
        <li class="rv" style="--d:80ms"><h3>Free home consultation</h3><p>We come to you, look at the room and talk through how you use it. The consultation and the quotation are free.</p></li>
        <li class="rv" style="--d:160ms"><h3>Design</h3><p>Each piece is designed for the room it goes in, and you agree the materials and finish with us.</p></li>
        <li class="rv" style="--d:240ms"><h3>Made in our workshop</h3><p>Everything is manufactured in our own workshop, from the strings of a staircase to the doors of a wardrobe.</p></li>
        <li class="rv" style="--d:320ms"><h3>Fitted by our team</h3><p>The same team installs it in your home and sees it through to the last detail.</p></li>
      </ol>
    </div>
    <div class="make__film">{ff}</div>
  </div>
</section>
'''
    words = reviews_block(['mel', 'carol', 'corinne'])
    body = h + nav('', over=True) + '<main id="content">\n' + hero + proof + intro + rooms + work + inch + make + words + close_band() + '</main>\n' + footer() + tail()
    write('/', body)

def reviews_block(keys, head_h='100% recommended on Facebook'):
    rv = [REVIEWS[k] for k in keys]
    def who(r):
        src = r.get('src', 'Facebook review'); url = r.get('url', FB_REVIEWS)
        return f'<p class="who"><b>{e(r["name"])}</b><span>{e(r["on"])}</span><a class="u" href="{url}" rel="noopener">{src}</a></p>'
    first = rv[0]
    rest = ''.join(f'<figure class="rv" style="--d:{120 + i * 100}ms"><blockquote>“{e(r["text"])}”</blockquote>{who(r)}</figure>' for i, r in enumerate(rv[1:]))
    return f'''<section class="words sec bg-2" aria-labelledby="words-h">
  <div class="wrap">
    <div class="head"><h2 id="words-h" class="t-h2 rv">{head_h}</h2><p class="rv" style="--d:120ms">Every review on our Facebook page recommends us. {"These are " + str(len(rv)) + " of them" if len(rv) > 1 else "This is one of them"}, word for word. <a class="u" href="{FB_REVIEWS}" rel="noopener">Read them all</a></p></div>
    <div class="words__grid hl{" words__grid--solo" if len(rv) == 1 else ""}">
      <figure class="q1 rv"><blockquote>“{e(first["text"])}”</blockquote>{who(first)}</figure>
      {'<div class="qs">' + rest + '</div>' if rest else ''}
    </div>
  </div>
</section>
'''

# ------------------------------------------------------------------ service pages
def service(s):
    title = f'{s["title"]} | Joinwell Joinery'
    h = head(title, s['desc'], f'/{s["slug"]}/')
    def plate(stem, pj, cls, cap=None, sizes='(max-width: 899px) 92vw, 56vw', lazy=True):
        if pj:
            p = PJ[pj]; cap = cap or p['title']
            return f'<figure class="{cls}"><a class="ph ph--link" href="/work/{pj}/"><span class="par" data-par="3">{img(stem, sizes, p["title"], lazy=lazy)}</span></a><figcaption class="cap"><a class="u" href="/work/{pj}/">{e(cap)}</a></figcaption></figure>'
        return f'<figure class="{cls}"><span class="ph"><span class="par" data-par="3">{img(stem, sizes, cap, lazy=lazy)}</span></span><figcaption class="cap">{e(cap)}</figcaption></figure>'
    a = plate(s['a'][0], s['a'][1], 'a', s.get('a_cap'), '(max-width: 899px) 92vw, 46vw', lazy=False)
    b = plate(s['b'][0], s['b'][1], 'b', None, '(max-width: 899px) 48vw, 28vw')
    c = plate(s['c'][0], s['c'][1], 'c', None, '(max-width: 899px) 48vw, 22vw')
    spec = ''.join(f'<div class="rv" style="--d:{i * 70}ms"><dt>{e(t)}</dt><dd>{e(d)}</dd></div>' for i, (t, d) in enumerate(s['spec']))
    projects = [PJ[k] for k in s['projects']]
    cards = ''.join(card(p) for p in projects)
    if len(projects) % 2:
        cards += f'''<a class="card card--cta fw" href="/contact/"><span class="ph"><b>Your {SING[s["slug"]].lower()} next</b><span>We come to you, measure the room and talk it through. The consultation and quotation are free.</span><em class="go">Book a consultation</em></span><span class="card__t hl"><h3>Free home consultation</h3><p>{PHONE_D}</p></span></a>'''
    gal = ''
    G = {}
    if s['extra']:
        G[s['slug']] = (s['nav'], [x[0] for x in s['extra']])
        items = ''.join(f'<a href="{big(st)}" data-open="{s["slug"]}" data-index="{i}"><span class="ph ph--link">{img(st, "(max-width: 899px) 48vw, 33vw", c)}</span><span class="cap" style="display:block;margin-top:10px">{e(c)}</span></a>' for i, (st, c) in enumerate(s['extra']))
        gal = f'''<section class="sec" aria-labelledby="more-h" style="--sec-top:0">
  <div class="wrap">
    <div class="head"><h2 id="more-h" class="t-h2 rv">More {s["nav"].lower()} from our Instagram</h2><p class="rv" style="--d:120ms">Open a photograph to see it full size.</p></div>
    <div class="show">{items}</div>
  </div>
</section>
'''
    ba = ''
    if s['slug'] == 'renovations':
        rows = ''
        for p in [PJ[k] for k in ('cloakroom-lytham-st-annes', 'shower-room-hidden-door', 'bedroom-hidden-doors', 'media-wall-xylocleaf')]:
            rows += f'''<div class="ba__row">
  <figure class="x"><span class="ph">{img(p["before"], "(max-width: 899px) 48vw, 32vw", p["title"] + ", before")}</span><figcaption class="cap">Before</figcaption></figure>
  <figure class="y"><a class="ph ph--link" href="/work/{p["slug"]}/">{img(p["cover"], "(max-width: 899px) 48vw, 40vw", p["title"] + ", after")}</a><figcaption class="cap">After</figcaption></figure>
  <div class="t rv"><h3>{e(p["title"])}</h3><p>{e(p["lead"])}</p><a class="go" href="/work/{p["slug"]}/">See the project</a></div>
</div>'''
        ba = f'''<section class="sec" aria-labelledby="ba-h" style="--sec-top:0">
  <div class="wrap">
    <div class="head"><h2 id="ba-h" class="t-h2 rv">Before and after</h2><p class="rv" style="--d:120ms">The same rooms, photographed before we started and after we finished.</p></div>
    <div class="ba">{rows}</div>
  </div>
</section>
'''
    rvw = ''
    if s['reviews']:
        rvw = reviews_block(s['reviews'], 'What our customers said')
    others = ''.join(f'<a class="u" href="/{k}/">{v}</a>' for k, v in SERV.items() if k != s['slug'])
    body = h + nav(s['slug']) + f'''<main id="content">
<section class="phead" aria-labelledby="h1">
  <div class="wrap g12">
    <p class="crumb"><a class="u" href="/">Joinwell Joinery</a><span aria-hidden="true">/</span><span>{e(s["nav"])}</span></p>
    <h1 id="h1" class="rv">{e(s["h1"])}</h1>
    <div class="phead__aside rv" style="--d:120ms"><p class="t-lead">{e(s["lead"])}</p><a class="go" href="/contact/">Book a free home consultation</a></div>
  </div>
</section>
<section aria-label="Photographs"><div class="wrap pair">{a}{b}{c}</div></section>
<section class="sec" aria-labelledby="spec-h">
  <div class="wrap spec"><h2 id="spec-h" class="t-h2 rv">{e(s["spec_h"])}</h2><dl class="hl">{spec}</dl></div>
</section>
{ba}<section class="sec{" bg-2" if not ba else ""}" aria-labelledby="pj-h">
  <div class="wrap">
    <div class="head"><h2 id="pj-h" class="t-h2 rv">{SING[s["slug"]]} projects</h2><p class="rv" style="--d:120ms">Each one designed, made in our workshop and fitted by our team.</p></div>
    <div class="works">{cards}</div>
  </div>
</section>
{gal}{rvw}{close_band()}<section class="sec--tight" aria-label="Other rooms"><div class="wrap" style="display:flex;flex-wrap:wrap;gap:12px 28px;align-items:center"><span class="muted">Other rooms:</span>{others}</div></section>
</main>
''' + footer() + lightbox() + tail(G)
    write(f'/{s["slug"]}/', body)

# ------------------------------------------------------------------ project pages
def project(p, nxt):
    title = f'{p["title"]} | Joinwell Joinery'
    desc = f'{p["title"]}: {p["lead"]}'
    if len(desc) > 158: desc = desc[:155].rsplit(' ', 1)[0] + '…'
    h = head(title, desc, f'/work/{p["slug"]}/')
    svc = ', '.join(f'<a class="u" href="/{k}/">{SERV[k]}</a>' for k in p['svc'])
    facts = f'<div class="rv" style="--d:200ms"><dt>Services</dt><dd>{svc}</dd></div>'
    facts += f'<div class="rv" style="--d:280ms"><dt>Location</dt><dd>{e(p["place"] or "North West")}</dd></div>'
    facts += f'<div class="rv" style="--d:360ms"><dt>Details</dt><dd>{e(p["details"])}</dd></div>'
    band_list = p['band'] or p['photos'][:3]
    band = ''.join(f'<a class="ph ph--link" href="{big(st)}" data-open="p" data-index="{p["photos"].index(st) if st in p["photos"] else 0}"><span class="par" data-par="3">{img(st, "(max-width: 899px) 82vw, 35vw", p["title"] + ", photograph " + str(i + 1), lazy=(i > 0))}</span></a>' for i, st in enumerate(band_list))
    rest_ph = [st for st in p['photos'] if st not in band_list and st != p.get('before')]
    if p.get('before'): rest_ph.insert(0, p['before'])
    gal_list = band_list + rest_ph
    rest_ph = rest_ph[:len(rest_ph) // 3 * 3]  # full rows only; every photo stays in the viewer
    items = ''.join(f'<a href="{big(st)}" data-open="p" data-index="{len(band_list) + i}"><span class="ph ph--link"><span class="par" data-par="3">{img(st, "(max-width: 899px) 48vw, 33vw", p["title"] + (", before" if st == p.get("before") else ", photograph " + str(len(band_list) + i + 1)))}</span></span>{BEFORE_CAP if st == p.get("before") else ""}</a>' for i, st in enumerate(rest_ph))
    G = {'p': (p['title'], gal_list)}
    rest = ''.join(f'<p>{e(x)}</p>' for x in p['rest'])
    body = h + nav('work') + f'''<main id="content">
<section class="phead" aria-labelledby="h1">
  <div class="wrap g12">
    <p class="crumb"><a class="u" href="/work/">Our work</a><span aria-hidden="true">/</span><span>{e(p["title"])}</span></p>
    <h1 id="h1" class="rv">{e(p["title"])}</h1>
    <div class="phead__aside rv" style="--d:120ms"><p class="t-lead">{e(p["sub"])}</p></div>
    <dl class="facts hl">{facts}</dl>
  </div>
</section>
<section class="band" aria-label="Photographs" style="--n:{len(band_list)}">{band}</section>
<section class="ptext sec" aria-label="About the project">
  <div class="wrap g12"><p class="lead rv">{e(p["lead"])}</p><div class="rest rv" style="--d:120ms">{rest}<a class="go" href="/contact/">Book a free home consultation</a></div></div>
</section>
{f'<section aria-label="More photographs" class="sec" style="--sec-top:0"><div class="wrap"><div class="gal">{items}</div></div></section>' if items else ''}
<section class="sec" style="--sec-top:0" aria-label="Next project">
  <div class="wrap"><a class="next" href="/work/{nxt["slug"]}/"><span class="ph ph--link"><span class="par" data-par="4">{img(nxt["cover"], "(max-width: 899px) 92vw, 92vw", nxt["title"])}</span></span><span class="next__t"><span>Next project</span><b>{e(nxt["title"])}</b><span>{e(svc_line(nxt))}</span></span></a></div>
</section>
{close_band()}</main>
''' + footer() + lightbox() + tail(G)
    write(f'/work/{p["slug"]}/', body)

# ------------------------------------------------------------------ work index
def work():
    h = head('Our work | Joinwell Joinery', 'Bespoke kitchens, wardrobes, media walls, bathrooms and staircases designed, made and fitted by Joinwell Joinery in the North West.', '/work/')
    rows = ''.join(f'<a class="ix__row rv" style="--d:{min(i, 8) * 60}ms" href="/work/{p["slug"]}/" data-k="{p["slug"]}"><span class="ix__name">{e(p["title"])}</span><span class="ix__meta">{e(svc_line(p))}{(" · " + e(p["place"].split(",")[0])) if p["place"] else ""}</span></a>' for i, p in enumerate(P))
    plates = ''.join(img(p['cover'], '(max-width: 899px) 1px, 40vw', p['title'], cls='is-on' if i == 0 else '', attrs=f' data-k="{p["slug"]}" data-cap="{e(p["details"])}"') for i, p in enumerate(P))
    rail = ''.join(f'<a href="/work/{p["slug"]}/"><span class="ph">{img(p["cover"], "78vw", p["title"])}</span><h3>{e(p["title"])}</h3><p class="cap">{e(svc_line(p))}</p></a>' for p in P)
    cats = ['kitchens', 'wardrobes', 'media-walls', 'bathrooms', 'staircases']
    shots = []
    for p in P:
        for st in [x for x in p['photos'] if x != p.get('before')][:3]:
            shots.append((st, p))
    btns = '<button type="button" data-f="all" aria-pressed="true">All</button>' + ''.join(f'<button type="button" data-f="{c}" aria-pressed="false">{SERV[c]}</button>' for c in cats)
    items = ''.join(f'<a href="/work/{p["slug"]}/" data-cat="{" ".join(p["svc"])}"><span class="ph ph--link">{img(st, "(max-width: 899px) 48vw, 25vw", p["title"])}</span><span class="cap">{e(p["title"])}</span></a>' for st, p in shots)
    body = h + nav('work') + f'''<main id="content">
<section class="phead" aria-labelledby="h1">
  <div class="wrap g12">
    <h1 id="h1" class="rv">Bespoke furniture we have designed, made and fitted</h1>
    <div class="phead__aside rv" style="--d:120ms"><p class="t-lead">{len(P)} projects from homes in the North West, each one designed, made in our workshop and fitted by our team.</p></div>
  </div>
</section>
<section class="sec" style="--sec-top:0" aria-label="Projects" data-client-only>
  <div class="wrap"><div class="ix" data-ix>
    <nav class="ix__rows hl" aria-label="Projects">{rows}</nav>
    <div class="ix__plate" aria-hidden="true">{plates}<p class="ix__cap">{e(P[0]["details"])}</p></div>
    <div class="ix__rail rail">{rail}</div>
  </div></div>
</section>
<section class="sec bg-2" aria-labelledby="show-h">
  <div class="wrap">
    <div class="head"><h2 id="show-h" class="t-h2 rv">Every room, by type</h2><p class="rv" style="--d:120ms"><span data-count>{len(shots)} photographs</span> from the projects above. Choose a room to filter.</p></div>
    <div class="filters" data-filters role="group" aria-label="Filter by room">{btns}</div>
    <div class="show" style="--cols:4">{items}</div>
  </div>
</section>
{close_band()}</main>
''' + footer() + tail()
    write('/work/', body)

# ------------------------------------------------------------------ contact, thanks, privacy, 404
def contact():
    h = head('Book a free home consultation | Joinwell Joinery', 'Book a free home consultation and quotation for a bespoke kitchen, wardrobe, media wall, bathroom or staircase in the North West. Call +44 7948 347730.', '/contact/')
    opts = ''.join(f'<option>{o}</option>' for o in ['Kitchen', 'Fitted wardrobes or bedroom', 'Media wall or living room', 'Bathroom or vanity unit', 'Staircase', 'Renovation', 'Something else'])
    area = ', '.join(AREA)
    body = h + nav('contact') + f'''<main id="content">
<section class="phead" aria-labelledby="h1">
  <div class="wrap g12">
    <h1 id="h1" class="rv">Book a free home consultation</h1>
    <div class="phead__aside rv" style="--d:120ms"><p class="t-lead">Tell us about the room. We will come to you for a complimentary home consultation and send a free quotation.</p><a class="close__tel" href="tel:{PHONE_T}">{PHONE_D}</a><a class="u" href="mailto:{EMAIL}">{EMAIL}</a></div>
  </div>
</section>
<section class="sec" style="--sec-top:0" aria-label="Enquiry form">
  <div class="wrap cform">
    <form action="https://formsubmit.co/{EMAIL}" method="POST" enctype="multipart/form-data" novalidate data-enquiry>
      <input type="hidden" name="_subject" value="New enquiry from the Joinwell Joinery website">
      <input type="hidden" name="_template" value="table">
      <input type="hidden" name="_next" value="/thanks/">
      <input type="text" name="_honey" class="hp" tabindex="-1" autocomplete="off" aria-hidden="true">
      <div class="field"><label for="f-name">Name</label><input id="f-name" name="name" autocomplete="name" required><p class="msg" aria-live="polite"></p></div>
      <div class="field"><label for="f-phone">Phone</label><input id="f-phone" name="phone" type="tel" autocomplete="tel" required><p class="msg" aria-live="polite"></p></div>
      <div class="field"><label for="f-email">Email</label><input id="f-email" name="email" type="email" autocomplete="email" required><p class="msg" aria-live="polite"></p></div>
      <div class="field"><label for="f-loc">Town or postcode</label><input id="f-loc" name="location" autocomplete="postal-code" required><p class="msg" aria-live="polite"></p></div>
      <div class="field field--full"><label for="f-svc">What would you like made?</label><select id="f-svc" name="service">{opts}</select><p class="msg" aria-live="polite"></p></div>
      <div class="field field--full"><label for="f-msg">Tell us about the room <span>(optional)</span></label><textarea id="f-msg" name="message" placeholder="e.g. alcove wardrobes either side of the chimney breast, sloping ceiling on one side"></textarea><p class="msg" aria-live="polite"></p></div>
      <div class="field field--full"><label for="f-photos">Photos of the room <span>(optional)</span></label><input id="f-photos" name="attachment" type="file" accept="image/jpeg,image/png,image/heic,image/webp"><p class="hint">One photo, JPG or PNG, up to 5 MB.</p><p class="msg" aria-live="polite"></p></div>
      <div class="send"><button class="btn" type="submit">Send enquiry</button><p>Free, no-obligation quotation. We use your details only to reply to this enquiry; see our <a class="u" href="/privacy/">privacy notice</a>.</p></div>
    </form>
    <aside>
      <figure><span class="ph">{img("p18-1", "(max-width: 899px) 92vw, 33vw", "Media wall with lit shelving and a fire, Lytham", lazy=False)}</span><figcaption class="cap" style="margin-top:10px">Media wall · Lytham</figcaption></figure>
      <ol class="next-steps hl">
        <li class="rv"><b>We get in touch</b>to arrange a time that suits you.</li>
        <li class="rv" style="--d:90ms"><b>We visit your home</b>to measure the room and talk it through.</li>
        <li class="rv" style="--d:180ms"><b>You receive a free quotation</b>for the design, making and fitting.</li>
      </ol>
      <p class="muted">We work across {area}, and throughout the North West.</p>
    </aside>
  </div>
</section>
</main>
''' + footer(tab=False) + tail()
    write('/contact/', body)

def simple(path, title, desc, h1, inner, noindex=False, cur=''):
    h = head(title, desc, path, noindex=noindex)
    body = h + nav(cur) + f'''<main id="content">
<section class="phead" aria-labelledby="h1"><div class="wrap g12"><h1 id="h1" class="rv">{h1}</h1></div></section>
<section class="sec" style="--sec-top:0"><div class="wrap"><div class="prose{" prose--one" if noindex else ""}">{inner}</div></div></section>
</main>
''' + footer() + tail()
    write(path, body)

def pages_misc():
    simple('/thanks/', 'Thank you | Joinwell Joinery', 'Your enquiry has been sent to Joinwell Joinery.', 'Thank you, your enquiry is on its way',
           f'<p class="t-lead">It has gone to {EMAIL}. We will be in touch to arrange your free home consultation.</p><p>If it is easier to talk, call <a class="u" href="tel:{PHONE_T}">{PHONE_D}</a>.</p><p><a class="go" href="/work/">Look through our work</a></p>', noindex=True)
    simple('/privacy/', 'Privacy notice | Joinwell Joinery', 'How Joinwell Joinery Ltd uses the details you send through this website.', 'Privacy notice', f'''
<p class="t-lead">This notice explains what happens to the details you send us through this website.</p>
<h2>Who we are</h2><p>{LEGAL} You can contact us at <a class="u" href="mailto:{EMAIL}">{EMAIL}</a> or on <a class="u" href="tel:{PHONE_T}">{PHONE_D}</a>.</p>
<h2>What we collect</h2><p>When you send an enquiry we receive the details you enter: your name, phone number, email address, town or postcode, the type of work, your message and any photo you attach.</p>
<h2>Why we use it</h2><p>We use these details only to reply to your enquiry, arrange a home consultation and prepare a quotation. Our lawful basis is taking steps at your request before entering into a contract.</p>
<h2>How it reaches us</h2><p>The form is delivered to our email inbox by FormSubmit, a form-handling service. We do not sell or share your details with anyone else.</p>
<h2>How long we keep it</h2><p>We keep enquiries for as long as we need them to deal with your enquiry and any work that follows, and then delete them.</p>
<h2>Cookies</h2><p>This website does not use analytics, advertising or tracking cookies.</p>
<h2>Your rights</h2><p>Under UK data protection law you can ask to see, correct or delete the details we hold about you. Email us and we will deal with it. You can also complain to the Information Commissioner’s Office at ico.org.uk.</p>''')
    h = head('Page not found | Joinwell Joinery', 'This page could not be found.', '/404.html', noindex=True)
    body = h + nav('') + f'''<main id="content"><section class="phead" aria-labelledby="h1"><div class="wrap g12"><h1 id="h1">This page could not be found</h1><div class="phead__aside"><p class="t-lead">The link may be out of date.</p><a class="go" href="/">Go to the home page</a><a class="go" href="/work/">See our work</a></div></div></section></main>
''' + footer() + tail()
    write('/404.html', body)

# ------------------------------------------------------------------ assets: css, js, sitemap
def build_assets():
    css = (ROOT / 'css/src/fonts.css').read_text() + '\n' + (ROOT / 'css/src/tokens.css').read_text() + '\n' + (LIB / 'base.css').read_text() + '\n' + (LIB / 'motion.css').read_text() + '\n' + (ROOT / 'css/src/joinwell.css').read_text()
    (ROOT / 'css/site.css').write_text(css)
    js = (LIB / 'motion.js').read_text() + '\n' + (ROOT / 'js/src/joinwell.js').read_text()
    (ROOT / 'js/site.js').write_text(js)

def sitemap():
    base = SITE
    order = ['/', '/work/', '/kitchens/', '/wardrobes/', '/media-walls/', '/bathrooms/', '/staircases/', '/renovations/', '/contact/',
             '/work/poolside/', '/work/cloakroom-lytham-st-annes/', '/work/black-kitchen-and-island/']
    rest = [f'/work/{p["slug"]}/' for p in P if f'/work/{p["slug"]}/' not in order] + ['/privacy/']
    urls = ''.join(f'<url><loc>{base}{u}</loc><lastmod>2026-10-01</lastmod></url>' for u in order + rest)
    (ROOT / 'sitemap.xml').write_text(f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{urls}</urlset>\n')
    (ROOT / 'robots.txt').write_text(f'User-agent: *\nAllow: /\nSitemap: {base}/sitemap.xml\n')

if __name__ == '__main__':
    build_assets()
    home(); work(); contact(); pages_misc()
    for s in S: service(s)
    for i, p in enumerate(P): project(p, P[(i + 1) % len(P)])
    sitemap()
    print('pages:', 2 + 1 + 3 + len(S) + len(P))
