"""Illustrations of the sample mother's album (mb360.persona). Drawn here, no real ultrasound or photograph (hard rule 3)."""


def _frame(body: str, defs: str = "") -> str:
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 400" width="800" height="800">'
            f'<defs>{defs}</defs>{body}</svg>')


def ultrasound(week: int, curl: float = 0) -> str:
    defs = ('<radialGradient id="f" cx="50%" cy="8%" r="95%"><stop offset="0" stop-color="#5A6A70"/><stop offset=".6" stop-color="#2E3A3F"/>'
            '<stop offset="1" stop-color="#1A2225"/></radialGradient>'
            '<filter id="n" x="0" y="0" width="100%" height="100%"><feTurbulence type="fractalNoise" baseFrequency=".9" numOctaves="2" seed="4"/>'
            '<feColorMatrix values="0 0 0 0 1 0 0 0 0 1 0 0 0 0 1 0 0 0 .55 0"/><feComposite in2="SourceGraphic" operator="in"/></filter>'
            '<radialGradient id="b" cx="45%" cy="40%" r="70%"><stop offset="0" stop-color="#E4EBED"/><stop offset="1" stop-color="#6F7F86"/></radialGradient>')
    fan = "M200 40 L372 300 A210 210 0 0 1 28 300 Z"
    baby = (f'<g transform="rotate({curl} 200 215)"><ellipse cx="160" cy="185" rx="50" ry="44" fill="url(#b)"/>'
            '<path d="M200 200c38-8 72 12 76 50 3 30-24 50-58 44-34-5-58-30-54-60z" fill="url(#b)" opacity=".92"/>'
            '<path d="M250 285c18 6 30 18 24 28M205 290c-6 14-18 22-30 18" stroke="#AEBBC0" stroke-width="10" stroke-linecap="round" fill="none"/></g>')
    ticks = "".join(f'<path d="M386 {y}h-{10 if i % 2 else 16}"/>' for i, y in enumerate(range(70, 350, 28)))
    return _frame(f'<rect width="400" height="400" fill="#10171A"/><path d="{fan}" fill="url(#f)"/><path d="{fan}" filter="url(#n)" opacity=".5"/>{baby}'
                  f'<text x="16" y="30" font-family="Roboto,Arial,sans-serif" font-size="16" fill="#B4C0C4">TCI · SA {week}W</text>'
                  f'<g stroke="#7F8F95" stroke-width="2">{ticks}</g>', defs)


def bump(bg: str = "#F4E3D7", dress: str = "#7FCFA4") -> str:
    return _frame(f'<rect width="400" height="400" fill="{bg}"/><circle cx="320" cy="80" r="46" fill="#fff" opacity=".55"/>'
                  '<circle cx="192" cy="82" r="42" fill="#F2C9A8"/><path d="M152 78c0-34 26-50 44-50s46 18 42 58c-8-20-22-30-40-30-20 0-36 8-46 22z" fill="#5A3A2C"/>'
                  f'<path d="M150 140c-22 60-30 150-38 260h172c0-40 4-70 22-96 22-32 8-74-34-82-16-3-30-30-36-82z" fill="{dress}"/>'
                  '<path d="M152 150c-22 30-18 80 32 118 22 16 58 14 70-4" stroke="#F2C9A8" stroke-width="22" stroke-linecap="round" fill="none"/>'
                  '<path d="M258 232c-4-10-20-8-20 4 0 12 20 24 20 24s20-12 20-24c0-12-16-14-20-4z" fill="#F66A0B"/>')


