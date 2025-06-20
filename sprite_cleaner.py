import pygame
import pygame_gui
import os
import sys
import json
from typing import List, Tuple, Optional
from pathlib import Path

from spritesheet_model import SpritesheetModel, SpriteData, Point
from sprite_analysis import SpriteAnalyzer
from sprite_renderer import SpriteRenderer
from ui_components import (
    FileOperationsPanel, AnalysisControlsPanel, NavigationPanel,
    BoundingBoxInfoPanel, ViewControlsPanel, SubDiamondControlsPanel
)
from input_handlers import InputHandlers

# Initialize Pygame
pygame.init()

# Constants - Made 600 pixels wider
WINDOW_WIDTH = 2400  # Was 1800, now 2400
WINDOW_HEIGHT = 1200
LEFT_PANEL_WIDTH = 350
RIGHT_PANEL_WIDTH = 350
DRAWING_AREA_WIDTH = WINDOW_WIDTH - LEFT_PANEL_WIDTH - RIGHT_PANEL_WIDTH
DRAWING_AREA_HEIGHT = WINDOW_HEIGHT

DEFAULT_SPRITESHEET_DIR = r"C:\Users\Tommaso\Documents\Dev\IsoSpriter\isometric_tiles"
DEFAULT_SAVE_DIR = r"C:\Users\Tommaso\Documents\Dev\IsoSpriter\analysis_data"


