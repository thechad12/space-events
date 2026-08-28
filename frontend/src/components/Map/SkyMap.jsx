import { useState, useEffect, useRef, useMemo, useCallback } from 'react'
import { Compass, Camera, CameraOff, Info, Layers, X } from 'lucide-react'
import EventModal from '../Events/EventModal'
import { raDecToAltAz, getPlanetRaDec } from '../../utils/astronomy'
import { BRIGHT_STARS, CONSTELLATIONS, DEEP_SKY, PLANET_NAMES, PLANET_CONFIG } from '../../data/skyData'
import clsx from 'clsx'

// ─── Constants ────────────────────────────────────────────────────────────────
const CX = 200, CY = 200, R = 156
const CLUSTER_DIST = 30   // SVG units — pins closer than this get grouped

const CARDINALS = [
  { label: 'N', az: 0 }, { label: 'NE', az: 45 }, { label: 'E', az: 90 },
  { label: 'SE', az: 135 },{ label: 'S', az: 180 },{ label: 'SW', az: 225 },
  { label: 'W', az: 270 }, { label: 'NW', az: 315 },
]

const EVENT_COLOR = {
  rocket_launch:'#38bdf8', meteor_shower:'#fbbf24', aurora:'#34d399',
  solar_eclipse:'#fde047', lunar_eclipse:'#f87171', planetary:'#a78bfa', comet:'#67e8f9',
}

const DIR_AZ = {
  north:0,'north (near polaris)':0,'north-northeast':22.5,northeast:45,
  'east-northeast':67.5,east:90,'east-southeast':112.5,southeast:135,
  'south-southeast':157.5,south:180,'south-southwest':202.5,southwest:225,
  'west-southwest':247.5,west:270,'north-northwest':337.5,northwest:315,
  'northeast to overhead':45,
}

// ─── Geometry helpers ─────────────────────────────────────────────────────────

function bearing(lat1, lng1, lat2, lng2) {
  const dL = ((lng2 - lng1) * Math.PI) / 180
  const φ1 = (lat1 * Math.PI) / 180, φ2 = (lat2 * Math.PI) / 180
  const y = Math.sin(dL) * Math.cos(φ2)
  const x = Math.cos(φ1) * Math.sin(φ2) - Math.sin(φ1) * Math.cos(φ2) * Math.cos(dL)
  return ((Math.atan2(y, x) * 180) / Math.PI + 360) % 360
}

// Alt/Az → SVG {sx, sy} relative to map center
function project(az, alt, rotation) {
  const a = ((az - rotation) * Math.PI) / 180
  const d = R * (1 - alt / 90)
  return { sx: CX + d * Math.sin(a), sy: CY - d * Math.cos(a) }
}

function eventSkyPos(ev, userLat, userLng) {
  switch (ev.type) {
    case 'rocket_launch': {
      const slat = ev.details?.launch_site_lat, slng = ev.details?.launch_site_lng
      if (!slat || !slng) return null
      return { az: bearing(userLat, userLng, slat, slng), alt: 8 }
    }
    case 'meteor_shower': {
      const az = DIR_AZ[ev.details?.radiant_direction?.toLowerCase()]
      return az != null ? { az, alt: 42 } : null
    }
    case 'aurora':    return { az: userLat >= 0 ? 0 : 180, alt: 18 }
    case 'solar_eclipse':
    case 'lunar_eclipse': return { az: userLat >= 0 ? 175 : 5, alt: 38 }
    case 'planetary': return { az: userLat >= 0 ? 180 : 0, alt: 33 }
    case 'comet':     return { az: userLat >= 0 ? 120 : 60, alt: 28 }
    default:          return null
  }
}

// ─── Clustering ───────────────────────────────────────────────────────────────
function clusterPins(pins) {
  const used = new Set()
  const clusters = []
  for (let i = 0; i < pins.length; i++) {
    if (used.has(i)) continue
    const group = [pins[i]]
    used.add(i)
    for (let j = i + 1; j < pins.length; j++) {
      if (used.has(j)) continue
      const dx = pins[i].sx - pins[j].sx, dy = pins[i].sy - pins[j].sy
      if (Math.sqrt(dx * dx + dy * dy) < CLUSTER_DIST) { group.push(pins[j]); used.add(j) }
    }
    const sx = group.reduce((s, p) => s + p.sx, 0) / group.length
    const sy = group.reduce((s, p) => s + p.sy, 0) / group.length
    clusters.push({ pins: group, sx, sy })
  }
  return clusters
}

