import Hero from "@/components/Hero";
import Footer from "@/components/Footer";
import { Gallery4 } from "@/components/ui/gallery4";
import { Button } from "@/components/ui/button";
import { ThemeToggle } from "@/components/ui/theme-toggle";
import { useProducts, getProductsWithPhotos, productToGalleryItem } from "@/lib/products";
import { useMemo } from "react";

const Index = () => {
  const { products, isLoading } = useProducts();
  const featuredProducts = useMemo(() => {
    const featured = getProductsWithPhotos(products).slice(0, 40); // Limit to 40 for best mobile experience
    return featured.map((product, index) => productToGalleryItem(product, index));
  }, [products]);

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="sticky top-0 z-50 border-b glass-strong">
        <div className="container mx-auto flex h-14 sm:h-16 items-center justify-end px-4 sm:px-6">
          <ThemeToggle />
        </div>
      </header>

      <main>
        <Hero />
        {featuredProducts.length > 0 && (
          <Gallery4 
            title="Featured Products"
            description="Browse our products with high-quality photos and detailed images"
            items={featuredProducts}
          />
        )}
        
        {/* CTA Section */}
        <section className="border-t bg-background/80 backdrop-blur-md py-12 sm:py-16 md:py-20 dark:bg-background/60">
          <div className="container mx-auto px-4 sm:px-6 text-center">
            <h2 className="mb-3 sm:mb-4 text-2xl sm:text-3xl md:text-4xl font-bold">
              Ready to Find Your Perfect Product?
            </h2>
            <p className="mb-6 sm:mb-8 text-base sm:text-lg text-muted-foreground">
              Browse our full catalog of {isLoading ? "..." : products.length} premium products
            </p>
            <Button size="lg" variant="outline" className="backdrop-blur-sm" asChild>
              <a href="/products">View All Products</a>
            </Button>
          </div>
        </section>
      </main>
      <Footer />
    </div>
  );
};

export default Index;
