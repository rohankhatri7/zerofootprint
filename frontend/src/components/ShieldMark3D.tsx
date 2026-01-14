import { useEffect, useMemo, useRef, useState } from "react";
import { Canvas, useFrame, useThree } from "@react-three/fiber";
import * as THREE from "three";
import { cn } from "@/lib/utils";

type ShieldMark3DProps = {
  size?: number;
  className?: string;
  speed?: number;
  intensity?: number;
  color?: string;
};

const DEFAULT_FOREGROUND = "#f3ede2";
const DEFAULT_ACCENT = "#76f0e1";
const LOOP_DURATION = 3.0;

function usePrefersReducedMotion() {
  const [prefersReducedMotion, setPrefersReducedMotion] = useState(false);

  useEffect(() => {
    const mediaQuery = window.matchMedia("(prefers-reduced-motion: reduce)");
    const updatePreference = () => setPrefersReducedMotion(mediaQuery.matches);

    updatePreference();

    if (mediaQuery.addEventListener) {
      mediaQuery.addEventListener("change", updatePreference);
      return () => mediaQuery.removeEventListener("change", updatePreference);
    }

    mediaQuery.addListener(updatePreference);
    return () => mediaQuery.removeListener(updatePreference);
  }, []);

  return prefersReducedMotion;
}

function useInView<T extends HTMLElement>(rootMargin = "0px") {
  const ref = useRef<T | null>(null);
  const [inView, setInView] = useState(true);

  useEffect(() => {
    const element = ref.current;
    if (!element || !("IntersectionObserver" in window)) {
      return;
    }

    const observer = new IntersectionObserver(
      (entries) => {
        const entry = entries[0];
        setInView(entry?.isIntersecting ?? true);
      },
      { rootMargin }
    );

    observer.observe(element);
    return () => observer.disconnect();
  }, [rootMargin]);

  return { ref, inView };
}

function isWebGLAvailable() {
  try {
    const canvas = document.createElement("canvas");
    return !!(
      canvas.getContext("webgl") || canvas.getContext("experimental-webgl")
    );
  } catch {
    return false;
  }
}

function easeInOutCubic(t: number) {
  return t < 0.5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2;
}

function easeOutCubic(t: number) {
  return 1 - Math.pow(1 - t, 3);
}

function createShieldShape() {
  const shape = new THREE.Shape();
  shape.moveTo(0, 1);
  shape.bezierCurveTo(0.55, 1, 1, 0.7, 1, 0.2);
  shape.bezierCurveTo(1, -0.4, 0.55, -0.86, 0, -1);
  shape.bezierCurveTo(-0.55, -0.86, -1, -0.4, -1, 0.2);
  shape.bezierCurveTo(-1, 0.7, -0.55, 1, 0, 1);
  return shape;
}

function StaticShieldMark({
  foreground,
  accent,
  className
}: {
  foreground: string;
  accent: string;
  className?: string;
}) {
  return (
    <svg
      width="100%"
      height="100%"
      viewBox="0 0 120 120"
      className={className}
      aria-hidden="true"
    >
      <defs>
        <linearGradient id="shield-stroke" x1="0" y1="0" x2="1" y2="1">
          <stop offset="0%" stopColor={foreground} stopOpacity="0.9" />
          <stop offset="100%" stopColor={foreground} stopOpacity="0.6" />
        </linearGradient>
      </defs>
      <path
        d="M60 10C78 10 98 18 98 40c0 22-18 44-38 52-20-8-38-30-38-52 0-22 20-30 38-30z"
        fill="none"
        stroke="url(#shield-stroke)"
        strokeWidth="6"
      />
      <circle
        cx="60"
        cy="52"
        r="18"
        fill="none"
        stroke={accent}
        strokeOpacity="0.85"
        strokeWidth="5"
      />
    </svg>
  );
}

