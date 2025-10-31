import Hero from "@/components/Hero";
import { Gallery4 } from "@/components/ui/gallery4";
import Categories from "@/components/Categories";
import TrustBadges from "@/components/TrustBadges";
import { ShoppingBag } from "lucide-react";
import { Button } from "@/components/ui/button";

const featuredProducts = [
  {
    id: "1",
    title: "Sony WH-1000XM5 Wireless Headphones",
    description: "Industry-leading noise canceling with premium sound quality. Perfect for music lovers and professionals.",
    href: "https://www.amazon.com/dp/B09XS7JWHH?tag=aipro00-20",
    image: "https://m.media-amazon.com/images/I/61+btxzpfDL._AC_SL1500_.jpg",
  },
  {
    id: "2",
    title: "Apple AirPods Pro (2nd Gen)",
    description: "Active noise cancellation, adaptive transparency, and personalized spatial audio for an immersive experience.",
    href: "https://www.amazon.com/dp/B0BDHWDR12?tag=aipro00-20",
    image: "https://m.media-amazon.com/images/I/61SUj2aKoEL._AC_SL1500_.jpg",
  },
  {
    id: "3",
    title: "Ninja Professional Blender",
    description: "1000-watt motor with Total Crushing Technology crushes ice, blends, purees, and controls processing.",
    href: "https://www.amazon.com/dp/B00NGV4506?tag=aipro00-20",
    image: "https://m.media-amazon.com/images/I/71S4N+KJZBL._AC_SL1500_.jpg",
  },
  {
    id: "4",
    title: "Instant Pot Duo 7-in-1",
    description: "Pressure cooker, slow cooker, rice cooker, steamer, sauté, yogurt maker & warmer all in one.",
    href: "https://www.amazon.com/dp/B00FLYWNYQ?tag=aipro00-20",
    image: "https://m.media-amazon.com/images/I/71V6q3LnzfL._AC_SL1500_.jpg",
  },
  {
    id: "5",
    title: "Fitbit Charge 6 Fitness Tracker",
    description: "Track your health and fitness with built-in GPS, heart rate monitoring, and 40+ exercise modes.",
    href: "https://www.amazon.com/dp/B0CC61S8FG?tag=aipro00-20",
    image: "https://m.media-amazon.com/images/I/61A0HbJ0PdL._AC_SL1500_.jpg",
  },
];

const Index = () => {
  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="sticky top-0 z-50 border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
        <div className="container mx-auto flex h-16 items-center justify-between px-4">
          <div className="flex items-center gap-2">
            <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-primary text-primary-foreground">
              <ShoppingBag className="h-6 w-6" />
            </div>
            <span className="text-xl font-bold">AIPro Store</span>
          </div>
          
          <nav className="hidden items-center gap-6 md:flex">
            <a href="#" className="text-sm font-medium transition-colors hover:text-primary">
              Home
            </a>
            <a href="#" className="text-sm font-medium transition-colors hover:text-primary">
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
        <TrustBadges />
        <Gallery4 
          title="Featured Products"
          description="Handpicked best sellers and premium picks from our catalog"
          items={featuredProducts}
        />
        <Categories />
        
        {/* CTA Section */}
        <section className="bg-gradient-to-br from-primary via-primary to-primary-glow py-20">
          <div className="container mx-auto px-4 text-center">
            <h2 className="mb-4 text-3xl font-bold text-white md:text-4xl">
              Ready to Find Your Perfect Product?
            </h2>
            <p className="mb-8 text-lg text-white/90">
              Browse our full catalog of 108 premium products
            </p>
            <Button size="lg" variant="secondary" className="shadow-lg">
              View All Products
            </Button>
          </div>
        </section>
      </main>

      {/* Footer */}
      <footer className="border-t bg-muted/30 py-12">
        <div className="container mx-auto px-4">
          <div className="grid gap-8 md:grid-cols-4">
            <div>
              <div className="mb-4 flex items-center gap-2">
                <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-primary text-primary-foreground">
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
