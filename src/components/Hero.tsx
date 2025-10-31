import { Search, ShoppingCart, Star } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";

const Hero = () => {
  return (
    <section className="relative overflow-hidden border-b bg-background py-20 md:py-32">
      <div className="container relative mx-auto px-4">
        <div className="mx-auto max-w-4xl text-center">
          <div className="mb-6 inline-flex items-center gap-2 rounded-full glass px-4 py-2 text-sm font-medium">
            <Star className="h-4 w-4" />
            <span>84 Curated Premium Products</span>
          </div>
          
          <h1 className="mb-6 text-4xl font-bold md:text-6xl lg:text-7xl">
            Shop Smart,
            <br />
            <span className="font-light">Live Better</span>
          </h1>
          
          <p className="mb-8 text-lg text-muted-foreground md:text-xl">
            Discover handpicked products from top brands on Amazon.
            <br />
            Quality guaranteed, shipped fast, backed by reviews.
          </p>

          <div className="mx-auto mb-10 max-w-2xl">
            <div className="flex gap-2">
              <div className="relative flex-1">
                <Search className="absolute left-4 top-1/2 h-5 w-5 -translate-y-1/2 text-muted-foreground" />
                <Input
                  type="search"
                  placeholder="Search products..."
                  className="h-14 glass-strong pl-12 pr-4 text-base"
                />
              </div>
              <Button size="lg" variant="default" className="h-14 px-8">
                Search
              </Button>
            </div>
          </div>

          <div className="flex flex-wrap items-center justify-center gap-6 text-muted-foreground">
            <div className="flex items-center gap-2">
              <div className="flex -space-x-2">
                <div className="h-8 w-8 rounded-full border-2 border-border bg-muted"></div>
                <div className="h-8 w-8 rounded-full border-2 border-border bg-muted"></div>
                <div className="h-8 w-8 rounded-full border-2 border-border bg-muted"></div>
              </div>
              <span className="text-sm font-medium">1000+ Happy Customers</span>
            </div>
            <div className="h-4 w-px bg-border"></div>
            <div className="flex items-center gap-2">
              <Star className="h-5 w-5" />
              <span className="text-sm font-medium">4.5 Average Rating</span>
            </div>
            <div className="h-4 w-px bg-border"></div>
            <div className="flex items-center gap-2">
              <ShoppingCart className="h-5 w-5" />
              <span className="text-sm font-medium">Fast Amazon Shipping</span>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};

export default Hero;