function ShieldScene({
  foreground,
  accent,
  speed,
  intensity,
  isVisible
}: {
  foreground: string;
  accent: string;
  speed: number;
  intensity: number;
  isVisible: boolean;
}) {
  const groupRef = useRef<THREE.Group | null>(null);
  const ringRef = useRef<THREE.Mesh | null>(null);
  const glowRef = useRef<THREE.Mesh | null>(null);
  const particleMaterialRef = useRef<THREE.PointsMaterial | null>(null);
  const elapsedRef = useRef(0);

  const shape = useMemo(() => createShieldShape(), []);
  const shieldGeometry = useMemo(() => new THREE.ShapeGeometry(shape, 48), [shape]);
  const shieldPoints = useMemo(() => shape.getPoints(180), [shape]);
  const shieldLineGeometry = useMemo(() => {
    const geometry = new THREE.BufferGeometry().setFromPoints(shieldPoints);
    geometry.computeBoundingSphere();
    return geometry;
  }, [shieldPoints]);

  const ringGeometry = useMemo(() => new THREE.RingGeometry(0.36, 0.46, 64), []);
  const glowGeometry = useMemo(() => new THREE.RingGeometry(0.34, 0.52, 64), []);
  const particleGeometry = useMemo(() => {
    const count = 220;
    const positions = new Float32Array(count * 3);
    const angles = new Float32Array(count);
    const radii = new Float32Array(count);

    for (let i = 0; i < count; i += 1) {
      const angle = (i / count) * Math.PI * 2;
      angles[i] = angle + THREE.MathUtils.randFloat(-0.08, 0.08);
      radii[i] = THREE.MathUtils.randFloat(0.52, 0.6);
      positions[i * 3] = Math.cos(angles[i]) * radii[i];
      positions[i * 3 + 1] = Math.sin(angles[i]) * radii[i];
      positions[i * 3 + 2] = 0;
    }

    const geometry = new THREE.BufferGeometry();
    geometry.setAttribute("position", new THREE.BufferAttribute(positions, 3));
    geometry.setAttribute("angle", new THREE.BufferAttribute(angles, 1));
    geometry.setAttribute("radius", new THREE.BufferAttribute(radii, 1));
    return geometry;
  }, []);

  const shieldMaterial = useMemo(
    () =>
      new THREE.MeshStandardMaterial({
        color: foreground,
        transparent: true,
        opacity: 0.16,
        roughness: 0.3,
        metalness: 0.2
      }),
    [foreground]
  );

  const ringMaterial = useMemo(
    () =>
      new THREE.MeshStandardMaterial({
        color: foreground,
        transparent: true,
        opacity: 0.85,
        roughness: 0.25,
        metalness: 0.4
      }),
    [foreground]
  );

  const glowMaterial = useMemo(
    () =>
      new THREE.MeshBasicMaterial({
        color: accent,
        transparent: true,
        opacity: 0.0,
        blending: THREE.AdditiveBlending,
        depthWrite: false
      }),
    [accent]
  );

  useEffect(() => {
    return () => {
      shieldGeometry.dispose();
      shieldLineGeometry.dispose();
      ringGeometry.dispose();
      glowGeometry.dispose();
      particleGeometry.dispose();
      shieldMaterial.dispose();
      ringMaterial.dispose();
      glowMaterial.dispose();
    };
  }, [
    shieldGeometry,
    shieldLineGeometry,
    ringGeometry,
    glowGeometry,
    particleGeometry,
    shieldMaterial,
    ringMaterial,
    glowMaterial
  ]);

  useFrame((_, delta) => {
    if (!isVisible) {
      return;
    }

    const advance = delta * Math.max(speed, 0.2);
    elapsedRef.current += advance;
    const t = (elapsedRef.current % LOOP_DURATION) / LOOP_DURATION;

    const collapseStart = 0.18;
    const collapseEnd = 0.62;
    const recoverEnd = 0.78;

    let ringScale = 1;
    let collapseProgress = 0;

    if (t >= collapseStart && t <= collapseEnd) {
      const local = (t - collapseStart) / (collapseEnd - collapseStart);
      collapseProgress = easeInOutCubic(local);
      ringScale = 1 - 0.68 * collapseProgress;
    } else if (t > collapseEnd && t <= recoverEnd) {
      const local = (t - collapseEnd) / (recoverEnd - collapseEnd);
      ringScale = 0.32 + 0.68 * easeOutCubic(local);
    } else {
      ringScale = 1;
    }

    if (ringRef.current) {
      ringRef.current.scale.setScalar(ringScale);
    }

    if (glowRef.current) {
      const pulse =
        collapseProgress > 0
          ? Math.exp(-Math.pow((collapseProgress - 0.9) / 0.18, 2))
          : 0;
      glowMaterial.opacity = pulse * 0.85 * intensity;
      glowRef.current.scale.setScalar(ringScale + 0.1 + pulse * 0.25 * intensity);
    }

    if (particleMaterialRef.current) {
      const burstProgress =
        t >= collapseStart && t <= collapseEnd
          ? easeOutCubic(collapseProgress)
          : 0;
      particleMaterialRef.current.opacity = burstProgress * 0.9 * intensity;

      const positions = particleGeometry.attributes.position as THREE.BufferAttribute;
      const angles = particleGeometry.attributes.angle as THREE.BufferAttribute;
      const radii = particleGeometry.attributes.radius as THREE.BufferAttribute;

      for (let i = 0; i < positions.count; i += 1) {
        const angle = angles.getX(i);
        const baseRadius = radii.getX(i);
        const expanded = baseRadius + burstProgress * 0.35 * intensity;
        positions.setXYZ(i, Math.cos(angle) * expanded, Math.sin(angle) * expanded, 0);
      }

      positions.needsUpdate = true;
    }

    if (groupRef.current) {
      const breathe = Math.sin(elapsedRef.current * 0.8) * 0.015;
      groupRef.current.scale.setScalar(1 + breathe);
      groupRef.current.position.y = Math.sin(elapsedRef.current * 0.6) * 0.02;
    }
  });

  return (
    <group ref={groupRef}>
      <mesh geometry={shieldGeometry}>
        <primitive object={shieldMaterial} attach="material" />
      </mesh>
      <lineLoop geometry={shieldLineGeometry}>
        <lineBasicMaterial
          color={foreground}
          transparent
          opacity={0.9}
        />
      </lineLoop>
      <mesh ref={ringRef} geometry={ringGeometry} position={[0, 0.05, 0]}>
        <primitive object={ringMaterial} attach="material" />
      </mesh>
      <mesh ref={glowRef} geometry={glowGeometry} position={[0, 0.05, 0.01]}>
        <primitive object={glowMaterial} attach="material" />
      </mesh>
      <points geometry={particleGeometry} position={[0, 0.05, 0.02]}>
        <pointsMaterial
          ref={particleMaterialRef}
          color={accent}
          size={0.045}
          transparent
          opacity={0}
          blending={THREE.AdditiveBlending}
          depthWrite={false}
        />
      </points>
    </group>
  );
}

