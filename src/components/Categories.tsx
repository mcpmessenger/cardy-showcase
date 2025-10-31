import { Headphones, Home, Sparkles, Shirt, Dumbbell, BookOpen } from "lucide-react";

const categories = [
  {
    name: "Electronics",
    icon: Headphones,
    count: 45,
    color: "from-blue-500 to-blue-600",
  },
  {
    name: "Home & Kitchen",
    icon: Home,
    count: 28,
    color: "from-green-500 to-green-600",
  },
  {
    name: "Beauty & Care",
    icon: Sparkles,
    count: 12,
    color: "from-pink-500 to-pink-600",
  },
  {
    name: "Fashion",
    icon: Shirt,
    count: 10,
    color: "from-purple-500 to-purple-600",
  },
  {
    name: "Sports & Fitness",
    icon: Dumbbell,
    count: 8,
    color: "from-orange-500 to-orange-600",
  },
  {
    name: "Books & Toys",
    icon: BookOpen,
    count: 5,
    color: "from-cyan-500 to-cyan-600",
  },
];

const Categories = () => {
  return (
    <section className="py-16 md:py-24">
      <div className="container mx-auto px-4">
        <div className="mb-12 text-center">
          <h2 className="mb-4 text-3xl font-bold md:text-4xl">Shop by Category</h2>
          <p className="text-lg text-muted-foreground">
            Browse our carefully curated collection across 6 categories
          </p>
        </div>

        <div className="grid grid-cols-2 gap-4 md:grid-cols-3 lg:grid-cols-6 lg:gap-6">
          {categories.map((category) => {
            const Icon = category.icon;
            return (
              <button
                key={category.name}
                className="group relative overflow-hidden rounded-2xl bg-card p-6 shadow-[var(--shadow-card)] transition-all duration-300 hover:-translate-y-1 hover:shadow-[var(--shadow-lg)]"
              >
                <div className={`mb-4 inline-flex h-16 w-16 items-center justify-center rounded-xl bg-gradient-to-br ${category.color} text-white shadow-lg transition-transform duration-300 group-hover:scale-110`}>
                  <Icon className="h-8 w-8" />
                </div>
                <h3 className="mb-1 text-base font-semibold">{category.name}</h3>
                <p className="text-sm text-muted-foreground">{category.count} products</p>
              </button>
            );
          })}
        </div>
      </div>
    </section>
  );
};

export default Categories;
