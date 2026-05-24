"use client";

import { useEffect, useRef } from 'react';

type Particle = {
  x: number;
  y: number;
  vx: number;
  vy: number;
  baseX: number;
  baseY: number;
  radius: number;
  phase: number;
};

export default function ParticlesBackdrop() {
  const canvasRef = useRef<HTMLCanvasElement | null>(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    const pointer = { x: window.innerWidth * 0.5, y: window.innerHeight * 0.35, active: false };
    let scrollY = window.scrollY;
    let scrollVelocity = 0;
    let frame = 0;
    let lastTime = performance.now();
    let width = 0;
    let height = 0;

    const count = reducedMotion ? 28 : 84;
    const particles: Particle[] = [];

    function resize() {
      const dpr = Math.min(window.devicePixelRatio || 1, 2);
      width = window.innerWidth;
      height = window.innerHeight;
      canvas.width = Math.round(width * dpr);
      canvas.height = Math.round(height * dpr);
      canvas.style.width = `${width}px`;
      canvas.style.height = `${height}px`;
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0);

      if (!particles.length) {
        for (let index = 0; index < count; index += 1) {
          const baseX = Math.random() * width;
          const baseY = Math.random() * height;
          particles.push({
            x: baseX,
            y: baseY,
            vx: 0,
            vy: 0,
            baseX,
            baseY,
            radius: 0.8 + Math.random() * 1.8,
            phase: Math.random() * Math.PI * 2,
          });
        }
      }
    }

    function onPointerMove(event: PointerEvent) {
      pointer.x = event.clientX;
      pointer.y = event.clientY;
      pointer.active = true;
    }

    function onPointerLeave() {
      pointer.active = false;
    }

    function onScroll() {
      const nextScroll = window.scrollY;
      scrollVelocity = Math.max(-40, Math.min(40, nextScroll - scrollY));
      scrollY = nextScroll;
    }

    function draw(now: number) {
      const delta = Math.min(32, now - lastTime) / 16.667;
      lastTime = now;

      ctx.clearRect(0, 0, width, height);

      const pointerInfluenceX = pointer.active ? pointer.x : width * 0.5;
      const pointerInfluenceY = pointer.active ? pointer.y : height * 0.35;
      const pointerStrength = reducedMotion ? 0.00015 : 0.00055;
      const scrollStrength = reducedMotion ? 0.0015 : 0.0045;

      for (let index = 0; index < particles.length; index += 1) {
        const particle = particles[index];
        const driftX = Math.sin((now / 1000) + particle.phase) * (reducedMotion ? 0.04 : 0.2);
        const driftY = Math.cos((now / 1200) + particle.phase) * (reducedMotion ? 0.04 : 0.2);

        particle.vx += ((particle.baseX - particle.x) * 0.0003 + driftX) * delta;
        particle.vy += ((particle.baseY - particle.y) * 0.0003 + driftY + scrollVelocity * scrollStrength * 0.01) * delta;

        const dx = particle.x - pointerInfluenceX;
        const dy = particle.y - pointerInfluenceY;
        const distance = Math.max(80, Math.hypot(dx, dy));
        const pull = pointer.active ? pointerStrength / distance : 0.00008 / distance;

        particle.vx += dx * pull * delta * -1;
        particle.vy += dy * pull * delta * -1;

        particle.x += particle.vx * delta;
        particle.y += particle.vy * delta;

        particle.vx *= 0.92;
        particle.vy *= 0.92;

        if (particle.x < -20) particle.x = width + 20;
        if (particle.x > width + 20) particle.x = -20;
        if (particle.y < -20) particle.y = height + 20;
        if (particle.y > height + 20) particle.y = -20;
      }

      ctx.lineWidth = 1;
      for (let i = 0; i < particles.length; i += 1) {
        for (let j = i + 1; j < Math.min(particles.length, i + 4); j += 1) {
          const a = particles[i];
          const b = particles[j];
          const distance = Math.hypot(a.x - b.x, a.y - b.y);
          if (distance > 150) continue;

          ctx.strokeStyle = `rgba(255,255,255,${0.03 + (1 - distance / 150) * 0.1})`;
          ctx.beginPath();
          ctx.moveTo(a.x, a.y);
          ctx.lineTo(b.x, b.y);
          ctx.stroke();
        }
      }

      for (const particle of particles) {
        const pulse = 0.5 + Math.sin(now / 700 + particle.phase) * 0.1;
        ctx.fillStyle = `rgba(255,255,255,${0.15 + pulse * 0.35})`;
        ctx.beginPath();
        ctx.arc(particle.x, particle.y, particle.radius + pulse, 0, Math.PI * 2);
        ctx.fill();
      }

      frame = window.requestAnimationFrame(draw);
    }

    resize();
    window.addEventListener('resize', resize);
    window.addEventListener('mousemove', onPointerMove, { passive: true });
    window.addEventListener('mouseleave', onPointerLeave);
    window.addEventListener('scroll', onScroll, { passive: true });
    frame = window.requestAnimationFrame(draw);

    return () => {
      window.cancelAnimationFrame(frame);
      window.removeEventListener('resize', resize);
      window.removeEventListener('mousemove', onPointerMove);
      window.removeEventListener('mouseleave', onPointerLeave);
      window.removeEventListener('scroll', onScroll);
    };
  }, []);

  return <canvas ref={canvasRef} aria-hidden="true" className="pointer-events-none fixed inset-0 z-0 opacity-90 mix-blend-screen" />;
}