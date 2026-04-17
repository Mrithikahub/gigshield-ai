"use client";

import { usePathname } from 'next/navigation';
import { useEffect, useState, useRef } from 'react';
import Image from 'next/image';

export function PageTransition() {
  const pathname = usePathname();
  const [isTransitioning, setIsTransitioning] = useState(false);
  const [imgError, setImgError] = useState(false);
  const isFirstRender = useRef(true);

  useEffect(() => {
    if (isFirstRender.current) {
      isFirstRender.current = false;
      return;
    }

    setIsTransitioning(true);
    const timer = setTimeout(() => {
      setIsTransitioning(false);
    }, 2500);
    return () => clearTimeout(timer);
  }, [pathname]);

  if (!isTransitioning) return null;

  return (
    <div className="fixed inset-0 z-[9999] pointer-events-none">
      <div className="absolute inset-0 bg-black/75 transition-opacity duration-500 opacity-100" />
      <div className="absolute bottom-[8%] left-0 w-full animate-pageTransition">
        {!imgError ? (
          <div className="relative w-[220px] h-[140px]">
            <Image
              src="/delivery-scooter.png"
              alt="Delivery Partner"
              fill
              className="object-contain drop-shadow-2xl"
              onError={() => setImgError(true)}
            />
          </div>
        ) : (
          <div className="flex items-center gap-1 text-4xl select-none">
            🏍️💨
          </div>
        )}
      </div>
    </div>
  );
}
