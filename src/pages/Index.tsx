import Hero from "@/components/Hero";
import { Gallery4 } from "@/components/ui/gallery4";
import { ShoppingBag } from "lucide-react";
import { Button } from "@/components/ui/button";
import { getFeaturedProducts, productToGalleryItem, products } from "@/lib/products";
import { useMemo } from "react";

const Index = () => {
  const featuredProducts = useMemo(() => {
    const featured = getFeaturedProducts(8);
    return featured.map((product, index) => productToGalleryItem(product, index));
  }, []);

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="sticky top-0 z-50 border-b glass-strong">
        <div className="container mx-auto flex h-16 items-center justify-between px-4">
          <div className="flex items-center gap-2">
            <div className="flex h-10 w-10 items-center justify-center rounded-lg border bg-background">
              <ShoppingBag className="h-6 w-6" />
            </div>
            <span className="text-xl font-bold">AIPro Store</span>
          </div>
          
          <nav className="hidden items-center gap-6 md:flex">
            <a href="#" className="text-sm font-medium transition-colors hover:text-primary">
              Home
            </a>
            <a href="/products" className="text-sm font-medium transition-colors hover:text-primary">
              Products
            </a>
            <a href="#" className="text-sm font-medium transition-colors hover:text-primary">
              Categories
            </a>
            <a href="#" className="text-sm font-medium transition-colors hover:text-primary">
              About
            </a>
          </nav>

          <Button size="sm">Browse All</Button>
        </div>
      </header>

      <main>
        <Hero />
        <Gallery4 
          title="Featured Products"
          description="Handpicked best sellers and premium picks from our catalog"
          items={featuredProducts}
        />
        
        {/* CTA Section */}
        <section className="border-t bg-background/80 backdrop-blur-md py-20 dark:bg-background/60">
          <div className="container mx-auto px-4 text-center">
            <h2 className="mb-4 text-3xl font-bold md:text-4xl">
              Ready to Find Your Perfect Product?
            </h2>
            <p className="mb-8 text-lg text-muted-foreground">
              Browse our full catalog of {products.length} premium products
            </p>
            <Button size="lg" variant="outline" className="backdrop-blur-sm" asChild>
              <a href="/products">View All Products</a>
            </Button>
          </div>
        </section>
      </main>

      {/* Footer */}
      <footer className="border-t glass-subtle py-12">
        <div className="container mx-auto px-4">
          <div className="grid gap-8 md:grid-cols-4">
            <div>
              <div className="mb-4 flex items-center gap-2">
                <div className="flex h-8 w-8 items-center justify-center rounded-lg border bg-background">
                  <ShoppingBag className="h-5 w-5" />
                </div>
                <span className="font-bold">AIPro Store</span>
              </div>
              <p className="text-sm text-muted-foreground">
                Your trusted source for premium products from Amazon.
              </p>
            </div>
            
            <div>
              <h3 className="mb-4 font-semibold">Shop</h3>
              <ul className="space-y-2 text-sm text-muted-foreground">
                <li><a href="#" className="hover:text-foreground">All Products</a></li>
                <li><a href="#" className="hover:text-foreground">Best Sellers</a></li>
                <li><a href="#" className="hover:text-foreground">New Arrivals</a></li>
                <li><a href="#" className="hover:text-foreground">Deals</a></li>
              </ul>
            </div>
            
            <div>
              <h3 className="mb-4 font-semibold">Support</h3>
              <ul className="space-y-2 text-sm text-muted-foreground">
                <li><a href="#" className="hover:text-foreground">FAQ</a></li>
                <li><a href="#" className="hover:text-foreground">Shipping</a></li>
                <li><a href="#" className="hover:text-foreground">Returns</a></li>
                <li><a href="#" className="hover:text-foreground">Contact</a></li>
              </ul>
            </div>
            
            <div>
              <h3 className="mb-4 font-semibold">Legal</h3>
              <ul className="space-y-2 text-sm text-muted-foreground">
                <li><a href="#" className="hover:text-foreground">Privacy Policy</a></li>
                <li><a href="#" className="hover:text-foreground">Terms of Service</a></li>
                <li><a href="#" className="hover:text-foreground">Affiliate Disclosure</a></li>
              </ul>
            </div>
          </div>
          
          <div className="mt-12 border-t pt-8 text-center text-sm text-muted-foreground">
            <p>© 2025 AIPro Store. As an Amazon Associate, we earn from qualifying purchases.</p>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default Index;
