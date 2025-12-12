interface ViewportInfo {
  width: number;
  height: number;
  isMobile: boolean;
  isTablet: boolean;
  isDesktop: boolean;
  orientation: 'portrait' | 'landscape';
  devicePixelRatio: number;
  touchSupport: boolean;
}

class ViewportDetector {
  private listeners: ((info: ViewportInfo) => void)[] = [];
  private currentInfo: ViewportInfo;
  private resizeTimeout: NodeJS.Timeout | null = null;
  
  constructor() {
    this.currentInfo = this.getViewportInfo();
    this.initializeEventListeners();
  }
  
  /**
   * Initialize event listeners for viewport changes
   */
  private initializeEventListeners(): void {
    // Window resize
    window.addEventListener('resize', this.handleResize.bind(this));
    
    // Orientation change
    window.addEventListener('orientationchange', this.handleOrientationChange.bind(this));
    
    // Device pixel ratio change (for zoom detection)
    const mediaQuery = window.matchMedia(`(resolution: ${window.devicePixelRatio}dppx)`);
    if (mediaQuery) {
      mediaQuery.addEventListener('change', this.handlePixelRatioChange.bind(this));
    }
  }
  
  /**
   * Get current viewport information
   */
  private getViewportInfo(): ViewportInfo {
    const width = window.innerWidth || document.documentElement.clientWidth || document.body.clientWidth;
    const height = window.innerHeight || document.documentElement.clientHeight || document.body.clientHeight;
    
    // Device detection based on width and touch support
    const isMobile = width <= 768 || ('ontouchstart' in window);
    const isTablet = width > 768 && width <= 1024;
    const isDesktop = width > 1024;
    
    // Orientation detection
    const orientation = width > height ? 'landscape' : 'portrait';
    
    // Touch support detection
    const touchSupport = 'ontouchstart' in window || navigator.maxTouchPoints > 0;
    
    return {
      width,
      height,
      isMobile,
      isTablet,
      isDesktop,
      orientation,
      devicePixelRatio: window.devicePixelRatio || 1,
      touchSupport
    };
  }
  
  /**
   * Handle window resize events
   */
  private handleResize(): void {
    if (this.resizeTimeout) {
      clearTimeout(this.resizeTimeout);
    }
    
    this.resizeTimeout = setTimeout(() => {
      const newInfo = this.getViewportInfo();
      
      // Only notify if significant change
      if (this.hasSignificantChange(this.currentInfo, newInfo)) {
        this.currentInfo = newInfo;
        this.notifyListeners(newInfo);
      }
    }, 150); // Debounce resize events
  }
  
  /**
   * Handle orientation change events
   */
  private handleOrientationChange(): void {
    setTimeout(() => {
      const newInfo = this.getViewportInfo();
      
      if (this.currentInfo.orientation !== newInfo.orientation) {
        this.currentInfo = newInfo;
        this.notifyListeners(newInfo);
      }
    }, 100); // Allow time for orientation change to complete
  }
  
  /**
   * Handle device pixel ratio change (zoom)
   */
  private handlePixelRatioChange(): void {
    const newInfo = this.getViewportInfo();
    
    if (this.currentInfo.devicePixelRatio !== newInfo.devicePixelRatio) {
      this.currentInfo = newInfo;
      this.notifyListeners(newInfo);
    }
  }
  
  /**
   * Check if viewport change is significant enough to notify
   */
  private hasSignificantChange(oldInfo: ViewportInfo, newInfo: ViewportInfo): boolean {
    // Width change of more than 50px
    if (Math.abs(oldInfo.width - newInfo.width) > 50) {
      return true;
    }
    
    // Height change of more than 50px
    if (Math.abs(oldInfo.height - newInfo.height) > 50) {
      return true;
    }
    
    // Device type change
    if (oldInfo.isMobile !== newInfo.isMobile || 
        oldInfo.isTablet !== newInfo.isTablet || 
        oldInfo.isDesktop !== newInfo.isDesktop) {
      return true;
    }
    
    // Orientation change
    if (oldInfo.orientation !== newInfo.orientation) {
      return true;
    }
    
    return false;
  }
  