// ─── Component ────────────────────────────────────────────────────────────────
const DEFAULT_LAYERS = { stars: true, constellations: true, planets: true, deepsky: false }

export default function SkyMap({ events = [], userLat, userLng }) {
  const [rotation, setRotation] = useState(0)
  const [arMode, setArMode] = useState(false)
  const [cameraOn, setCameraOn] = useState(false)
  const [compassAvail, setCompassAvail] = useState(false)
  const [layers, setLayers] = useState(DEFAULT_LAYERS)
  const [showLayers, setShowLayers] = useState(false)
  const [selected, setSelected] = useState(null)
  const [clusterPopup, setClusterPopup] = useState(null)  // { pins, sx, sy }
  const [dragState, setDragState] = useState(null)
  const [now] = useState(() => new Date())

  const videoRef = useRef(null)
  const streamRef = useRef(null)
  const svgRef = useRef(null)

  // ── Device orientation ──────────────────────────────────────────────────────
  useEffect(() => {
    if (!arMode) return
    const handler = (e) => { if (e.alpha != null) setRotation(e.alpha) }
    const name = 'ondeviceorientationabsolute' in window ? 'deviceorientationabsolute' : 'deviceorientation'
    window.addEventListener(name, handler)
    setCompassAvail(true)
    return () => window.removeEventListener(name, handler)
  }, [arMode])

  // ── Camera ──────────────────────────────────────────────────────────────────
  const startCamera = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        video: { facingMode: { ideal: 'environment' } },
      })
      streamRef.current = stream
      if (videoRef.current) { videoRef.current.srcObject = stream; videoRef.current.play() }
      setCameraOn(true)
    } catch { /* camera unavailable */ }
  }

  const stopCamera = () => {
    streamRef.current?.getTracks().forEach((t) => t.stop())
    streamRef.current = null
    setCameraOn(false)
  }

  const toggleAR = async () => {
    if (arMode) { setArMode(false); stopCamera(); return }
    if (typeof DeviceOrientationEvent?.requestPermission === 'function') {
      const r = await DeviceOrientationEvent.requestPermission()
      if (r !== 'granted') return
    }
    setArMode(true)
    startCamera()
  }

  // ── Drag to rotate ──────────────────────────────────────────────────────────
  const angleFromCenter = (cx, cy) => {
    if (!svgRef.current) return 0
    const b = svgRef.current.getBoundingClientRect()
    return Math.atan2(cy - (b.top + b.height / 2), cx - (b.left + b.width / 2))
  }
  const onPD = (e) => {
    if (arMode) return
    svgRef.current?.setPointerCapture(e.pointerId)
    setDragState({ a0: angleFromCenter(e.clientX, e.clientY), r0: rotation })
  }
  const onPM = useCallback((e) => {
    if (!dragState) return
    const diff = (angleFromCenter(e.clientX, e.clientY) - dragState.a0) * 180 / Math.PI
    setRotation(((dragState.r0 - diff) % 360 + 360) % 360)
  }, [dragState])
  const onPU = () => setDragState(null)

  const toggleLayer = (k) => setLayers((l) => ({ ...l, [k]: !l[k] }))

  // ── Heavy computations (memoized on location, not rotation) ─────────────────
  const skyData = useMemo(() => {
    // Stars
    const stars = BRIGHT_STARS.map(([name, ra, dec, mag]) => {
      const { alt, az } = raDecToAltAz(ra, dec, userLat, userLng, now)
      return { name, mag, alt, az }
    }).filter((s) => s.alt > 0)

    // Constellation lines — map [ra,dec] pairs to alt/az
    const constLines = Object.entries(CONSTELLATIONS).map(([name, polylines]) => ({
      name,
      segs: polylines.flatMap((pl) => {
        const pts = pl.map(([ra, dec]) => {
          const { alt, az } = raDecToAltAz(ra, dec, userLat, userLng, now)
          return { alt, az }
        })
        const segs = []
        for (let i = 0; i < pts.length - 1; i++) {
          if (pts[i].alt > -5 && pts[i + 1].alt > -5)  // allow slightly below horizon
            segs.push([pts[i], pts[i + 1]])
        }
        return segs
      }),
    }))

    // Planets
    const planets = PLANET_NAMES.map((name) => {
      const { ra, dec } = getPlanetRaDec(name, now)
      const { alt, az } = raDecToAltAz(ra, dec, userLat, userLng, now)
      return { name, alt, az, ...PLANET_CONFIG[name] }
    }).filter((p) => p.alt > 0)

    // Deep sky objects
    const deepSky = DEEP_SKY.map(([id, name, ra, dec, type, mag]) => {
      const { alt, az } = raDecToAltAz(ra, dec, userLat, userLng, now)
      return { id, name, type, mag, alt, az }
    }).filter((d) => d.alt > 0)

    // Event pins
    const eventPins = events
      .filter((e) => e.visibility.visible)
      .flatMap((e) => {
        const pos = eventSkyPos(e, userLat, userLng)
        return pos ? [{ event: e, az: pos.az, alt: pos.alt }] : []
      })

    return { stars, constLines, planets, deepSky, eventPins }
  }, [userLat, userLng, events])  // 'now' is stable (set at mount)

  // ── Project to SVG (fast, runs on every rotation change) ───────────────────
  const { stars, constLines, planets, deepSky, eventPins } = skyData

  const projStars = stars.map((s) => ({ ...s, ...project(s.az, s.alt, rotation) }))
  const projPlanets = planets.map((p) => ({ ...p, ...project(p.az, p.alt, rotation) }))
  const projDSO = deepSky.map((d) => ({ ...d, ...project(d.az, d.alt, rotation) }))
  const rawPins = eventPins.map((p) => ({ ...p, ...project(p.az, p.alt, rotation) }))
  const clusters = clusterPins(rawPins)

  const heading = `${Math.round(rotation)}° ${['N','NE','E','SE','S','SW','W','NW','N'][Math.round(rotation / 45) % 8]}`

  const DSO_ICON = { Galaxy: '◯', GC: '⊕', OC: '⊙', Nebula: '△', PN: '◎' }

  return (
    <div className="relative w-full h-full flex flex-col items-center overflow-hidden">

      {/* Camera feed */}
      <video ref={videoRef} muted playsInline
        className={clsx('absolute inset-0 w-full h-full object-cover transition-opacity',
          cameraOn ? 'opacity-55' : 'opacity-0 pointer-events-none')} />

      {/* Layer panel */}
      {showLayers && (
        <div className="absolute top-3 right-3 z-30 glass border border-white/10 p-3 rounded-xl shadow-xl min-w-[160px]">
          <div className="flex items-center justify-between mb-2">
            <span className="text-xs font-semibold text-white/60">Layers</span>
            <button onClick={() => setShowLayers(false)} className="text-white/40 hover:text-white/70">
              <X className="w-3.5 h-3.5" />
            </button>
          </div>
          {[
            { key: 'stars', label: 'Stars', color: 'text-white' },
            { key: 'constellations', label: 'Constellations', color: 'text-blue-300' },
            { key: 'planets', label: 'Planets', color: 'text-yellow-300' },
            { key: 'deepsky', label: 'Deep Sky Objects', color: 'text-purple-300' },
          ].map(({ key, label, color }) => (
            <button key={key} onClick={() => toggleLayer(key)}
              className="flex items-center gap-2 w-full py-1.5 text-left"
            >
              <span className={clsx('w-3.5 h-3.5 rounded border transition-all flex items-center justify-center',
                layers[key] ? 'bg-nebula-purple border-nebula-purple' : 'border-white/30'
              )}>
                {layers[key] && <span className="text-white text-[8px]">✓</span>}
              </span>
              <span className={clsx('text-xs', layers[key] ? color : 'text-white/35')}>{label}</span>
            </button>
          ))}
        </div>
      )}

      {/* Sky SVG */}
      <div className="flex-1 flex items-center justify-center w-full px-3 min-h-0">
        <svg
          ref={svgRef}
          viewBox="0 0 400 400"
          className={clsx('w-full max-w-[min(90vw,82vh)] aspect-square touch-none',
            !arMode && 'cursor-grab active:cursor-grabbing')}
          onPointerDown={onPD} onPointerMove={onPM} onPointerUp={onPU}
          onClick={() => setClusterPopup(null)}
        >
          <defs>
            <radialGradient id="skybg" cx="50%" cy="50%" r="50%">
              <stop offset="0%"   stopColor="#0c0c24" stopOpacity={cameraOn ? 0.2 : 1} />
              <stop offset="70%"  stopColor="#05050f" stopOpacity={cameraOn ? 0.4 : 1} />
              <stop offset="100%" stopColor="#010108" stopOpacity={cameraOn ? 0.6 : 1} />
            </radialGradient>
            <clipPath id="skyclip"><circle cx={CX} cy={CY} r={R} /></clipPath>
            <filter id="bloom" x="-50%" y="-50%" width="200%" height="200%">
              <feGaussianBlur stdDeviation="2" result="b"/>
              <feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge>
            </filter>
            <filter id="softglow" x="-100%" y="-100%" width="300%" height="300%">
              <feGaussianBlur stdDeviation="4" result="b"/>
              <feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge>
            </filter>
            {Object.entries(EVENT_COLOR).map(([t, c]) => (
              <radialGradient key={t} id={`eg-${t}`} cx="50%" cy="50%" r="50%">
                <stop offset="0%" stopColor={c} stopOpacity="0.8"/>
                <stop offset="100%" stopColor={c} stopOpacity="0"/>
              </radialGradient>
            ))}
          </defs>

          {/* Sky backdrop */}
          <circle cx={CX} cy={CY} r={R} fill="url(#skybg)" />

          {/* ── Stars layer ── */}
          {layers.stars && (
            <g clipPath="url(#skyclip)">
              {projStars.map((s, i) => {
                const sz = Math.max(0.4, 2.6 - s.mag * 0.5)
                const op = Math.min(0.95, Math.max(0.25, (5.5 - s.mag) / 6))
                return (
                  <circle key={i} cx={s.sx} cy={s.sy} r={sz}
                    fill="white" opacity={op}
                    filter={s.mag < 1.5 ? 'url(#bloom)' : undefined}
                  />
                )
              })}
            </g>
          )}

          {/* ── Constellation lines layer ── */}
          {layers.constellations && (
            <g clipPath="url(#skyclip)" opacity={0.45}>
              {constLines.map(({ name, segs }) =>
                segs.map((seg, i) => {
                  const a = project(seg[0].az, seg[0].alt, rotation)
                  const b = project(seg[1].az, seg[1].alt, rotation)
                  return (
                    <line key={`${name}-${i}`}
                      x1={a.sx} y1={a.sy} x2={b.sx} y2={b.sy}
                      stroke="#8899cc" strokeWidth={0.6} strokeLinecap="round"
                    />
                  )
                })
              )}
              {/* Constellation name labels */}
              {layers.constellations && constLines.map(({ name, segs }) => {
                if (!segs.length) return null
                const all = segs.flat()
                const ax = segs.reduce((s, seg) => {
                  const a = project(seg[0].az, seg[0].alt, rotation)
                  const b = project(seg[1].az, seg[1].alt, rotation)
                  return { sx: s.sx + a.sx + b.sx, sy: s.sy + a.sy + b.sy, n: s.n + 2 }
                }, { sx: 0, sy: 0, n: 0 })
                const cx2 = ax.sx / ax.n, cy2 = ax.sy / ax.n
                // Only show label if centroid is within the sky circle
                const dist = Math.sqrt((cx2 - CX) ** 2 + (cy2 - CY) ** 2)
                if (dist > R) return null
                return (
                  <text key={name} x={cx2} y={cy2}
                    textAnchor="middle" dominantBaseline="middle"
                    fill="#8899cc" fillOpacity={0.55} fontSize={6} letterSpacing={0.5}
                    style={{ pointerEvents: 'none', userSelect: 'none', fontFamily: 'system-ui' }}
                  >{name.toUpperCase()}</text>
                )
              })}
            </g>
          )}

          {/* Altitude rings */}
          {[30, 60].map((alt) => (
            <circle key={alt} cx={CX} cy={CY} r={R * (1 - alt / 90)}
              fill="none" stroke="white" strokeOpacity={0.09}
              strokeWidth={0.6} strokeDasharray="3 8" />
          ))}

          {/* Horizon ring */}
          <circle cx={CX} cy={CY} r={R}
            fill="none" stroke="white" strokeOpacity={0.2} strokeWidth={1.5} />

          {/* Cardinal labels (rotate with map) */}
          {CARDINALS.map(({ label, az }) => {
            const { sx, sy } = project(az, -5.5, rotation)
            const main = label.length === 1
            return (
              <text key={label} x={sx} y={sy}
                textAnchor="middle" dominantBaseline="middle"
                fill={label === 'N' ? '#a78bfa' : 'white'}
                fillOpacity={main ? 0.75 : 0.3}
                fontSize={main ? 11 : 7.5}
                fontWeight={main ? '700' : '400'}
              >{label}</text>
            )
          })}

          {/* Altitude labels */}
          {[30, 60].map((alt) => (
            <text key={alt} x={CX + 3} y={CY - R * (1 - alt / 90) + 5}
              fill="white" fillOpacity={0.16} fontSize={6}>{alt}°</text>
          ))}

          {/* ── Deep Sky Objects layer ── */}
          {layers.deepsky && projDSO.map((d) => (
            <g key={d.id}>
              <text x={d.sx} y={d.sy + 1}
                textAnchor="middle" dominantBaseline="middle"
                fill="#c084fc" fontSize={8} opacity={0.65}
                style={{ pointerEvents: 'none' }}
              >{DSO_ICON[d.type] ?? '○'}</text>
              <text x={d.sx} y={d.sy + 10}
                textAnchor="middle"
                fill="#c084fc" fontSize={5.5} opacity={0.5}
                style={{ pointerEvents: 'none' }}
              >{d.id}</text>
            </g>
          ))}

          {/* ── Planets layer ── */}
          {layers.planets && projPlanets.map((p) => (
            <g key={p.name} filter="url(#softglow)">
              <circle cx={p.sx} cy={p.sy} r={p.radius + 5}
                fill={p.color} fillOpacity={0.15} />
              <circle cx={p.sx} cy={p.sy} r={p.radius}
                fill={p.color} stroke="white" strokeWidth={0.5} strokeOpacity={0.4} />
              <text x={p.sx} y={p.sy + p.radius + 8}
                textAnchor="middle" fill={p.color} fontSize={7} opacity={0.9}
                style={{ pointerEvents: 'none' }}
              >{p.name}</text>
            </g>
          ))}

          {/* ── Aurora glow ── */}
          {clusters.filter((c) => c.pins.some((p) => p.event.type === 'aurora'))
            .map((c, i) => (
              <ellipse key={i} cx={c.sx} cy={c.sy} rx={58} ry={17}
                fill="#34d399" fillOpacity={0.06}
                stroke="#34d399" strokeOpacity={0.18} strokeWidth={1} />
            ))}

          {/* ── Event clusters ── */}
          {clusters.map((cluster, ci) => {
            const { sx, sy, pins } = cluster
            const single = pins.length === 1
            const ev = pins[0].event
            const color = EVENT_COLOR[ev.type] ?? '#ffffff'

            if (single) {
              const label = ev.name.split(/[|—–]/)[0].trim().split(' ').slice(0, 3).join(' ')
              return (
                <g key={ci} className="cursor-pointer" role="button"
                  onClick={(e) => { e.stopPropagation(); setSelected(ev); setClusterPopup(null) }}>
                  <circle cx={sx} cy={sy} r={20} fill={`url(#eg-${ev.type})`} />
                  <circle cx={sx} cy={sy} r={4.5} fill={color}
                    stroke="white" strokeWidth={0.7} strokeOpacity={0.7}
                    filter="url(#bloom)" />
                  <text x={sx} y={sy + 13} textAnchor="middle"
                    fill={color} fontSize={6.5} opacity={0.9}
                    style={{ pointerEvents: 'none' }}>{label}</text>
                </g>
              )
            }

            // Multi-event cluster
            const isOpen = clusterPopup && clusterPopup.ci === ci
            return (
              <g key={ci} className="cursor-pointer"
                onClick={(e) => {
                  e.stopPropagation()
                  setClusterPopup(isOpen ? null : { ci, pins, sx, sy })
                }}>
                {/* Outer rings */}
                {pins.map((_, k) => (
                  <circle key={k} cx={sx + k * 2} cy={sy - k * 2} r={4}
                    fill={EVENT_COLOR[pins[k].event.type] ?? '#fff'}
                    opacity={0.4 - k * 0.1} />
                ))}
                {/* Main dot */}
                <circle cx={sx} cy={sy} r={7} fill="#7c3aed"
                  stroke="white" strokeWidth={0.8} strokeOpacity={0.6}
                  filter="url(#bloom)" />
                {/* Count badge */}
                <text x={sx} y={sy + 1} textAnchor="middle" dominantBaseline="middle"
                  fill="white" fontSize={6.5} fontWeight="600"
                  style={{ pointerEvents: 'none' }}>{pins.length}</text>
                <text x={sx} y={sy + 14} textAnchor="middle"
                  fill="#a78bfa" fontSize={6} opacity={0.8}
                  style={{ pointerEvents: 'none' }}>tap to expand</text>
              </g>
            )
          })}

          {/* Zenith marker */}
          <circle cx={CX} cy={CY} r={3} fill="white" fillOpacity={0.3} />
          <circle cx={CX} cy={CY} r={6} fill="none"
            stroke="white" strokeOpacity={0.1} strokeWidth={0.7} />
        </svg>
      </div>

      {/* Cluster popup — outside SVG so it can overflow the circle */}
      {clusterPopup && (
        <div className="absolute z-30 glass border border-nebula-purple/30 rounded-xl shadow-xl p-2 min-w-[180px]"
          style={{
            left: `calc(50% + ${(clusterPopup.sx - CX) / 400 * 100}% - 90px)`,
            top: `calc(${(clusterPopup.sy - CY + R + 20) / 400 * 100}% + 4px)`,
          }}
          onClick={(e) => e.stopPropagation()}
        >
          <p className="text-xs text-white/40 mb-1.5 px-1">{clusterPopup.pins.length} events here</p>
          {clusterPopup.pins.map(({ event }) => {
            const color = EVENT_COLOR[event.type] ?? '#fff'
            return (
              <button key={event.id}
                className="flex items-center gap-2 w-full text-left px-2 py-1.5 rounded-lg hover:bg-white/8 transition-colors"
                onClick={() => { setSelected(event); setClusterPopup(null) }}
              >
                <span className="w-2 h-2 rounded-full shrink-0" style={{ background: color }} />
                <span className="text-xs text-white/80 leading-tight">
                  {event.name.split(/[|—–]/)[0].trim()}
                </span>
              </button>
            )
          })}
        </div>
      )}

      {/* Controls */}
      <div className="shrink-0 pb-3 flex items-center gap-2 flex-wrap justify-center px-3">
        <div className="flex items-center gap-1.5 glass-sm px-3 py-1.5 text-xs text-white/50">
          <Compass className="w-3.5 h-3.5" />{heading}
        </div>
        <button onClick={toggleAR}
          className={clsx('flex items-center gap-2 px-3 py-1.5 glass-sm rounded-lg text-xs border transition-all',
            arMode
              ? 'border-nebula-purple/50 text-nebula-purple bg-nebula-purple/10'
              : 'border-white/10 text-white/50 hover:text-white hover:border-white/20')}>
          {cameraOn ? <CameraOff className="w-3.5 h-3.5" /> : <Camera className="w-3.5 h-3.5" />}
          {arMode ? 'Exit AR' : 'AR Mode'}
        </button>
        <button onClick={() => setShowLayers((v) => !v)}
          className={clsx('flex items-center gap-2 px-3 py-1.5 glass-sm rounded-lg text-xs border transition-all',
            showLayers
              ? 'border-nebula-purple/50 text-nebula-purple bg-nebula-purple/10'
              : 'border-white/10 text-white/50 hover:text-white hover:border-white/20')}>
          <Layers className="w-3.5 h-3.5" /> Layers
        </button>
        {!arMode && <span className="text-xs text-white/20">Drag to rotate</span>}
        {arMode && !compassAvail && (
          <span className="text-xs text-amber-400/60 flex items-center gap-1">
            <Info className="w-3 h-3" />No compass
          </span>
        )}
      </div>

      {/* Legend */}
      <div className="shrink-0 pb-3 flex items-center gap-3 flex-wrap justify-center px-4">
        {Object.entries(EVENT_COLOR).map(([type, color]) => (
          <div key={type} className="flex items-center gap-1">
            <span className="w-2 h-2 rounded-full" style={{ background: color }} />
            <span className="text-xs text-white/30 capitalize">{type.replace('_', ' ')}</span>
          </div>
        ))}
      </div>

      {selected && <EventModal event={selected} onClose={() => setSelected(null)} />}
    </div>
  )
}
