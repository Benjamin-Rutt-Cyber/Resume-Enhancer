import React, { useRef, useEffect, useState } from 'react';

interface HeroAnimationProps {
  className?: string;
}

export const HeroAnimation: React.FC<HeroAnimationProps> = ({ className = '' }) => {
  const containerRef = useRef<HTMLDivElement>(null);
  const imgRef = useRef<HTMLImageElement>(null);
  const [hasPlayed, setHasPlayed] = useState(false);
  const [isVisible, setIsVisible] = useState(false);

  useEffect(() => {
    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting && !hasPlayed) {
            setIsVisible(true);
            setHasPlayed(true);
          }
        });
      },
      {
        threshold: 0.3,
        rootMargin: '0px',
      }
    );

    if (containerRef.current) {
      observer.observe(containerRef.current);
    }

    return () => {
      if (containerRef.current) {
        observer.unobserve(containerRef.current);
      }
    };
  }, [hasPlayed]);

  return (
    <div
      ref={containerRef}
      className={`hero-animation-container ${className}`}
      style={{
        display: 'flex',
        justifyContent: 'center',
        alignItems: 'center',
        width: '100%',
        maxWidth: '600px',
        opacity: isVisible ? 1 : 0,
        transform: isVisible ? 'translateY(0)' : 'translateY(20px)',
        transition: 'opacity 0.6s ease-out, transform 0.6s ease-out',
      }}
    >
      {isVisible && (
        <img
          ref={imgRef}
          src="/resume-animation.webp"
          alt="AI Resume Enhancement Animation"
          style={{
            width: '100%',
            height: 'auto',
            borderRadius: '20px',
            boxShadow: '0 25px 50px -12px rgba(0, 0, 0, 0.15)',
          }}
        />
      )}
    </div>
  );
};

export default HeroAnimation;