  /**
   * Notify all listeners of viewport changes
   */
  private notifyListeners(info: ViewportInfo): void {
    this.listeners.forEach(listener => {
      try {
        listener(info);
      } catch (error) {
        console.error('Error in viewport listener:', error);
      }
    });
  }
  
  /**
   * Add listener for viewport changes
   */
  public addListener(listener: (info: ViewportInfo) => void): void {
    this.listeners.push(listener);
    
    // Immediately call with current info
    try {
      listener(this.currentInfo);
    } catch (error) {
      console.error('Error in viewport listener:', error);
    }
  }
  
  /**
   * Remove listener for viewport changes
   */
  public removeListener(listener: (info: ViewportInfo) => void): void {
    const index = this.listeners.indexOf(listener);
    if (index > -1) {
      this.listeners.splice(index, 1);
    }
  }
  
  /**
   * Get current viewport information
   */
  public getCurrentInfo(): ViewportInfo {
    return { ...this.currentInfo };
  }
  
  /**
   * Check if current viewport is mobile
   */
  public isMobile(): boolean {
    return this.currentInfo.isMobile;
  }
  
  /**
   * Check if current viewport is tablet
   */
  public isTablet(): boolean {
    return this.currentInfo.isTablet;
  }
  
  /**
   * Check if current viewport is desktop
   */
  public isDesktop(): boolean {
    return this.currentInfo.isDesktop;
  }
  
  /**
   * Check if current orientation is landscape
   */
  public isLandscape(): boolean {
    return this.currentInfo.orientation === 'landscape';
  }
  
  /**
   * Check if current orientation is portrait
   */
  public isPortrait(): boolean {
    return this.currentInfo.orientation === 'portrait';
  }
  
  /**
   * Get device type string
   */
  public getDeviceType(): string {
    if (this.currentInfo.isMobile) {
      return 'mobile';
    } else if (this.currentInfo.isTablet) {
      return 'tablet';
    } else {
      return 'desktop';
    }
  }
  
  /**
   * Get responsive breakpoint
   */
  public getBreakpoint(): string {
    const width = this.currentInfo.width;
    
    if (width <= 480) {
      return 'xs';
    } else if (width <= 768) {
      return 'sm';
    } else if (width <= 1024) {
      return 'md';
    } else if (width <= 1200) {
      return 'lg';
    } else {
      return 'xl';
    }
  }
  
  /**
   * Check if touch is supported
   */
  public hasTouchSupport(): boolean {
    return this.currentInfo.touchSupport;
  }
  
  /**
   * Get optimal chat widget dimensions for current viewport
   */
  public getOptimalChatDimensions(): { width: string; height: string } {
    const { width, height, isMobile, isTablet } = this.currentInfo;
    
    if (isMobile) {
      return {
        width: '95%',
        height: Math.min(400, height * 0.8) + 'px'
      };
    } else if (isTablet) {
      return {
        width: Math.min(450, width * 0.6) + 'px',
        height: Math.min(500, height * 0.7) + 'px'
      };
    } else {
      return {
        width: Math.min(350, width * 0.4) + 'px',
        height: Math.min(500, height * 0.6) + 'px'
      };
    }
  }
  
  /**
   * Cleanup event listeners
   */
  public destroy(): void {
    window.removeEventListener('resize', this.handleResize.bind(this));
    window.removeEventListener('orientationchange', this.handleOrientationChange.bind(this));
    
    if (this.resizeTimeout) {
      clearTimeout(this.resizeTimeout);
    }
    
    this.listeners = [];
  }
}

// Factory function to create viewport detector (browser only)
export const createViewportDetector = (): ViewportDetector | null => {
  if (typeof window === 'undefined') {
    return null;
  }
  return new ViewportDetector();
};

// Export a default instance for compatibility (only in browser)
export const viewportDetector = createViewportDetector();