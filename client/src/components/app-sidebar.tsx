import { Link, useLocation } from "wouter";
import {
  Sidebar,
  SidebarContent,
  SidebarGroup,
  SidebarGroupContent,
  SidebarGroupLabel,
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
  SidebarHeader,
  SidebarFooter,
} from "@/components/ui/sidebar";
import { 
  LayoutDashboard, 
  Layers, 
  ShieldCheck, 
  FileCheck, 
  BarChart3,
  Compass,
  Settings,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { useTheme } from "./theme-provider";
import { Sun, Moon } from "lucide-react";

const mainNavItems = [
  {
    title: "Dashboard",
    url: "/",
    icon: LayoutDashboard,
  },
  {
    title: "Pattern Library",
    url: "/patterns",
    icon: Layers,
  },
  {
    title: "Validation",
    url: "/validation",
    icon: FileCheck,
  },
  {
    title: "Rules",
    url: "/rules",
    icon: ShieldCheck,
  },
  {
    title: "Analytics",
    url: "/analytics",
    icon: BarChart3,
  },
];

export function AppSidebar() {
  const [location] = useLocation();
  const { theme, toggleTheme } = useTheme();

  return (
    <Sidebar>
      <SidebarHeader className="border-b border-sidebar-border p-4">
        <Link href="/" className="flex items-center gap-3">
          <div className="flex items-center justify-center w-9 h-9 rounded-md bg-primary text-primary-foreground">
            <Compass className="w-5 h-5" />
          </div>
          <div className="flex flex-col">
            <span className="font-semibold text-base">Compass</span>
            <span className="text-xs text-muted-foreground">Architecture Validation</span>
          </div>
        </Link>
      </SidebarHeader>
      <SidebarContent>
        <SidebarGroup>
          <SidebarGroupLabel>Navigation</SidebarGroupLabel>
          <SidebarGroupContent>
            <SidebarMenu>
              {mainNavItems.map((item) => {
                const isActive = location === item.url || 
                  (item.url !== "/" && location.startsWith(item.url));
                return (
                  <SidebarMenuItem key={item.title}>
                    <SidebarMenuButton 
                      asChild 
                      isActive={isActive}
                      data-testid={`nav-${item.title.toLowerCase().replace(" ", "-")}`}
                    >
                      <Link href={item.url}>
                        <item.icon className="w-4 h-4" />
                        <span>{item.title}</span>
                      </Link>
                    </SidebarMenuButton>
                  </SidebarMenuItem>
                );
              })}
            </SidebarMenu>
          </SidebarGroupContent>
        </SidebarGroup>
      </SidebarContent>
      <SidebarFooter className="border-t border-sidebar-border p-4">
        <div className="flex items-center justify-between">
          <Button 
            variant="ghost" 
            size="icon"
            onClick={toggleTheme}
            data-testid="button-theme-toggle"
          >
            {theme === "light" ? (
              <Moon className="w-4 h-4" />
            ) : (
              <Sun className="w-4 h-4" />
            )}
          </Button>
          <Button variant="ghost" size="icon" data-testid="button-settings">
            <Settings className="w-4 h-4" />
          </Button>
        </div>
      </SidebarFooter>
    </Sidebar>
  );
}
