#!/usr/bin/env python3
"""Generate a premium animated certifications SVG for the profile README."""
import os
import html

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
OUTPUT = os.path.join(ROOT, "assets", "certifications.svg")

CERTS = [
    ("IBM", "IBM Cybersecurity Analyst", "COMPLETED", "#2FD9E8", "01"),
    ("CISCO", "Cisco Networking Basics", "COMPLETED", "#2F9BF4", "02"),
    ("IoT", "Introduction to IoT", "COMPLETED", "#8B68F5", "03"),
    ("EH", "Ethical Hacking", "COMPLETED", "#39C98A", "04"),
    ("CCNA", "CCNA", "IN PROGRESS", "#FFB52E", "05"),
]

W, H = 1200, 760

def esc(value):
    return html.escape(value, quote=True)

def main():
    svg = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" role="img" aria-labelledby="title desc">',
        '<title id="title">Certifications — Cybersecurity and Networking Credentials</title>',
        '<desc id="desc">Premium animated certification cards showing completed credentials and CCNA in progress.</desc>',
        '<defs>',
        '<linearGradient id="bg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#081018"/><stop offset="0.55" stop-color="#0A121B"/><stop offset="1" stop-color="#060C12"/></linearGradient>',
        '<linearGradient id="line" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#2FD9E8" stop-opacity="0"/><stop offset="0.5" stop-color="#2FD9E8" stop-opacity="0.9"/><stop offset="1" stop-color="#2FD9E8" stop-opacity="0"/></linearGradient>',
        '<filter id="glow" x="-80%" y="-80%" width="260%" height="260%"><feGaussianBlur stdDeviation="5" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>',
        '<filter id="soft" x="-30%" y="-30%" width="160%" height="160%"><feGaussianBlur stdDeviation="12"/></filter>',
        '<pattern id="grid" width="42" height="42" patternUnits="userSpaceOnUse"><path d="M42 0H0V42" fill="none" stroke="#17303B" stroke-width="1" opacity=".42"/></pattern>',
        '<style>',
        '.card{transform-box:fill-box;transform-origin:center;animation:float 6s ease-in-out infinite}',
        '.c2{animation-delay:-1.2s}.c3{animation-delay:-2.4s}.c4{animation-delay:-3.6s}.c5{animation-delay:-4.8s}',
        '.pulse{animation:pulse 2.8s ease-in-out infinite}.scan{animation:scan 5s linear infinite}',
        '.shine{animation:shine 3.8s ease-in-out infinite}.orbit{animation:orbit 8s linear infinite}',
        '@keyframes float{0%,100%{transform:translateY(0)}50%{transform:translateY(-5px)}}',
        '@keyframes pulse{0%,100%{opacity:.45}50%{opacity:1}}',
        '@keyframes scan{0%{transform:translateX(-500px);opacity:0}12%{opacity:.8}60%{opacity:.8}100%{transform:translateX(1450px);opacity:0}}',
        '@keyframes shine{0%,55%{transform:translateX(-520px);opacity:0}65%{opacity:.7}100%{transform:translateX(900px);opacity:0}}',
        '@keyframes orbit{to{transform:rotate(360deg)}}',
        '</style>',
        '</defs>',
        '<rect x="10" y="10" width="1180" height="740" rx="24" fill="url(#bg)" stroke="#243541"/>',
        '<rect x="11" y="11" width="1178" height="738" rx="23" fill="url(#grid)" opacity=".36"/>',
        '<g font-family="Inter,Segoe UI,Arial,sans-serif">',
        '<circle cx="1040" cy="96" r="78" fill="#2FD9E8" opacity=".035" filter="url(#soft)"/>',
        '<circle cx="1040" cy="96" r="54" fill="none" stroke="#2FD9E8" stroke-opacity=".16" stroke-dasharray="3 8" class="orbit"/>',
        '<circle cx="1040" cy="96" r="5" fill="#2FD9E8" filter="url(#glow)" class="pulse"/>',
        '<text x="62" y="78" font-size="36" font-weight="750" fill="#F2F6FA">Certifications <tspan fill="#2FD9E8">/</tspan> Credentials</text>',
        '<text x="62" y="112" font-size="19" fill="#91A4B7">Security, networking and connected-systems foundation</text>',
        '<g transform="translate(62 142)"><rect width="160" height="36" rx="18" fill="#071D1A" stroke="#126D61"/><circle cx="20" cy="18" r="6" fill="#31E6B4" class="pulse"/><text x="35" y="24" font-size="14" font-weight="700" fill="#31E6B4">CREDENTIAL LEDGER</text></g>',
        '<g transform="translate(965 142)"><rect width="177" height="36" rx="18" fill="#15160F" stroke="#73591B"/><circle cx="20" cy="18" r="6" fill="#FFB52E" class="pulse"/><text x="35" y="24" font-size="14" font-weight="700" fill="#FFCC67">1 IN PROGRESS</text></g>',
    ]

    positions = [
        (62, 215, "c1"),
        (414, 215, "c2"),
        (766, 215, "c3"),
        (238, 472, "c4"),
        (590, 472, "c5"),
    ]

    for (issuer, name, status, color, number), (x, y, cls) in zip(CERTS, positions):
        completed = status == "COMPLETED"
        w, h = 322, 220
        status_fill = "#071D1A" if completed else "#1B160A"
        status_stroke = "#126D61" if completed else "#73591B"
        status_text = "#31E6B4" if completed else "#FFCC67"
        icon_size = 58
        svg += [
            f'<g class="card {cls}">',
            f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="20" fill="#0B151E" stroke="{color}" stroke-opacity=".34"/>',
            f'<rect x="{x+1}" y="{y+1}" width="{w-2}" height="{h-2}" rx="19" fill="none" stroke="#FFFFFF" stroke-opacity=".035"/>',
            f'<circle cx="{x+42}" cy="{y+42}" r="{icon_size/2}" fill="{color}" fill-opacity=".10" stroke="{color}" stroke-opacity=".52"/>',
            f'<text x="{x+42}" y="{y+49}" text-anchor="middle" font-size="{18 if len(issuer)>3 else 21}" font-weight="800" fill="{color}">{esc(issuer)}</text>',
            f'<text x="{x+90}" y="{y+32}" font-size="12" letter-spacing="2" font-weight="700" fill="#718596">CREDENTIAL {number}</text>',
            f'<text x="{x+90}" y="{y+59}" font-size="18" font-weight="700" fill="#F2F6FA">{esc(name)}</text>',
            f'<g transform="translate({x+90} {y+78})"><rect width="{130 if completed else 137}" height="28" rx="14" fill="{status_fill}" stroke="{status_stroke}"/><circle cx="14" cy="14" r="4.5" fill="{status_text}" class="pulse"/><text x="25" y="19" font-size="11" font-weight="800" letter-spacing="1" fill="{status_text}">{esc(status)}</text></g>',
            f'<text x="{x+26}" y="{y+145}" font-size="13" fill="#91A4B7">{ "Credential verified" if completed else "Current learning track" }</text>',
        ]
        if completed:
            svg += [
                f'<rect x="{x+26}" y="{y+168}" width="270" height="5" rx="2.5" fill="#1C3038"/>',
                f'<rect x="{x+26}" y="{y+168}" width="270" height="5" rx="2.5" fill="{color}" opacity=".88"/>',
                f'<circle cx="{x+296}" cy="{y+170.5}" r="5" fill="{color}" filter="url(#glow)" class="pulse"/>',
            ]
        else:
            svg += [
                f'<rect x="{x+26}" y="{y+168}" width="270" height="5" rx="2.5" fill="#2B2414"/>',
                f'<rect x="{x+26}" y="{y+168}" width="82" height="5" rx="2.5" fill="{color}" opacity=".95"/>',
                f'<rect x="{x+26}" y="{y+168}" width="82" height="5" rx="2.5" fill="#FFFFFF" opacity=".30" class="shine"/>',
            ]
        svg += [
            f'<text x="{x+26}" y="{y+198}" font-size="11" fill="#617586">{ "COMPLETED" if completed else "IN PROGRESS · NO COMPLETION DATE CLAIMED" }</text>',
            '</g>',
        ]

    svg += [
        '<rect x="20" y="195" width="1160" height="1.5" fill="url(#line)" opacity=".35"/>',
        '<rect x="20" y="450" width="1160" height="1.5" fill="url(#line)" opacity=".20"/>',
        '<g clip-path="url(#scanClip)">',
        '<rect x="20" y="180" width="2" height="560" fill="#2FD9E8" opacity=".16" class="scan"/>',
        '</g>',
        '<defs><clipPath id="scanClip"><rect x="20" y="180" width="1160" height="560" rx="18"/></clipPath></defs>',
        '<g transform="translate(62 710)">',
        '<circle cx="0" cy="-4" r="4" fill="#2FD9E8" class="pulse"/>',
        '<text x="14" y="0" font-size="13" fill="#718596">Premium credential view · vector-only · animated status telemetry</text>',
        '</g>',
        '</g></svg>',
    ]

    with open(OUTPUT, "w", encoding="utf-8") as handle:
        handle.write("\n".join(svg) + "\n")

if __name__ == "__main__":
    main()