class AdvancedSpritesheetUI:
    """Advanced UI with modular components - CLEAN MODULAR VERSION"""
    
    def __init__(self):
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Advanced Spritesheet Alpha Analyzer - CLEAN MODULAR")
        
        self.clock = pygame.time.Clock()
        self.manager = pygame_gui.UIManager((WINDOW_WIDTH, WINDOW_HEIGHT))
        
        # Core components
        self.model: Optional[SpritesheetModel] = None
        self.analyzer: Optional[SpriteAnalyzer] = None
        self.spritesheet_surface: Optional[pygame.Surface] = None
        
        # Initialize the renderer module
        self.renderer = SpriteRenderer(DRAWING_AREA_WIDTH, DRAWING_AREA_HEIGHT, LEFT_PANEL_WIDTH)
        
        # Initialize the input handlers
        self.input_handlers = InputHandlers(self)
        
        # UI state
        self.keys_pressed = set()
        
        # Mouse position tracking for pixeloid display
        self.mouse_x = 0
        self.mouse_y = 0
        self.sprite_pixel_x = 0
        self.sprite_pixel_y = 0
        self.mouse_in_drawing_area = False
        
        # Create UI panels
        self.setup_ui_panels()
        
        # Ensure save directory exists
        Path(DEFAULT_SAVE_DIR).mkdir(parents=True, exist_ok=True)
    
    def setup_ui_panels(self):
        """Set up all UI panels in both sidebars"""
        # Left sidebar panels
        current_y = 0
        
        self.file_ops_panel = FileOperationsPanel(self.manager, 0, current_y, LEFT_PANEL_WIDTH)
        current_y += self.file_ops_panel.height + 10
        
        self.analysis_controls_panel = AnalysisControlsPanel(self.manager, 0, current_y, LEFT_PANEL_WIDTH)
        current_y += self.analysis_controls_panel.height + 10
        
        self.navigation_panel = NavigationPanel(self.manager, 0, current_y, LEFT_PANEL_WIDTH)
        current_y += self.navigation_panel.height + 10
        
        self.bbox_info_panel = BoundingBoxInfoPanel(self.manager, 0, current_y, LEFT_PANEL_WIDTH)
        
        # Right sidebar panels
        right_start_x = LEFT_PANEL_WIDTH + DRAWING_AREA_WIDTH
        current_y = 0
        
        self.view_controls_panel = ViewControlsPanel(self.manager, right_start_x, current_y, RIGHT_PANEL_WIDTH)
        current_y += self.view_controls_panel.height + 10
        
        self.sub_diamond_panel = SubDiamondControlsPanel(self.manager, right_start_x, current_y, RIGHT_PANEL_WIDTH)
    
    def get_all_ui_elements(self):
        """Get all UI elements for event handling"""
        elements = {}
        
        # Collect from all panels
        for panel_name, panel in [
            ('file_ops', self.file_ops_panel),
            ('analysis', self.analysis_controls_panel),
            ('navigation', self.navigation_panel),
            ('bbox', self.bbox_info_panel),
            ('view', self.view_controls_panel),
            ('sub_diamond', self.sub_diamond_panel)
        ]:
            for element_name, element in panel.components.items():
                elements[f'{panel_name}_{element_name}'] = element
        
        return elements
    
    def load_spritesheet(self, path: str):
        """Load a spritesheet from file"""
        try:
            surface = pygame.image.load(path).convert_alpha()
            self.spritesheet_surface = surface
            
            # Clear cache when new spritesheet is loaded
            self.renderer._clear_sprite_display_cache()
            
            # Reset manual vertex state for new image
            self.renderer.manual_vertices = {}
            self.renderer.manual_vertex_mode = False
            self.analysis_controls_panel.components['manual_vertex_button'].set_text('Manual Vertex Mode: OFF')
            self.analysis_controls_panel.components['vertex_info_label'].visible = False
            
            # Reset UI inputs to default values for new file
            self.file_ops_panel.components['rows_input'].set_text('1')
            self.file_ops_panel.components['cols_input'].set_text('4')
            self.analysis_controls_panel.components['threshold_slider'].set_current_value(0)
            self.analysis_controls_panel.components['global_z_input'].set_text('0')
            self.analysis_controls_panel.components['frame_z_input'].set_text('0')
            
            print(f"Successfully loaded: {path}")
            return True
        except Exception as e:
            print(f"Failed to load spritesheet: {e}")
            return False
    
    def create_model_from_inputs(self, image_path: str):
        """Create a new model from current UI inputs"""
        try:
            rows = int(self.file_ops_panel.components['rows_input'].get_text())
            cols = int(self.file_ops_panel.components['cols_input'].get_text())
            
            if rows <= 0 or cols <= 0:
                print(f"Invalid grid size: {rows}x{cols}")
                return False
            
            if not self.spritesheet_surface:
                print("No spritesheet loaded")
                return False
            
            total_width = self.spritesheet_surface.get_width()
            total_height = self.spritesheet_surface.get_height()
            
            self.model = SpritesheetModel.create_from_image(
                image_path, rows, cols, total_width, total_height
            )
            
            # Apply current UI settings
            self.model.alpha_threshold = int(self.analysis_controls_panel.components['threshold_slider'].get_current_value())
            self.model.upper_z_offset = int(self.analysis_controls_panel.components['global_z_input'].get_text() or '0')
            self.model.show_overlay = True
            self.model.show_diamond_height = True
            
            # Create analyzer and load surface
            self.analyzer = SpriteAnalyzer(self.model)
            self.analyzer.load_spritesheet_surface(self.spritesheet_surface)
            
            # Reset UI state
            self.model.current_sprite_index = 0
            self.model.pixeloid_multiplier = 1
            self.model.pan_x = 0
            self.model.pan_y = 0
            
            # Clear cache when new model is created
            self.renderer._clear_sprite_display_cache()
            
            self.update_sprite_info()
            print(f"Created model with {len(self.model.sprites)} sprites ({rows}x{cols})")
            return True
            
        except ValueError as e:
            print(f"Invalid input values: {e}")
            return False
        except Exception as e:
            print(f"Error creating model: {e}")
            return False
    
    def update_sprite_info(self):
        """Update sprite information displays"""
        if not self.model or not self.analyzer:
            self.clear_sprite_info()
            return
        
        current_sprite = self.model.get_current_sprite()
        if not current_sprite:
            self.clear_sprite_info()
            return
        
        # Update sprite counter
        self.navigation_panel.components['sprite_info_label'].set_text(
            f'Sprite: {self.model.current_sprite_index + 1}/{len(self.model.sprites)}'
        )
        
        # Analyze current sprite if not already analyzed
        # BUT: Don't re-analyze if sprite has comprehensive diamond data loaded from JSON
        needs_analysis = (current_sprite.pixel_count is None and
                         not self._has_comprehensive_diamond_analysis(current_sprite))
        
        if needs_analysis:
            self.analyzer.analyze_sprite(self.model.current_sprite_index)
        
        # Update pixel count
        pixel_count = current_sprite.pixel_count or 0
        self.navigation_panel.components['pixel_count_label'].set_text(f'Pixels above threshold: {pixel_count}')
        
        # Update bounding box info
        if current_sprite.bbox:
            bbox = current_sprite.bbox
            self.bbox_info_panel.components['bbox_label'].set_text(
                f'Bounding Box:\nSize: {bbox.width}x{bbox.height}\nPosition: ({bbox.x}, {bbox.y})'
            )
            
            # Update size comparison
            savings_percent = current_sprite.calculate_savings_percent()
            original_size = current_sprite.original_size
            self.bbox_info_panel.components['size_info_label'].set_text(
                f'Original: {original_size[0]}x{original_size[1]}\n'
                f'Cropped: {bbox.width}x{bbox.height}\n'
                f'Savings: {savings_percent:.1f}%'
            )
        else:
            self.bbox_info_panel.components['bbox_label'].set_text('Bounding Box:\nNo pixels above threshold')
            original_size = current_sprite.original_size
            self.bbox_info_panel.components['size_info_label'].set_text(
                f'Original: {original_size[0]}x{original_size[1]}\nCropped: N/A\nSavings: N/A'
            )
        
        # Update frame-specific Z offset
        frame_z_offset = current_sprite.frame_upper_z_offset
        self.analysis_controls_panel.components['frame_z_input'].set_text(str(frame_z_offset))
    
    def _has_comprehensive_diamond_analysis(self, sprite):
        """Check if sprite has comprehensive diamond analysis data that shouldn't be overwritten"""
        if not sprite.diamond_info:
            return False
        
        # Check if we have meaningful sub-diamond data
        has_sub_diamond_data = False
        
        # Check lower diamond for sub-diamond data
        if (sprite.diamond_info.lower_diamond and
            hasattr(sprite.diamond_info.lower_diamond, 'sub_diamonds') and
            sprite.diamond_info.lower_diamond.sub_diamonds):
            
            # Check if any sub-diamond has actual properties (not all None)
            for sub_diamond in sprite.diamond_info.lower_diamond.sub_diamonds.values():
                if (sub_diamond.is_walkable is not None or
                    any(getattr(getattr(sub_diamond, edge_name, None), 'blocks_line_of_sight', None) is not None or
                        getattr(getattr(sub_diamond, edge_name, None), 'blocks_movement', None) is not None or
                        getattr(getattr(sub_diamond, edge_name, None), 'z_portal', None) is not None
                        for edge_name in ['north_west_edge', 'north_east_edge', 'south_west_edge', 'south_east_edge'])):
                    has_sub_diamond_data = True
                    break
        
        # Check upper diamond for sub-diamond data
        if (not has_sub_diamond_data and sprite.diamond_info.upper_diamond and
            hasattr(sprite.diamond_info.upper_diamond, 'sub_diamonds') and
            sprite.diamond_info.upper_diamond.sub_diamonds):
            
            for sub_diamond in sprite.diamond_info.upper_diamond.sub_diamonds.values():
                if (sub_diamond.is_walkable is not None or
                    any(getattr(getattr(sub_diamond, edge_name, None), 'blocks_line_of_sight', None) is not None or
                        getattr(getattr(sub_diamond, edge_name, None), 'blocks_movement', None) is not None or
                        getattr(getattr(sub_diamond, edge_name, None), 'z_portal', None) is not None
                        for edge_name in ['north_west_edge', 'north_east_edge', 'south_west_edge', 'south_east_edge'])):
                    has_sub_diamond_data = True
                    break
        
        # Check custom diamonds for sub-diamond data
        if (not has_sub_diamond_data and sprite.diamond_info.extra_diamonds):
            for custom_diamond in sprite.diamond_info.extra_diamonds.values():
                if (hasattr(custom_diamond, 'sub_diamonds') and custom_diamond.sub_diamonds):
                    for sub_diamond in custom_diamond.sub_diamonds.values():
                        if (sub_diamond.is_walkable is not None or
                            any(getattr(getattr(sub_diamond, edge_name, None), 'blocks_line_of_sight', None) is not None or
                                getattr(getattr(sub_diamond, edge_name, None), 'blocks_movement', None) is not None or
                                getattr(getattr(sub_diamond, edge_name, None), 'z_portal', None) is not None
                                for edge_name in ['north_west_edge', 'north_east_edge', 'south_west_edge', 'south_east_edge'])):
                            has_sub_diamond_data = True
                            break
                if has_sub_diamond_data:
                    break
        
        # Also check for custom diamonds existence (indicates loaded data)
        has_custom_diamonds = (sprite.diamond_info.extra_diamonds and
                               len(sprite.diamond_info.extra_diamonds) > 0)
        
        # Also check for manual vertices existence
        has_manual_vertices = (hasattr(sprite, 'has_manual_vertices') and sprite.has_manual_vertices)
        
        # Consider it comprehensive if it has sub-diamond data, custom diamonds, or manual vertices
        comprehensive = has_sub_diamond_data or has_custom_diamonds or has_manual_vertices
        
        if comprehensive:
            print(f"Sprite {getattr(sprite, 'sprite_index', '?')} has comprehensive analysis - skipping re-analysis")
            print(f"  Sub-diamond data: {has_sub_diamond_data}")
            print(f"  Custom diamonds: {has_custom_diamonds}")
            print(f"  Manual vertices: {has_manual_vertices}")
        
        return comprehensive
    
    def clear_sprite_info(self):
        """Clear all sprite information displays"""
        self.navigation_panel.components['sprite_info_label'].set_text('Sprite: 0/0')
        self.navigation_panel.components['pixel_count_label'].set_text('Pixels above threshold: 0')
        self.bbox_info_panel.components['bbox_label'].set_text('Bounding Box:\nN/A')
        self.bbox_info_panel.components['size_info_label'].set_text('Original: N/A\nCropped: N/A\nSavings: N/A')
    
    def run(self):
        """Main game loop - clean and simple"""
        running = True
        
        while running:
            time_delta = self.clock.tick(60) / 1000.0  # Convert to seconds as pygame_gui expects
            ui_elements = self.get_all_ui_elements()
            
            # Process events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame_gui.UI_BUTTON_PRESSED:
                    self.input_handlers.handle_button_press(event, ui_elements)
                elif event.type == pygame_gui.UI_HORIZONTAL_SLIDER_MOVED:
                    self.input_handlers.handle_slider_move(event, ui_elements)
                elif event.type == pygame_gui.UI_TEXT_ENTRY_FINISHED:
                    self.input_handlers.handle_text_change(event, ui_elements)
                elif event.type == pygame.MOUSEWHEEL:
                    self.input_handlers.handle_mouse_wheel(event)
                elif event.type == pygame.MOUSEMOTION:
                    self.input_handlers.handle_mouse_motion(event)
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:  # Left click
                        self.input_handlers.handle_left_click(event)
                    elif event.button == 3:  # Right click
                        self.input_handlers.handle_right_click(event)
                elif event.type == pygame.KEYDOWN:
                    self.keys_pressed.add(event.key)
                    # Handle manual vertex mode and sub-diamond key commands
                    self.input_handlers.handle_manual_vertex_keys(event.key)
                elif event.type == pygame.KEYUP:
                    self.keys_pressed.discard(event.key)
                
                self.manager.process_events(event)
            
            # Update systems
            self.manager.update(time_delta)
            self.input_handlers.update_panning(self.keys_pressed)
            
            # Update sub-diamond panel status
            if hasattr(self, 'sub_diamond_panel'):
                self.sub_diamond_panel.update_status(
                    self.renderer.sub_diamond_mode,
                    self.renderer.selected_sub_diamond_layer,
                    self.renderer.sub_diamond_editing_mode
                )
            
            # Draw everything
            self.screen.fill((40, 40, 40))
            pygame.draw.rect(self.screen, (60, 60, 60), (0, 0, LEFT_PANEL_WIDTH, WINDOW_HEIGHT))
            pygame.draw.rect(self.screen, (60, 60, 60), (LEFT_PANEL_WIDTH + DRAWING_AREA_WIDTH, 0, RIGHT_PANEL_WIDTH, WINDOW_HEIGHT))
            
            # Use renderer for sprite display
            self.renderer.draw_sprite_display(self.screen, self.model, self.analyzer, LEFT_PANEL_WIDTH)
            self.renderer.draw_mouse_position_display(self.screen, self.model, self.mouse_in_drawing_area,
                                                    self.sprite_pixel_x, self.sprite_pixel_y, WINDOW_WIDTH)
            self.manager.draw_ui(self.screen)
            pygame.display.flip()
        
        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    app = AdvancedSpritesheetUI()
    app.run()
