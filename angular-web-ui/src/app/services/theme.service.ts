import { Injectable, signal, effect, PLATFORM_ID, inject, computed } from '@angular/core';
import { isPlatformBrowser } from '@angular/common';

export type Theme = 'light' | 'dark' | 'auto';

@Injectable({
  providedIn: 'root'
})
export class ThemeService {
  private platformId = inject(PLATFORM_ID);

  // Signal to track the selected theme mode
  themeMode = signal<Theme>('auto');

  // Signal to track system preference
  private systemPrefersDark = signal<boolean>(false);

  // Computed signal that determines the actual theme to apply
  isDarkMode = computed(() => {
    const mode = this.themeMode();

    switch (mode) {
      case 'dark':
        return true;
      case 'light':
        return false;
      case 'auto':
        return this.systemPrefersDark();
      default:
        return false;
    }
  });

  constructor() {
    if (isPlatformBrowser(this.platformId)) {
      this.initializeTheme();
      this.setupSystemPreferenceListener();
    }

    // Effect to apply theme changes to DOM
    effect(() => {
      if (isPlatformBrowser(this.platformId)) {
        this.applyTheme(this.isDarkMode());
      }
    });
  }

  private initializeTheme(): void {
    // Get saved theme mode from localStorage
    const savedThemeMode = localStorage.getItem('themeMode') as Theme;

    // Get initial system preference
    const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
    this.systemPrefersDark.set(prefersDark);

    // Set theme mode (default to 'auto' if nothing saved)
    this.themeMode.set(savedThemeMode || 'auto');
  }

  private setupSystemPreferenceListener(): void {
    // Create media query matcher
    const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');

    // Update signal when system preference changes
    const handleChange = (e: MediaQueryListEvent) => {
      this.systemPrefersDark.set(e.matches);
    };

    // Listen for changes (modern browsers)
    if (mediaQuery.addEventListener) {
      mediaQuery.addEventListener('change', handleChange);
    } else {
      // Fallback for older browsers
      mediaQuery.addListener(handleChange);
    }

    // Cleanup listener when service is destroyed
    // Note: In a real app, you might want to implement OnDestroy
    // and remove the listener, but services are typically singletons
  }

  // Toggle between the three modes
  toggleTheme(): void {
    const currentMode = this.themeMode();

    switch (currentMode) {
      case 'light':
        this.setThemeMode('dark');
        break;
      case 'dark':
        this.setThemeMode('auto');
        break;
      case 'auto':
        this.setThemeMode('light');
        break;
    }
  }

  // Set specific theme mode
  setThemeMode(mode: Theme): void {
    this.themeMode.set(mode);
    localStorage.setItem('themeMode', mode);
  }

  // Get current theme info for UI display
  getThemeInfo(): { mode: Theme; actualTheme: 'light' | 'dark'; isSystemDark: boolean } {
    return {
      mode: this.themeMode(),
      actualTheme: this.isDarkMode() ? 'dark' : 'light',
      isSystemDark: this.systemPrefersDark()
    };
  }

  private applyTheme(isDark: boolean): void {
    const htmlElement = document.documentElement;

    if (isDark) {
      htmlElement.classList.add('dark-theme');
    } else {
      htmlElement.classList.remove('dark-theme');
    }
  }
}
