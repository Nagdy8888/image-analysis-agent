"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { Tag, Search } from "lucide-react";
import { ThemeToggle } from "./ThemeToggle";
import { cn } from "@/lib/utils";

export function Navbar() {
  const pathname = usePathname();

  return (
    <header className="sticky top-0 z-50 w-full border-b border-border/40 bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
      <div className="container flex h-14 items-center justify-between">
        <Link href="/" className="flex items-center gap-2 font-semibold">
          <Tag className="h-6 w-6" />
          <span>Image Tagger</span>
        </Link>
        <nav className="flex items-center gap-1">
          <Link
            href="/"
            className={cn(
              "flex items-center gap-2 rounded-md px-3 py-2 text-sm font-medium transition-colors hover:bg-accent hover:text-accent-foreground",
              pathname === "/" ? "bg-accent text-accent-foreground" : "text-muted-foreground"
            )}
          >
            <Tag className="h-4 w-4" />
            Tag Image
          </Link>
          <Link
            href="/search"
            className={cn(
              "flex items-center gap-2 rounded-md px-3 py-2 text-sm font-medium transition-colors hover:bg-accent hover:text-accent-foreground",
              pathname === "/search" ? "bg-accent text-accent-foreground" : "text-muted-foreground"
            )}
          >
            <Search className="h-4 w-4" />
            Search
          </Link>
          <ThemeToggle />
        </nav>
      </div>
    </header>
  );
}
