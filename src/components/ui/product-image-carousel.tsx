"use client";

import { useState, useRef, useEffect } from "react";
import { ChevronLeft, ChevronRight } from "lucide-react";
import { cn } from "@/lib/utils";
import type { Product } from "@/types/product";

interface ProductImageCarouselProps {
  product: Product;
  className?: string;
  showIndicators?: boolean;
  autoPlay?: boolean;
}

export function ProductImageCarousel({
  product,
  className,
  showIndicators = true,
  autoPlay = false,
}: ProductImageCarouselProps) {
  // Get images: prefer local_images, fallback to image_url if no local images
  // Limit to first 20 images max to prevent performance issues
  const MAX_IMAGES = 20;
  const allImages = product.local_images && product.local_images.length > 0 
    ? product.local_images 
    : (product.image_url ? [product.image_url] : []);
  const images = allImages.slice(0, MAX_IMAGES);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [touchStart, setTouchStart] = useState(0);
  const [touchEnd, setTouchEnd] = useState(0);
  const carouselRef = useRef<HTMLDivElement>(null);

  // Auto-play functionality
  useEffect(() => {
    if (!autoPlay || images.length <= 1) return;

    const interval = setInterval(() => {
      setCurrentIndex((prev) => (prev + 1) % images.length);
    }, 4000);

    return () => clearInterval(interval);
  }, [autoPlay, images.length]);

  const minSwipeDistance = 50;

  const onTouchStart = (e: React.TouchEvent) => {
    setTouchEnd(0);
    setTouchStart(e.targetTouches[0].clientX);
  };

  const onTouchMove = (e: React.TouchEvent) => {
    setTouchEnd(e.targetTouches[0].clientX);
  };

  const onTouchEnd = () => {
    if (!touchStart || !touchEnd) return;

    const distance = touchStart - touchEnd;
    const isLeftSwipe = distance > minSwipeDistance;
    const isRightSwipe = distance < -minSwipeDistance;

    if (isLeftSwipe && currentIndex < images.length - 1) {
      setCurrentIndex(currentIndex + 1);
    }
    if (isRightSwipe && currentIndex > 0) {
      setCurrentIndex(currentIndex - 1);
    }
  };

  const goToSlide = (index: number) => {
    setCurrentIndex(index);
  };

  const goToPrevious = () => {
    setCurrentIndex((prev) => (prev === 0 ? images.length - 1 : prev - 1));
  };

  const goToNext = () => {
    setCurrentIndex((prev) => (prev === images.length - 1 ? 0 : prev + 1));
  };

  if (images.length === 0) {
    return (
      <div className={cn("relative aspect-square overflow-hidden rounded-t-xl bg-muted", className)}>
        <img
          src="/placeholder.png"
          alt={product.name}
          className="h-full w-full object-cover"
        />
      </div>
    );
  }

  return (
    <div
      ref={carouselRef}
      className={cn("relative aspect-square overflow-hidden rounded-t-xl touch-pan-y", className)}
      onTouchStart={onTouchStart}
      onTouchMove={onTouchMove}
      onTouchEnd={onTouchEnd}
    >
      {/* Image Container */}
      <div
        className="flex h-full transition-transform duration-300 ease-in-out"
        style={{ transform: `translateX(-${currentIndex * 100}%)` }}
      >
        {images.map((img, index) => {
          // Handle different image URL formats
          let imageUrl: string;
          
          if (img.startsWith('product_media/')) {
            // Local image from public folder
            imageUrl = `/${img}`;
          } else if (img.startsWith('http://') || img.startsWith('https://')) {
            // Direct HTTP URL (Amazon images)
            imageUrl = img;
          } else if (img.startsWith('/')) {
            // Absolute path
            imageUrl = img;
          } else {
            // Fallback: treat as relative path or use image_url
            imageUrl = product.image_url || '/placeholder.png';
          }
          
          return (
            <div key={`${img}-${index}`} className="min-w-full flex-shrink-0">
              <img
                src={imageUrl}
                alt={`${product.name} - Image ${index + 1}`}
                className="h-full w-full object-cover"
                loading={index === 0 ? "eager" : "lazy"}
                onError={(e) => {
                  // Prevent infinite loop by checking if already on fallback
                  const currentSrc = e.currentTarget.src;
                  if (currentSrc.includes('placeholder.png')) {
                    return; // Already on placeholder, don't change again
                  }
                  
                  // Try fallback to image_url if not already using it
                  if (imageUrl !== product.image_url && product.image_url && !currentSrc.includes(product.image_url)) {
                    e.currentTarget.src = product.image_url;
                  } else {
                    e.currentTarget.src = '/placeholder.png';
                  }
                }}
              />
            </div>
          );
        })}
      </div>

      {/* Navigation Arrows (desktop only) */}
      {images.length > 1 && (
        <>
          <button
            onClick={goToPrevious}
            className="absolute left-2 top-1/2 -translate-y-1/2 rounded-full bg-black/50 p-2 text-white opacity-0 transition-opacity hover:bg-black/70 group-hover:opacity-100 md:opacity-30"
            aria-label="Previous image"
          >
            <ChevronLeft className="h-5 w-5" />
          </button>
          <button
            onClick={goToNext}
            className="absolute right-2 top-1/2 -translate-y-1/2 rounded-full bg-black/50 p-2 text-white opacity-0 transition-opacity hover:bg-black/70 group-hover:opacity-100 md:opacity-30"
            aria-label="Next image"
          >
            <ChevronRight className="h-5 w-5" />
          </button>
        </>
      )}

      {/* Indicators */}
      {showIndicators && images.length > 1 && (
        <div className="absolute bottom-2 left-1/2 flex -translate-x-1/2 gap-1.5">
          {images.map((_, index) => (
            <button
              key={index}
              onClick={() => goToSlide(index)}
              className={cn(
                "h-1.5 rounded-full transition-all",
                currentIndex === index
                  ? "w-6 bg-white"
                  : "w-1.5 bg-white/50 hover:bg-white/75"
              )}
              aria-label={`Go to image ${index + 1}`}
            />
          ))}
        </div>
      )}
    </div>
  );
}

