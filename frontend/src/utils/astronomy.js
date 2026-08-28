// Astronomical calculations: RA/Dec ↔ Alt/Az, planet positions
// Accuracy: ~1–2° for planets, <1′ for star positions (sufficient for sky-map display)

const D = Math.PI / 180

function norm360(x) { return ((x % 360) + 360) % 360 }
function norm24(x)  { return ((x % 24)  + 24)  % 24  }

// Julian Date from a JS Date
export function julianDate(date = new Date()) {
  return date.getTime() / 86400000 + 2440587.5
}

// Greenwich Mean Sidereal Time in degrees
function gmst(jd) {
  const T = (jd - 2451545.0) / 36525
  return norm360(280.46061837 + 360.98564736629 * (jd - 2451545) +
                 0.000387933 * T * T - T * T * T / 38710000)
}

// Local Sidereal Time in degrees
function lst(jd, lngDeg) {
  return norm360(gmst(jd) + lngDeg)
}

/**
 * Convert equatorial (RA hours, Dec degrees) → topocentric { alt, az } in degrees.
 * alt > 0 means above the horizon.
 */
export function raDecToAltAz(ra_h, dec_deg, lat_deg, lng_deg, date = new Date()) {
  const jd  = julianDate(date)
  const LST = lst(jd, lng_deg)
  const HA  = norm360(LST - ra_h * 15)        // hour angle in degrees

  const ha  = HA * D
  const dec = dec_deg * D
  const lat = lat_deg * D

  const sinAlt = Math.sin(dec) * Math.sin(lat) + Math.cos(dec) * Math.cos(lat) * Math.cos(ha)
  const alt = Math.asin(Math.max(-1, Math.min(1, sinAlt))) / D

  const cosAz = (Math.sin(dec) - Math.sin(lat) * sinAlt) / (Math.cos(lat) * Math.cos(alt * D))
  let az = Math.acos(Math.max(-1, Math.min(1, cosAz))) / D
  if (Math.sin(ha) > 0) az = 360 - az

  return { alt, az }
}

// ─── Planet positions ─────────────────────────────────────────────────────────
// Keplerian elements at J2000.0 with rates per Julian century (Meeus Table 33.a)
// Columns: [a0, e0, i0, L0, lp0, Om0, da, de, di, dL, dlp, dOm]
const KEP = {
  Mercury: [0.38709927,0.20563593,7.00497902,252.25032350,77.45779628,48.33076593,
            0.00000037,0.00001906,-0.00594749,149472.67411175,0.16047689,-0.12534081],
  Venus:   [0.72333566,0.00677672,3.39467605,181.97909950,131.60246718,76.67984255,
            0.00000390,-0.00004107,-0.00078890,58517.81538729,0.00268329,-0.27769418],
  Earth:   [1.00000261,0.01671123,-0.00001531,100.46457166,102.93768193,0.0,
            0.00000562,-0.00004392,-0.01294668,35999.37244981,0.32327364,0.0],
  Mars:    [1.52371034,0.09339410,1.84969142,-4.55343205,-23.94362959,49.55953891,
            0.00001847,0.00007882,-0.00813131,19140.30268499,0.44441088,-0.29257343],
  Jupiter: [5.20288700,0.04838624,1.30439695,34.39644051,14.72847983,100.47390909,
            -0.00011607,-0.00013253,-0.00183714,3034.74612775,0.21252668,0.20469106],
  Saturn:  [9.53667594,0.05386179,2.48599187,49.95424423,92.59887831,113.66242448,
            -0.00125060,-0.00050991,0.00193609,1222.49362201,-0.41897216,-0.28867794],
  Uranus:  [19.18916464,0.04725744,0.77263783,313.23810451,170.95427630,74.01692503,
            -0.00196176,-0.00004397,-0.00242939,428.48202785,0.40805281,0.04240589],
  Neptune: [30.06992276,0.00859048,1.77004347,-55.12002969,44.96476227,131.78422574,
            0.00026291,0.00005105,0.00035372,218.45945325,-0.32241464,-0.00508664],
}

function solveKepler(M_deg, e) {
  let E = M_deg
  for (let i = 0; i < 10; i++) E = M_deg + (e * 180 / Math.PI) * Math.sin(E * D)
  return E
}

function heliocentricXYZ(name, T) {
  const [a0,e0,i0,L0,lp0,Om0,da,de,di,dL,dlp,dOm] = KEP[name]
  const a  = a0 + da * T
  const e  = e0 + de * T
  const i  = (i0 + di * T) * D
  const L  = norm360(L0 + dL * T)
  const lp = lp0 + dlp * T
  const Om = Om0 + dOm * T

  const w  = norm360(lp - Om) * D
  const Om_r = Om * D
  const M  = norm360(L - lp)
  const E  = solveKepler(M, e) * D

  const nu_sin = Math.sqrt(1 - e * e) * Math.sin(E)
  const nu_cos = Math.cos(E) - e
  const nu = Math.atan2(nu_sin, nu_cos)
  const r  = a * (1 - e * Math.cos(E))

  const x = r * (Math.cos(Om_r) * Math.cos(w + nu) - Math.sin(Om_r) * Math.sin(w + nu) * Math.cos(i))
  const y = r * (Math.sin(Om_r) * Math.cos(w + nu) + Math.cos(Om_r) * Math.sin(w + nu) * Math.cos(i))
  const z = r * (Math.sin(w + nu) * Math.sin(i))
  return { x, y, z }
}

/** Return { ra (hours), dec (degrees) } for a planet on the given date */
export function getPlanetRaDec(name, date = new Date()) {
  const T = (julianDate(date) - 2451545.0) / 36525
  const p = heliocentricXYZ(name, T)
  const e = heliocentricXYZ('Earth', T)

  const dx = p.x - e.x
  const dy = p.y - e.y
  const dz = p.z - e.z

  // Obliquity of ecliptic
  const eps = (23.439291111 - 0.013004167 * T) * D
  const X = dx
  const Y = dy * Math.cos(eps) - dz * Math.sin(eps)
  const Z = dy * Math.sin(eps) + dz * Math.cos(eps)

  const ra  = norm24(Math.atan2(Y, X) / D / 15)
  const dec = Math.atan2(Z, Math.sqrt(X * X + Y * Y)) / D
  return { ra, dec }
}
