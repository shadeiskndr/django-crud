import { Component, inject } from '@angular/core';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatTooltipModule } from '@angular/material/tooltip';
import { MatMenuModule } from '@angular/material/menu';
import { ThemeService, Theme } from '../services/theme.service';

@Component({
  selector: 'app-theme-toggle',
  template: `
    <button
      mat-icon-button
      [matMenuTriggerFor]="themeMenu"
      [matTooltip]="getTooltipText()"
      class="theme-toggle-button">
      <mat-icon>{{ getThemeIcon() }}</mat-icon>
    </button>

    <mat-menu #themeMenu="matMenu">
      <button
        mat-menu-item
        (click)="setTheme('light')"
        [class.active]="themeService.themeMode() === 'light'">
        <mat-icon>light_mode</mat-icon>
        <span>Light</span>
      </button>

      <button
        mat-menu-item
        (click)="setTheme('dark')"
        [class.active]="themeService.themeMode() === 'dark'">
        <mat-icon>dark_mode</mat-icon>
        <span>Dark</span>
      </button>

      <button
        mat-menu-item
        (click)="setTheme('auto')"
        [class.active]="themeService.themeMode() === 'auto'">
        <mat-icon>brightness_auto</mat-icon>
        <span>Auto ({{ themeService.getThemeInfo().isSystemDark ? 'Dark' : 'Light' }})</span>
      </button>
    </mat-menu>
  `,
  styles: [`
    .theme-toggle-button {
      transition: transform 0.2s ease-in-out;
    }
    .theme-toggle-button:hover {
      transform: scale(1.1);
    }
    .active {
      background-color: var(--mat-sys-primary-container);
      color: var(--mat-sys-on-primary-container);
    }
  `],
  imports: [
    MatButtonModule,
    MatIconModule,
    MatTooltipModule,
    MatMenuModule
  ]
})
export class ThemeToggleComponent {
  themeService = inject(ThemeService);

  setTheme(mode: Theme): void {
    this.themeService.setThemeMode(mode);
  }

  getThemeIcon(): string {
    const mode = this.themeService.themeMode();

    switch (mode) {
      case 'light':
        return 'light_mode';
      case 'dark':
        return 'dark_mode';
      case 'auto':
        return 'brightness_auto';
      default:
        return 'brightness_auto';
    }
  }

  getTooltipText(): string {
    const info = this.themeService.getThemeInfo();

    switch (info.mode) {
      case 'light':
        return 'Theme: Light';
      case 'dark':
        return 'Theme: Dark';
      case 'auto':
        return `Theme: Auto (${info.isSystemDark ? 'Dark' : 'Light'})`;
      default:
        return 'Theme settings';
    }
  }
}
