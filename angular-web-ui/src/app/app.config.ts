import { MAT_ICON_DEFAULT_OPTIONS } from "@angular/material/icon";
import { ApplicationConfig, provideZoneChangeDetection } from '@angular/core';
import { provideRouter } from "@angular/router";
import { ThemeService } from "./services/theme.service";

export const appConfig: ApplicationConfig = {
  providers: [provideZoneChangeDetection({ eventCoalescing: true }), {
      provide: MAT_ICON_DEFAULT_OPTIONS,
      useValue: {
        fontSet: 'material-symbols-outlined',
      },
    }, provideRouter([]), ThemeService]
};