function AnimatedShieldCanvas({
  foreground,
  accent,
  speed,
  intensity,
  isVisible
}: {
  foreground: string;
  accent: string;
  speed: number;
  intensity: number;
  isVisible: boolean;
}) {
  const { invalidate } = useThree();

  useEffect(() => {
    if (isVisible) {
      invalidate();
    }
  }, [isVisible, invalidate]);

  return (
    <>
      <ambientLight intensity={0.55} />
      <directionalLight position={[3, 4, 5]} intensity={0.85} />
      <directionalLight position={[-4, -2, 6]} intensity={0.45} />
      <ShieldScene
        foreground={foreground}
        accent={accent}
        speed={speed}
        intensity={intensity}
        isVisible={isVisible}
      />
    </>
  );
}

export default function ShieldMark3D({
  size = 120,
  className,
  speed = 1,
  intensity = 1,
  color
}: ShieldMark3DProps) {
  const prefersReducedMotion = usePrefersReducedMotion();
  const { ref, inView } = useInView<HTMLDivElement>("120px");
  const [webglAvailable, setWebglAvailable] = useState(true);
  const [foreground, setForeground] = useState(color ?? DEFAULT_FOREGROUND);
  const [accent, setAccent] = useState(DEFAULT_ACCENT);

  useEffect(() => {
    setWebglAvailable(isWebGLAvailable());
  }, []);

  useEffect(() => {
    if (color) {
      setForeground(color);
      return;
    }

    const element = ref.current;
    if (!element) {
      return;
    }

    const styles = getComputedStyle(element);
    const cssForeground = styles.getPropertyValue("--brand-foreground").trim();
    const cssAccent = styles.getPropertyValue("--brand-accent").trim();

    if (cssForeground) {
      setForeground(cssForeground);
    }

    if (cssAccent) {
      setAccent(cssAccent);
    }
  }, [color, ref]);

  const sizeStyle = { width: `clamp(110px, 20vw, ${size}px)`, height: `clamp(110px, 20vw, ${size}px)` };

  if (!webglAvailable || prefersReducedMotion) {
    return (
      <div
        ref={ref}
        className={cn("flex items-center justify-center", className)}
        style={sizeStyle}
        aria-hidden="true"
      >
        <StaticShieldMark
          foreground={foreground}
          accent={accent}
          className="drop-shadow-[0_10px_30px_rgba(0,0,0,0.35)]"
        />
      </div>
    );
  }

  return (
    <div
      ref={ref}
      className={cn("flex items-center justify-center", className)}
      style={sizeStyle}
      aria-hidden="true"
    >
      <Canvas
        orthographic
        dpr={[1, 2]}
        frameloop={inView ? "always" : "demand"}
        camera={{ position: [0, 0, 6], zoom: 95 }}
        gl={{ antialias: true, alpha: true, preserveDrawingBuffer: false }}
      >
        <AnimatedShieldCanvas
          foreground={foreground}
          accent={accent}
          speed={speed}
          intensity={intensity}
          isVisible={inView}
        />
      </Canvas>
    </div>
  );
}
