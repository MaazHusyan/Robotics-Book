export interface TextSelection {
  text: string;
  range: {
    start: number;
    end: number;
    startOffset: number;
    endOffset: number;
  };
  context: {
    beforeText: string;
    afterText: string;
    fullContext: string;
  };
  metadata: {
    element: string;
    className: string;
    id: string;
  };
}

export interface TextSelectionEvent {
  type: 'text_selected';
  data: TextSelection;
  timestamp: number;
}

export interface TextClearEvent {
  type: 'text_cleared';
  timestamp: number;
}

export type TextSelectionListener = (event: TextSelectionEvent | TextClearEvent) => void;

class TextSelectionManager {
  private listeners: TextSelectionListener[] = [];
  private currentSelection: TextSelection | null = null;
  private selectionTimeout: NodeJS.Timeout | null = null;
  
  constructor() {
    this.initializeSelectionDetection();
  }
  
  /**
   * Initialize text selection detection on the page
   */
  private initializeSelectionDetection(): void {
    // Mouse up event for text selection
    document.addEventListener('mouseup', this.handleMouseUp.bind(this));
    
    // Touch end event for mobile
    document.addEventListener('touchend', this.handleTouchEnd.bind(this));
    
    // Selection change event (modern browsers)
    document.addEventListener('selectionchange', this.handleSelectionChange.bind(this));
    
    // Double click for word selection
    document.addEventListener('dblclick', this.handleDoubleClick.bind(this));
  }
  
  /**
   * Handle mouse up event
   */
  private handleMouseUp(event: MouseEvent): void {
    // Small delay to ensure selection is complete
    if (this.selectionTimeout) {
      clearTimeout(this.selectionTimeout);
    }
    
    this.selectionTimeout = setTimeout(() => {
      this.processSelection();
    }, 100);
  }
  
  /**
   * Handle touch end event for mobile devices
   */
  private handleTouchEnd(event: TouchEvent): void {
    if (this.selectionTimeout) {
      clearTimeout(this.selectionTimeout);
    }
    
    this.selectionTimeout = setTimeout(() => {
      this.processSelection();
    }, 200);
  }
  
  /**
   * Handle selection change event
   */
  private handleSelectionChange(event: Event): void {
    if (this.selectionTimeout) {
      clearTimeout(this.selectionTimeout);
    }
    
    this.selectionTimeout = setTimeout(() => {
      this.processSelection();
    }, 50);
  }
  
  /**
   * Handle double click for word selection
   */
  private handleDoubleClick(event: MouseEvent): void {
    setTimeout(() => {
      this.processSelection();
    }, 50);
  }
  
  /**
   * Process current text selection
   */
  private processSelection(): void {
    const selection = window.getSelection();
    
    if (!selection || selection.isCollapsed) {
      this.clearSelection();
      return;
    }
    
    const selectedText = selection.toString().trim();
    
    if (!selectedText || selectedText.length < 3) {
      this.clearSelection();
      return;
    }
    
    const range = selection.getRangeAt(0);
    if (!range) {
      return;
    }
    
    const textSelection: TextSelection = {
      text: selectedText,
      range: {
        start: range.startOffset,
        end: range.endOffset,
        startOffset: range.startOffset,
        endOffset: range.endOffset
      },
      context: this.extractContext(range),
      metadata: this.extractMetadata(range)
    };
    
    this.setSelection(textSelection);
  }
  
  /**
   * Extract context around selected text
   */
  private extractContext(range: Range): TextSelection['context'] {
    const container = range.commonAncestorContainer;
    const fullText = container.textContent || '';
    
    // Get surrounding context (100 characters before and after)
    const beforeText = fullText.substring(
      Math.max(0, range.startOffset - 100),
      range.startOffset
    );
    
    const afterText = fullText.substring(
      range.endOffset,
      Math.min(fullText.length, range.endOffset + 100)
    );
    
    return {
      beforeText: beforeText.trim(),
      afterText: afterText.trim(),
      fullContext: beforeText + range.toString() + afterText
    };
  }
  
