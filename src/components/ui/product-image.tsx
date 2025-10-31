import { useState } from "react";
import { getPlaceholderImage } from "@/lib/image-utils";
import { cn } from "@/lib/utils";

interface ProductImageProps {
  src: string;
  alt: string;
  className?: string;
  fallbackSrc?: string;
  category?: string;
  onError?: () => void;
  loading?: "lazy" | "eager";
}

/**
 * ProductImage component with automatic fallback handling
 * Handles broken images gracefully with placeholder fallback
 */
export function ProductImage({
  src,
  alt,
  className,
  fallbackSrc,
  category,
  onError,
  loading = "lazy",
}: ProductImageProps) {
  const [imageSrc, setImageSrc] = useState(src);
  const [hasError, setHasError] = useState(false);

  const handleError = () => {
    if (!hasError) {
      setHasError(true);
      // Try fallback, then placeholder
      if (fallbackSrc) {
        setImageSrc(fallbackSrc);
      } else {
        setImageSrc(getPlaceholderImage(category));
      }
      onError?.();
    }
  };

  return (
    <img
      src={imageSrc}
      alt={alt}
      className={cn("object-cover object-center", className)}
      onError={handleError}
      loading={loading}
      decoding="async"
    />
  );
}

/**
 * OptimizedProductImage with responsive images
 */
interface OptimizedProductImageProps extends ProductImageProps {
  width?: number;
  height?: number;
}

export function OptimizedProductImage({
  src,
  alt,
  className,
  width = 800,
  height,
  ...props
}: OptimizedProductImageProps) {
  return (
    <ProductImage
      src={src}
      alt={alt}
      className={className}
      {...props}
      // You can add width/height attributes for CLS prevention
      style={{
        aspectRatio: height ? `${width}/${height}` : undefined,
      }}
    />
  );
}