def hands(bg: str = "#DCEBE1") -> str:
    return _frame(f'<rect width="400" height="400" fill="{bg}"/><circle cx="200" cy="240" r="130" fill="#BFE5C9"/>'
                  '<path d="M60 400c10-70 50-110 110-120 20-3 34 10 30 26-3 12-16 18-40 22 40 0 50 24 30 72z" fill="#F2C9A8"/>'
                  '<path d="M340 400c-10-70-50-110-110-120-20-3-34 10-30 26 3 12 16 18 40 22-40 0-50 24-30 72z" fill="#E6B48F"/>'
                  '<path d="M200 176c-12-26-58-18-58 18 0 38 58 72 58 72s58-34 58-72c0-36-46-44-58-18z" fill="#00A651"/>'
                  '<path d="M200 200c-6-12-26-8-26 8 0 16 26 32 26 32s26-16 26-32c0-16-20-20-26-8z" fill="#fff"/>')


def park(bg: str = "#CDEBF3") -> str:
    return _frame(f'<rect width="400" height="400" fill="{bg}"/><circle cx="310" cy="84" r="40" fill="#FFD27A"/>'
                  '<path d="M0 270c80-50 150-50 220-20s120 20 180-10v160H0z" fill="#8FD6A2"/><path d="M0 320c100-40 220-30 400-10v90H0z" fill="#48D07C"/>'
                  '<rect x="92" y="170" width="16" height="110" fill="#8A5A3C"/><circle cx="100" cy="146" r="56" fill="#00A651"/><circle cx="62" cy="176" r="34" fill="#48D07C"/>'
                  '<circle cx="136" cy="178" r="32" fill="#48D07C"/><circle cx="262" cy="232" r="16" fill="#F2C9A8"/><path d="M246 252c-8 20-12 50-14 80h60c2-16 6-26 10-36 6-18-6-30-22-34-6-2-8-6-8-10z" fill="#F66A0B"/>')


def clothes(bg: str = "#F6EBC9") -> str:
    return _frame(f'<rect width="400" height="400" fill="{bg}"/><path d="M40 90h320" stroke="#B9A77C" stroke-width="5"/>'
                  '<path d="M130 92l-46 34 22 34 18-12v96h100v-96l18 12 22-34-46-34c-8 22-20 30-44 30s-36-8-44-30z" fill="#7FCFA4"/>'
                  '<circle cx="174" cy="176" r="8" fill="#fff"/><circle cx="174" cy="204" r="8" fill="#fff"/>'
                  '<path d="M286 92l-14 44 10 8v60h44v-60l10-8-14-44c-4 10-10 14-18 14s-14-4-18-14z" fill="#F7B38A"/>'
                  '<path d="M104 300c0-18 20-30 40-30s40 12 40 30-18 22-40 22-40-4-40-22zM216 300c0-18 20-30 40-30s40 12 40 30-18 22-40 22-40-4-40-22z" fill="#fff"/>')


def flowers(bg: str = "#F6DCE3") -> str:
    def f(x, y, c):
        petals = "".join(f'<circle cx="{x + dx}" cy="{y + dy}" r="20" fill="{c}"/>' for dx, dy in ((0, -22), (21, -7), (13, 18), (-13, 18), (-21, -7)))
        return petals + f'<circle cx="{x}" cy="{y}" r="13" fill="#FFD27A"/>'
    return _frame(f'<rect width="400" height="400" fill="{bg}"/><path d="M200 400V210M120 400V250M280 400V240" stroke="#00A651" stroke-width="8"/>'
                  f'{f(200, 170, "#F66A0B")}{f(116, 226, "#fff")}{f(284, 214, "#E86A92")}')


FILES = {"us-24.svg": lambda: ultrasound(24), "us-20.svg": lambda: ultrasound(20, -8), "us-16.svg": lambda: ultrasound(16, 6),
         "us-12.svg": lambda: ultrasound(12, -14), "us-8.svg": lambda: ultrasound(8, 10),
         "bump-1.svg": lambda: bump(), "bump-2.svg": lambda: bump("#E2EFE3", "#F7B38A"), "bump-3.svg": lambda: bump("#F6EBC9", "#8CC9D8"),
         "hands.svg": hands, "park.svg": park, "clothes.svg": clothes, "flowers.svg": flowers}