  /**
   * Extract metadata from selection
   */
  private extractMetadata(range: Range): TextSelection['metadata'] {
    const container = range.commonAncestorContainer;
    
    return {
      element: container.tagName.toLowerCase(),
      className: container.className || '',
      id: container.id || ''
    };
  }
  
  /**
   * Set current selection and notify listeners
   */
  private setSelection(selection: TextSelection): void {
    this.currentSelection = selection;
    
    const event: TextSelectionEvent = {
      type: 'text_selected',
      data: selection,
      timestamp: Date.now()
    };
    
    this.notifyListeners(event);
  }
  
  /**
   * Clear current selection
   */
  private clearSelection(): void {
    if (this.currentSelection) {
      this.currentSelection = null;
      
      const event: TextClearEvent = {
        type: 'text_cleared',
        timestamp: Date.now()
      };
      
      this.notifyListeners(event);
    }
  }
  
  /**
   * Notify all listeners of selection events
   */
  private notifyListeners(event: TextSelectionEvent | TextClearEvent): void {
    this.listeners.forEach(listener => {
      try {
        listener(event);
      } catch (error) {
        console.error('Error in text selection listener:', error);
      }
    });
  }
  
  /**
   * Add listener for text selection events
   */
  public addListener(listener: TextSelectionListener): void {
    this.listeners.push(listener);
  }
  
  /**
   * Remove listener for text selection events
   */
  public removeListener(listener: TextSelectionListener): void {
    const index = this.listeners.indexOf(listener);
    if (index > -1) {
      this.listeners.splice(index, 1);
    }
  }
  
  /**
   * Get current selection
   */
  public getCurrentSelection(): TextSelection | null {
    return this.currentSelection;
  }
  
  /**
   * Check if there's an active selection
   */
  public hasActiveSelection(): boolean {
    return this.currentSelection !== null;
  }
  
  /**
   * Get selected text only
   */
  public getSelectedText(): string {
    return this.currentSelection ? this.currentSelection.text : '';
  }
  
  /**
   * Highlight selected text visually
   */
  public highlightSelection(): void {
    if (!this.currentSelection) {
      return;
    }
    
    const selection = window.getSelection();
    if (!selection || selection.rangeCount === 0) {
      return;
    }
    
    const range = selection.getRangeAt(0);
    if (!range) {
      return;
    }
    
    // Create highlight span
    const span = document.createElement('span');
    span.className = 'rag-chat-highlight';
    span.style.backgroundColor = '#ffeb3b';
    span.style.padding = '2px';
    span.style.borderRadius = '3px';
    
    try {
      // Surround the selected text with highlight
      range.surroundContents(span);
    } catch (error) {
      console.error('Failed to highlight selection:', error);
    }
  }
  
  /**
   * Remove all highlights
   */
  public removeHighlights(): void {
    const highlights = document.querySelectorAll('.rag-chat-highlight');
    highlights.forEach(highlight => {
      const parent = highlight.parentNode;
      if (parent) {
        parent.replaceChild(
          document.createTextNode(highlight.textContent || ''),
          highlight
        );
      }
    });
  }
  
  /**
   * Cleanup event listeners
   */
  public destroy(): void {
    document.removeEventListener('mouseup', this.handleMouseUp.bind(this));
    document.removeEventListener('touchend', this.handleTouchEnd.bind(this));
    document.removeEventListener('selectionchange', this.handleSelectionChange.bind(this));
    document.removeEventListener('dblclick', this.handleDoubleClick.bind(this));
    
    if (this.selectionTimeout) {
      clearTimeout(this.selectionTimeout);
    }
    
    this.listeners = [];
    this.currentSelection = null;
  }
}

// Factory function to create text selection manager (browser only)
export const createTextSelectionManager = (): TextSelectionManager | null => {
  if (typeof window === 'undefined') {
    return null;
  }
  return new TextSelectionManager();
};