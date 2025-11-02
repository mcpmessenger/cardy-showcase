import { Link } from "react-router-dom";

const Footer = () => {
  return (
    <footer className="border-t bg-background py-8 sm:py-12">
      <div className="container mx-auto px-4 sm:px-6">
        <div className="grid grid-cols-1 gap-8 md:grid-cols-3">
          {/* Brand */}
          <div>
            <h3 className="mb-4 text-lg font-semibold">tubbyAI</h3>
            <p className="text-sm text-muted-foreground">
              Voice-powered shopping assistant. Find products faster with AI.
            </p>
          </div>

          {/* Quick Links */}
          <div>
            <h3 className="mb-4 text-lg font-semibold">Quick Links</h3>
            <ul className="space-y-2 text-sm">
              <li>
                <Link to="/products" className="text-muted-foreground hover:text-primary transition-colors">
                  All Products
                </Link>
              </li>
              <li>
                <Link to="/privacy" className="text-muted-foreground hover:text-primary transition-colors">
                  Privacy Policy
                </Link>
              </li>
              <li>
                <a 
                  href="mailto:privacy@tubbyai.com" 
                  className="text-muted-foreground hover:text-primary transition-colors"
                >
                  Contact Us
                </a>
              </li>
            </ul>
          </div>

          {/* Legal */}
          <div>
            <h3 className="mb-4 text-lg font-semibold">Legal</h3>
            <ul className="space-y-2 text-sm">
              <li>
                <Link to="/privacy" className="text-muted-foreground hover:text-primary transition-colors">
                  Privacy Policy
                </Link>
              </li>
              <li className="text-muted-foreground">
                Amazon Associates Participant
              </li>
            </ul>
          </div>
        </div>

        <div className="mt-8 border-t pt-8">
          <div className="flex flex-col items-center justify-between gap-4 sm:flex-row">
            <p className="text-xs text-muted-foreground text-center sm:text-left">
              © {new Date().getFullYear()} tubbyAI. All rights reserved.
            </p>
            <p className="text-xs text-muted-foreground text-center sm:text-right">
              Voice Assistant Store | Powered by AI
            </p>
          </div>
        </div>
      </div>
    </footer>
  );
};

export default Footer;

