import { Shield, Truck, CreditCard, HeadphonesIcon } from "lucide-react";

const badges = [
  {
    icon: Shield,
    title: "Secure Shopping",
    description: "Your data is protected",
  },
  {
    icon: Truck,
    title: "Fast Shipping",
    description: "Amazon Prime eligible",
  },
  {
    icon: CreditCard,
    title: "Safe Payment",
    description: "100% secure checkout",
  },
  {
    icon: HeadphonesIcon,
    title: "24/7 Support",
    description: "Always here to help",
  },
];

const TrustBadges = () => {
  return (
    <section className="border-y bg-muted/30 py-12">
      <div className="container mx-auto px-4">
        <div className="grid grid-cols-2 gap-8 md:grid-cols-4">
          {badges.map((badge) => {
            const Icon = badge.icon;
            return (
              <div key={badge.title} className="flex flex-col items-center text-center">
                <div className="mb-4 inline-flex h-14 w-14 items-center justify-center rounded-full bg-primary/10 text-primary">
                  <Icon className="h-7 w-7" />
                </div>
                <h3 className="mb-1 font-semibold">{badge.title}</h3>
                <p className="text-sm text-muted-foreground">{badge.description}</p>
              </div>
            );
          })}
        </div>
      </div>
    </section>
  );
};

export default TrustBadges;
